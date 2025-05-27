import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'job_platform.settings')
django.setup()

import pytest
from django.utils import timezone
from datetime import timedelta
from ninja.testing import TestClient
from job_platform.api import api
from jobs.models import Job
from django.contrib.auth import get_user_model

User = get_user_model()

test_client = TestClient(api)

@pytest.fixture
def client():
    return test_client

@pytest.fixture
def test_user_data():
    return {"username": "testuser", "password": "testpassword123"}

@pytest.fixture
def test_user(db, test_user_data):
    """創建一個測試用戶。"""
    try:
        user = User.objects.create_user(
            username=test_user_data["username"],
            password=test_user_data["password"]
        )
    except Exception:
        user = User.objects.get(username=test_user_data["username"])
    return user

@pytest.fixture
def authenticated_client(client, test_user):
    """提供一個已認證的 TestClient，包含有效的 JWT token。"""
    # 登入獲取 JWT token
    login_data = {
        "username": test_user.username,
        "password": "testpassword123"
    }
    response = client.post("/auth/login", json=login_data)
    assert response.status_code == 200, f"Login failed: {response.content}"
    
    token_data = response.json()
    access_token = token_data["access"]
    
    # 為客戶端設置 Authorization header
    client.headers = {"Authorization": f"Bearer {access_token}"}
    return client

# --- Authentication Tests --- #
@pytest.mark.django_db
def test_create_job_without_auth(client):
    """測試未認證時創建職位會返回 401"""
    expiration_dt = timezone.now() + timedelta(days=30)
    job_data = {
        "title": "Unauthorized Job",
        "description": "This should fail.",
        "location": "Remote",
        "salary_range": "100k-150k USD",
        "company_name": "No Auth Inc.",
        "expiration_date": expiration_dt.isoformat(),
        "required_skills": ["Python"],
        "is_scheduled": False,
    }
    response = client.post("/jobs", json=job_data)
    assert response.status_code == 401, response.content

@pytest.mark.django_db
def test_get_job_list_without_auth(client):
    """測試未認證時取得職位列表會返回 401"""
    response = client.get("/jobs")
    assert response.status_code == 401, response.content

@pytest.mark.django_db
def test_get_job_detail_without_auth(client):
    """測試未認證時取得職位詳情會返回 401"""
    expiration_dt = timezone.now() + timedelta(days=30)
    job = Job.objects.create(title="Test Job", description="Test", location="Test", 
                           salary_range="Test", company_name="Test Co.", expiration_date=expiration_dt)
    response = client.get(f"/jobs/{job.id}")
    assert response.status_code == 401, response.content

@pytest.mark.django_db
def test_update_job_without_auth(client):
    """測試未認證時更新職位會返回 401"""
    expiration_dt = timezone.now() + timedelta(days=30)
    job = Job.objects.create(title="Test Job", description="Test", location="Test", 
                           salary_range="Test", company_name="Test Co.", expiration_date=expiration_dt)
    update_data = {"title": "Updated Title"}
    response = client.put(f"/jobs/{job.id}", json=update_data)
    assert response.status_code == 401, response.content

@pytest.mark.django_db
def test_delete_job_without_auth(client):
    """測試未認證時刪除職位會返回 401"""
    expiration_dt = timezone.now() + timedelta(days=30)
    job = Job.objects.create(title="Test Job", description="Test", location="Test", 
                           salary_range="Test", company_name="Test Co.", expiration_date=expiration_dt)
    response = client.delete(f"/jobs/{job.id}")
    assert response.status_code == 401, response.content

# --- Job Creation Tests --- #
@pytest.mark.django_db
def test_create_job_success(authenticated_client):
    expiration_dt = timezone.now() + timedelta(days=30)
    job_data = {
        "title": "Software Engineer",
        "description": "Develop amazing software.",
        "location": "Remote",
        "salary_range": "100k-150k USD",
        "company_name": "Tech Solutions Inc.",
        "expiration_date": expiration_dt.isoformat(),
        "required_skills": ["Python", "Django"],
        "is_scheduled": False,
    }
    response = authenticated_client.post("/jobs", json=job_data)
    assert response.status_code == 201, response.content
    result = response.json()
    assert result["title"] == job_data["title"]
    assert result["company_name"] == job_data["company_name"]
    assert result["status"] == "Active" # 立即發布應為 Active
    assert Job.objects.count() == 1

