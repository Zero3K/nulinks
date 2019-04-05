from django import forms
from files.models import TorrentFile, MtCategory


class TorrentFileForm(forms.ModelForm):
    location = forms.CharField(label='Paste Link :')

    class Meta:
        model = TorrentFile
        fields = ('location', 'category')

    def __init__(self, *args, **kwargs):
        super(TorrentFileForm, self).__init__(*args, **kwargs)
        self.fields['category'].queryset = MtCategory.objects.order_by('name')
