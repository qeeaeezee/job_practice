import logging
from ninja import Router
from ninja.pagination import paginate, PageNumberPagination
from ninja.params import Query
from typing import List, Optional
from django.shortcuts import get_object_or_404
from django.db.models import Q
from django.utils import timezone

from .models import Job
from .schemas import JobSchema, JobCreateSchema, JobUpdateSchema, MessageSchema, JobFilterSchema, OrderSchema, JobListSchema
from user_auth.authentication import jwt_auth

logger = logging.getLogger(__name__)

router = Router()

@router.post("", response={201: JobSchema, 400: MessageSchema, 401: MessageSchema}, auth=jwt_auth)
def create_job(request, payload: JobCreateSchema):
    data = payload.dict()
    
    # 處理時區
    now = timezone.now()
    
    # 處理 scheduled 職位邏輯
    if data.get("is_scheduled", False):
        # Scheduled 職位必須有發布日期
        if not data.get("posting_date"):
            return 400, {"message": "Scheduled job must have a posting_date"}
        
        # 檢查發布日期是否在未來
        posting_date = data["posting_date"]
        if isinstance(posting_date, str):
            try:
                posting_date = timezone.datetime.fromisoformat(posting_date.replace("Z", "+00:00"))
            except ValueError:
                return 400, {"message": "Invalid posting_date format"}
        
        # 確保有時區資訊
        if posting_date.tzinfo is None:
            posting_date = timezone.make_aware(posting_date)
        
        if posting_date <= now:
            return 400, {"message": "Scheduled job posting_date must be in the future"}
        
        data["posting_date"] = posting_date
    else:
        # 非排程職位，設定發布日期為現在
        data["posting_date"] = now
        data["is_scheduled"] = False
    
    # 驗證到期日期
    expiration_date = data.get("expiration_date")
    if isinstance(expiration_date, str):
        try:
            expiration_date = timezone.datetime.fromisoformat(expiration_date.replace("Z", "+00:00"))
        except ValueError:
            return 400, {"message": "Invalid expiration_date format"}
    
    if expiration_date.tzinfo is None:
        expiration_date = timezone.make_aware(expiration_date)
    
    data["expiration_date"] = expiration_date
    
    # 檢查發布日期必須在到期日期之前
    if data["posting_date"] >= expiration_date:
        return 400, {"message": "Posting date must be before expiration date"}
    
    # 創建職位
    try:
        job = Job.objects.create(**data)
        logger.info(f"Created job: {job.title} (ID: {job.id}, Status: {job.status})")
        return 201, job
    except Exception as e:
        logger.error(f"Error creating job: {str(e)}")
        return 400, {"message": f"Error creating job: {str(e)}"}

@router.get("", response=List[JobListSchema], auth=jwt_auth)
@paginate(PageNumberPagination, page_size=10)
def list_jobs(
    request,
    title: Optional[str] = None,
    description: Optional[str] = None,
    company_name: Optional[str] = None,
    location: Optional[str] = None,
    salary_range: Optional[str] = None,
    required_skills: Optional[str] = None,
    status: Optional[str] = None,
    order_by: Optional[str] = None
):
    jobs = Job.objects.all()

    if title:
        jobs = jobs.filter(title__icontains=title)
    if description:
        jobs = jobs.filter(description__icontains=description)
    if company_name:
        jobs = jobs.filter(company_name__icontains=company_name)
    if location:
        jobs = jobs.filter(location__icontains=location)
    if salary_range:
        jobs = jobs.filter(salary_range__icontains=salary_range)
    if required_skills:
        skills = [skill.strip() for skill in required_skills.split(',') if skill.strip()]
        query = Q()
        for skill in skills:
            query &= Q(required_skills__icontains=skill)
        if query:
            jobs = jobs.filter(query)

    if status:
        now = timezone.now()
        if status.lower() == "active":
            # 活躍職位：is_active=True + 過了發布日期(或未設定) + 未過期
            jobs = jobs.filter(
                Q(is_active=True) &
                Q(posting_date__lte=now) &
                Q(expiration_date__gt=now) &
                Q(is_scheduled=False)  # 排程職位不能是活躍的
            )
        elif status.lower() == "expired":
            # 過期職位：過期日期已過
            jobs = jobs.filter(expiration_date__lt=now)
        elif status.lower() == "scheduled":
            # 排程職位：is_scheduled=True + 發布日期在未來
            jobs = jobs.filter(
                Q(is_scheduled=True) &
                Q(posting_date__gt=now)
            )

    logger.debug(f"Filtered order_by: {order_by}")
    if order_by:
        valid_order_fields = ["posting_date", "-posting_date", "expiration_date", "-expiration_date"]
        if order_by in valid_order_fields:
            jobs = jobs.order_by(order_by)
    else:
        jobs = jobs.order_by(*Job._meta.ordering)

    return jobs

@router.get("/{job_id}", response={200: JobSchema, 404: MessageSchema}, auth=jwt_auth)
def get_job(request, job_id: int):
    job = get_object_or_404(Job, id=job_id)
    return job

@router.put("/{job_id}", response={200: JobSchema, 400: MessageSchema, 404: MessageSchema}, auth=jwt_auth)
def update_job(request, job_id: int, payload: JobUpdateSchema):
    job = get_object_or_404(Job, id=job_id)
    data = payload.dict(exclude_unset=True)

    if "company_name" in data:
        return 400, {"message": "Company name cannot be changed."}

    current_posting_date = data.get("posting_date", job.posting_date)
    current_expiration_date = data.get("expiration_date", job.expiration_date)

    if isinstance(current_posting_date, str):
        current_posting_date = timezone.datetime.fromisoformat(current_posting_date.replace("Z", "+00:00"))
    if isinstance(current_expiration_date, str):
        current_expiration_date = timezone.datetime.fromisoformat(current_expiration_date.replace("Z", "+00:00"))

    if current_posting_date and current_expiration_date and current_posting_date >= current_expiration_date:
        return 400, {"message": "Posting date must be before expiration date."}

    is_scheduled_payload = data.get("is_scheduled")
    posting_date_payload_str = data.get("posting_date")
    posting_date_payload = None
    if posting_date_payload_str:
        posting_date_payload = timezone.datetime.fromisoformat(posting_date_payload_str.replace("Z", "+00:00"))

    if is_scheduled_payload is True:
        if not posting_date_payload:
            data["posting_date"] = job.posting_date if job.posting_date else timezone.now()
        elif posting_date_payload < timezone.now():
            data["posting_date"] = timezone.now()
    elif is_scheduled_payload is False:
        data["posting_date"] = timezone.now()
        data["is_scheduled"] = False
    elif is_scheduled_payload is None and posting_date_payload:
        if job.is_scheduled and posting_date_payload < timezone.now():
            data["posting_date"] = timezone.now()
            data["is_scheduled"] = False
        elif not job.is_scheduled:
             data["posting_date"] = timezone.now()
    
    # Convert datetime objects back to isoformat strings if they were converted for comparison
    if "posting_date" in data and isinstance(data["posting_date"], timezone.datetime):
        data["posting_date"] = data["posting_date"].isoformat()

    for attr, value in data.items():
        setattr(job, attr, value)
    
    job.save()
    job.refresh_from_db() # 確保 status 等 property 在返回前已更新
    return job

@router.delete("/{job_id}", response={204: None, 404: MessageSchema}, auth=jwt_auth)
def delete_job(request, job_id: int):
    job = get_object_or_404(Job, id=job_id)
    job.delete()
    return 204, None
