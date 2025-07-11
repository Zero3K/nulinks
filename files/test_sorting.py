from django.test import TestCase, Client
from django.urls import reverse
from files.models import TorrentFile, MtCategory
from django.utils import timezone
from datetime import timedelta


class SortingPersistenceTest(TestCase):
    def setUp(self):
        """Set up test data with various timestamps"""
        self.client = Client()
        
        # Create test category
        self.category = MtCategory.objects.create(name='Test Category')
        
        # Create test files with different timestamps
        base_time = timezone.now()
        
        self.file1 = TorrentFile.objects.create(
            name='Zebra File',
            uploader='user1',
            location='fopnu://zebra-file',
            uploadTime=base_time - timedelta(days=5),
            category=self.category
        )
        
        self.file2 = TorrentFile.objects.create(
            name='Alpha File',
            uploader='user2',
            location='fopnu://alpha-file',
            uploadTime=base_time - timedelta(days=2),
            category=self.category
        )
        
        self.file3 = TorrentFile.objects.create(
            name='Beta File',
            uploader='user3',
            location='fopnu://beta-file',
            uploadTime=base_time,
            category=self.category
        )

    def test_index_page_loads(self):
        """Test that the index page loads successfully"""
        response = self.client.get(reverse('home'))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'myTable')
        self.assertContains(response, 'Zebra File')
        self.assertContains(response, 'Alpha File')
        self.assertContains(response, 'Beta File')

    def test_sorting_javascript_included(self):
        """Test that the sorting JavaScript is included in the page"""
        response = self.client.get(reverse('home'))
        self.assertEqual(response.status_code, 200)
        
        # Check for sorting functionality
        self.assertContains(response, 'nulinks_table_sort')
        self.assertContains(response, 'localStorage')
        self.assertContains(response, 'sortTable')
        self.assertContains(response, 'updateSortIndicator')

    def test_table_structure(self):
        """Test that the table has the correct structure for sorting"""
        response = self.client.get(reverse('home'))
        self.assertEqual(response.status_code, 200)
        
        # Check table headers
        self.assertContains(response, 'Category')
        self.assertContains(response, 'Name')
        self.assertContains(response, 'Added on')
        self.assertContains(response, 'Posted by')
        
        # Check that table has correct ID
        self.assertContains(response, 'id="myTable"')

    def test_default_ordering(self):
        """Test that the default ordering is by upload time descending"""
        response = self.client.get(reverse('home'))
        content = response.content.decode()
        
        # The default ordering should be by -uploadTime (newest first)
        # So we should see Beta File (newest) before Alpha File before Zebra File (oldest)
        beta_pos = content.find('Beta File')
        alpha_pos = content.find('Alpha File') 
        zebra_pos = content.find('Zebra File')
        
        self.assertTrue(beta_pos < alpha_pos < zebra_pos)

    def test_css_styles_included(self):
        """Test that the sorting CSS styles are included"""
        response = self.client.get(reverse('home'))
        self.assertEqual(response.status_code, 200)
        
        # Check for sorting-related CSS
        self.assertContains(response, 'cursor: pointer')
        self.assertContains(response, 'sort-indicator')
        self.assertContains(response, 'sort-asc, .sort-desc')