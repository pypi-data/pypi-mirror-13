from paginatify import Pagination as _Pagination


class QueryWrapper(object):
    def __init__(self, query):
        self.query = query

    def __len__(self):
        return self.query.count()

    def __getitem__(self, item):
        return self.query.__getitem__(item)


class Pagination(_Pagination):
    def __init__(self, query, **kwargs):
        super(Pagination, self).__init__(QueryWrapper(query), **kwargs)


# to prevent naming convention
SQLPagination = Pagination
