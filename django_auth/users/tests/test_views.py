from django.test import RequestFactory
from django.urls import reverse
from . models import User

class TestViews:
    def login_detail(self):
        path=reverse()

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

    assert (response.status_code, status.HTTP_201_CREATED)


