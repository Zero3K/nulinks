from django.conf import settings
from django.contrib.auth import views
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from django.core.files.storage import FileSystemStorage
from django.http import HttpResponse
from django.shortcuts import redirect, render

from files.forms import TorrentFileForm
from files.models import TorrentFile


def index(request):
    torrentFile = TorrentFile.objects.all().order_by('-uploadTime')
    return render(request, 'index.html', {'tFiles': torrentFile})


def register(request):
    return render(request, 'register.html')


@login_required(login_url="/login/")
def get_name(request):
    if request.method == 'POST':
        fileUploadForm = TorrentFileForm(request.POST)

        if fileUploadForm.is_valid():
            torrentForm = fileUploadForm.save(commit=False)

            # name of the uploader
            torrentForm.uploader = request.user.username

            # address of the link
            torrentForm.name = request.POST.get('location', 'default_value')

            torrentForm.save()
            # return HttpResponse("form is valid")
            return redirect('profile')
        else:
            return HttpResponse("form is not valid")
        #    return HttpResponse("<h1>file not valid</h1>")
    else:
        fileUploadForm = TorrentFileForm()
    return render(request, 'torrentFileUpload.html', {'form': fileUploadForm})


# def search(request, q):
#     userQuery = request.GET['q']
#     torrentFile = TorrentFile.objects.filter(name__icontains=userQuery)
#     return render(request, 'search.html', {'tFiles': torrentFile})

'''
def torrentDownload(request, torrentPath):
    file_path = os.torrentPath.join(settings.MEDIA_ROOT, torrentPath)
    if os.path.exists(file_path):
        with open(file_path, 'rb') as fh:
            response = HttpResponse(fh.read(), content_type="application/x-bittorrent")
            response['Content-Disposition'] = 'inline; filename=' + os.path.basename(file_path)
            return response
    else:
        raise Http404
'''
