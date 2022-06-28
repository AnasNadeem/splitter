import jwt
from django.conf import settings
from django.contrib import auth
from django.db.models import Q
from rest_framework.generics import GenericAPIView, ListAPIView
from rest_framework.viewsets import ModelViewSet
from rest_framework import status, response, views
from rest_framework.permissions import IsAuthenticated
from .serializers import (
    LoginSerializer,
    RegisterSerializer,
    UserSerializerWithDepth2,
    ExpenseGroupSerializer,
    ExpenseGroupSerializerForGet,
    FriendReqSerializer,
    PendingPaymentSerializer,
    ExpenseSerializer,
    ExpenseSerializerForGet,
)
from splitterapp.models import (
    Expense,
    ExpenseGroup,
    FriendRequest,
    PendingPayment,
    User,
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
            user_serializer_data = UserSerializerWithDepth2(user).data
            data = {'user': user_serializer_data, 'token': auth_token}
            return response.Response(data, status=status.HTTP_200_OK)
        return response.Response({'error': 'Invalid credentials'}, status=status.HTTP_401_UNAUTHORIZED)


class ExpenseGroupViewset(ModelViewSet):
    queryset = ExpenseGroup.objects.all()
    serializer_class = ExpenseGroupSerializer
    permission_classes = (IsAuthenticated,)

    def get_serializer_class(self):
        if self.action in ['list', 'retrieve']:
            return ExpenseGroupSerializerForGet
        return self.serializer_class

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
                  .filter((Q(sender=request.user) & Q(receiver=receiver_qs)) | (Q(sender=receiver_qs) & Q(receiver=request.user)))
                  .first()
                  )
        if fr_req:
            response_error = {
                "error": "Request already exists.",
                "status": f"{fr_req.status}"
            }
            return response.Response(response_error, status=status.HTTP_400_BAD_REQUEST)

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


class DeleteFriendReqView(views.APIView):
    permission_classes = (IsAuthenticated,)

    def post(self, request):
        data = request.data
        fr_req_id = data.get('fr_req_id')
        if not fr_req_id:
            return response.Response({"status": "Need a parameter 'fr_req_id'"}, status=status.HTTP_400_BAD_REQUEST)

        # Check if Friend Request already exist
        fr_req_qs = (FriendRequest.objects
                     .filter(id=fr_req_id)
                     .filter(Q(sender=request.user) | Q(receiver=request.user))
                     .first()
                     )

        if not fr_req_qs:
            return response.Response({"status": "Friend Request doesn't exists!"}, status=status.HTTP_400_BAD_REQUEST)

        # Delete the Friend Request
        fr_req_qs.delete()

        return response.Response({"status": "Friend request deleted"}, status=status.HTTP_201_CREATED)


class FriendReqListView(ListAPIView):
    queryset = FriendRequest.objects.all()
    serializer_class = FriendReqSerializer
    permission_classes = (IsAuthenticated,)

    def get_queryset(self):
        qs = (FriendRequest.objects
              .filter(Q(sender=self.request.user) | Q(receiver=self.request.user.id))
              )
        return qs


class ExpenseViewset(ModelViewSet):
    queryset = Expense.objects.all()
    serializer_class = ExpenseSerializer
    permission_classes = (IsAuthenticated,)

    def get_serializer_class(self):
        if self.action in ['list', 'retrieve']:
            return ExpenseSerializerForGet
        return self.serializer_class

    def get_queryset(self):
        qs = Expense.objects.filter(Q(paid_by=self.request.user) | Q(participants__id=self.request.user.id))
        return qs

    def create(self, request, *args, **kwargs):
        # split_amounts = [{'user_id': user_id, 'amount': amount}]
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.save()

        expense_id = serializer.data.get('id')
        expense_amount = serializer.data.get('amount')
        participants = serializer.data.get('participants')

        if participants:
            for participant in participants:
                pending_payment = PendingPayment()
                pending_payment.expense_id = expense_id
                pending_payment.user_id = participant
                pending_payment.amount = expense_amount / len(participants)
                pending_payment.save()

        headers = self.get_success_headers(serializer.data)
        return response.Response(serializer.data, status=status.HTTP_201_CREATED, headers=headers)


class PendingPaymentListView(ListAPIView):
    queryset = PendingPayment.objects.all()
    serializer_class = PendingPaymentSerializer
    permission_classes = (IsAuthenticated,)
    filterset_fields = ('expense__id', 'user', 'is_paid')

    # def get_queryset(self):
    #     expense_id = self.request.query_params.get('expense_id')
    #     expense_qs = Expense.objects.filter(pk=expense_id).first()
    #     qs = (PendingPayment.objects
    #           .filter(expense=expense_qs)
    #           )
    #     return qs
