from django.test import TestCase
import django
from packaging import version

# CVE-2019-19844 Security Test
class CVE_2019_19844_Test(TestCase):
    def test_django_version_cve_2019_19844_fixed(self):
        """
        Test that Django version is sufficient to fix CVE-2019-19844.
        
        CVE-2019-19844 affects Django before 1.11.27, 2.x before 2.2.9, and 3.x before 3.0.1.
        This test ensures we're using a patched version.
        """
        current_version = version.parse(django.get_version())
        
        # Minimum safe versions for each major release
        min_version_1_11 = version.parse("1.11.27")
        min_version_2_x = version.parse("2.2.9") 
        min_version_3_x = version.parse("3.0.1")
        
        # Check if we're using a safe version
        is_safe = (
            (current_version >= min_version_3_x) or
            (min_version_2_x <= current_version < version.parse("3.0.0")) or
            (min_version_1_11 <= current_version < version.parse("2.0.0"))
        )
        
        self.assertTrue(is_safe, 
                       f"Django {current_version} is vulnerable to CVE-2019-19844. "
                       f"Minimum safe versions: 1.11.27, 2.2.9, or 3.0.1")
        
        # Specifically verify we're using Django 3.2 which is definitely safe
        self.assertGreaterEqual(current_version, version.parse("3.2"), 
                               "Expected Django 3.2 or higher")
        
    def test_django_admin_accessible(self):
        """Test that Django admin is accessible (basic functionality test)."""
        response = self.client.get('/admin/')
        # Should redirect to login page
        self.assertEqual(response.status_code, 302)
