# middleware.py
from django.http import JsonResponse
from django.utils.deprecation import MiddlewareMixin
from jwt import ExpiredSignatureError, InvalidTokenError, PyJWTError
from rest_framework_jwt.settings import api_settings


class JwtAuthenticationMiddleware(MiddlewareMixin):

    def process_request(self, request):
        white_list = [
            "/user/login",
            "/user/captcha",
            "/lcs1/articles/",
            "/lcs1/blogger_articles",
            "/lcs1/upload_image/",
            "/menu/menus/",
        ]

        path = request.path
        print(f"Request path: {path}")  # 添加调试信息

        # 检查路径是否在白名单中或是否以 /media, /article/ 开头
        if not any(path.startswith(prefix) for prefix in white_list + ["/media", "/article/"]):
            print("要进行token验证")
            token = request.META.get('HTTP_AUTHORIZATION')
            if not token:
                return JsonResponse({'error': 'Token缺失！'}, status=401)
            try:
                jwt_decode_handler = api_settings.JWT_DECODE_HANDLER
                jwt_decode_handler(token)
            except ExpiredSignatureError:
                return JsonResponse({'error': 'Token过期，请重新登录！'}, status=401)
            except InvalidTokenError:
                return JsonResponse({'error': 'Token验证失败！'}, status=401)
            except PyJWTError:
                return JsonResponse({'error': 'Token验证异常！'}, status=401)
        else:
            print("不需要token验证")  # 添加调试信息
            return None

