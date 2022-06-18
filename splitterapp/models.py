from django.db import models
# Create your models here.
# User, Profile
# Friend Request
# Group
# Expense
# Settlement


class TimeBase(models.Model):
    created_at = models.DateField(auto_now_add=True)
    updated_at = models.DateField(auto_now=True)

    class Meta:
        abstract = True


class User(models.Model):
    friends = models.ManyToManyField("User", blank=True)


STATUS_CHOICES = (
    ('send', 'send'),
    ('accepted', 'accepted')
)


class FriendRequest(TimeBase):
    sender = models.ForeignKey(User, on_delete=models.CASCADE)
    receiver = models.ForeignKey(User, on_delete=models.CASCADE)
    status = models.CharField(max_length=10, choices=STATUS_CHOICES, default='send')

    def __str__(self):
        return f"{self.sender} - {self.receiver} - {self.status} - {self.updated_at.strftime('%d-%m-%Y')} - {self.created_at.strftime('%d-%m-%Y')}"


class ExpenseGroup(TimeBase):
    owner = models.ForeignKey(User, on_delete=models.CASCADE)
    name = models.CharField(max_length=100)
    description = models.TextField()
    group_users = models.ManyToManyField(User, blank=True)

    def __str__(self):
        return self.name


class Expense(TimeBase):
    group = models.ForeignKey(ExpenseGroup, on_delete=models.CASCADE)
    name = models.CharField(max_length=100)
    description = models.TextField()
    amount = models.IntegerField()
    participants = models.ManyToManyField(User, blank=True)
    split_equal = models.BooleanField(default=True)
    split_amount = models.JSONField()
    paid_by = models.ForeignKey(User, on_delete=models.SET_NULL)

    def __str__(self):
        return self.name


# class PendingPayment(TimeBase):
#     expense = models.ForeignKey(Expense, on_delete=models.CASCADE)
#     user = models.ForeignKey(User, on_delete=models.DO_NOTHING)
#     amount = models.IntegerField()
#     is_paid = models.BooleanField(default=False)

#     def __str__(self):
#         return f"Pay {self.expense.paid_by.username}"