@pytest.mark.django_db
def test_create_job_scheduled_success(authenticated_client):
    posting_dt = timezone.now() + timedelta(days=5)
    expiration_dt = timezone.now() + timedelta(days=35)
    job_data = {
        "title": "Scheduled Product Manager",
        "description": "Manage product lifecycle.",
        "location": "New York",
        "salary_range": "120k-160k USD",
        "company_name": "Innovate Corp.",
        "posting_date": posting_dt.isoformat(),
        "expiration_date": expiration_dt.isoformat(),
        "required_skills": ["Agile", "Roadmap"],
        "is_scheduled": True,
    }
    response = authenticated_client.post("/jobs", json=job_data)
    assert response.status_code == 201, response.content
    result = response.json()
    assert result["is_scheduled"] == True
    assert result["status"] == "Scheduled"
    assert Job.objects.count() == 1

@pytest.mark.django_db
def test_create_job_scheduled_past_posting_date(authenticated_client):
    # 排程日設為過去，API 應該拒絕並返回錯誤
    past_posting_dt = timezone.now() - timedelta(days=2)
    expiration_dt = timezone.now() + timedelta(days=30)
    job_data = {
        "title": "Scheduled Past Post Date",
        "description": "Should post now.",
        "location": "Remote",
        "salary_range": "60k-80k USD",
        "company_name": "Past Corp.",
        "posting_date": past_posting_dt.isoformat(),
        "expiration_date": expiration_dt.isoformat(),
        "required_skills": ["Planning"],
        "is_scheduled": True,
    }
    response = authenticated_client.post("/jobs", json=job_data)
    assert response.status_code == 400, response.content
    result = response.json()
    assert result["message"] == "Scheduled job posting_date must be in the future" 

@pytest.mark.django_db
def test_create_job_missing_posting_date_for_scheduled(authenticated_client):
    expiration_dt = timezone.now() + timedelta(days=30)
    job_data = {
        "title": "Scheduled Fail No Date",
        "description": "This should fail.",
        "location": "Remote",
        "salary_range": "50k-70k USD",
        "company_name": "Test Co.",
        "expiration_date": expiration_dt.isoformat(),
        "is_scheduled": True, # Scheduled but no posting_date
    }
    response = authenticated_client.post("/jobs", json=job_data)
    assert response.status_code == 400, response.content
    assert response.json()["message"] == "Scheduled job must have a posting_date"

@pytest.mark.django_db
def test_create_job_posting_date_after_expiration_date(authenticated_client):
    posting_dt = timezone.now() + timedelta(days=5)
    expiration_dt = timezone.now() + timedelta(days=3) # Expiration before posting
    job_data = {
        "title": "Date Logic Fail Create",
        "description": "This should fail due to date logic.",
        "location": "Remote",
        "salary_range": "50k-70k USD",
        "company_name": "Test Co.",
        "posting_date": posting_dt.isoformat(),
        "expiration_date": expiration_dt.isoformat(),
        "is_scheduled": True,
    }
    response = authenticated_client.post("/jobs", json=job_data)
    assert response.status_code == 400, response.content
    assert response.json()["message"] == "Posting date must be before expiration date"

# --- Job Retrieval Tests --- #
@pytest.mark.django_db
def test_get_job_list_empty(authenticated_client):
    response = authenticated_client.get("/jobs")
    assert response.status_code == 200, response.content
    assert response.json()["items"] == []
    assert response.json()["count"] == 0

@pytest.mark.django_db
def test_get_job_list_with_data(authenticated_client):
    now = timezone.now()
    exp1 = now + timedelta(days=30)
    exp2 = now + timedelta(days=60)
    # 創建時 posting_date 會自動設為 now (如果 is_scheduled=False)
    Job.objects.create(
        title="DevOps Engineer", description="Desc1", location="Austin", salary_range="110k", company_name="Cloud Ltd.", 
        posting_date=now - timedelta(days=2), expiration_date=exp1, required_skills=["AWS"]
    )
    Job.objects.create(
        title="Frontend Developer", description="Desc2", location="SF", salary_range="100k", company_name="WebWorks", 
        posting_date=now - timedelta(days=1), expiration_date=exp2, required_skills=["React"]
    )
    response = authenticated_client.get("/jobs")
    assert response.status_code == 200, response.content
    result = response.json()
    assert result["count"] == 2
    assert len(result["items"]) == 2
    # 預設排序是 -posting_date (最新的在前)
    assert result["items"][0]["title"] == "Frontend Developer"
    assert result["items"][1]["title"] == "DevOps Engineer"

