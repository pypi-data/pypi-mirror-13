from pprint import pformat
from django.conf import settings
from pyelasticsearch import ElasticSearch

from ievv_opensource.utils.singleton import Singleton


class Connection(Singleton):
    """
    Singleton wrapper around :class:`pyelasticsearch.ElasticSearch`.

    We do not try to wrap everything, instead we use the pyelasticsearch
    API as it is, and add extra features that makes it easier to use
    with IEVV and Django. We provide shortcuts for the most commonly
    used methods of :class:`pyelasticsearch.ElasticSearch`, some custom
    methods and we add some code to make unit testing easier.

    Usage::

        from ievv_opensource.ievv_elasticsearch import search

        searchapi = search.Connection.get_instance()
        searchapi.bulk_index(
            index='contacts',
            doc_type='person',
            docs=[{'name': 'Joe Tester'},
                  {'name': 'Peter The Super Tester'}])
        searchresult1 = searchapi.wrapped_search('name:joe OR name:freddy', index='contacts')
        searchresult2 = searchapi.wrapped_search({
            'query': {
                'match': {
                    'name': {
                        'query': 'Joe'
                    }
                }
            }
        })
        print(searchresult1.total)
        for item in searchresult1:
            print(item.doc['name'])

    .. attribute:: elasticsearch

        The :class:`pyelasticsearch.ElasticSearch` object.
    """
    def __init__(self):
        super().__init__()
        self._testmode = getattr(settings, 'IEVV_ELASTICSEARCH_TESTMODE', False)
        self._autorefresh_after_index_changes = self._testmode
        if self._testmode:
            self._connectionurl = settings.IEVV_ELASTICSEARCH_TESTURL
        else:
            if getattr(settings, 'IEVV_ELASTICSEARCH_URL', None):
                self._connectionurl = settings.IEVV_ELASTICSEARCH_URL
            else:
                raise ValueError('ievv_opensource.ievv_elasticsearch.search.Connection '
                                 'requires the IEVV_ELASTICSEARCH_URL setting')
        self.elasticsearch = ElasticSearch(self._connectionurl)

    def clear_all_data(self):
        """
        Clear all data from ElasticSearch. Perfect for
        unit tests.

        Only allowed when the ``IEVV_ELASTICSEARCH_TESTMODE``-setting is ``True``.

        Usage::

            class MyTest(TestCase):
                def setUp(self):
                    self.searchapi = search.Connection.get_instance()
                    self.searchapi.clear_all_data()
        """
        if not self._testmode:
            raise Exception('clear_all_data() is only allowed when settings.IEVV_ELASTICSEARCH_TESTMODE=True.')
        self.elasticsearch.delete_all_indexes()
        self.elasticsearch.refresh()

    def index(self, *args, **kwargs):
        """
        Wrapper around :meth:`pyelasticsearch.ElasticSearch.index`.

        Works exactly like the wrapped function, except that we provide some
        extra features that makes testing easier. When the
        ``IEVV_ELASTICSEARCH_TESTMODE``-setting is ``True``, we automatically
        run :meth:`pyelasticsearch.ElasticSearch.refresh` before returning.
        """
        result = self.elasticsearch.index(*args, **kwargs)
        if self._autorefresh_after_index_changes:
            self.refresh()
        return result

    def bulk_index(self, *args, **kwargs):
        """
        Wrapper around :meth:`pyelasticsearch.ElasticSearch.bulk_index`.

        Works exactly like the wrapped function, except that we provide some
        extra features that makes testing easier. When the
        ``IEVV_ELASTICSEARCH_TESTMODE``-setting is ``True``, we automatically
        run :meth:`pyelasticsearch.ElasticSearch.refresh` before returning.
        """
        result = self.elasticsearch.bulk_index(*args, **kwargs)
        if self._autorefresh_after_index_changes:
            self.refresh()
        return result

    def bulk(self, *args, **kwargs):
        """
        Wrapper around :meth:`pyelasticsearch.ElasticSearch.bulk`.

        Works exactly like the wrapped function, except that we provide some
        extra features that makes testing easier. When the
        ``IEVV_ELASTICSEARCH_TESTMODE``-setting is ``True``, we automatically
        run :meth:`pyelasticsearch.ElasticSearch.refresh` before returning.
        """
        result = self.elasticsearch.bulk(*args, **kwargs)
        if self._autorefresh_after_index_changes:
            self.refresh()
        return result

    def search(self, *args, **kwargs):
        """
        Wrapper around :meth:`pyelasticsearch.ElasticSearch.search`.

        Works exactly like the wrapped function.
        """
        return self.elasticsearch.search(*args, **kwargs)

    def refresh(self, *args, **kwargs):
        """
        Wrapper around :meth:`pyelasticsearch.ElasticSearch.refresh`.

        Works exactly like the wrapped function.
        """
        return self.elasticsearch.refresh(*args, **kwargs)

    def delete_index(self, *args, **kwargs):
        """
        Wrapper around :meth:`pyelasticsearch.ElasticSearch.delete_index`.

        Works exactly like the wrapped function.
        """
        return self.elasticsearch.delete_index(*args, **kwargs)

    def delete(self, *args, **kwargs):
        """
        Wrapper around :meth:`pyelasticsearch.ElasticSearch.delete`.

        Works exactly like the wrapped function.
        """
        return self.elasticsearch.delete(*args, **kwargs)

    def get(self, *args, **kwargs):
        """
        Wrapper around :meth:`pyelasticsearch.ElasticSearch.get`.

        Works exactly like the wrapped function.
        """
        return self.elasticsearch.get(*args, **kwargs)

    def wrapped_get(self, *args, **kwargs):
        """
        Just like :meth:`.get`, but we return a :class:`.SearchResultItem`
        instead of the raw search response.
        """
        return SearchResultItem(self.get(*args, **kwargs))

    def wrapped_search(self, *args, **kwargs):
        """
        Just like :meth:`.search`, but we return a :class:`.SearchResultWrapper`
        instead of the raw search response.
        """
        return SearchResultWrapper(self.search(*args, **kwargs))

    def paginated_search(self, query, page_number=0, page_size=100, resultitemwrapper=None, **kwargs):
        """
        Performs a search much like :meth:`.wrapped_search`, but
        limit the size of the result to ``page_size``, and start
        the results at ``page_number * page_size``.

        Parameters:
            page_number: The page number to retrieve.
            page_size: The size of each page.
            query: A query dict for :meth:`pyelasticsearch.ElasticSearch.search`.
               We add the ``size`` and ``from`` keys to this dict (calculated
               from ``page_number`` and ``page_size``.
            resultitemwrapper: Forwarded to :class:`.Paginator`.
            kwargs: Forwarded to :meth:`.wrapped_search` alon with ``query``.

        Return:
            Paginator: The search results wrapped in a :class:`.Paginator`.
        """
        query['size'] = page_size
        query['from'] = page_number * page_size
        searchresultwrapper = self.wrapped_search(query, **kwargs)
        return Paginator(searchresultwrapper=searchresultwrapper,
                         page_number=page_number,
                         page_size=page_size,
                         resultitemwrapper=resultitemwrapper)

    def search_all(self):
        """
        Get all documents in the index. Nice for testing
        and debugging of small datasets. Useless in production.
        """
        return self.search({
            'query': {
                'match_all': {}
            }
        })

    def wrapped_search_all(self):
        """
        Just like :meth:`.search_all`, but wraps the results in
        a :class:`.SearchResultWrapper`.
        """
        return SearchResultWrapper(self.search_all())


