from rest_framework import generics, status
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.authtoken.models import Token
from django.contrib.auth import authenticate
from django.contrib.auth.models import User
from .models import TorrentFile, MtCategory
from .serializers import TorrentFileSerializer, BulkTorrentFileSerializer, MtCategorySerializer


@api_view(['POST'])
@permission_classes([])
def api_login(request):
    """
    API endpoint for authentication. Returns an API token for subsequent requests.
    
    POST /api/auth/login/
    {
        "username": "your_username",
        "password": "your_password"
    }
    
    Returns:
    {
        "token": "your_api_token",
        "user_id": 123,
        "username": "your_username"
    }
    """
    username = request.data.get('username')
    password = request.data.get('password')
    
    if not username or not password:
        return Response({
            'error': 'Username and password are required'
        }, status=status.HTTP_400_BAD_REQUEST)
    
    user = authenticate(username=username, password=password)
    if user:
        token, created = Token.objects.get_or_create(user=user)
        return Response({
            'token': token.key,
            'user_id': user.id,
            'username': user.username
        })
    else:
        return Response({
            'error': 'Invalid credentials'
        }, status=status.HTTP_401_UNAUTHORIZED)


class TorrentFileListCreateView(generics.ListCreateAPIView):
    """
    List all torrent files for the authenticated user or create a new one.
    
    GET /api/links/
    - Lists all links posted by the authenticated user
    
    POST /api/links/
    {
        "location": "fopnu://file:/path/to/file",
        "category_id": 1  // optional
    }
    """
    serializer_class = TorrentFileSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        return TorrentFile.objects.filter(uploader=self.request.user.username).order_by('-uploadTime')


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def bulk_create_links(request):
    """
    Create multiple torrent file links at once.
    
    POST /api/links/bulk/
    {
        "links": [
            "fopnu://file:/path/to/file1",
            "fopnu://file:/path/to/file2",
            "fopnu://file:/path/to/file3"
        ],
        "category_id": 1  // optional, applies to all links
    }
    
    Returns:
    {
        "created": [
            {"id": 1, "name": "file1", "location": "fopnu://file:/path/to/file1", ...},
            {"id": 2, "name": "file2", "location": "fopnu://file:/path/to/file2", ...},
            ...
        ],
        "count": 3
    }
    """
    serializer = BulkTorrentFileSerializer(data=request.data, context={'request': request})
    
    if serializer.is_valid():
        created_files = serializer.save()
        file_serializer = TorrentFileSerializer(created_files, many=True)
        return Response({
            'created': file_serializer.data,
            'count': len(created_files)
        }, status=status.HTTP_201_CREATED)
    
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class CategoryListView(generics.ListAPIView):
    """
    List all available categories.
    
    GET /api/categories/
    """
    queryset = MtCategory.objects.all().order_by('name')
    serializer_class = MtCategorySerializer
    permission_classes = [IsAuthenticated]


@api_view(['GET'])
@permission_classes([])
def api_info(request):
    """
    Get API information and usage instructions.
    
    GET /api/info/
    """
    return Response({
        'name': 'Nulinks API',
        'version': '1.0',
        'description': 'API for automated posting of Fopnu links',
        'authentication': {
            'type': 'Token Authentication',
            'header': 'Authorization: Token <your_token>',
            'login_endpoint': '/api/auth/login/'
        },
        'endpoints': {
            'login': 'POST /api/auth/login/',
            'list_user_links': 'GET /api/links/',
            'create_single_link': 'POST /api/links/',
            'create_bulk_links': 'POST /api/links/bulk/',
            'list_categories': 'GET /api/categories/',
            'api_info': 'GET /api/info/'
        },
        'usage_example': {
            'step1': 'Login: POST /api/auth/login/ with {"username": "user", "password": "pass"}',
            'step2': 'Get token from response',
            'step3': 'Use token in Authorization header for subsequent requests',
            'step4': 'Post links: POST /api/links/ or /api/links/bulk/ with link data'
        }
    })