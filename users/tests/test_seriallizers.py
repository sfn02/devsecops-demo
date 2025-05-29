from users.serializers import UserSerializer,PatientRegistrationSerializer
from users.models import User,Patient,Doctor
import pytest
from model_bakery import baker

@pytest.fixture
def user_instance():
    user = User.objects.create_user(
        first_name="testUser",
        last_name="testUser",
        email="test@example.com",
        password="testPassword"
    )
    user.save()
    return user

@pytest.mark.django_db
def test_user_serializer(user_instance):
    user = user_instance
    serializer = UserSerializer(instance=user)  
    assert serializer.data['first_name'] == user.first_name 
    assert serializer.data['last_name'] == user.last_name
    assert serializer.data['email'] == user.email
    assert not serializer.data.get('password')

@pytest.mark.django_db
def test_users_group(user_instance):
    user1 = baker.make(User)
    user2 = baker.make(User)
    users = User.objects.all()
    serializer = UserSerializer(instance=users,many=True)
    assert len(serializer.data) == User.objects.count()
