from ninja.security import HttpBearer


class JWTBearer(HttpBearer):
    """
    自定義 JWT Bearer 認證類別，用於 Django Ninja
    """
    def authenticate(self, request, token):
        from ninja_jwt.tokens import UntypedToken
        from ninja_jwt.exceptions import InvalidToken, TokenError
        from django.contrib.auth import get_user_model
        
        User = get_user_model()
        
        try:
            UntypedToken(token)
            
            from ninja_jwt.state import token_backend
            payload = token_backend.decode(token, verify=True)
            
            user = User.objects.get(id=payload['user_id'])
            
            if not user.is_active:
                return None
                
            return user
            
        except (InvalidToken, TokenError, User.DoesNotExist):
            return None

jwt_auth = JWTBearer()
