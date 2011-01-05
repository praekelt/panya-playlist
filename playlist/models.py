from datetime import datetime, timedelta

from django.conf import settings
from django.db import models

from adactus import epg as adactus_epg
from panya.models import ModelBase
from dstv import epg as dstv_epg
from playlist.managers import ContentPlaylistManager

class Playlist(ModelBase):
    
    class Meta():
        verbose_name = "Playlist"
        verbose_name_plural = "Playlists"

    def current_entry(self):
        now = datetime.now()
        entries = self.playlistentry_set.filter(start__lt=now, end__gt=now, state="published").order_by('-start')
        return entries[0] if entries else None
    
    def next_entry(self):
        now = datetime.now()
        entries = self.playlistentry_set.filter(start__gt=now, state="published").order_by('start')
        return entries[0] if entries else None

    def __unicode__(self):
        return self.title

class ManualPlaylist(Playlist):
    class Meta():
        verbose_name = "Manual Playlist"
        verbose_name_plural = "Manual Playlists"

    def __unicode__(self):
        return '%s (Manual)' % self.title

class DSTVPlaylist(Playlist):
    channel_id = models.CharField(
        max_length=128,
    )
    
    class Meta():
        verbose_name = "DSTV Playlist"
        verbose_name_plural = "DSTV Playlists"

    def update(self):
        schedule = dstv_epg.Schedule(
            url = settings.DSTV_EPG_URL, 
            user = settings.DSTV_WEBSERVICE_USERNAME, 
            passwd = settings.DSTV_WEBSERVICE_PASSWORD, 
            channel_id = int(self.channel_id),
            day_id = 0,
        )

        # delete entries older than 2 days
        delete_cutoff = datetime.now() - timedelta(days=2)
        PlaylistEntry.objects.filter(playlist=self, end__lt=delete_cutoff).delete()
        
        for show in schedule.shows:
            entry, created = PlaylistEntry.objects.get_or_create(playlist=self, title=show.title, start=show.start_time, end=show.end_time,  state="published")
            if created:
                entry.save()

    def __unicode__(self):
        return '%s (DSTV)' % self.title

class AdactusPlaylist(Playlist):
    channel_id = models.CharField(
        max_length=128,
    )
    
    class Meta():
        verbose_name = "Adactus Playlist"
        verbose_name_plural = "Adactus Playlists"

    def update(self):
        schedule = adactus_epg.Schedule(
            url = settings.ADACTUS_RESTFUL_WEBSERVICE_URL, 
            user = settings.ADACTUS_RESTFUL_WEBSERVICE_USER, 
            passwd = settings.ADACTUS_RESTFUL_WEBSERVICE_PASS, 
            channel_id = self.channel_id,
        )
        
        # delete entries older than 2 days
        delete_cutoff = datetime.now() - timedelta(days=2)
        PlaylistEntry.objects.filter(playlist=self, end__lt=delete_cutoff).delete()
        
        print "Creating %s new entries" % len(schedule.shows)
        for show in schedule.shows:
            entry, created = PlaylistEntry.objects.get_or_create(playlist=self, title=show.title, start=show.start_time, end=show.end_time,  state="published")
            if created:
                entry.save()
                print "Created %s" % entry
   
    def __unicode__(self):
        return '%s (Adactus)' % self.title


class PlaylistEntry(ModelBase):
    
    playlist = models.ForeignKey(Playlist)
    start = models.DateTimeField(
        verbose_name="Starting Date & Time", 
        help_text="Date and time at which this entry starts."
    )
    end = models.DateTimeField(
        verbose_name="Ending Date & Time", 
        help_text="Date and time at which this entry ends."
    )

    def __unicode__(self):
        return '%s %s - %s' % (self.title, self.start, self.end)

    class Meta():
        verbose_name = "Playlist Entry"
        verbose_name_plural = "Playlist Entries"
        ordering = ['start', 'end']


class ContentPlaylist(models.Model):
    objects = ContentPlaylistManager()

    content = models.ForeignKey("panya.ModelBase", related_name="content_content_playlist_set")
    playlist = models.ForeignKey(Playlist, related_name="playlist_content_playlist_set")
    commence = models.DateTimeField()
    expire = models.DateTimeField()

    def get_inclusive_entries(self):
        """
        Returns those playlist entries that fall between commence and expire.
        A playlist entry falls between commence and expire if it starts on or after
        commence and before expire. Order by start.
        """
        return self.playlist.playlistentry_set.filter(start__gt=self.commence, start__lt=self.expire, is_public=True).order_by('start')

    def get_inclusive_entries_today(self):
        """
        Get inclusive entries limited to entries for the current day
        A playlist entry applies to the current day if it ends on or after
        00:00 today and starts before 23:59:59 today. Order by start.
        """
        today = datetime.now().date()
        start = datetime(year=today.year, month=today.month, day=today.day)
        end = datetime(year=today.year, month=today.month, day=today.day, hour=23, minute=59, second=59)
        return self.get_inclusive_entries().filter(end__gt=start, start__lt=end).order_by('start')