@pytest.mark.django_db
def test_get_job_detail_success(authenticated_client):
    expiration_dt = timezone.now() + timedelta(days=30)
    job = Job.objects.create(title="Data Scientist", description="Analyze data.", location="Boston", salary_range="130k", company_name="Data Insights", expiration_date=expiration_dt)
    response = authenticated_client.get(f"/jobs/{job.id}")
    assert response.status_code == 200, response.content
    result = response.json()
    assert result["title"] == job.title

@pytest.mark.django_db
def test_get_job_detail_not_found(authenticated_client):
    response = authenticated_client.get("/jobs/99999") # Use a non-existent ID
    assert response.status_code == 404, response.content
    # 預期 django-ninja 對 get_object_or_404 返回的 HTTP 404 錯誤，其 body 可能是 {"detail": "Not found."}
    # 或根據我們的 MessageSchema，是 {"message": "Not Found"} (取決於 api.py 中的設定)
    # 在 api.py 中 get_job 使用了 `response={200: JobSchema, 404: MessageSchema}`
    # get_object_or_404(Job, id=job_id) 會引發 Http404，Ninja 會轉換它
    # 預設的 Ninja 404 響應是 {"detail": "Not found"}
    # 如果我們想自訂，需要在 api router 層級捕捉 Http404 並返回 MessageSchema
    # 目前的 api.py get_job 會讓 Ninja 自動處理 404
    assert response.json().get("detail") == "Not Found" # Ninja 的實際 404 訊息

# --- Job Update Tests --- #
@pytest.mark.django_db
def test_update_job_success(authenticated_client):
    job_posting_date = timezone.now() - timedelta(days=5)
    job_expiration_dt = timezone.now() + timedelta(days=30)
    job = Job.objects.create(title="Original Title", description="Original Desc", location="Original Location", 
                             salary_range="Original Salary", company_name="Original Company", 
                             posting_date=job_posting_date, expiration_date=job_expiration_dt, is_active=True)
    
    new_expiration_dt = timezone.now() + timedelta(days=60)
    update_data = {
        "title": "Updated Title",
        "description": "Updated Description",
        "location": "Updated Location",
        "salary_range": "Updated Salary",
        "expiration_date": new_expiration_dt.isoformat(),
        "required_skills": ["NewSkill1", "NewSkill2"],
        "is_active": False
    }
    response = authenticated_client.put(f"/jobs/{job.id}", json=update_data)
    assert response.status_code == 200, response.content
    result = response.json()
    assert result["title"] == "Updated Title"
    assert result["description"] == "Updated Description"
    assert result["location"] == "Updated Location"
    assert result["salary_range"] == "Updated Salary"
    assert result["company_name"] == "Original Company"  # 公司名稱不應改變
    assert result["is_active"] == False
    assert result["required_skills"] == ["NewSkill1", "NewSkill2"]
    # 驗證 status 是否變為 Inactive (因為 is_active=False)
    # 注意：PUT 操作後，result["status"] 應該是更新後的值
    # 需要確認 api.py 中的 update_job 是否在返回前更新了 status
    # job.refresh_from_db(fields=['status']) 這一行在 api.py 的 update_job 中是註解掉的
    # 如果沒有更新，Schema 可能會拿到舊的 status，或者 property 會即時計算
    # 讓我們假設 property 會即時計算
    updated_job = Job.objects.get(id=job.id)
    assert updated_job.status == "Inactive" # 驗證 DB 中的 status
    assert result["status"] == "Inactive" # 驗證 response 中的 status

@pytest.mark.django_db
def test_update_job_cannot_change_company_name(authenticated_client):
    expiration_dt = timezone.now() + timedelta(days=30)
    job = Job.objects.create(title="Test Job CoName", company_name="Immutable Inc.", expiration_date=expiration_dt, location="L", salary_range="S")
    update_data = {
        "title": "New Title CoName",
        "company_name": "TryToChangeItAnyway" # 嘗試更改公司名稱
    }
    response = authenticated_client.put(f"/jobs/{job.id}", json=update_data)
    assert response.status_code == 400, response.content
    assert response.json()["message"] == "Company name cannot be changed."
    job.refresh_from_db()
    assert job.company_name == "Immutable Inc."

