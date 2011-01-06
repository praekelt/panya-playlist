from django.contrib import admin
from django.contrib.contenttypes.models import ContentType

from playlist.models import Playlist, ScheduledPlaylist, PlaylistEntry
from panya.admin import ModelBaseAdmin

class PlaylistEntryInline(admin.TabularInline):
    model = PlaylistEntry

class PlaylistAdmin(ModelBaseAdmin):
    inlines = ModelBaseAdmin.inlines + [
        PlaylistEntryInline,
    ]

class LimitedPlaylistAdmin(ModelBaseAdmin):
    def queryset(self, request):
        """
        Limit queryset to Playlist objects (those of content type Playlist)
        """
        playlist_type = ContentType.objects.get_for_model(Playlist)
        return self.model.objects.filter(content_type=playlist_type)

class ScheduledPlaylistAdmin(admin.ModelAdmin):
    list_display = ('__unicode__','content','playlist','start','end')
    list_filter = ('content',)
    search_fields = ['playlist__title']

admin.site.register(Playlist, LimitedPlaylistAdmin)
admin.site.register(PlaylistEntry)
admin.site.register(ScheduledPlaylist, ScheduledPlaylistAdmin)
