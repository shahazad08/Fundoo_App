from django.urls import reverse, resolve
import pytest


pytestmark = pytest.mark.django_db


class TestUrls:

    def test_signup_url(self):
        path = reverse('signup')
        assert resolve(path).view_name == 'signup'


    def test_createnote(self):
        path=reverse('createnote')
        assert resolve(path).view_name=='createnote'

    def readnote(self):
        path=reverse('readnote',kwargs={'pk':1})
        assert resolve(path).view_name=='readnote'

    def table(self):
        path=reverse('table')
        assert resolve(path).view_name=='table'



