from django.test import RequestFactory
from django.urls import reverse
from . models import User

class TestViews:
    def login_detail(self):
        path=reverse()


class RegisterModel:
    def test_save(self):
            register = RestRegistration.objects.create(
                email="sk.shahazad@gmail.com",
                first_name="shahazad",
                last_name="shaikh",
                password=500,
                confirm_password=500,
            )
            assert register.email == "sk.shahazad@gmail.com"
            assert register.password == 500
            assert register.confirm_password == 500
    assert register.email == "sk.shahazad@gmail.com"

def setUp(self):
    valid_payload = {
        'title': 'test',
        'description': "test",
        'color': "test",
        'label': 'test'}

    response = client.post(
        reverse('createnote'),
        data=json.dumps(valid_payload),
        content_type='application/json'
    )

    assert (response.status_code)


def update(self):
    valid_payload = {
        'title': 'test',
        'description': "test",
        'color': "test",
        'label': 'test'}

    response = client.post(
        reverse('updatenote'),
        data=json.dumps(valid_payload),
        content_type='application/json'
    )
    assert (response.status_code)

