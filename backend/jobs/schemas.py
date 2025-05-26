from ninja import Schema, ModelSchema
from typing import List, Optional, Any
from datetime import datetime
from .models import Job

class JobSchema(Schema):
    id: int
    title: str
    description: str
    location: str
    salary_range: str
    company_name: str
    posting_date: datetime
    expiration_date: datetime
    required_skills: List[str]
    is_active: bool
    is_scheduled: bool
    status: str

class JobCreateSchema(Schema):
    title: str
    description: str
    location: str
    salary_range: str
    company_name: str
    expiration_date: datetime
    required_skills: List[str] = []
    is_scheduled: Optional[bool] = False
    posting_date: Optional[datetime] = None
    
    def dict(self, **kwargs):
        """覆寫 dict 方法以提供額外的驗證邏輯"""
        data = super().dict(**kwargs)
        
        # 如果是 scheduled 職位但沒有提供 posting_date，這在 API 層會被處理
        # 這裡主要是提供數據結構
        
        return data

class JobUpdateSchema(Schema):
    title: Optional[str] = None
    description: Optional[str] = None
    location: Optional[str] = None
    salary_range: Optional[str] = None
    company_name: Optional[str] = None  # 包含此欄位以便 API 可以檢查並拒絕更改
    expiration_date: Optional[datetime] = None
    required_skills: Optional[List[str]] = None
    is_active: Optional[bool] = None
    is_scheduled: Optional[bool] = None
    posting_date: Optional[datetime] = None

class JobListSchema(Schema):
    id: int
    title: str
    company_name: str
    location: str
    posting_date: datetime
    expiration_date: datetime
    status: str
    required_skills: List[str]

class JobFilterSchema(Schema):
    title: Optional[str] = None
    description: Optional[str] = None
    company_name: Optional[str] = None
    location: Optional[str] = None
    salary_range: Optional[str] = None
    required_skills: Optional[str] = None # 假設技能是以逗號分隔的字串傳入
    status: Optional[str] = None # "Active", "Expired", "Scheduled"

class OrderSchema(Schema):
    order_by: Optional[str] = None # "posting_date", "-posting_date", "expiration_date", "-expiration_date"

class MessageSchema(Schema):
    message: str
