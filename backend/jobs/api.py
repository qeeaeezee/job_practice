import logging
import datetime
from ninja import Router
from ninja.pagination import paginate, PageNumberPagination
from ninja.params import Query
from typing import List, Optional
from django.shortcuts import get_object_or_404
from django.db.models import Q
from django.utils import timezone
from django.core.management import call_command

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
        try:
            # 檢查是否為字串類型
            if isinstance(posting_date_payload_str, str):
                # 嘗試解析 ISO 格式日期字串
                try:
                    posting_date_payload = datetime.datetime.fromisoformat(posting_date_payload_str.replace("Z", "+00:00"))
                    # 確保時間有時區信息
                    if posting_date_payload.tzinfo is None:
                        posting_date_payload = posting_date_payload.replace(tzinfo=datetime.timezone.utc)
                except ValueError:
                    # 如果無法解析為 ISO 格式，則使用當前時間
                    logger.error(f"Invalid ISO format for posting_date: {posting_date_payload_str}")
                    posting_date_payload = timezone.now()
            elif isinstance(posting_date_payload_str, datetime.datetime):
                # 如果已經是 datetime 對象，直接使用
                posting_date_payload = posting_date_payload_str
            else:
                # 其他類型，使用當前時間
                logger.error(f"Unsupported type for posting_date: {type(posting_date_payload_str)}")
                posting_date_payload = timezone.now()
        except Exception as e:
            # 捕捉所有其他錯誤
            logger.error(f"Error processing posting_date: {e}")
            posting_date_payload = timezone.now()

    now = timezone.now()
    if is_scheduled_payload is True:
        # 如果沒有提供發布日期，使用現有的（如果存在）
        if not posting_date_payload:
            if job.posting_date and job.posting_date > now:
                data["posting_date"] = job.posting_date
            else:
                # 如果要設為排程狀態，但沒提供未來的發布日期
                return 400, {"message": "Scheduled job posting_date must be in the future"}
        # 如果提供的發布日期已經過去，返回錯誤
        elif posting_date_payload <= now:
            return 400, {"message": "Scheduled job posting_date must be in the future"}
    elif is_scheduled_payload is False:
        data["posting_date"] = now
        data["is_scheduled"] = False
    elif is_scheduled_payload is None and posting_date_payload:
        if job.is_scheduled and posting_date_payload < now:
            data["posting_date"] = now
            data["is_scheduled"] = False
        elif not job.is_scheduled:
            data["posting_date"] = now
    
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

@router.post("/update-status", response={200: MessageSchema}, auth=jwt_auth)
def update_job_statuses(request):
    """手動觸發更新所有職缺狀態"""
    # 使用與命令相同的日誌記錄器，確保日誌一致性
    status_logger = logging.getLogger('jobs.management.commands.update_job_status')
    start_time = datetime.now()
    
    try:
        now = timezone.now()
        status_logger.info(f"手動API觸發更新職缺狀態，當前時間：{now}")
        status_logger.info(f"執行環境時間：{start_time.strftime('%Y-%m-%d %H:%M:%S')}")
        
        # 處理已到期的職缺（無論之前是什麼狀態）
        expired_jobs = Job.objects.filter(expiration_date__lt=now)
        expired_count = expired_jobs.update(is_active=False, is_scheduled=False)
        
        # 處理排程中但已到發布時間的職缺
        scheduled_jobs = Job.objects.filter(
            is_scheduled=True,
            posting_date__lte=now,
            expiration_date__gt=now
        )
        scheduled_count = scheduled_jobs.update(is_active=True, is_scheduled=False)
        
        # 確保所有活躍的職缺狀態正確
        active_jobs = Job.objects.filter(
            posting_date__lte=now,
            expiration_date__gt=now,
            is_active=True
        )
        active_count = active_jobs.count()
        
        total_updated = expired_count + scheduled_count
        
        # 計算執行時間
        execution_time = datetime.now() - start_time
        
        # 記錄到專用日誌
        status_logger.info(f"職缺狀態更新完成 - 已過期: {expired_count}, 轉為活躍: {scheduled_count}, 執行時間: {execution_time.total_seconds():.3f}秒")
        
        # 一般日誌
        logger.info(f"手動觸發更新職缺狀態: 共更新 {total_updated} 個職缺")
        
        return 200, {
            "message": f"成功更新 {total_updated} 個職缺狀態：{expired_count} 個已過期，{scheduled_count} 個轉為活躍，目前共有 {active_count} 個活躍職缺"
        }
    except Exception as e:
        status_logger.error(f"更新職缺狀態時發生錯誤: {str(e)}")
        logger.error(f"更新職缺狀態時發生錯誤: {str(e)}")
        return 200, {"message": f"更新職缺狀態時發生錯誤: {str(e)}"}
