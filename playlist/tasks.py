from celery.task import task

from playlist.models import Playlist
from generic_api.epg import WebserviceResponseError


@task
def update_playlist(playlist_id):
    logger = update_playlist.get_logger()
    results = []
    
    try:
        playlist = Playlist.objects.get(pk=playlist_id)
        pl = playlist.as_leaf_class()
        if pl.__class__.__name__ in ('GenericPlaylist'):
            results += pl.update()
        elif pl.__class__.__name__ == 'AdactusPlaylist':
            if pl.adactus_id is not None:
                results += pl.update()
            else:
                logger.error('Update failed for AdactusPlaylist playlist: %s, it has no adactus_id' % playlist.title)
                results.append('Update failed for AdactusPlaylist playlist: %s, it has no adactus_id' % playlist.title)
    except WebserviceResponseError, e:
        logger.exception('Updating playlist failed')
        results.append('Update failed for Playlist playlist %s: %s' % (playlist.title, e))
        raise
    
    return results
