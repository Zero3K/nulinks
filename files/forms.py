from django import forms
from django.core.exceptions import ValidationError
from files.models import TorrentFile, MtCategory


class TorrentFileForm(forms.ModelForm):
    location = forms.CharField(label='Paste Link :')

    class Meta:
        model = TorrentFile
        fields = ('location', 'category')

    def __init__(self, *args, **kwargs):
        super(TorrentFileForm, self).__init__(*args, **kwargs)
        self.fields['category'].queryset = MtCategory.objects.order_by('name')
    
    def clean_location(self):
        """Check for duplicate links"""
        location = self.cleaned_data['location']
        
        # Check if this link already exists
        existing_file = TorrentFile.find_duplicate(location)
        if existing_file:
            raise ValidationError(
                f'This link has already been posted by {existing_file.uploader} '
                f'on {existing_file.uploadTime.strftime("%Y-%m-%d %H:%M")} '
                f'with the name "{existing_file.name}".'
            )
        
        return location


class TorrentFileEditForm(forms.ModelForm):
    class Meta:
        model = TorrentFile
        fields = ('category',)
        widgets = {
            'category': forms.Select(attrs={'class': 'form-control'})
        }

    def __init__(self, *args, **kwargs):
        super(TorrentFileEditForm, self).__init__(*args, **kwargs)
        self.fields['category'].queryset = MtCategory.objects.order_by('name')
        self.fields['category'].label = 'Category'
