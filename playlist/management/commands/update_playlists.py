from django.conf import settings
from django.core.management.base import BaseCommand
from playlist.models import Playlist
from dstv.epg import WebserviceResponseError, Countries, Channels


class Command(BaseCommand):
    def handle(self, **options):
        print "Updating playlists, please wait..."
        sa_country_id = None
        channels =[]
        print "Start by fetching SA country id from dstv..."
        try:
            countries  = Countries(
                settings.TVGUIDE_FEED_COUNTRIES_URL,
                settings.TVGUIDE_FEED_USERNAME,
                settings.TVGUIDE_FEED_PASSWORD,
                settings.TVGUIDE_FEED_UID
                ).countries
            print "Got %s countries" % len(countries)
            for c in countries:
                if c.name == 'South Africa':
                    if c.has_dstv_mobile:
                        sa_country_id = c.id
                        del countries
                        print "South Africa id is  %s" % sa_country_id
                    else:
                        raise WebserviceResponseError("South Africa does not support dstv mobile")
            if not sa_country_id:
                raise WebserviceResponseError("South Africa is not in the list of countries")
            print "Fetching South African channels from dstv..."
            channels = Channels(
                settings.TVGUIDE_FEED_CHANNELS_URL,
                settings.TVGUIDE_FEED_USERNAME,
                settings.TVGUIDE_FEED_PASSWORD,
                settings.TVGUIDE_FEED_UID,
                sa_country_id
                ).channels
            print "Got %s channels" % len(channels)
            print "channel names are %s" % " ,".join([ "--".join([str(i.id), i.name]) for i in channels])
            
        except WebserviceResponseError, e:
            print "Update failed: %s" % e

        for playlist in Playlist.objects.exclude(class_name='ManualPlaylist'):
            print "Updating %s" % playlist
            try:
                pl = playlist.as_leaf_class()
                if pl.__class__.__name__ == 'DSTVPlaylist':
                    if pl.dstv_id is not None:
                        has_valid_dstv_id = False
                        for channel in channels:
                            if int(channel.id) == int(pl.dstv_id):
                                has_valid_dstv_id = True
                        if  has_valid_dstv_id:
                            pl.update()
                        else:
                           print "Update failed for DSTVPlaylist playlist: %s, it has no dstv_id" % playlist.title
                    else:
                        print "Update failed for DSTVPlaylist playlist: %s, it has no matching dstv_id" % playlist.title
                else:
                    if pl.adactus_id is not None:
                        pl.update()
                    else:
                        print "Update failed for DSTVPlaylist playlist: %s, it has no adactus_id" % playlist.title
            except WebserviceResponseError, e:
                print "Update failed : %s" % e
                
        print "Update complete."
