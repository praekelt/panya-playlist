
## django imports
from django.contrib import admin

## our own app imports
from playlist.models import AdactusPlaylist, DSTVPlaylist, ManualPlaylist, ContentPlaylist, PlaylistEntry
from panya.admin import ModelBaseAdmin

class AdminContentPlaylist(admin.ModelAdmin):
    list_display = ('__str__','content','playlist','commence','expire')
    list_filter = ('content',)
    search_fields = ['playlist__title']

admin.site.register(AdactusPlaylist,ModelBaseAdmin)
admin.site.register(DSTVPlaylist,ModelBaseAdmin)
admin.site.register(ManualPlaylist,ModelBaseAdmin)
admin.site.register(PlaylistEntry,ModelBaseAdmin)
admin.site.register(ContentPlaylist,AdminContentPlaylist)