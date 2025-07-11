from django.test import TestCase, Client
from django.urls import reverse
from files.models import TorrentFile, MtCategory
from django.utils import timezone
from datetime import datetime
import pytz


class DateSortingFixTest(TestCase):
    def setUp(self):
        """Set up test data with specific dates that reproduce the issue"""
        self.client = Client()
        
        # Create test category
        self.category = MtCategory.objects.create(name='Movies')
        
        # Create test files with dates that match the reported issue
        # Brave Story.mkv from April 6, 2019, 4:08 a.m.
        brave_story_date = datetime(2019, 4, 6, 4, 8, 0, tzinfo=pytz.UTC)
        recent_date = datetime(2025, 7, 10, 12, 0, 0, tzinfo=pytz.UTC)
        older_date = datetime(2018, 1, 1, 12, 0, 0, tzinfo=pytz.UTC)
        
        self.brave_story = TorrentFile.objects.create(
            name='Brave Story.mkv',
            uploader='Zero3K',
            location='fopnu://file/Brave%20Story.mkv',
            category=self.category
        )
        self.brave_story.uploadTime = brave_story_date
        self.brave_story.save()
        
        self.recent_file = TorrentFile.objects.create(
            name='Recent Movie.mkv',
            uploader='testuser',
            location='fopnu://file/Recent%20Movie.mkv',
            category=self.category
        )
        self.recent_file.uploadTime = recent_date
        self.recent_file.save()
        
        self.old_file = TorrentFile.objects.create(
            name='Old Movie.mkv',
            uploader='testuser',
            location='fopnu://file/Old%20Movie.mkv',
            category=self.category
        )
        self.old_file.uploadTime = older_date
        self.old_file.save()

    def test_index_page_has_data_timestamp_attributes(self):
        """Test that the index page includes data-timestamp attributes for date sorting"""
        response = self.client.get(reverse('home'))
        self.assertEqual(response.status_code, 200)
        
        # Check that data-timestamp attributes are present in the HTML
        content = response.content.decode()
        
        # Should contain ISO formatted timestamps
        self.assertIn('data-timestamp="2019-04-06T04:08:00+00:00"', content)
        self.assertIn('data-timestamp="2025-07-10T12:00:00+00:00"', content)
        self.assertIn('data-timestamp="2018-01-01T12:00:00+00:00"', content)

    def test_search_page_has_data_timestamp_attributes(self):
        """Test that the search page includes data-timestamp attributes for date sorting"""
        response = self.client.get(reverse('search'))
        self.assertEqual(response.status_code, 200)
        
        # Check that data-timestamp attributes are present in the HTML
        content = response.content.decode()
        
        # Should contain ISO formatted timestamps
        self.assertIn('data-timestamp="2019-04-06T04:08:00+00:00"', content)
        self.assertIn('data-timestamp="2025-07-10T12:00:00+00:00"', content)
        self.assertIn('data-timestamp="2018-01-01T12:00:00+00:00"', content)

    def test_default_database_ordering_preserved(self):
        """Test that the default database ordering (newest first) is preserved"""
        response = self.client.get(reverse('home'))
        content = response.content.decode()
        
        # In descending order by uploadTime, Recent should come first, then Brave Story, then Old
        recent_pos = content.find('Recent Movie.mkv')
        brave_pos = content.find('Brave Story.mkv')
        old_pos = content.find('Old Movie.mkv')
        
        self.assertTrue(recent_pos < brave_pos < old_pos, 
                       "Default ordering should be newest first (Recent < Brave Story < Old)")

    def test_brave_story_not_last_in_descending_order(self):
        """Test that Brave Story (2019) is not the last entry when sorted by date descending"""
        response = self.client.get(reverse('home'))
        content = response.content.decode()
        
        # Find positions in the HTML content
        recent_pos = content.find('Recent Movie.mkv')
        brave_pos = content.find('Brave Story.mkv')
        old_pos = content.find('Old Movie.mkv')
        
        # In descending order: Recent (2025) should be first, 
        # Brave Story (2019) should be middle, Old (2018) should be last
        self.assertTrue(recent_pos < brave_pos, 
                       "Recent Movie (2025) should come before Brave Story (2019)")
        self.assertTrue(brave_pos < old_pos, 
                       "Brave Story (2019) should come before Old Movie (2018)")
        
        # Most importantly: Brave Story should NOT be last
        self.assertTrue(brave_pos < old_pos, 
                       "Brave Story (2019) should NOT be the last entry in descending order")

    def test_search_ordering_matches_index(self):
        """Test that search page has the same ordering as index page"""
        index_response = self.client.get(reverse('home'))
        search_response = self.client.get(reverse('search'))
        
        index_content = index_response.content.decode()
        search_content = search_response.content.decode()
        
        # Extract the relative positions in both pages
        index_recent = index_content.find('Recent Movie.mkv')
        index_brave = index_content.find('Brave Story.mkv')
        index_old = index_content.find('Old Movie.mkv')
        
        search_recent = search_content.find('Recent Movie.mkv')
        search_brave = search_content.find('Brave Story.mkv')
        search_old = search_content.find('Old Movie.mkv')
        
        # Both should have the same relative ordering
        self.assertTrue(index_recent < index_brave < index_old)
        self.assertTrue(search_recent < search_brave < search_old)