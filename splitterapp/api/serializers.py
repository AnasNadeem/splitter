from rest_framework import serializers
from splitterapp.models import (
    Expense,
    ExpenseGroup,
    FriendRequest,
    PendingPayment,
    User,
)
from django.db.models import Q


class UserSerializer(serializers.ModelSerializer):
    password = serializers.CharField(max_length=50, min_length=4, write_only=True)

    class Meta:
        model = User
        fields = '__all__'


class UserSerializerWithDepth1(serializers.ModelSerializer):
    password = serializers.CharField(max_length=50, min_length=4, write_only=True)

    class Meta:
        model = User
        fields = '__all__'
        depth = 1


class UserSerializerWithDepth2(serializers.ModelSerializer):
    password = serializers.CharField(max_length=50, min_length=4, write_only=True)
    expense_group = serializers.SerializerMethodField()

    class Meta:
        model = User
        fields = '__all__'
        depth = 2

    def get_expense_group(self, obj):
        expense_group_qs = (ExpenseGroup.objects
                            .filter(Q(owner_id=obj.id) | Q(group_users__id=obj.id))
                            .distinct()
                            )
        expense_group_qs_data = ExpenseGroupSerializerForGet(expense_group_qs, many=True).data
        return expense_group_qs_data


class LoginSerializer(serializers.ModelSerializer):
    password = serializers.CharField(max_length=50, min_length=4, write_only=True)
    username = serializers.CharField(max_length=255)

    class Meta:
        model = User
        fields = ('username', 'password')


class RegisterSerializer(serializers.ModelSerializer):
    password = serializers.CharField(max_length=50, min_length=4, write_only=True)
    email = serializers.EmailField(max_length=100)
    first_name = serializers.CharField(max_length=155)
    last_name = serializers.CharField(max_length=155)

    class Meta:
        model = User
        fields = ('username', 'email', 'first_name', 'last_name', 'password')

    def validate(self, attrs):
        email = attrs.get('email', '')
        if User.objects.filter(email=email).exists():
            raise serializers.ValidationError({'error': ('Email is already in use')})
        return super().validate(attrs)

    def create(self, validated_data):
        return User.objects.create_user(**validated_data)


class ExpenseGroupSerializer(serializers.ModelSerializer):

    class Meta:
        model = ExpenseGroup
        fields = '__all__'


class ExpenseGroupSerializerForGet(serializers.ModelSerializer):
    expense = serializers.SerializerMethodField()
    class Meta:
        model = ExpenseGroup
        fields = '__all__'
        depth = 1

    def get_expense(self, obj):
        expense_qs = Expense.objects.filter(group_id=obj.id)
        expense_qs_data = ExpenseSerializerForGet(expense_qs, many=True).data
        return expense_qs_data


class FriendReqSerializer(serializers.ModelSerializer):
    sender = UserSerializerWithDepth2()
    receiver = UserSerializerWithDepth2()

    class Meta:
        model = FriendRequest
        fields = '__all__'


class ExpenseSerializerForGet(serializers.ModelSerializer):

    class Meta:
        model = Expense
        fields = '__all__'
        depth = 1


class ExpenseSerializer(serializers.ModelSerializer):

    class Meta:
        model = Expense
        fields = '__all__'


class PendingPaymentSerializer(serializers.ModelSerializer):
    expense = ExpenseSerializerForGet()
    user = UserSerializer()

    class Meta:
        model = PendingPayment
        fields = '__all__'
