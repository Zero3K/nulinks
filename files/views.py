from urllib.parse import unquote

from django.conf import settings
from django.contrib.auth import views
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from django.core.files.storage import FileSystemStorage
from django.core.paginator import Paginator
from django.http import HttpResponse, Http404
from django.shortcuts import redirect, render, get_object_or_404

from files.forms import TorrentFileForm, TorrentFileEditForm
from files.models import TorrentFile, MtCategory


def index(request):
    torrent_files = TorrentFile.objects.all().order_by("-uploadTime")
    categories = MtCategory.objects.all().order_by('name')
    
    # Add pagination
    paginator = Paginator(torrent_files, 20)  # Show 20 files per page
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    
    return render(request, "index.html", {
        "tFiles": page_obj,
        "categories": categories,
        "page_obj": page_obj,
    })


def register(request):
    return render(request, "register.html")


@login_required(login_url="/login/")
def get_name(request):
    if request.method == "POST":
        fileUploadForm = TorrentFileForm(request.POST)

        if fileUploadForm.is_valid():
            torrentForm = fileUploadForm.save(commit=False)

            # name of the uploader
            torrentForm.uploader = request.user.username

            # address of the link
            url_location = request.POST.get("location")

            if url_location:
                name = None
                if "fopnu" in url_location:
                    words = ["chat:", "file:", "user:"]
                    if any(word in url_location for word in words):
                        url_location_parsed = unquote(url_location)
                        name = url_location_parsed.split("/")[-1]
                    # elif "file:" in url_location:
                    #     url_location_parsed = unquote(url_location)
                    #     name = url_location_parsed.split("/")[-1]
                    # elif "user:" in url_location:
                    #     url_location_parsed = unquote(url_location)
                    #     name = url_location_parsed.split("/")[-1]
            else:
                torrentForm.name = "default_value"

            if name:
                torrentForm.name = name
            else:
                torrentForm.name = url_location

            torrentForm.save()
            # return HttpResponse("form is valid")
            return redirect("profile")
        else:
            # Form is not valid, return to template with errors
            return render(request, "torrentFileUpload.html", {"form": fileUploadForm})
    else:
        fileUploadForm = TorrentFileForm()
    return render(request, "torrentFileUpload.html", {"form": fileUploadForm})


def search(request):
    """Search for torrent files with optional category filtering"""
    query = request.GET.get('q', '')
    category_id = request.GET.get('category', '')
    
    # Start with all files
    torrent_files = TorrentFile.objects.all()
    
    # Apply text search filter if query is provided
    if query:
        torrent_files = torrent_files.filter(name__icontains=query)
    
    # Apply category filter if category is selected
    selected_category_obj = None
    if category_id:
        try:
            selected_category_obj = MtCategory.objects.get(id=category_id)
            torrent_files = torrent_files.filter(category_id=category_id)
        except MtCategory.DoesNotExist:
            pass
    
    # Order by upload time (newest first)
    torrent_files = torrent_files.order_by('-uploadTime')
    
    # Get all categories for the dropdown
    categories = MtCategory.objects.all().order_by('name')
    
    context = {
        'tFiles': torrent_files,
        'query': query,
        'selected_category': category_id,
        'selected_category_obj': selected_category_obj,
        'categories': categories,
    }
    
    return render(request, 'search.html', context)

"""
def torrentDownload(request, torrentPath):
    file_path = os.torrentPath.join(settings.MEDIA_ROOT, torrentPath)
    if os.path.exists(file_path):
        with open(file_path, 'rb') as fh:
            response = HttpResponse(fh.read(), content_type="application/x-bittorrent")
            response['Content-Disposition'] = 'inline; filename=' + os.path.basename(file_path)
            return response
    else:
        raise Http404
"""


@login_required(login_url="/login/")
def edit_torrent_file(request, file_id):
    """Edit category of a torrent file. Only the uploader can edit their own files."""
    torrent_file = get_object_or_404(TorrentFile, id=file_id)
    
    # Check if the current user is the uploader
    if torrent_file.uploader != request.user.username:
        raise Http404("You can only edit your own files")
    
    if request.method == "POST":
        form = TorrentFileEditForm(request.POST, instance=torrent_file)
        if form.is_valid():
            form.save()
            return redirect("profile")
    else:
        form = TorrentFileEditForm(instance=torrent_file)
    
    return render(request, "edit_torrent_file.html", {
        "form": form, 
        "torrent_file": torrent_file
    })
