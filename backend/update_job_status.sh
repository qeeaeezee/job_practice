#!/bin/bash
# 執行職缺狀態更新命令的腳本

# 切換到腳本所在目錄
SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" &> /dev/null && pwd )"
cd $SCRIPT_DIR

# 顯示當前時間
echo "開始執行職缺狀態更新 $(date)"

# 啟用虛擬環境並執行命令
source venv/bin/activate
python manage.py update_job_status
echo "更新完成時間：$(date)"

# 說明
echo ""
echo "此腳本可手動執行進行職缺狀態更新"
echo "也可以通過呼叫 API 端點 /api/jobs/update-status 來更新狀態"
