from rest_framework_simplejwt.authentication import JWTAuthentication

from rest_framework_simplejwt.exceptions import InvalidToken, TokenError
from rest_framework.authentication import get_authorization_header
from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework.response import Response

class CustomJWTAuthentication(JWTAuthentication):
    def authenticate(self, request):
        header = get_authorization_header(request).split()
        if header and header[0].lower() == b'bearer':
            try:
                return super().authenticate(request)
            except (InvalidToken, TokenError):
                print("Header authentication failed")
                return None  

        raw_token = request.COOKIES.get('access_token')
        refresh_token_string = request.COOKIES.get('refresh_token')
        print(f"trying with refresh token {refresh_token_string}")
        if raw_token:
            try:
                print(11)
                validated_token = self.get_validated_token(raw_token)
                user = self.get_user(validated_token)
                user.role = validated_token.get('role')
                return user, validated_token
            except InvalidToken:
                print("cookies authentication failed trying refresh !!")
                if refresh_token_string:
                    print("fall")
                    new_validated_token = RefreshToken(refresh_token_string) 
                    new_refresh = str(new_validated_token)
                    user = self.get_user(new_validated_token)
                    new_access = str(new_validated_token.access_token)
                    print({
                        "access":new_access,
                        "refresh":new_refresh
                    })
                    return user, new_validated_token
            except TokenError:
                pass
        return None