@pytest.mark.django_db
def test_update_job_posting_date_after_expiration_date(authenticated_client):
    job = Job.objects.create(title="Date Logic Update", company_name="Date Corp", 
                             posting_date=timezone.now() - timedelta(days=1), 
                             expiration_date=timezone.now() + timedelta(days=10), location="L", salary_range="S")
    update_data = {
        "posting_date": (timezone.now() + timedelta(days=5)).isoformat(),
        "expiration_date": (timezone.now() + timedelta(days=3)).isoformat() # 到期日在發布日之前
    }
    response = authenticated_client.put(f"/jobs/{job.id}", json=update_data)
    assert response.status_code == 400, response.content
    assert response.json()["message"] == "Posting date must be before expiration date."

# --- Job Deletion Tests --- #
@pytest.mark.django_db
def test_delete_job_success(authenticated_client):
    expiration_dt = timezone.now() + timedelta(days=30)
    job = Job.objects.create(title="To Be Deleted Job", company_name="Temp Co.", expiration_date=expiration_dt, location="L", salary_range="S")
    response = authenticated_client.delete(f"/jobs/{job.id}")
    assert response.status_code == 204, response.content  # DELETE 成功應返回 204 No Content
    assert Job.objects.count() == 0

@pytest.mark.django_db
def test_delete_job_not_found(authenticated_client):
    response = authenticated_client.delete("/jobs/99999")
    assert response.status_code == 404, response.content
    assert response.json().get("detail") == "Not Found" # Ninja 實際 404

# --- Filtering and Ordering Tests --- #
@pytest.mark.django_db
def test_list_jobs_filter_by_title(authenticated_client):
    exp_dt = timezone.now() + timedelta(days=30)
    Job.objects.create(title="Senior Python Developer", company_name="CompA", expiration_date=exp_dt, location="L1", salary_range="S1", description="D1")
    Job.objects.create(title="Junior Java Developer", company_name="CompB", expiration_date=exp_dt, location="L2", salary_range="S2", description="D2")
    
    response = authenticated_client.get("/jobs?title=Python")
    assert response.status_code == 200, response.content
    result = response.json()
    assert result["count"] == 1
    assert result["items"][0]["title"] == "Senior Python Developer"

@pytest.mark.django_db
def test_list_jobs_filter_by_description(authenticated_client):
    exp_dt = timezone.now() + timedelta(days=30)
    Job.objects.create(title="T1", description="Looking for a Python expert.", company_name="CompA", expiration_date=exp_dt, location="L1", salary_range="S1")
    Job.objects.create(title="T2", description="We need a Java guru.", company_name="CompB", expiration_date=exp_dt, location="L2", salary_range="S2")
    
    response = authenticated_client.get("/jobs?description=expert")
    assert response.status_code == 200, response.content
    result = response.json()
    assert result["count"] == 1
    # JobListSchema 不包含 description，只驗證 title 
    assert result["items"][0]["title"] == "T1"

@pytest.mark.django_db
def test_list_jobs_filter_by_company_name(authenticated_client):
    exp_dt = timezone.now() + timedelta(days=30)
    Job.objects.create(title="T1", company_name="Alpha Corp", expiration_date=exp_dt, location="L1", salary_range="S1", description="D1")
    Job.objects.create(title="T2", company_name="Beta Inc", expiration_date=exp_dt, location="L2", salary_range="S2", description="D2")
    
    response = authenticated_client.get("/jobs?company_name=Alpha")
    assert response.status_code == 200, response.content
    result = response.json()
    assert result["count"] == 1
    assert result["items"][0]["company_name"] == "Alpha Corp"

