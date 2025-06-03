from users.serializers import UserSerializer
from users.models import User,Patient,Doctor
import pytest
from model_bakery import baker

@pytest.fixture
def user_instance():
    user = User.objects.create_user(
        first_name="testUser",
        last_name="testUser",
        email="test@example.com",
        password="testPassword",
        _cin='HH654321'
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
def test_users_group():
    user1 = baker.make(User, _cin='AA909090')
    user2 = baker.make(User, _cin='BB909090')
    users = User.objects.all()
    serializer = UserSerializer(instance=users,many=True)
    assert len(serializer.data) == User.objects.count()
    

@pytest.mark.django_db
def test_user_cin_anonymization(user_instance):

    user = user_instance
    serializer = UserSerializer(instance=user)
    assert serializer.data.get('cin') == user.cin
    assert serializer.data.get('cin')[2:-2] == '****' # AA123456 -> AA****56