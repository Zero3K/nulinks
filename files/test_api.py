from django.test import TestCase
from django.contrib.auth.models import User
from django.urls import reverse
from rest_framework.test import APITestCase
from rest_framework.authtoken.models import Token
from rest_framework import status
import json
from .models import TorrentFile, MtCategory


class APIAuthenticationTest(APITestCase):
    def setUp(self):
        self.user = User.objects.create_user(
            username='testuser',
            password='testpass123'
        )
        self.login_url = reverse('api_login')

    def test_api_login_success(self):
        """Test successful API login returns token"""
        data = {
            'username': 'testuser',
            'password': 'testpass123'
        }
        response = self.client.post(self.login_url, data)
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn('token', response.data)
        self.assertIn('user_id', response.data)
        self.assertIn('username', response.data)
        self.assertEqual(response.data['username'], 'testuser')

    def test_api_login_invalid_credentials(self):
        """Test API login with invalid credentials"""
        data = {
            'username': 'testuser',
            'password': 'wrongpass'
        }
        response = self.client.post(self.login_url, data)
        
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)
        self.assertIn('error', response.data)

    def test_api_login_missing_data(self):
        """Test API login with missing username or password"""
        data = {'username': 'testuser'}
        response = self.client.post(self.login_url, data)
        
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn('error', response.data)


class APILinkPostingTest(APITestCase):
    def setUp(self):
        self.user = User.objects.create_user(
            username='testuser',
            password='testpass123'
        )
        self.token = Token.objects.create(user=self.user)
        self.client.credentials(HTTP_AUTHORIZATION='Token ' + self.token.key)
        
        self.category = MtCategory.objects.create(name='Test Category')
        self.links_url = reverse('api_links')
        self.bulk_links_url = reverse('api_bulk_links')

    def test_create_single_link(self):
        """Test creating a single link via API"""
        data = {
            'location': 'fopnu://file:/test/sample_file.txt',
            'category_id': self.category.id
        }
        response = self.client.post(self.links_url, data)
        
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(response.data['location'], data['location'])
        self.assertEqual(response.data['uploader'], 'testuser')
        self.assertEqual(response.data['name'], 'sample_file.txt')
        
        # Verify the object was created in the database
        torrent_file = TorrentFile.objects.get(id=response.data['id'])
        self.assertEqual(torrent_file.uploader, 'testuser')
        self.assertEqual(torrent_file.location, data['location'])

    def test_create_link_without_authentication(self):
        """Test creating a link without authentication fails"""
        self.client.credentials()  # Remove authentication
        
        data = {
            'location': 'fopnu://file:/test/sample_file.txt'
        }
        response = self.client.post(self.links_url, data)
        
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_create_bulk_links(self):
        """Test creating multiple links at once"""
        data = {
            'links': [
                'fopnu://file:/test/file1.txt',
                'fopnu://file:/test/file2.txt',
                'fopnu://file:/test/file3.txt'
            ],
            'category_id': self.category.id
        }
        response = self.client.post(self.bulk_links_url, data)
        
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(response.data['count'], 3)
        self.assertEqual(len(response.data['created']), 3)
        
        # Verify all files were created
        for i, created_file in enumerate(response.data['created']):
            self.assertEqual(created_file['uploader'], 'testuser')
            self.assertEqual(created_file['location'], data['links'][i])
            self.assertIn('file', created_file['name'])

    def test_bulk_links_too_many(self):
        """Test bulk creation with too many links fails"""
        links = [f'fopnu://file:/test/file{i}.txt' for i in range(101)]
        data = {'links': links}
        
        response = self.client.post(self.bulk_links_url, data)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_list_user_links(self):
        """Test listing links for authenticated user"""
        # Create some test links
        TorrentFile.objects.create(
            name='Test File 1',
            location='fopnu://file:/test/file1.txt',
            uploader='testuser'
        )
        TorrentFile.objects.create(
            name='Test File 2',
            location='fopnu://file:/test/file2.txt',
            uploader='testuser'
        )
        # Create a link for another user
        other_user = User.objects.create_user(username='other', password='pass')
        TorrentFile.objects.create(
            name='Other File',
            location='fopnu://file:/test/other.txt',
            uploader='other'
        )
        
        response = self.client.get(self.links_url)
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 2)  # Only user's own files
        for file_data in response.data:
            self.assertEqual(file_data['uploader'], 'testuser')

    def test_fopnu_link_name_extraction(self):
        """Test that Fopnu link names are extracted correctly"""
        test_cases = [
            {
                'location': 'fopnu://file:/Movies/Action/Sample%20Movie.mkv',
                'expected_name': 'Sample Movie.mkv'
            },
            {
                'location': 'fopnu://user:/some/user/path',
                'expected_name': 'path'
            },
            {
                'location': 'regular_url_not_fopnu',
                'expected_name': 'regular_url_not_fopnu'
            }
        ]
        
        for test_case in test_cases:
            data = {'location': test_case['location']}
            response = self.client.post(self.links_url, data)
            
            self.assertEqual(response.status_code, status.HTTP_201_CREATED)
            self.assertEqual(response.data['name'], test_case['expected_name'])


class APICategoryTest(APITestCase):
    def setUp(self):
        self.user = User.objects.create_user(
            username='testuser',
            password='testpass123'
        )
        self.token = Token.objects.create(user=self.user)
        self.client.credentials(HTTP_AUTHORIZATION='Token ' + self.token.key)
        
        MtCategory.objects.create(name='Movies')
        MtCategory.objects.create(name='Music')
        MtCategory.objects.create(name='Software')
        
        self.categories_url = reverse('api_categories')

    def test_list_categories(self):
        """Test listing all categories"""
        response = self.client.get(self.categories_url)
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 3)
        category_names = [cat['name'] for cat in response.data]
        self.assertIn('Movies', category_names)
        self.assertIn('Music', category_names)
        self.assertIn('Software', category_names)


class APIInfoTest(APITestCase):
    def test_api_info_endpoint(self):
        """Test API info endpoint provides documentation"""
        info_url = reverse('api_info')
        response = self.client.get(info_url)
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn('name', response.data)
        self.assertIn('version', response.data)
        self.assertIn('endpoints', response.data)
        self.assertIn('usage_example', response.data)
        self.assertEqual(response.data['name'], 'Nulinks API')