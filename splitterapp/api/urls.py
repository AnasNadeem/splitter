from django.urls import path
from .views import (
    RegisterAPiView,
    LoginApiView,
    ExpenseGroupView,
    SendFriendReqView,
    AcceptFriendReqView,
    FriendReqListView,
)
from rest_framework import routers
from rest_framework.urlpatterns import format_suffix_patterns


router = routers.SimpleRouter(trailing_slash=False)
router.register(r"group", ExpenseGroupView, basename="expense_group")

urlpatterns = [
    path('register/', RegisterAPiView.as_view()),
    path('login/', LoginApiView.as_view()),
    path('list-friend-request/', FriendReqListView.as_view()),
    path('send-request/', SendFriendReqView.as_view()),
    path('accept-request/', AcceptFriendReqView.as_view()),
]

urlpatterns += router.urls
urlpatterns = format_suffix_patterns(urlpatterns)
