from django import forms
from files.models import TorrentFile


class TorrentFileForm(forms.ModelForm):
    location = forms.CharField(label='Paste Link :')

    class Meta:
        model = TorrentFile
        fields = ('location', 'category')
