import falcon
import msgpack

from pianodb.pianodb import update_db


def validate(req, resp, songfinish, params):
    # Verify authentication
    if req.get_header('X-Auth-Token') != songfinish.token:
        raise falcon.HTTPUnauthorized(
            title='Authentication required',
            description='Missing or invalid authentication token')

    if not req.content_type == 'application/msgpack':
        raise falcon.HTTPUnsupportedMediaType('Payload must be msgpack')


@falcon.before(validate)
class SongFinish:

    def __init__(self, token):
        self.token = token
        self.song_finish_fields = (
            'artist',
            'title',
            'album',
            'coverArt',
            'stationName',
            'songDuration',
            'songPlayed',
            'rating',
            'detailUrl'
        )

    def on_post(self, req, resp):

        # TODO: What happens if we can't read from the stream?
        try:
            songfinish = msgpack.unpackb(req.stream.read(), encoding='utf-8')
        except msgpack.exceptions.UnpackValueError:
            msg = 'Could not unpack msgpack data'
            raise falcon.HTTPBadRequest('Bad request', msg)

        # Attempt to validate the songfinish keys.
        try:
            if not all(k in songfinish.keys() for k in self.song_finish_fields):
                msg = 'Missing required songfinish field'
                raise falcon.HTTPBadRequest('Bad request', msg)
        except AttributeError:
            msg = 'Invalid datatype'
            raise falcon.HTTPBadRequest('Bad request', msg)

        update_db(songfinish)

        resp.data = msgpack.packb({'created': True})
        resp.content_type = 'application/msgpack'
        resp.status = falcon.HTTP_201
