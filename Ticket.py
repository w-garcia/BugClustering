class Ticket:
    def __init__(self, id, description, classes, system, vector=None, kw=None):
        self._id = id
        self._description = description
        self._classes = classes
        self._system = system
        self._vector = vector
        self._keywords = kw
        if vector is not None:
            self._nonzero_vector = [x for x in vector if x > 0]
        else:
            self._nonzero_vector = None

    @property
    def description(self):
        return self._description

    @property
    def classes(self):
        return self._classes

    @property
    def system(self):
        return self._system

    @property
    def id(self):
        return self._id

    @property
    def vector(self):
        return self._vector

    @property
    def nonzero_vector(self):
        return self._nonzero_vector

    @property
    def keywords(self):
        return self._keywords
