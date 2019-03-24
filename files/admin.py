from django.contrib import admin
from files.models import TorrentFile

# Register your models here.

NO_SEARCH_FIELDS = {"uploadTime", "location", "id"}

UNEDITABLE_FIELDS = {"uploadTime", "id"}

NO_FILTER_FIELDS = {"uploadTime", "location", "id"}


class MyModelAdmin(admin.ModelAdmin):

    ALL_FIELDS = set(i.name for i in TorrentFile._meta.fields)
    foreign_keys = [
        i.name
        for i in TorrentFile._meta.fields
        if i.get_internal_type() == "ForeignKey"
    ]
    list_display = [i.name for i in TorrentFile._meta.fields]
    list_editable = tuple(ALL_FIELDS - UNEDITABLE_FIELDS)

    list_display_links = None
    list_filter = tuple(ALL_FIELDS - NO_FILTER_FIELDS)
    search_fields = tuple(ALL_FIELDS - NO_SEARCH_FIELDS)
    autocomplete_fields = foreign_keys
    list_per_page = 10

admin.site.register(TorrentFile, MyModelAdmin)
