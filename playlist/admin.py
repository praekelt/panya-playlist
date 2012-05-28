from django.contrib import admin
from django.contrib.contenttypes.models import ContentType

from playlist.models import Playlist, ScheduledPlaylist, PlaylistEntry
from panya.admin import ModelBaseAdmin


def update_epg(modeladmin, request, queryset):
    try:
        from celery.execute import send_task
        for playlist in queryset.all():
            send_task('playlist.tasks.update_playlist', [playlist.id])
        if queryset.count() == 1:
            message_bit = '1 item was'
        else:
            message_bit = '%s items were' % queryset.count()
        modeladmin.message_user(request, '%s queued for EPG update.' % message_bit)
    except ImportError:
        modeladmin.message_user(request, 'EPG update could not be queued - please install celery on this platform.')
update_epg.short_description = 'Update EPG for selected items'


class PlaylistEntryInline(admin.TabularInline):
    model = PlaylistEntry


class PlaylistAdmin(ModelBaseAdmin):
    inlines = ModelBaseAdmin.inlines + [
        PlaylistEntryInline,
    ]
    actions = ModelBaseAdmin.actions + [update_epg]


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
