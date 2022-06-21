import jwt
from django.conf import settings
from django.contrib import auth
from rest_framework.generics import GenericAPIView
from rest_framework.viewsets import ModelViewSet
from rest_framework import status, response
from rest_framework.permissions import IsAuthenticated
from .serializers import RegisterSerializer, LoginSerializer, ExpenseGroupSerializer
from splitterapp.models import (
    User,
    ExpenseGroup,
    Expense,
    FriendRequest
)


class RegisterAPiView(GenericAPIView):
    serializer_class = RegisterSerializer

    def post(self, request):
        serializer = self.serializer_class(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return response.Response(serializer.data, status=status.HTTP_201_CREATED)
        return response.Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class LoginApiView(GenericAPIView):
    serializer_class = LoginSerializer

    def post(self, request):
        data = request.data
        username = data.get('username', '')
        password = data.get('password', '')
        user = auth.authenticate(username=username, password=password)
        if user:
            auth_token = jwt.encode(
                {'username': user.username},
                settings.SECRET_KEY,
                algorithm='HS256'
            )
            data = {'username': user.username, 'token': auth_token}
            return response.Response(data, status=status.HTTP_200_OK)
        return response.Response({'error': 'Invalid credentials'}, status=status.HTTP_401_UNAUTHORIZED)


class ExpenseGroupView(ModelViewSet):
    queryset = ExpenseGroup.objects.all()
    serializer_class = ExpenseGroupSerializer
    permission_classes = (IsAuthenticated,)