@pytest.mark.django_db
def test_list_jobs_filter_by_status_active(authenticated_client):
    now = timezone.now()
    Job.objects.create(title="Active Job 1", company_name="ActiveCo", posting_date=now - timedelta(days=1), expiration_date=now + timedelta(days=10), is_active=True, is_scheduled=False, location="L1", salary_range="S1", description="D1")
    Job.objects.create(title="Expired Job 1", company_name="ExpiredCo", posting_date=now - timedelta(days=10), expiration_date=now - timedelta(days=1), is_active=True, is_scheduled=False, location="L2", salary_range="S2", description="D2")
    Job.objects.create(title="Scheduled Job 1", company_name="ScheduledCo", posting_date=now + timedelta(days=5), expiration_date=now + timedelta(days=15), is_active=True, is_scheduled=True, location="L3", salary_range="S3", description="D3")
    
    response = authenticated_client.get("/jobs?status=Active")
    assert response.status_code == 200, response.content
    result = response.json()
    assert result["count"] == 1
    assert result["items"][0]["title"] == "Active Job 1"

@pytest.mark.django_db
def test_list_jobs_filter_by_status_expired(authenticated_client):
    now = timezone.now()
    Job.objects.create(title="Active Job 2", company_name="ActiveCo2", posting_date=now - timedelta(days=1), expiration_date=now + timedelta(days=10), is_active=True, is_scheduled=False, location="L1", salary_range="S1", description="D1")
    Job.objects.create(title="Expired Job 2", company_name="ExpiredCo2", posting_date=now - timedelta(days=10), expiration_date=now - timedelta(days=1), is_active=True, is_scheduled=False, location="L2", salary_range="S2", description="D2")
    Job.objects.create(title="Scheduled Job 2", company_name="ScheduledCo2", posting_date=now + timedelta(days=5), expiration_date=now + timedelta(days=15), is_active=True, is_scheduled=True, location="L3", salary_range="S3", description="D3")
    
    response = authenticated_client.get("/jobs?status=Expired")
    assert response.status_code == 200, response.content
    result = response.json()
    assert result["count"] == 1
    assert result["items"][0]["title"] == "Expired Job 2"

@pytest.mark.django_db
def test_list_jobs_filter_by_status_scheduled(authenticated_client):
    now = timezone.now()
    Job.objects.create(title="Active Job 3", company_name="ActiveCo3", posting_date=now - timedelta(days=1), expiration_date=now + timedelta(days=10), is_active=True, is_scheduled=False, location="L1", salary_range="S1", description="D1")
    Job.objects.create(title="Expired Job 3", company_name="ExpiredCo3", posting_date=now - timedelta(days=10), expiration_date=now - timedelta(days=1), is_active=True, is_scheduled=False, location="L2", salary_range="S2", description="D2")
    Job.objects.create(title="Scheduled Job 3", company_name="ScheduledCo3", posting_date=now + timedelta(days=5), expiration_date=now + timedelta(days=15), is_active=True, is_scheduled=True, location="L3", salary_range="S3", description="D3")
    
    response = authenticated_client.get("/jobs?status=Scheduled")
    assert response.status_code == 200, response.content
    result = response.json()
    assert result["count"] == 1
    assert result["items"][0]["title"] == "Scheduled Job 3"

@pytest.mark.django_db
def test_list_jobs_order_by_posting_date(authenticated_client):
    now = timezone.now()
    Job.objects.create(title="Job Old Post", company_name="C1", posting_date=now - timedelta(days=5), expiration_date=now + timedelta(days=10), location="L1", salary_range="S1", description="D1")
    Job.objects.create(title="Job New Post", company_name="C2", posting_date=now - timedelta(days=1), expiration_date=now + timedelta(days=15), location="L2", salary_range="S2", description="D2")
    
    # Ascending posting_date (oldest first)
    response_asc = authenticated_client.get("/jobs?order_by=posting_date")
    assert response_asc.status_code == 200, response_asc.content
    result_asc = response_asc.json()
    assert result_asc["count"] == 2
    assert result_asc["items"][0]["title"] == "Job Old Post"
    assert result_asc["items"][1]["title"] == "Job New Post"

    # Descending posting_date (newest first - default if Meta.ordering is used and no order_by param)
    response_desc = authenticated_client.get("/jobs?order_by=-posting_date")
    assert response_desc.status_code == 200, response_desc.content
    result_desc = response_desc.json()
    assert result_desc["count"] == 2
    assert result_desc["items"][0]["title"] == "Job New Post"
    assert result_desc["items"][1]["title"] == "Job Old Post"

