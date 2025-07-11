from django.test import TestCase, Client
from django.contrib.auth.models import User
from django.urls import reverse
import django
from packaging import version
from files.models import TorrentFile, MtCategory

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


class TorrentFileEditTest(TestCase):
    def setUp(self):
        """Set up test data."""
        # Create test users
        self.user1 = User.objects.create_user(username='testuser1', password='testpass123')
        self.user2 = User.objects.create_user(username='testuser2', password='testpass123')
        
        # Create test categories
        self.category1 = MtCategory.objects.create(name='Movies')
        self.category2 = MtCategory.objects.create(name='Music')
        
        # Create test torrent files
        self.torrent_file1 = TorrentFile.objects.create(
            name='Test Movie',
            uploader='testuser1',
            location='fopnu://file:/test-movie.mkv',
            category=self.category1
        )
        
        self.torrent_file2 = TorrentFile.objects.create(
            name='Test Song',
            uploader='testuser2',
            location='fopnu://file:/test-song.mp3',
            category=self.category2
        )
        
        self.client = Client()

    def test_edit_torrent_file_get_request(self):
        """Test GET request to edit torrent file page."""
        self.client.login(username='testuser1', password='testpass123')
        response = self.client.get(reverse('edit_torrent_file', kwargs={'file_id': self.torrent_file1.id}))
        
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Edit Category for:')
        self.assertContains(response, 'Test Movie')
        self.assertContains(response, 'Movies')

    def test_edit_torrent_file_post_request(self):
        """Test POST request to update torrent file category."""
        self.client.login(username='testuser1', password='testpass123')
        
        # Update category from Movies to Music
        response = self.client.post(
            reverse('edit_torrent_file', kwargs={'file_id': self.torrent_file1.id}),
            {'category': self.category2.id}
        )
        
        # Should redirect to profile after successful update
        self.assertEqual(response.status_code, 302)
        self.assertRedirects(response, reverse('profile'))
        
        # Verify the category was updated
        self.torrent_file1.refresh_from_db()
        self.assertEqual(self.torrent_file1.category, self.category2)

    def test_edit_torrent_file_permission_denied(self):
        """Test that users cannot edit other users' files."""
        self.client.login(username='testuser1', password='testpass123')
        
        # Try to edit user2's file
        response = self.client.get(reverse('edit_torrent_file', kwargs={'file_id': self.torrent_file2.id}))
        
        # Should return 404 (permission denied)
        self.assertEqual(response.status_code, 404)

    def test_edit_torrent_file_requires_login(self):
        """Test that edit functionality requires login."""
        response = self.client.get(reverse('edit_torrent_file', kwargs={'file_id': self.torrent_file1.id}))
        
        # Should redirect to login page
        self.assertEqual(response.status_code, 302)
        self.assertIn('/login/', response.url)

    def test_profile_page_has_edit_links(self):
        """Test that profile page contains edit links for user's files."""
        self.client.login(username='testuser1', password='testpass123')
        response = self.client.get(reverse('profile'))
        
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Edit Category')
        self.assertContains(response, reverse('edit_torrent_file', kwargs={'file_id': self.torrent_file1.id}))
