from django.test import TestCase, Client
from django.contrib.auth.models import User
from django.urls import reverse
from files.models import TorrentFile, MtCategory


class PaginationTest(TestCase):
    def setUp(self):
        """Set up test data for pagination tests."""
        # Create test user and category
        self.user = User.objects.create_user(username='testuser', password='testpass123')
        self.category = MtCategory.objects.create(name='Movies')
        
        # Create 50 test records to test pagination
        for i in range(50):
            TorrentFile.objects.create(
                name=f'Test Movie {i+1}',
                uploader='testuser',
                location=f'fopnu://file:/test-movie-{i+1}.mkv',
                category=self.category
            )
        
        self.client = Client()

    def test_index_page_pagination_default(self):
        """Test that index page shows 20 items by default."""
        response = self.client.get(reverse('home'))
        
        self.assertEqual(response.status_code, 200)
        self.assertIn('page_obj', response.context)
        self.assertEqual(len(response.context['tFiles']), 20)
        self.assertEqual(response.context['page_obj'].number, 1)
        self.assertTrue(response.context['page_obj'].has_next())
        self.assertFalse(response.context['page_obj'].has_previous())

    def test_index_page_pagination_page_2(self):
        """Test that page 2 shows the next 20 items."""
        response = self.client.get(reverse('home') + '?page=2')
        
        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(response.context['tFiles']), 20)
        self.assertEqual(response.context['page_obj'].number, 2)
        self.assertTrue(response.context['page_obj'].has_next())
        self.assertTrue(response.context['page_obj'].has_previous())

    def test_index_page_pagination_last_page(self):
        """Test that last page shows remaining items."""
        response = self.client.get(reverse('home') + '?page=3')
        
        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(response.context['tFiles']), 10)  # 50 total - 40 from first 2 pages = 10
        self.assertEqual(response.context['page_obj'].number, 3)
        self.assertFalse(response.context['page_obj'].has_next())
        self.assertTrue(response.context['page_obj'].has_previous())

    def test_index_page_pagination_total_count(self):
        """Test that pagination correctly shows total count."""
        response = self.client.get(reverse('home'))
        
        self.assertEqual(response.context['page_obj'].paginator.count, 50)
        self.assertEqual(response.context['page_obj'].paginator.num_pages, 3)

    def test_index_page_pagination_invalid_page(self):
        """Test that invalid page numbers are handled gracefully."""
        # Test page number too high
        response = self.client.get(reverse('home') + '?page=999')
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.context['page_obj'].number, 3)  # Should show last page
        
        # Test invalid page parameter
        response = self.client.get(reverse('home') + '?page=invalid')
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.context['page_obj'].number, 1)  # Should show first page

    def test_index_page_pagination_template_context(self):
        """Test that pagination template variables are properly set."""
        response = self.client.get(reverse('home'))
        
        # Check that both tFiles and page_obj are in context
        self.assertIn('tFiles', response.context)
        self.assertIn('page_obj', response.context)
        
        # They should be the same object (page_obj)
        self.assertEqual(response.context['tFiles'], response.context['page_obj'])