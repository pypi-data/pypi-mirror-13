class _Items():
    def __init__(self, iterable, length=None):
        self.ilist = []
        self.iterable = iterable
        self.length = length

    def __getitem__(self, sliced):
        if isinstance(sliced, slice):
            stop = sliced.stop
        else:
            stop = sliced
        # To get the last item in an iterable, must iterate over all items
        if stop < 0:
            stop = None
        while True if (stop is None) else (stop > len(self.ilist) - 1):
            try:
                self.ilist.append(next(self.iterable))
            except StopIteration:
                break

        return self.ilist[sliced]


class Content:
    def __init__(self):
        self.items = _Items(self.get_content(), self.get_length())

    def get_content(self):
        """Must be overridden by child class.
        Should return an iterator of the items to display on the screen."""
        raise NotImplementedError

    def format_item(self, item, width):
        raise NotImplementedError

    def get_length(self):
        """Should return the number of items, or None if that is unavailable.
        The default implementation returns None."""
        return None

    def get_message(self):
        """Should return the message to display, or None for no message.
        The default implementation returns None."""
        return None


def TabularContent(Content):
    def __init__(self, headers, tableiter):
        self.headers = headers
        self.tableiter = tableiter
        super().__init__()

    def get_content(self):
        for i in self.tableiter:
            yield i

    def format_item(self, item, width):
         
