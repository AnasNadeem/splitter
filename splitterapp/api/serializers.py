from rest_framework import serializers
from splitterapp.models import (
    FriendRequest,
    User,
    ExpenseGroup,
    Expense,
)


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


class LoginSerializer(serializers.ModelSerializer):
    password = serializers.CharField(max_length=50, min_length=4, write_only=True)
    username = serializers.CharField(max_length=255)

    class Meta:
        model = User
        fields = ('username', 'password')


class ExpenseGroupSerializer(serializers.ModelSerializer):

    class Meta:
        model = ExpenseGroup
        fields = '__all__'


class FriendReqSerializer(serializers.ModelSerializer):

    class Meta:
        model = FriendRequest
        fields = '__all__'
