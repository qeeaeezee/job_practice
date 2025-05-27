from ninja import Schema
from typing import Optional


class UserRegisterSchema(Schema):
    """用戶註冊 Schema"""
    username: str
    email: str
    password: str
    first_name: Optional[str] = None
    last_name: Optional[str] = None


class UserLoginSchema(Schema):
    """用戶登入 Schema"""
    username: str
    password: str


class UserSchema(Schema):
    """用戶資訊 Schema"""
    id: int
    username: str
    email: str
    first_name: Optional[str] = None
    last_name: Optional[str] = None
    is_active: bool
    date_joined: str


class TokenSchema(Schema):
    """JWT Token Schema"""
    access: str
    refresh: str


class TokenRefreshSchema(Schema):
    """Token 更新 Schema"""
    refresh: str


class MessageSchema(Schema):
    """通用訊息 Schema"""
    message: str