import logging
from ninja import Router
from django.contrib.auth import authenticate
from django.contrib.auth.models import User
from django.db import IntegrityError
from ninja_jwt.tokens import RefreshToken

from .schemas import (
    UserRegisterSchema, 
    UserLoginSchema, 
    UserSchema, 
    TokenSchema, 
    TokenRefreshSchema,
    MessageSchema
)

logger = logging.getLogger(__name__)

router = Router()


@router.post("/register", response={201: TokenSchema, 400: MessageSchema})
def register(request, payload: UserRegisterSchema):
    """用戶註冊端點"""
    try:
        # 檢查用戶名是否已存在
        if User.objects.filter(username=payload.username).exists():
            return 400, {"message": "Username already exists"}
        
        # 檢查 email 是否已存在
        if User.objects.filter(email=payload.email).exists():
            return 400, {"message": "Email already exists"}
        
        # 創建用戶
        user = User.objects.create_user(
            username=payload.username,
            email=payload.email,
            password=payload.password,
            first_name=payload.first_name or "",
            last_name=payload.last_name or "",
        )
        
        # 生成 JWT tokens
        refresh = RefreshToken.for_user(user)
        
        logger.info(f"User registered successfully: {user.username}")
        
        return 201, {
            "access": str(refresh.access_token),
            "refresh": str(refresh)
        }
        
    except IntegrityError as e:
        logger.error(f"Registration error: {str(e)}")
        return 400, {"message": "Registration failed"}
    except Exception as e:
        logger.error(f"Unexpected registration error: {str(e)}")
        return 400, {"message": "Registration failed"}


@router.post("/login", response={200: TokenSchema, 401: MessageSchema})
def login(request, payload: UserLoginSchema):
    """用戶登入端點"""
    try:
        # 先檢查用戶是否存在
        try:
            user = User.objects.get(username=payload.username)
            if not user.is_active:
                return 401, {"message": "Account is disabled"}
        except User.DoesNotExist:
            pass
        
        user = authenticate(username=payload.username, password=payload.password)
        
        if user is None:
            return 401, {"message": "Invalid credentials"}
        
        if not user.is_active:
            return 401, {"message": "Account is disabled"}
        
        # 生成 JWT tokens
        refresh = RefreshToken.for_user(user)
        
        logger.info(f"User logged in successfully: {user.username}")
        
        return 200, {
            "access": str(refresh.access_token),
            "refresh": str(refresh)
        }
        
    except Exception as e:
        logger.error(f"Login error: {str(e)}")
        return 401, {"message": "Login failed"}


@router.post("/refresh", response={200: dict, 400: MessageSchema})
def refresh_token(request, payload: TokenRefreshSchema):
    """更新 access token"""
    try:
        refresh = RefreshToken(payload.refresh)
        return 200, {
            "access": str(refresh.access_token)
        }
    except Exception as e:
        logger.error(f"Token refresh error: {str(e)}")
        return 400, {"message": "Invalid refresh token"}
