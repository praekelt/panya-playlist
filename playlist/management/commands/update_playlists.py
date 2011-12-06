from django.conf import settings
from django.core.management.base import BaseCommand
from playlist.models import Playlist
from generic_api.epg import WebserviceResponseError


class Command(BaseCommand):
    def handle(self, **options):
        print "Updating playlists, please wait..."
        for playlist in Playlist.objects.filter(class_name__in=('GenericPlaylist', 'AdactusPlaylist')):
            print "Updating %s" % playlist
            try:
                pl = playlist.as_leaf_class()
                if pl.__class__.__name__ in ('GenericPlaylist'):
                    if pl.dstv_id is not None:
                        pl.update()
                    else:
                        print "Update failed for %s playlist: %s, it has no matching dstv_id" % (pl.__class__.__name__, playlist.title)
                elif pl.__class__.__name__ == 'AdactusPlaylist':
                    if pl.adactus_id is not None:
                        pl.update()
                    else:
                        print "Update failed for AdactusPlaylist playlist: %s, it has no adactus_id" % playlist.title
            except WebserviceResponseError, e:
                print "Update failed : %s" % e
                
        print "Update complete."
