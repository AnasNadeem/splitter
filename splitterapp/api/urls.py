from django.urls import path
from .views import (
    RegisterAPiView,
    LoginApiView,
    LoginApiByTokenView,
    ExpenseGroupViewset,
    ExpenseViewset,
    SendFriendReqView,
    AcceptFriendReqView,
    DeleteFriendReqView,
    FriendReqListView,
    PendingPaymentListView,
)
from rest_framework import routers
from rest_framework.urlpatterns import format_suffix_patterns


router = routers.SimpleRouter(trailing_slash=False)
router.register(r"group", ExpenseGroupViewset, basename="expense_group")
router.register(r"expense", ExpenseViewset, basename="expense")

urlpatterns = [
    # Authentication Urls
    path('register/', RegisterAPiView.as_view()),
    path('login/', LoginApiView.as_view()),
    path('login-by-token/', LoginApiByTokenView.as_view()),
    # Friend Request Urls
    path('list-friend-request/', FriendReqListView.as_view()),
    path('send-request/', SendFriendReqView.as_view()),
    path('accept-request/', AcceptFriendReqView.as_view()),
    path('delete-request/', DeleteFriendReqView.as_view()),
    # Pending Payment Urls
    path('pending-payments/', PendingPaymentListView.as_view()),
]

urlpatterns += router.urls
urlpatterns = format_suffix_patterns(urlpatterns)