@pytest.mark.django_db
def test_list_jobs_order_by_expiration_date(authenticated_client):
    now = timezone.now()
    Job.objects.create(title="Job Expires Sooner", company_name="C1", expiration_date=now + timedelta(days=5), posting_date=now - timedelta(days=2), location="L1", salary_range="S1", description="D1")
    Job.objects.create(title="Job Expires Later", company_name="C2", expiration_date=now + timedelta(days=10), posting_date=now - timedelta(days=1), location="L2", salary_range="S2", description="D2")
    
    response_asc = authenticated_client.get("/jobs?order_by=expiration_date") # Ascending
    assert response_asc.status_code == 200, response_asc.content
    result_asc = response_asc.json()
    assert result_asc["count"] == 2
    assert result_asc["items"][0]["title"] == "Job Expires Sooner"
    assert result_asc["items"][1]["title"] == "Job Expires Later"

    response_desc = authenticated_client.get("/jobs?order_by=-expiration_date") # Descending
    assert response_desc.status_code == 200, response_desc.content
    result_desc = response_desc.json()
    assert result_desc["count"] == 2
    assert result_desc["items"][0]["title"] == "Job Expires Later"
    assert result_desc["items"][1]["title"] == "Job Expires Sooner"

@pytest.mark.django_db
def test_list_jobs_filter_by_required_skills(authenticated_client):
    exp_dt = timezone.now() + timedelta(days=30)
    Job.objects.create(title="Dev Python", required_skills=["Python", "API"], company_name="CompP", expiration_date=exp_dt, location="L1", salary_range="S1", description="D1")
    Job.objects.create(title="Dev Java", required_skills=["Java", "Spring"], company_name="CompJ", expiration_date=exp_dt, location="L2", salary_range="S2", description="D2")
    Job.objects.create(title="Dev Fullstack Python", required_skills=["Python", "React", "API"], company_name="CompFP", expiration_date=exp_dt, location="L3", salary_range="S3", description="D3")

    # Single skill
    response_py = authenticated_client.get("/jobs?required_skills=Python")
    assert response_py.status_code == 200, response_py.content
    result_py = response_py.json()
    assert result_py["count"] == 2
    titles_py = {item["title"] for item in result_py["items"]}
    assert "Dev Python" in titles_py
    assert "Dev Fullstack Python" in titles_py

    # Multiple skills (AND logic)
    response_py_api = authenticated_client.get("/jobs?required_skills=Python,API")
    assert response_py_api.status_code == 200, response_py_api.content
    result_py_api = response_py_api.json()
    assert result_py_api["count"] == 2 # Both have Python and API
    titles_py_api = {item["title"] for item in result_py_api["items"]}
    assert "Dev Python" in titles_py_api
    assert "Dev Fullstack Python" in titles_py_api
    
    response_py_react = authenticated_client.get("/jobs?required_skills=Python,React")
    assert response_py_react.status_code == 200, response_py_react.content
    result_py_react = response_py_react.json()
    assert result_py_react["count"] == 1
    assert result_py_react["items"][0]["title"] == "Dev Fullstack Python"

# --- Pagination Test --- #
@pytest.mark.django_db
def test_list_jobs_pagination(authenticated_client):
    exp_dt = timezone.now() + timedelta(days=30)
    for i in range(15):
        Job.objects.create(title=f"Job {i+1}", company_name=f"Comp {i+1}", expiration_date=exp_dt, 
                           location=f"Loc {i+1}", salary_range="S", description=f"D {i+1}",
                           posting_date=timezone.now() - timedelta(days=15-i) # Ensure consistent ordering for test
                           )
    
    # Default page size is 10 (as per api.py @paginate)
    response_page1 = authenticated_client.get("/jobs?page=1")
    assert response_page1.status_code == 200, response_page1.content
    result_page1 = response_page1.json()
    assert result_page1["count"] == 15
    assert len(result_page1["items"]) == 10
    assert result_page1["items"][0]["title"] == "Job 15" # Newest first by posting_date

    response_page2 = authenticated_client.get("/jobs?page=2")
    assert response_page2.status_code == 200, response_page2.content
    result_page2 = response_page2.json()
    assert result_page2["count"] == 15
    assert len(result_page2["items"]) == 5
    assert result_page2["items"][0]["title"] == "Job 5"

    # Test with a different page size
    response_page_size = authenticated_client.get("/jobs?page=1&page_size=7")
    assert response_page_size.status_code == 200, response_page_size.content
    result_page_size = response_page_size.json()
    assert result_page_size["count"] == 15
    assert len(result_page_size["items"]) == 7
