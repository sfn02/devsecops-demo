from rest_framework import serializers
from rest_framework_simplejwt.serializers import TokenObtainPairSerializer
from django.contrib.auth import get_user_model
from users.models import Patient
from rest_framework.validators import UniqueValidator
User = get_user_model()



class UserSerializer(serializers.ModelSerializer):
    cin = serializers.CharField(required=True)
    password = serializers.CharField(
        min_length=8,
        required=False,
        write_only=True
    )
    confirm_password = serializers.CharField(
        write_only=True,
        required=True
    )

    class Meta:
        model = User
        fields = ['id','first_name', 'last_name', 'email','phone_number','cin', 'password', 'confirm_password', 'role']
        extra_kwargs = {"role": {"write_only": True, "required": False}}

    def validate(self, data):
        confirm_password = data.get('confirm_password')
        if confirm_password:
            if data['password'] != data['confirm_password']:
                raise serializers.ValidationError({"password": "Passwords do not match"})
        return data

    def validate_cin(self, value):
        import re
        if not re.match(r'^[A-Z]{1,2}\d{5,6}$', value):
            raise serializers.ValidationError("Format CIN invalide")
        if User.objects.filter(_cin=value).exists():
            raise serializers.ValidationError("CIN already in use")
        return value

    def validate_password(self, value):
        import re
        password_pattern = "^(?=.*?[A-Z])(?=.*?[a-z])(?=.*?[0-9])(?=.*?[#?!@$%^&*-]).{8,}$"
        if not re.fullmatch(password_pattern, value):
            raise serializers.ValidationError("Password must contain at least 8 characters, one uppercase, one lowercase, one digit and one special character")
        return value

    def create(self, validated_data):
        validated_data.pop('confirm_password')  
        user = User.objects.create_user(
            email=validated_data['email'],
            password=validated_data['password'],
            first_name=validated_data['first_name'],
            last_name=validated_data['last_name'],
            cin=validated_data['cin'],
            role=validated_data.get('role', 'patient') 
        )
        patient = Patient.objects.create(
            user=user
        )
        patient.save()
        return user

    def update(self, instance, validated_data):
        if 'password' in validated_data:
            instance.set_password(validated_data['password'])
            validated_data.pop('password')
        
        if 'confirm_password' in validated_data:
            validated_data.pop('confirm_password')
            
        for attr, value in validated_data.items():
            setattr(instance, attr, value)
        
        instance.save()
        return instance





class ProfileSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['id', 'first_name', 'last_name', 'email', 'role']
        read_only_fields = ['id', 'email', 'role']

class CustomTokenObtainPairSerializer(TokenObtainPairSerializer):
    @classmethod
    def get_token(cls,user):
        token = super().get_token(user)
        token['user_id'] = user.id
        token['role'] = user.role
        return token

