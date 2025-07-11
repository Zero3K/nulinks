from rest_framework import serializers
from django.contrib.auth.models import User
from .models import TorrentFile, MtCategory


class MtCategorySerializer(serializers.ModelSerializer):
    class Meta:
        model = MtCategory
        fields = ['id', 'name']


class TorrentFileSerializer(serializers.ModelSerializer):
    uploader = serializers.CharField(read_only=True)
    category = MtCategorySerializer(read_only=True)
    category_id = serializers.PrimaryKeyRelatedField(
        queryset=MtCategory.objects.all(),
        source='category',
        write_only=True,
        required=False,
        allow_null=True
    )
    name = serializers.CharField(required=False)  # Make name optional, we'll generate it

    class Meta:
        model = TorrentFile
        fields = ['id', 'name', 'location', 'uploader', 'uploadTime', 'category', 'category_id']
        read_only_fields = ['id', 'uploader', 'uploadTime']

    def create(self, validated_data):
        # Extract name from location if not provided
        location = validated_data.get('location', '')
        if 'name' not in validated_data or not validated_data['name']:
            validated_data['name'] = self._extract_name_from_link(location)
        
        # Set the uploader to the current user
        validated_data['uploader'] = self.context['request'].user.username
        return super().create(validated_data)

    def _extract_name_from_link(self, url_location):
        """Extract name from Fopnu link, similar to existing logic"""
        from urllib.parse import unquote
        
        if url_location and "fopnu" in url_location:
            words = ["chat:", "file:", "user:"]
            if any(word in url_location for word in words):
                url_location_parsed = unquote(url_location)
                return url_location_parsed.split("/")[-1]
        
        return url_location or "default_value"


class BulkTorrentFileSerializer(serializers.Serializer):
    links = serializers.ListField(
        child=serializers.CharField(max_length=255),
        min_length=1,
        max_length=100  # Limit bulk operations
    )
    category_id = serializers.PrimaryKeyRelatedField(
        queryset=MtCategory.objects.all(),
        required=False,
        allow_null=True
    )

    def create(self, validated_data):
        links = validated_data['links']
        category = validated_data.get('category_id')
        user = self.context['request'].user
        
        created_files = []
        for link in links:
            # Parse the name from the link similar to the existing logic
            name = self._extract_name_from_link(link)
            
            torrent_file = TorrentFile.objects.create(
                name=name,
                location=link,
                uploader=user.username,
                category=category
            )
            created_files.append(torrent_file)
        
        return created_files

    def _extract_name_from_link(self, url_location):
        """Extract name from Fopnu link, similar to existing logic"""
        from urllib.parse import unquote
        
        if url_location and "fopnu" in url_location:
            words = ["chat:", "file:", "user:"]
            if any(word in url_location for word in words):
                url_location_parsed = unquote(url_location)
                return url_location_parsed.split("/")[-1]
        
        return url_location or "default_value"