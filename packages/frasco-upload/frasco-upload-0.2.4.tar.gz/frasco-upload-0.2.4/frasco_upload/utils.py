import mimetypes
from werkzeug import FileStorage
from StringIO import StringIO


__all__ = ('StringFileStorage',)


mimetypes.init()


class StringFileStorage(FileStorage):
    def __init__(self, data, filename, mimetype=None, **kwargs):
        super(StringFileStorage, self).__init__(StringIO(data), filename, **kwargs)
        if mimetype is None:
            mimetype = mimetypes.guess_type(filename)[0]
        self._mimetype = mimetype

    @property
    def mimetype(self):
        return self._mimetype