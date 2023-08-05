==============================================================================
collective.querynextprev
==============================================================================

.. image:: https://secure.travis-ci.org/collective/collective.querynextprev.png
    :target: http://travis-ci.org/collective/collective.querynextprev

.. image:: https://coveralls.io/repos/collective/collective.querynextprev/badge.png?branch=master
    :alt: Coveralls badge
    :target: https://coveralls.io/r/collective/collective.querynextprev


This package adds next/previous buttons that allow you to navigate through your query results.

Out of the box, it works with `eea.facetednavigation <https://github.com/collective/eea.facetednavigation>`__ queries (requires ``eea.facetednavigation`` > 8.2).


To add support for more queries, you have to record the query in the request session and optionnaly a search url (see ``record_query_in_session`` subscriber).
The `search url` is the url that will be used by the next/previous links when there is no more result. If no search url is provided, it redirects to the portal url.


Translations
------------

This product has been translated into

- French


Installation
------------

Install collective.querynextprev by adding it to your buildout::

   [buildout]

    ...

    eggs =
        collective.querynextprev


and then running "bin/buildout"


Contribute
----------

- Issue Tracker: https://github.com/collective/collective.querynextprev/issues
- Source Code: https://github.com/collective/collective.querynextprev
- Documentation: https://docs.plone.org/foo/bar


Support
-------

If you are having issues, please let us know.


License
-------

The project is licensed under the GPLv2.
