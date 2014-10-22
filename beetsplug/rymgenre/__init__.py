import logging
import os
import requests
import yaml

from beets.plugins import BeetsPlugin
from beets import ui
from lxml import html

log = logging.getLogger('beets')

GENRES_TREE = os.path.join(os.path.dirname(__file__), 'genres-tree.yaml')

class RymGenrePlugin(BeetsPlugin):
    headers = {
         'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
         'Accept-Charset': 'ISO-8859-1,utf-8;q=0.7,*;q=0.3',
         'Accept-Language': 'en-US,en;q=0.8',
         'Cache-Control': 'max-age=0',
         'Connection': 'keep-alive',
         'Pragma': 'no-cache',
         'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_8_3) AppleWebKit/537.31 (KHTML, like Gecko) Chrome/26.0.1410.65 Safari/537.31'
    }

    def __init__(self):
        super(RymGenrePlugin, self).__init__()

        self.config.add({
            'separator': u', ',
            'level': 'parent'
        })

        self.setup()

    def setup(self):
        def build_parents(elem, path, parents):
            if not path:
                path = []

            if isinstance(elem, dict):
                for (k, v) in elem.items():
                    parents[k] = parents.get(k, set([])) | set(path)
                    build_parents(v, [k] + path, parents)
            elif isinstance(elem, list):
                for sub in elem:
                    build_parents(sub, path, parents)
            else:
                parents[elem] = parents.get(elem, set([])) | set(path)

        self.parent_genres = {}
        build_parents(yaml.load(open(GENRES_TREE, 'r')), [], self.parent_genres)

    def _get_albums(self, album):
        search_results = requests.post(
            'http://rateyourmusic.com/httprequest',
            data = {
                'searchterm': album['albumartist'] + " " + album['album'],
                'type': 'l',
                'page': 1,
                'action': 'Search',
                'rym_ajax_req': 1
            },
            headers = self.headers)

        def build_release(release_element):
            release_information = { 'artist': None, 'album': None, 'href': None }

            artist = release_element.xpath('.//a[@class="artist"]/text()')
            if artist:
                release_information['artist'] = artist[0]

            album = release_element.xpath('.//a[@class="searchpage"]/text()')
            if album:
                release_information['album'] = album[0]

            href = release_element.xpath('.//a[@class="searchpage"]/@href')
            if href:
                release_information['href'] = href[0]

            return release_information

        return [build_release(release_element) for release_element in
                html.fromstring(search_results.text).xpath('//tr[@class="infobox"]')]

    def _get_genres(self, release_url):
        release_page = html.fromstring(requests.get(release_url, headers = self.headers).text)
        primary_genres = release_page.xpath('//span[@class="release_pri_genres"]//a[@class="genre"]/text()')
        secondary_genres = release_page.xpath('//span[@class="release_sec_genres"]//a[@class="genre"]/text()')

        level = self.config['level'].as_choice(('primary', 'secondary', 'parent'))
        genres = set([])
        if level == 'primary':
            genres = set(primary_genres)
        elif level == 'secondary':
            genres = set(primary_genres + secondary_genres)
        elif level == 'parent':
            for genre in primary_genres + secondary_genres:
                genres.add(genre)
                if genre in self.parent_genres:
                    genres |= set(self.parent_genres[genre])

        return genres

    def _get_best_release(self, albums):
        return albums[0]

    def _get_genre(self, album):
        release = self._get_best_release(self._get_albums(album))
        genres = self._get_genres('http://rateyourmusic.com/' + release['href'])

        log.info(u'genres for album {0} - {1}: {2}'.format(
            album.albumartist,
            album.album,
            self.config['separator'].get(unicode).join(genres)))

        return self.config['separator'].get(unicode).join(genres)

    def commands(self):
        rymgenre_cmd = ui.Subcommand('rymgenre', help='fetch genres from rateyourmusic.com')
        def rymgenre_func(lib, opts, args):
            for album in lib.albums(ui.decargs(args)):
                album.genre = self._get_genre(album)
                album.store()

        rymgenre_cmd.func = rymgenre_func
        return [rymgenre_cmd]
