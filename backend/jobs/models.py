from django.db import models
from django.utils import timezone

# Create your models here.

class Job(models.Model):
    title = models.CharField(max_length=255)
    description = models.TextField()
    location = models.CharField(max_length=255)
    salary_range = models.CharField(max_length=255)  # 根據需求，未來可以改為 JSONField 或獨立的 SalaryRange 模型
    company_name = models.CharField(max_length=255)
    posting_date = models.DateTimeField(default=timezone.now)
    expiration_date = models.DateTimeField()
    required_skills = models.JSONField(default=list)  # 使用 JSONField 來儲存技能列表
    is_active = models.BooleanField(default=True)
    is_scheduled = models.BooleanField(default=False)

    def __str__(self):
        return self.title

    class Meta:
        ordering = ['-posting_date']

    @property
    def status(self):
        now = timezone.now()
        
        # 確保 posting_date 和 expiration_date 都有時區資訊
        posting_date = self.posting_date
        if posting_date and posting_date.tzinfo is None:
            posting_date = timezone.make_aware(posting_date)
            
        expiration_date = self.expiration_date
        if expiration_date and expiration_date.tzinfo is None:
            expiration_date = timezone.make_aware(expiration_date)
        
        if self.is_scheduled and posting_date and posting_date > now:
            return "Scheduled"
        # 檢查是否已過期，即使是 is_active=True，只要過期就算 Expired
        elif expiration_date and expiration_date < now:
            return "Expired"
        # 檢查是否有效，且 posting_date 已到或未設定 (代表立即發布)
        elif self.is_active and (posting_date is None or posting_date <= now):
            return "Active"
        else:
            return "Inactive" # 其他情況，例如 is_active=False 但未過期
