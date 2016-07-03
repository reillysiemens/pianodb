import os
from peewee import SqliteDatabase
from pianodb.pianodb import create_database
from pianodb.model import Artist


def test_sqlite():
    # Setup the database.
    db_path = '/tmp/test-piano.db'
    database = SqliteDatabase(db_path)
    create_database(database)

    # Create a database entry.
    artist = Artist.create(name='test')
    assert artist.name == 'test'

    # Read a database entry.
    artist = Artist.select().where(Artist.name == 'test').first()

    # Update a database entry.
    artist.name = 'test2'
    artist.save()
    artist = Artist.select().where(Artist.name == 'test2').first()
    assert artist.name == 'test2'

    # Delete a database entry.
    artist.delete_instance()
    artist = Artist.select().where(Artist.name == 'test2').first()
    assert artist is None

    # Teardown the database.
    os.remove(db_path)
