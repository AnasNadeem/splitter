import jwt
from django.contrib.auth.models import User
from rest_framework.authentication import BaseAuthentication, get_authorization_header
from django.conf import settings
from rest_framework import exceptions


class JWTAuthentication(BaseAuthentication):
    def authenticate(self, request):
        auth_header = get_authorization_header(request)
        super().authenticate(request)

        if not auth_header:
            return None

        prefix, token = auth_header.decode('utf-8').split(' ')

        try:
            payload = jwt.decode(token, settings.SECRET_KEY, algorithms='HS256')
            user = User.objects.get(username=payload['username'])
            return (user, token)

        except jwt.ExpiredSignatureError as ex:
            raise exceptions.AuthenticationFailed(f'Token has been expired. Login again {ex}')

        except jwt.DecodeError as ex:
            raise exceptions.AuthenticationFailed(f'Invalid Token. {ex}')

        except User.DoesNotExist as no_user:
            raise exceptions.AuthenticationFailed(f'No such user exist. {no_user}')    