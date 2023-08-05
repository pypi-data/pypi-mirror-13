class MovieNotFound(Exception):
    def __init__(self, release_name, message=None, *args, **kwargs):
        super(MovieNotFound, self).__init__(*args, **kwargs)
        self.message = message
        self.release_name = release_name


class SubtitleNotFound(Exception):
    def __init__(self, movie, params, detail=None, *args, **kwargs):
        super(SubtitleNotFound, self).__init__(*args, **kwargs)
        self.movie = movie
        self.params = params
        self.detail = detail


class SubtitleFileBroken(Exception):
    def __init__(self, url, message=None, *args, **kwargs):
        super(SubtitleFileBroken, self).__init__(*args, **kwargs)
        self.message = message
        self.url = url


class HTTPConnectionError(Exception):
    def __repr__(self, url, return_code, body, *args, **kwargs):
        self.url = url
        self.return_code = return_code
        self.body = body
        return super(HTTPConnectionError, self).__repr__(*args, **kwargs)