class SearchResultItem(object):
    """
    Wrapper around a single dictionary in the ``hits.hits`` list of
    the result returned by :meth:`pyelasticsearch.ElasticSearch.search`.
    """
    def __init__(self, search_hit):
        self.search_hit = search_hit

    @property
    def id(self):
        """
        Returns the value of the ``_id`` key of the search hit.
        """
        return self.search_hit['_id']

    @property
    def index(self):
        """
        Returns the value of the ``_index`` key of the search hit.
        """
        return self.search_hit['_index']

    @property
    def score(self):
        """
        Returns the value of the ``_score`` key of the search hit.
        """
        return self.search_hit['_score']

    @property
    def source(self):
        """
        Returns the value of the ``_source`` key of the search hit.
        """
        return self.search_hit['_source']

    @property
    def doc_type(self):
        """
        Returns the value of the ``_type`` key of the search hit.
        """
        return self.search_hit['_type']

    def __str__(self):
        return pformat(self.search_hit)

    def __repr__(self):
        return 'SearchResultItem({!r})'.format(self.search_hit)


class SearchResultWrapper(object):
    """
    An efficient wrapper around the data returned by :meth:`pyelasticsearch.ElasticSearch.search`.
    """
    def __init__(self, searchresult):
        """
        :param searchresult: Data returned by :meth:`pyelasticsearch.ElasticSearch.search`.
        """
        self.searchresult = searchresult

    @property
    def total(self):
        """
        Returns the total number of hits.
        """
        return self.searchresult['hits']['total']

    @property
    def retrieved_hits_count(self):
        """
        Returns the number of retrieved hits.
        """
        return len(self.searchresult['hits']['hits'])

    def __iter__(self):
        """
        Iterate over the search result hits, and yield :class:`.SearchResultItem` objects.
        """
        for search_hit in self.searchresult['hits']['hits']:
            yield SearchResultItem(search_hit)

    def __getitem__(self, index):
        """
        Get the search result at the given index as
        a :class:`.SearchResultItem`
        """
        return SearchResultItem(self.searchresult['hits']['hits'][index])

    def first(self):
        """
        Shortcut for getting the first search result as
        a :class:`.SearchResultItem`.
        """
        return self[0]

    def __str__(self):
        return pformat(self.searchresult)

    def __repr__(self):
        return repr(self.searchresult)


