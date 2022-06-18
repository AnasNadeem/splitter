from django.contrib import admin
from splitterapp.models import (
    User,
    FriendRequest,
    ExpenseGroup,
    Expense,
)
# Register your models here.

admin.site.register(User)
admin.site.register(FriendRequest)
admin.site.register(ExpenseGroup)
admin.site.register(Expense)
