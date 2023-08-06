from .utilities import Logger
from .helpers import ignored


class Statistics:
    def __init__(self):
        self.requests = 0
        self.cache_hits = 0
        self.unrecognized_hits = 0
        self.rating_added = 0
        self.rating = 0

    @Logger()
    def add_request(self):
        self.requests += 1

    @Logger()
    def add_cache_hit(self):
        self.cache_hits += 1

    @Logger()
    def add_unrecognized_hit(self):
        self.unrecognized_hits += 1

    @Logger('rating')
    def add_rating(self, rating):
        with ignored(ValueError):
            self.rating_added += 1
            self.rating += float(rating)

    def average_movie_rating(self):
        try:
            return self.rating / self.rating_added
        except ZeroDivisionError:
            return 0

    def string_output(self):
        items_processed = self.requests + self.cache_hits
        if items_processed > 0:
            data = ["\nStatistics"]
            data.append("{:>6} items processed".format(items_processed))
            data.append("{:>6} unrecognized items".format(self.unrecognized_hits))
            data.append("{:>6} external requests".format(self.requests))
            data.append("{:>6} hits on the cache".format(self.cache_hits))
            data.append("\nAverage movie-rating: {}".format(round(self.average_movie_rating(), 1)))
            return "\n".join(data)
        else:
            return ""

    def __repr__(self):
        return "Statistics"
