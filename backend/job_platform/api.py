from ninja import NinjaAPI
from jobs.api import router as jobs_router
from user_auth.api import router as auth_router

api = NinjaAPI(
    title="Job Platform API",
    description="API for managing job postings. Spec: https://django-ninja.dev/guides/api-docs/",
    version="1.0.0",
    docs_url="/docs/"
)

api.add_router("/auth", auth_router, tags=["Authentication"])
api.add_router("/jobs", jobs_router, tags=["jobs"])