class Paginator:
    """
    Paginator for :class:`ievv_opensource.ievv_elasticsearch.search.SearchResultWrapper`.

    The paginator counts the first page as 0, the second as 1, and so on.
    """
    def __init__(self, searchresultwrapper, page_number,
                 page_size=100,
                 resultitemwrapper=None):
        """
        Parameters:
            searchresultwrapper: A :class:`ievv_opensource.ievv_elasticsearch.search.SearchResultWrapper`.
            page_number: The current page number.
            page_size: Number of items per page.
            resultitemwrapper: A class/callable that takes a single item in
               the ``searchresultwrapper`` and does something with it before
               returning it when iterating the search result.
               Defaults to just returning the item as returned from
               ``searchresultwrapper.__iter__``.
        """
        self.searchresultwrapper = searchresultwrapper
        self.page_number = page_number
        self.page_size = page_size
        if resultitemwrapper:
            self.resultitemwrapper = resultitemwrapper
        else:
            self.resultitemwrapper = lambda item: item

    @property
    def total_items(self):
        """
        Returns the number of items in total in all pages.
        """
        return self.searchresultwrapper.total

    @property
    def number_of_items_in_current_page(self):
        """
        Returns the number of items in the current page.
        """
        return self.searchresultwrapper.retrieved_hits_count

    @property
    def previous_page_number(self):
        return self.page_number - 1

    @property
    def next_page_number(self):
        return self.page_number + 1

    def get_page_startindex(self, pagenumber):
        """
        Get the start index of the given ``pagenumber``.
        """
        return self.page_size * pagenumber

    def get_current_page_startindex(self):
        """
        Get the start index of the current page.
        """
        return self.get_page_startindex(self.page_number)

    def page_has_content(self, pagenumber):
        """
        Check if the given ``pagenumber`` is within the total number of items
        in the given ``searchresultwrapper``.

        Returns:
            A boolean.
        """
        if pagenumber < 0:
            return False
        else:
            return self.get_page_startindex(pagenumber) < self.searchresultwrapper.total

    def current_page_has_content(self):
        """
        Check if current page is within the total number of items
        in the given ``searchresultwrapper``.

        Returns:
            A boolean.
        """
        return self.page_has_content(self.get_current_page_startindex())

    def has_next(self):
        """
        Check if we have a next page. Checks if the start index of the next
        page is lower than ``searchresultwrapper.total``.

        Returns:
            A boolean.
        """
        return self.page_has_content(self.page_number + 1)

    def has_previous(self):
        """
        Check if we have a previous page. Checks if the start index of the previous
        page is larger than 0.

        Returns:
            A boolean.
        """
        return self.page_has_content(self.page_number - 1)

    def __iter__(self):
        """
        Iterate the search results, yielding objects wrapped by
        the ``resultitemwrapper`` given to the constructor (or
        the raw search result items if no ``resultitemwrapper``
        was provided).
        """
        for item in self.searchresultwrapper:
            yield self.resultitemwrapper(item)
