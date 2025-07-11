from django.test import TestCase, Client
from django.contrib.auth.models import User
from django.urls import reverse
import django
from packaging import version
from files.models import TorrentFile, MtCategory

from django.test import TestCase, Client
from django.contrib.auth.models import User
from django.urls import reverse
from django.core.exceptions import ValidationError
import django
from packaging import version
from files.models import TorrentFile, MtCategory
from files.forms import TorrentFileForm
from rest_framework.test import APIClient
from rest_framework.authtoken.models import Token


class DuplicateLinkDetectionTest(TestCase):
    def setUp(self):
        """Set up test data for duplicate detection tests."""
        # Create test users
        self.user1 = User.objects.create_user(username='testuser1', password='testpass123')
        self.user2 = User.objects.create_user(username='testuser2', password='testpass123')
        
        # Create test categories
        self.category1 = MtCategory.objects.create(name='Movies')
        self.category2 = MtCategory.objects.create(name='Music')
        
        # Create a test link that will be used for duplicate testing
        self.existing_link = 'fopnu://file:/test-movie.mkv'
        self.torrent_file1 = TorrentFile.objects.create(
            name='Test Movie',
            uploader='testuser1',
            location=self.existing_link,
            category=self.category1
        )
        
        self.client = Client()
        self.api_client = APIClient()

    def test_find_duplicate_method(self):
        """Test the find_duplicate class method."""
        # Test finding existing duplicate
        duplicate = TorrentFile.find_duplicate(self.existing_link)
        self.assertEqual(duplicate, self.torrent_file1)
        
        # Test with non-existing link
        non_duplicate = TorrentFile.find_duplicate('fopnu://file:/non-existing.mkv')
        self.assertIsNone(non_duplicate)

    def test_form_validation_duplicate_detection(self):
        """Test form validation prevents duplicate links."""
        form_data = {
            'location': self.existing_link,
            'category': self.category2.id
        }
        form = TorrentFileForm(data=form_data)
        
        # Form should be invalid due to duplicate link
        self.assertFalse(form.is_valid())
        self.assertIn('location', form.errors)
        self.assertIn('This link has already been posted', str(form.errors['location']))

    def test_form_validation_allows_new_links(self):
        """Test form validation allows new unique links."""
        form_data = {
            'location': 'fopnu://file:/unique-new-file.mkv',
            'category': self.category2.id
        }
        form = TorrentFileForm(data=form_data)
        
        # Form should be valid for new unique link
        self.assertTrue(form.is_valid())

    def test_web_interface_duplicate_prevention(self):
        """Test web interface prevents duplicate link submission."""
        self.client.login(username='testuser2', password='testpass123')
        
        response = self.client.post(reverse('upload'), {
            'location': self.existing_link,
            'category': self.category2.id
        })
        
        # Should return to form with error, not redirect to profile
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'This link has already been posted')
        
        # Verify no new TorrentFile was created
        torrent_count = TorrentFile.objects.filter(location=self.existing_link).count()
        self.assertEqual(torrent_count, 1)  # Only the original one

    def test_web_interface_allows_new_links(self):
        """Test web interface allows new unique links."""
        self.client.login(username='testuser2', password='testpass123')
        
        new_link = 'fopnu://file:/unique-web-file.mkv'
        response = self.client.post(reverse('upload'), {
            'location': new_link,
            'category': self.category2.id
        })
        
        # Should redirect to profile after successful submission
        self.assertEqual(response.status_code, 302)
        self.assertRedirects(response, reverse('profile'))
        
        # Verify new TorrentFile was created
        new_file = TorrentFile.objects.get(location=new_link)
        self.assertEqual(new_file.uploader, 'testuser2')

    def test_api_single_link_duplicate_prevention(self):
        """Test API prevents duplicate single link submission."""
        # Create API token for user2
        token = Token.objects.create(user=self.user2)
        self.api_client.credentials(HTTP_AUTHORIZATION='Token ' + token.key)
        
        response = self.api_client.post('/api/links/', {
            'location': self.existing_link,
            'category_id': self.category2.id
        })
        
        # Should return 400 Bad Request with validation error
        self.assertEqual(response.status_code, 400)
        self.assertIn('location', response.data)
        self.assertIn('This link has already been posted', str(response.data['location']))

    def test_api_single_link_allows_new_links(self):
        """Test API allows new unique single links."""
        # Create API token for user2
        token = Token.objects.create(user=self.user2)
        self.api_client.credentials(HTTP_AUTHORIZATION='Token ' + token.key)
        
        new_link = 'fopnu://file:/unique-api-file.mkv'
        response = self.api_client.post('/api/links/', {
            'location': new_link,
            'category_id': self.category2.id
        })
        
        # Should return 201 Created
        self.assertEqual(response.status_code, 201)
        self.assertEqual(response.data['location'], new_link)
        self.assertEqual(response.data['uploader'], 'testuser2')

    def test_api_bulk_link_duplicate_prevention(self):
        """Test API prevents duplicate bulk link submission."""
        # Create API token for user2
        token = Token.objects.create(user=self.user2)
        self.api_client.credentials(HTTP_AUTHORIZATION='Token ' + token.key)
        
        response = self.api_client.post('/api/links/bulk/', {
            'links': [
                'fopnu://file:/new-file1.mkv',
                self.existing_link,  # This is a duplicate
                'fopnu://file:/new-file2.mkv'
            ],
            'category_id': self.category2.id
        })
        
        # Should return 400 Bad Request with validation error
        self.assertEqual(response.status_code, 400)
        self.assertIn('links', response.data)
        self.assertIn('has already been posted', str(response.data['links']))

    def test_api_bulk_link_allows_all_new_links(self):
        """Test API allows bulk submission when all links are unique."""
        # Create API token for user2
        token = Token.objects.create(user=self.user2)
        self.api_client.credentials(HTTP_AUTHORIZATION='Token ' + token.key)
        
        new_links = [
            'fopnu://file:/bulk-file1.mkv',
            'fopnu://file:/bulk-file2.mkv',
            'fopnu://file:/bulk-file3.mkv'
        ]
        
        response = self.api_client.post('/api/links/bulk/', {
            'links': new_links,
            'category_id': self.category2.id
        })
        
        # Should return 201 Created
        self.assertEqual(response.status_code, 201)
        self.assertEqual(response.data['count'], 3)
        self.assertEqual(len(response.data['created']), 3)
        
        # Verify all files were created
        for link in new_links:
            file_exists = TorrentFile.objects.filter(location=link).exists()
            self.assertTrue(file_exists)

    def test_duplicate_detection_error_message_format(self):
        """Test that duplicate detection error messages contain useful information."""
        form_data = {
            'location': self.existing_link,
            'category': self.category2.id
        }
        form = TorrentFileForm(data=form_data)
        form.is_valid()
        
        error_message = str(form.errors['location'][0])
        self.assertIn('testuser1', error_message)  # Original uploader
        self.assertIn('Test Movie', error_message)  # Original name
        self.assertIn('already been posted', error_message)  # Clear message


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
