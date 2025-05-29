from django.core.management.base import BaseCommand
from django.utils import timezone
from jobs.models import Job
import logging
from datetime import datetime

logger = logging.getLogger(__name__)

class Command(BaseCommand):
    help = '更新職缺狀態：將已經開始的 job 狀態改為 Active，已經到期的狀態改為 Expired，排程中的保持 Scheduled'

    def add_arguments(self, parser):
        parser.add_argument(
            '--silent',
            action='store_true',
            help='不輸出結果訊息',
        )

    def handle(self, *args, **options):
        start_time = datetime.now()
        now = timezone.now()
        updated_count = 0
        silent = options.get('silent', False)
        
        logger.info(f"開始更新職缺狀態，當前時間：{now}")
        logger.info(f"執行環境時間：{start_time.strftime('%Y-%m-%d %H:%M:%S')}")
        
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
        
        success_message = f'成功更新 {total_updated} 個職缺狀態：\n' \
            f'- {expired_count} 個職缺標記為已過期\n' \
            f'- {scheduled_count} 個排程職缺轉為活躍\n' \
            f'- 目前共有 {active_count} 個活躍職缺'
        
        # 計算執行時間
        execution_time = datetime.now() - start_time
        
        # 增加執行時間到日誌中
        extended_message = f"{success_message}\n" \
                          f"- 更新操作完成時間: {execution_time.total_seconds():.3f} 秒"
        
        # 輸出到控制台
        self.stdout.write(self.style.SUCCESS(extended_message))
        
        # 輸出到日誌
        logger.info(f"職缺狀態更新完成 - 已過期: {expired_count}, 轉為活躍: {scheduled_count}, 執行時間: {execution_time.total_seconds():.3f}秒")
        
        # 如果使用 --silent 參數，則返回數字，否則返回字符串信息
        if options.get('silent'):
            return total_updated  # 返回更新數量，方便外部函數使用
        else:
            return extended_message  # 返回成功信息
