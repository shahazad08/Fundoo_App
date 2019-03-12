import pytest
from django_auth.Notes.models import User
pytestmark = pytest.mark.django_db
class TestRegisterModel:
    def test_save(self):
        register = User.object.create(
            email="sk.shahazad@@gmail.com",
            first_name="PyTest",
        )
        assert register.email == "sk.shahazad@gmail.com"
        assert register.first_name == "PyTest"






# Create your tests here.

# from .forms import *
# class Setup_class(self):
#     self.user=User.object.create(email="sk.shahazad@gmail.com",first_name="fname",last_name=lname)
#
#
# class User_form_Test(TestCase):
#     def test_UserForm_valid(self):
#         form=UserForm(data={'email': 'sk.shahazad@gmailcom','first_name':'fname','last_name':'lname'})
#         self.assertTrue(form.is_valid)
#


