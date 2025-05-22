from rest_framework import serializers
from rest_framework_simplejwt.serializers import TokenObtainPairSerializer
from django.contrib.auth import get_user_model

User = get_user_model()



class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['first_name','last_name','email','password']
        extra_kwargs = {"password":{"write_only":True}}


class PatientRegistrationSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True)

    class Meta:
        model = User
        fields = ['first_name', 'last_name', 'email']
        extra_kwargs = {'password': {'write_only': True}}

    def create(self, validated_data):
        if User.objects.filter(email=validated_data.get('email')).exists():
            raise IntegrityError('email already exists')
        user = User.objects.create_user(
            email=validated_data.get('email'),
            first_name=validated_data.get('first_name'),
            last_name=validated_data.get('last_name'),
            password=validated_data.get('password'),
            role='patient',
            is_superuser=False,
            is_staff=False 
        )
        return user 

class ProfileSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['id', 'first_name', 'last_name', 'email', 'role']
        read_only_fields = ['id', 'email', 'role']

class CustomTokenObtainPairSerializer(TokenObtainPairSerializer):
    @classmethod
    def get_token(cls,user):
        token = super().get_token(user)
        token['user_id']=user.id
        token['role'] = user.role
        return token
