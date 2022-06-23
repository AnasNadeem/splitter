import jwt
from django.conf import settings
from django.contrib import auth
from django.db.models import Q
from rest_framework.generics import GenericAPIView, ListAPIView
from rest_framework.viewsets import ModelViewSet
from rest_framework import status, response, views
from rest_framework.permissions import IsAuthenticated
from .serializers import (
    RegisterSerializer,
    UserSerializer,
    ExpenseGroupSerializer,
    FriendReqSerializer,
)
from splitterapp.models import (
    User,
    ExpenseGroup,
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
    serializer_class = UserSerializer

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
            user_serializer_data = self.serializer_class(user).data
            data = {'user': user_serializer_data, 'token': auth_token}
            return response.Response(data, status=status.HTTP_200_OK)
        return response.Response({'error': 'Invalid credentials'}, status=status.HTTP_401_UNAUTHORIZED)


class ExpenseGroupView(ModelViewSet):
    queryset = ExpenseGroup.objects.all()
    serializer_class = ExpenseGroupSerializer
    permission_classes = (IsAuthenticated,)

    def get_queryset(self):
        qs = ExpenseGroup.objects.filter(Q(owner=self.request.user) | Q(group_users__id=self.request.user.id))
        return qs


class SendFriendReqView(views.APIView):
    permission_classes = (IsAuthenticated,)

    def post(self, request):
        data = request.data
        receiver = data.get('receiver')
        if not receiver:
            return response.Response({"status": "Need a parameter 'receiver'"}, status=status.HTTP_400_BAD_REQUEST)

        # Check if receiver exist
        receiver_qs = (User.objects.filter(id=receiver).first() if isinstance(receiver, int)
                       else User.objects.filter(username=receiver).first())
        if not receiver_qs:
            return response.Response({"status": "receiver doesn't exists!"}, status=status.HTTP_400_BAD_REQUEST)

        # Check if Friend Request already exist
        fr_req = (FriendRequest.objects
                  .filter(sender=request.user, receiver=receiver_qs, status='send')
                  .first()
                  )
        if fr_req:
            return response.Response({"status": "Request already exists!"}, status=status.HTTP_400_BAD_REQUEST)

        fr_req = FriendRequest()
        fr_req.sender = request.user
        fr_req.receiver = receiver_qs
        fr_req.status = "send"
        fr_req.save()
        return response.Response({"status": "Friend request sent"}, status=status.HTTP_201_CREATED)


class AcceptFriendReqView(views.APIView):
    permission_classes = (IsAuthenticated,)

    def post(self, request):
        data = request.data
        fr_req_id = data.get('fr_req_id')
        if not fr_req_id:
            return response.Response({"status": "Need a parameter 'fr_req_id'"}, status=status.HTTP_400_BAD_REQUEST)

        # Check if the Friend request exist
        fr_req_qs = (FriendRequest.objects
                     .filter(id=fr_req_id)
                     .filter(receiver=request.user)
                     .filter(status='send')
                     .first()
                     )
        if not fr_req_qs:
            return response.Response({"status": "Friend Request doesn't exists!"}, status=status.HTTP_400_BAD_REQUEST)

        # Update the Friend Request
        fr_req_qs.status = 'accepted'
        fr_req_qs.save()

        # Add to User friend list
        sender = fr_req_qs.sender
        receiver = fr_req_qs.receiver
        sender.friends.add(receiver)
        sender.save()
        receiver.friends.add(sender)
        receiver.save()

        return response.Response({"status": "Friend request accepted"}, status=status.HTTP_201_CREATED)


class FriendReqListView(ListAPIView):
    queryset = FriendRequest.objects.all()
    serializer_class = FriendReqSerializer
    permission_classes = (IsAuthenticated,)

    def get_queryset(self):
        qs = (FriendRequest.objects
              .filter(Q(sender=self.request.user) | Q(receiver=self.request.user.id))
              .filter(status='send')
              )
        return qs
