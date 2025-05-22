import pytest
from model_bakery import baker
from users.models import User

@pytest.fixture
def patient(db):
    patient = baker.make(User)
    assert str(patient) == f"Patient: {patient.user.username}"
