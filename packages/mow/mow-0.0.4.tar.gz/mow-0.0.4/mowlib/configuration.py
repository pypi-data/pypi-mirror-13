import os
import mowlib as mlb

trace = 0
verbose = 2
application_name = "mow"
movie_cache_filename = "mow-cache.json"


class Config(object):
    def __init__(self):
        self.verbose = False
        self.input_folder = "."
        self.output_folder = "."
        self.unknown_folder = "."
        self.posters_folder = os.path.join(mlb.cache_dir(mlb.application_name), "posters")
        self.preview = False
        self.movie_extensions = ['.mkv', '.mov', '.m4v', '.mp4', 'avi']

    def __repr__(self):
        return "{},{}".format(self.verbose and 'on' or 'off', self.input_folder)

    def list(self):
        data = {"Verbose": self.verbose, "Input_folder": self.input_folder}
        return mlb.m_format(data.items())
