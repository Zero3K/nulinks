from django.contrib import admin
from files.models import TorrentFile, MtCategory

# Register your models here.

NO_SEARCH_FIELDS = {'created_at', 'modified_at', "uploadTime", "location", "id"}

UNEDITABLE_FIELDS = {'created_at', 'modified_at', "uploadTime", "id"}

NO_FILTER_FIELDS = {"uploadTime", "location", "id"}

MODELS = (TorrentFile, MtCategory)

for my_model in MODELS:
    class MyModelAdmin(admin.ModelAdmin):

        ALL_FIELDS = set(i.name for i in my_model._meta.fields)
        foreign_keys = [
            i.name
            for i in my_model._meta.fields
            if i.get_internal_type() == "ForeignKey"
        ]
        list_display = [i.name for i in my_model._meta.fields]
        list_editable = tuple(ALL_FIELDS - UNEDITABLE_FIELDS)

        list_display_links = None
        list_filter = tuple(ALL_FIELDS - NO_FILTER_FIELDS)
        search_fields = tuple(ALL_FIELDS - NO_SEARCH_FIELDS)
        autocomplete_fields = foreign_keys
        list_per_page = 10

    admin.site.register(my_model, MyModelAdmin)
