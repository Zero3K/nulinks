from django.test import TestCase
from django.contrib.auth.models import User
from django.contrib.auth.forms import UserCreationForm
from django.urls import reverse

# Create your tests here.

class NumericPasswordTestCase(TestCase):
    """Test that all-numeric passwords are now allowed"""
    
    def test_numeric_password_allowed(self):
        """Test that a user can register with an all-numeric password"""
        # Test that all-numeric passwords are now allowed
        form_data = {
            'username': 'testuser',
            'password1': '847362951847',  # All numeric, not in common passwords
            'password2': '847362951847',
        }
        form = UserCreationForm(form_data)
        self.assertTrue(form.is_valid(), f"Form should be valid with numeric password. Errors: {form.errors}")
        
    def test_common_numeric_password_still_blocked(self):
        """Test that common numeric passwords are still blocked by CommonPasswordValidator"""
        form_data = {
            'username': 'testuser2',
            'password1': '123456789',  # Common numeric password
            'password2': '123456789',
        }
        form = UserCreationForm(form_data)
        self.assertFalse(form.is_valid(), "Form should be invalid with common numeric password")
        self.assertIn('password2', form.errors)
        
    def test_signup_view_with_numeric_password(self):
        """Test the signup view accepts numeric passwords"""
        response = self.client.post(reverse('register'), {
            'username': 'testuser3',
            'password1': '847362951847',
            'password2': '847362951847',
        })
        # Should redirect to home on success
        self.assertEqual(response.status_code, 302)
        self.assertEqual(response.url, '/')
        # User should be created
        self.assertTrue(User.objects.filter(username='testuser3').exists())
