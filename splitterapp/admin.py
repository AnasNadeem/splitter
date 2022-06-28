from django.contrib import admin
from splitterapp.models import (
    User,
    FriendRequest,
    ExpenseGroup,
    Expense,
    PendingPayment,
)
# Register your models here.

admin.site.register(User)
admin.site.register(FriendRequest)
admin.site.register(ExpenseGroup)
admin.site.register(Expense)
admin.site.register(PendingPayment)
