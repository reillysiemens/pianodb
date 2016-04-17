import datetime
from peewee import Model, CharField, ForeignKeyField, TimeField, DateTimeField, SqliteDatabase
from playhouse.fields import ManyToManyField

db = SqliteDatabase('piano.db')


class BaseModel(Model):
    class Meta:
        database = db


class Artist(BaseModel):
    name = CharField(unique=True)


class Album(BaseModel):
    title = CharField()
    artist = ForeignKeyField(Artist, related_name='albums')
    cover_art = CharField(null=True)


# TODO: Get song features from `detailUrl`.
class Song(BaseModel):
    title = CharField()
    album = ForeignKeyField(Album, related_name='songs')
    duration = TimeField()


class Feature(BaseModel):
    text = CharField(unique=True)
    songs = ManyToManyField(Song, related_name='features')


SongFeature = Feature.songs.get_through_model()


class Station(BaseModel):
    name = CharField(unique=True)
    artists = ManyToManyField(Artist, related_name='stations')
    songs = ManyToManyField(Song, related_name='stations')


StationArtist = Station.artists.get_through_model()
StationSong = Station.songs.get_through_model()


class Play(BaseModel):
    timestamp = DateTimeField(default=datetime.datetime.now)
    station = ForeignKeyField(Station, related_name='plays')
    song = ForeignKeyField(Song, related_name='plays')
    duration = TimeField()
