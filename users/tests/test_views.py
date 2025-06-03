from users.models import User,Patient,Doctor
import pytest
from model_bakery import baker
from django.core.exceptions import ValidationError
from django.urls import reverse
from bs4 import BeautifulSoup as bs


def test_unauthenticated_root_redirect(client):
    response = client.get(
        'http://localhost:8000'
    )
    assert response.status_code == 302
    assert response.headers.get('Location') == '/users/auth/login/'



def test_login_page(client):
    response = client.get(
        reverse('login_view')
    )
    soup = bs(response.text,'html.parser')
    assert soup.title.string == 'Login'

def test_register_page(client):
    response = client.get(
        reverse('register_view')
    )
    soup = bs(response.text,'html.parser')
    assert soup.title.string == 'Register'       


