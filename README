# Job Platform Backend API

這是一個基於 Django 和 Django Ninja 構建的職位管理平台後端 API。

## 🚀 功能特色

### 核心功能
- **完整的職位管理 CRUD 操作**
- **JWT 認證系統**
- **搜尋和過濾功能**
- **分頁支援**
- **職位排程功能**
- **API 文檔自動生成 (OpenAPI)**

### 技術棧
- **框架**: Django 5.2 + Django Ninja
- **認證**: Django Ninja JWT
- **資料庫**: SQLite
- **測試**: Pytest + pytest-django
- **API 文檔**: OpenAPI (Swagger)
- **驗證**: Django Ninja Schema

## 📁 專案目錄架構

```
exercise/
├── backend/
│   ├── job_platform/           # Django 專案主目錄
│   │   ├── __init__.py
│   │   ├── settings.py         # Django 設定檔
│   │   ├── urls.py             # 主路由配置
│   │   ├── api.py              # API 路由聚合
│   │   ├── wsgi.py             # WSGI 部署配置
│   │   └── asgi.py             # ASGI 部署配置
│   ├── jobs/                   # 職位管理應用程式
│   │   ├── __init__.py
│   │   ├── admin.py            # Django Admin 配置
│   │   ├── apps.py             # 應用程式配置
│   │   ├── models.py           # 資料模型
│   │   ├── schemas.py          # API Schema 定義
│   │   ├── api.py              # 職位相關 API 端點
│   │   ├── tests.py            # 完整的 API 測試
│   │   └── migrations/         # 資料庫遷移檔案
│   │       ├── __init__.py
│   │       └── 0001_initial.py
│   ├── user_auth/              # 認證應用程式
│   │   ├── __init__.py
│   │   ├── apps.py             # 應用程式配置
│   │   ├── api.py              # 認證相關 API 端點
│   │   ├── schemas.py          # 認證 Schema 定義
│   │   ├── authentication.py   # JWT 認證處理
│   │   ├── tests.py            # 認證測試
│   │   └── migrations/         # 資料庫遷移檔案
│   │       └── __init__.py
│   ├── manage.py               # Django 管理工具
│   ├── requirements.txt        # Python 依賴套件
│   ├── pytest.ini             # Pytest 配置
│   ├── db.sqlite3              # SQLite 資料庫
│   └── venv/                   # Python 虛擬環境
```

## 🛠️ 環境設置

### 系統需求
- Python 3.8+
- pip
- virtualenv (建議)

### 安裝步驟

1. **複製專案並進入目錄**
```bash
cd /home/eric/code/exercise/backend
```

2. **創建並啟動虛擬環境**
```bash
python3 -m venv venv
source venv/bin/activate
```

3. **安裝依賴套件**
```bash
pip install -r requirements.txt
```

4. **執行資料庫遷移**
```bash
source venv/bin/activate && python3 manage.py migrate
```

5. **創建超級用戶 (可選)**
```bash
source venv/bin/activate && python3 manage.py createsuperuser
```

6. **啟動開發服務器**
```bash
source venv/bin/activate && python3 manage.py runserver 8000
```

## 📚 API 端點

### 認證端點
| 方法 | 端點 | 描述 | 認證需求 |
|------|------|------|----------|
| POST | `/api/auth/register` | 用戶註冊 | ❌ |
| POST | `/api/auth/login` | 用戶登入 | ❌ |
| POST | `/api/auth/refresh` | 刷新 Token | ❌ |

### 職位管理端點
| 方法 | 端點 | 描述 | 認證需求 |
|------|------|------|----------|
| POST | `/api/jobs` | 創建職位 | ✅ |
| GET | `/api/jobs` | 取得職位列表 | ✅ |
| GET | `/api/jobs/{id}` | 取得職位詳情 | ✅ |
| PUT | `/api/jobs/{id}` | 更新職位 | ✅ |
| DELETE | `/api/jobs/{id}` | 刪除職位 | ✅ |

### 查詢參數

#### GET /api/jobs 支援的參數：
- **搜尋**: `title`, `description`, `company_name`, `location`, `salary_range`
- **過濾**: `status` (active, expired, scheduled), `required_skills`
- **排序**: `order_by` (posting_date, -posting_date, expiration_date, -expiration_date)
- **分頁**: 自動分頁，每頁 10 筆

#### 範例查詢：
```bash
GET /api/jobs?title=engineer&status=active&order_by=-posting_date
GET /api/jobs?required_skills=Python,Django&location=Remote
```

## 🗄️ 資料模型

### Job (職位)
```python
{
  "id": 1,
  "title": "Software Engineer",           # 職位標題
  "description": "Develop applications",  # 職位描述
  "location": "Remote",                   # 工作地點
  "salary_range": "100k-150k USD",       # 薪資範圍
  "company_name": "Tech Corp",            # 公司名稱
  "posting_date": "2025-01-01T00:00:00Z", # 發布日期
  "expiration_date": "2025-02-01T00:00:00Z", # 到期日期
  "required_skills": ["Python", "Django"], # 技能要求
  "is_active": true,                      # 是否啟用
  "is_scheduled": false,                  # 是否為排程職位
  "status": "Active"                      # 職位狀態 (Active/Expired/Scheduled)
}
```

## 🔐 認證系統

使用 JWT (JSON Web Token) 進行 API 認證：

1. **註冊/登入**取得 access_token
2. **在 HTTP Header 中包含**: `Authorization: Bearer <access_token>`
3. **Token 過期時**使用 refresh_token 更新

## 🧪 測試

### 運行所有測試
```bash
source venv/bin/activate && python3 -m pytest jobs/tests.py -v
source venv/bin/activate && python3 -m pytest user_auth/tests.py -v
```

### 測試覆蓋範圍
- ✅ **認證測試**: 註冊、登入、未認證訪問
- ✅ **職位 CRUD 測試**: 創建、讀取、更新、刪除
- ✅ **搜尋和過濾測試**: 各種查詢參數
- ✅ **排程職位測試**: 排程邏輯驗證
- ✅ **分頁測試**: 分頁功能驗證
- ✅ **錯誤處理測試**: 各種錯誤狀況

## 📖 API 文檔

啟動服務器後，可以在以下位置查看自動生成的 API 文檔：

- **Swagger UI**: http://127.0.0.1:8000/api/docs
- **OpenAPI JSON**: http://127.0.0.1:8000/api/openapi.json

## 🔧 開發工具

### Django Admin
訪問 Django Admin 管理介面：
```bash
# 創建超級用戶
source venv/bin/activate && python3 manage.py createsuperuser

# 訪問 Admin: http://127.0.0.1:8000/admin/
```

### 資料庫管理
```bash
# 檢視 migrations 狀態
source venv/bin/activate && python3 manage.py showmigrations

# 生成新的 migrations
source venv/bin/activate && python3 manage.py makemigrations

# 執行 migrations
source venv/bin/activate && python3 manage.py migrate
```

## 🚀 部署考量

### 生產環境建議
- 使用 PostgreSQL 替代 SQLite
- 設定環境變數 (`DJANGO_SETTINGS_MODULE`, `SECRET_KEY`)
- 使用 Gunicorn + Nginx
- 啟用 HTTPS
- 配置日誌系統

### 環境變數範例
```bash
export DJANGO_SETTINGS_MODULE=job_platform.settings
export SECRET_KEY=your-secret-key
export DEBUG=False
```