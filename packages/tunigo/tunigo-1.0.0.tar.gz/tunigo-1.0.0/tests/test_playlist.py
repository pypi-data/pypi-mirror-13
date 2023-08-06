from __future__ import unicode_literals

from tunigo.genre import Genre, SubGenre
from tunigo.playlist import Playlist


class TestPlaylist(object):

    def test_repr(self):
        playlist = Playlist(uri='some:uri')

        assert playlist.__repr__() == "Playlist(uri='some:uri')"

    def test_str(self):
        playlist = Playlist(title='Title', uri='some:uri')

        assert playlist.__str__() == 'Title (some:uri)'

    def test_creates_instance_from_item_array(self):
        playlist = Playlist(item_array={
            'created': 1,
            'description': 'Some description',
            'id': 'Some id',
            'image': 'Some image',
            'location': 'Some location',
            'numSubscribers': 2,
            'title': 'Some title',
            'updated': 3,
            'uri': 'some:uri',
            'version': 4
        })

        assert playlist.created == 1
        assert playlist.description == 'Some description'
        assert playlist.id == 'Some id'
        assert playlist.image == 'Some image'
        assert playlist.location == 'Some location'
        assert isinstance(playlist.main_genre, Genre)
        assert playlist.main_genre.playlist == playlist
        assert playlist.num_subscribers == 2
        assert isinstance(playlist.sub_genre, SubGenre)
        assert playlist.sub_genre.main_genre == playlist.main_genre
        assert playlist.title == 'Some title'
        assert playlist.updated == 3
        assert playlist.uri == 'some:uri'
        assert playlist.version == 4

    def test_creates_genre_from_template_in_item_array(self):
        playlist = Playlist(item_array={
            'mainGenreTemplate': 'Some main genre template',
            'subGenreTemplate': 'Some sub genre template'
        })

        assert isinstance(playlist.main_genre, Genre)
        assert playlist.main_genre.playlist == playlist
        assert playlist.main_genre.template_name == 'Some main genre template'
        assert playlist.main_genre_template == 'Some main genre template'

        assert isinstance(playlist.sub_genre, SubGenre)
        assert playlist.sub_genre.main_genre == playlist.main_genre
        assert playlist.sub_genre.key == 'Some sub genre template'
        assert playlist.sub_genre_template == 'Some sub genre template'

    def test_creates_genre_from_template_in_arguments(self):
        playlist = Playlist(
            main_genre_template='Some main genre template',
            sub_genre_template='Some sub genre template'
        )

        assert isinstance(playlist.main_genre, Genre)
        assert playlist.main_genre.playlist == playlist
        assert playlist.main_genre.template_name == 'Some main genre template'
        assert playlist.main_genre_template == 'Some main genre template'

        assert isinstance(playlist.sub_genre, SubGenre)
        assert playlist.sub_genre.main_genre == playlist.main_genre
        assert playlist.sub_genre.key == 'Some sub genre template'
        assert playlist.sub_genre_template == 'Some sub genre template'

    def test_sets_genre_to_given_genre_instance_in_arguments(self):
        genre = Genre(template_name='Some main genre template')
        sub_genre = SubGenre(key='Some sub genre template')
        playlist = Playlist(main_genre=genre, sub_genre=sub_genre)

        assert isinstance(playlist.main_genre, Genre)
        assert playlist.main_genre.playlist == playlist
        assert playlist.main_genre == genre
        assert playlist.main_genre_template == 'Some main genre template'

        assert isinstance(playlist.sub_genre, SubGenre)
        assert playlist.sub_genre.main_genre == playlist.main_genre
        assert playlist.sub_genre == sub_genre
        assert playlist.sub_genre_template == 'Some sub genre template'

    def test_creates_empty_genre_if_not_given(self):
        playlist = Playlist()

        assert isinstance(playlist.main_genre, Genre)
        assert playlist.main_genre.playlist == playlist

        assert isinstance(playlist.sub_genre, SubGenre)
        assert playlist.sub_genre.main_genre == playlist.main_genre
