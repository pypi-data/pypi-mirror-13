from .utilities import Result, ensure_exists, Logger, format_filename
from .helpers import ignored

import os
import re
import json
from http.client import HTTPConnection
from urllib.parse import urlencode
from urllib.request import urlretrieve
from collections import namedtuple

R_result = namedtuple('r3', 'title year filename')


class MovieQuery:
    def __init__(self, result_tuple):
        self.title, self.year, self.original_file = result_tuple.title, result_tuple.year, result_tuple.filename
        _, self.ext = os.path.splitext(self.original_file)

    def formatted_filename(self):
        return format_filename(self.title, self.year, self.ext)

    def __str__(self):
        return "{}\n\t{}\n\t{}".format(self.title, self.year, self.original_file)

    def __repr__(self):
        return "MovieQuery<{}>".format(self.title)


class MovieResult(MovieQuery):
    def __init__(self, r, original_filename):
        super().__init__(R_result(title=r["Title"], year=r["Year"], filename=original_filename))
        self.genre = r["Genre"].split(",")
        self.director = r["Director"]
        self.dict = r

    def __str__(self):
        return "{}\n{}\n".format(super().__str__(), self.genre)

    @Logger()
    def save_link(self, path) -> Result:
        name = format_filename(self.title, self.year, self.ext)

        filename = os.path.join(path, name)
        with ignored(FileExistsError):
            os.link(self.original_file, filename)

        return Result.success(filename)

    @Logger()
    def save_poster(self, path) -> Result:
        try:
            poster_url = self.dict["Poster"]
            _, ext = os.path.splitext(poster_url)

            destination_filename = format_filename(self.title, self.year, ext)
            poster_filename = os.path.join(path, destination_filename)
            urlretrieve(poster_url, poster_filename)

            return Result.success(poster_filename)
        except ValueError:
            return Result.failure("Error saving poster")

    @Logger()
    def prepare_data_cache(self, output_folder, posters_folder):
        def map1(fn, path):
            return fn(ensure_exists(path)).value

        data_to_cache = {'link': map1(self.save_link, output_folder),
                         'poster': map1(self.save_poster, posters_folder),
                         'data': self.dict}

        return data_to_cache

    @property
    def rating(self):
        return self.dict["imdbRating"]

    def __repr__(self):
        return "MovieResult"


@Logger()
def perform_web_request(movie_query):
    conn = HTTPConnection("www.omdbapi.com")
    fields = {"t": movie_query.title, "y": movie_query.year, "plot": "short", "r": "json"}
    encoded_fields = urlencode(fields, encoding="utf-8")
    conn.request("GET", "/?" + encoded_fields)
    server_response = conn.getresponse()
    if server_response.status == 200:
        data = server_response.read()
        result_json = json.loads(data.decode("utf-8"))

        if "Error" in result_json:
            return None
        return result_json
    else:
        return None  # {'status': server_response.status, 'reason': server_response.reason}


@Logger()
def process_file(filename_with_path) -> R_result:
    def clean_filename(name):
        return ' '.join(name.strip(" -.").split(' .-')).replace('.', ' ')

    filename = os.path.basename(filename_with_path)

    title_pattern = r'(.*)(?:.)'
    year_pattern = r'((?:[\(\[])*(?:19|20)(?:\d{2})(?:[\)\]])*?)'
    extension_pattern = '(.+)?\.(mkv|mov|avi|mp4|m4v){1}'
    pattern = re.compile(title_pattern + year_pattern + extension_pattern)
    r = re.findall(pattern, filename)

    if len(r) > 0:
        result = r[0]
        if len(result) == 4:
            return R_result(title=clean_filename(result[0]), year=result[1], filename=filename)
    else:
        return None


@Logger('destination_path, source_filename')
def link_file_into_unrecognized_folder(destination_path, source_filename):
    with ignored(FileExistsError):
        destination = os.path.join(ensure_exists(destination_path), os.path.basename(source_filename))
        os.link(source_filename, destination)


@Logger('filename')
def main_process(cfg, root, filename, cache, stats):
    @Logger('filename')
    def unrecognized_hit(unknown_folder, filename):
        stats.add_unrecognized_hit()
        link_file_into_unrecognized_folder(destination_path=unknown_folder, source_filename=filename)

    cache_lookup_result = cache.lookup_in_cache(key=filename)
    if cache_lookup_result:
        stats.add_cache_hit()
        stats.add_rating(rating=cache_lookup_result["data"]["imdbRating"])

    else:
        result_tuple = process_file(os.path.join(root, filename))
        if result_tuple:
            query = MovieQuery(result_tuple)

            stats.add_request()
            result_json = perform_web_request(query)

            if result_json:
                movie = MovieResult(result_json, original_filename=os.path.join(root, filename))
                stats.add_rating(rating=movie.rating)
                cache.add(key=filename, data=movie.prepare_data_cache(cfg.output_folder, cfg.posters_folder))

            else:
                # todo: movie not found / request denied
                unrecognized_hit(cfg.unknown_folder, filename=os.path.join(root, filename))

        else:
            # probable cause: unrecognized format of filename
            unrecognized_hit(cfg.unknown_folder, filename=os.path.join(root, filename))


@Logger('root')
def process_folder(cfg, root, cache, stats):
    for root, dirs, files in os.walk(root):
        for filename in files:
            _, ext = os.path.splitext(filename)
            if ext in cfg.movie_extensions:
                main_process(cfg=cfg, root=root, filename=filename, cache=cache, stats=stats)

# def rating(args):
#     cache = Cache(application_name, "movie-cache.json")
#     genres = defaultdict(int)
#     max_genres = 0
#     genre_max_length = 0
#
#     # Find how many genres per movie exists...
#     for each in cache.data.keys():
#         genre_list = cache.data[each]["data"]["Genre"].split(", ")
#         max_genres = max(len(genre_list), max_genres)
#
#         for each in genre_list:
#             genres[each] += 1
#             genre_max_length = max(len(each), genre_max_length)
#
#     cols = "{:<" + str(genre_max_length + 2) + "}"
#
#     # ...in order to know how many columns to build
#     for each in cache.data.keys():
#         s = "{p[imdbRating]} {p[Title]}"
#
#         g = cache.data[each]["data"]["Genre"].split(", ")
#         r_col = ""
#         for i in g:
#             r_col += cols.format(i)
#         s1 = "{p[Runtime]:>7}   {p[imdbRating]}   {p[Title]}".format(p=cache.data[each]["data"])
#
#         s2 = ("{:<" + str((genre_max_length + 2) * 3) + "}{}").format(r_col, s1)
#         print(s2)
#
#     # sorted_x = sorted(genres.items(), key=operator.itemgetter(1))
#     # print(sorted_x)
#     # print(max_genres)
#     sys.exit()
