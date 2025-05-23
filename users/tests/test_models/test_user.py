from users.models import User,Patient,Doctor
import pytest
from model_bakery import baker
from django.core.exceptions import ValidationError
from django.urls import reverse

@pytest.mark.django_db
def test_user_creation():
    user = baker.make(User)
    print(f"first name :{user.first_name}\nlast name {user.email}")
    assert user.role == 'patient'

@pytest.mark.django_db
def test_patient_creation():
    user = baker.make(User,first_name='soufiane')
    patient = baker.make(Patient,user=user)
    print(patient)
    assert patient.user.first_name == 'soufiane'


@pytest.mark.django_db
def test_doctor_requires_doctor_role():

    patient_user = baker.make(User, role='patient', first_name='Soufiane')
    
    with pytest.raises(ValidationError) as excinfo:
        baker.make(Doctor, user=patient_user)
    
    assert "User must be a doctor" in str(excinfo.value)
        

@pytest.mark.django_db
def test_login_page_access(client):
    response = client.get(reverse('login_view'))
    print(response.status_code)
    assert response.status_code == 200

@pytest.mark.django_db
def test_user_register(client):
    
    response = client.post('http://localhost:8000/users/auth/register/',
    {
        "first_name":"soufiane",
        "last_name":"fhaili",
        "email":"soufiane@gmail.com",
        "password":"Complex_password"
    }
    )
    assert response.status_code == 201

@pytest.mark.django_db
def test_user_login(client):
    user = baker.make(User,email='soufiane@gmail.com')
    user.set_password('password')
    user.save()
    response = client.post(
        reverse('login_view'),
        {
            "email":"soufiane@gmail.com",
            "password":"password"
        }
    )
    assert response.cookies.get('access_token')
    response = client.post(
    reverse('login_view'),
        {
            "email":"soufiane@gmail.com",
            "password":"wrong_pass"
        }
    )
    assert not response.cookies.get('access_token')

@pytest.mark.django_db
def test_user_unauthorized_login(client):
    user = baker.make(User,email='soufiane@gmail.com')
    user.set_password('password')
    user.save()
    response = client.post(
        reverse('login_view'),
        {
            "email":"soufiane@gmail.com",
            "password":"wrong_password"
        }
    )
    assert response.status_code == 401

@pytest.mark.django_db
def test_user_update_profile(client):
    user = baker.make(User,first_name='soufiane',email='soufiane@gmail.com')
    user.set_password('password')
    user.save()
    response = client.post(
        reverse('login_view'),
        {
            "email":"soufiane@gmail.com",
            "password":"password"
        }
    )
    header = {
        'Accept':'application/json'
    }
    cookie = response.cookies.get('access_token')
    response = client.post(reverse('profile_view'),
    json={
        "first_name":"mohamed"
    },
    cookies=cookie,
    headers=header
    )
    msg = response.data.get('msg')
    assert response.status_code == 201 and "Profile updated succesfully" in msg