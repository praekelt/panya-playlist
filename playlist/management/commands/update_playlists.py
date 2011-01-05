from django.core.management.base import BaseCommand
from playlist.models import Playlist
from dstv.epg import WebserviceResponseError

class Command(BaseCommand):
    def handle(self, **options):
        print "Updating playlists, please wait..."
        for playlist in Playlist.objects.exclude(classname='ManualPlaylist'):
            print "Updating %s" % playlist
            try:
                playlist.as_leaf_class().update()
            except WebserviceResponseError, e:
                print "Update failed: %s" % e
        print "Update complete."
