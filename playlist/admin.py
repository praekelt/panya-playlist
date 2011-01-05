from django.contrib import admin

from playlist.models import Playlist, ScheduledPlaylist, PlaylistEntry
from panya.admin import ModelBaseAdmin

class PlaylistEntryInline(admin.TabularInline):
    model = PlaylistEntry

class PlaylistAdmin(ModelBaseAdmin):
    inlines = ModelBaseAdmin.inlines + [
        PlaylistEntryInline,
    ]

class ScheduledPlaylistAdmin(admin.ModelAdmin):
    list_display = ('__unicode__','content','playlist','start','end')
    list_filter = ('content',)
    search_fields = ['playlist__title']

admin.site.register(Playlist, PlaylistAdmin)
admin.site.register(PlaylistEntry)
admin.site.register(ScheduledPlaylist, ScheduledPlaylistAdmin)
