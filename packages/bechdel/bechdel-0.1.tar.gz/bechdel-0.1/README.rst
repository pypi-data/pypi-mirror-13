Bechdel
=======

Introduction
~~~~~~~~~~~~

The ``Bechdel`` package wraps the
`bechdeltest.com <http://bechdeltest.com>`__ API and allows users to
programmatically retrieve the `Bechdel
score <https://enwikipedia.org/wiki/Bechdel_test>`__ for movies.

You can search for movies either by title...

.. code:: python


    import bechdel
    movies = bechdel.getMoviesByTitle('terminator')
    len(movies) # 5
    print movies[0]

    {u'date': u'2015-07-02 06:24:18',
     u'dubious': u'0',
     u'id': u'6340',
     u'imdbid': u'1340138',
     u'rating': u'0',
     u'submitterid': u'12302',
     u'title': u'Terminator Genisys',
     u'visible': u'1',
     u'year': u'2015'}

...or by IMDb id:

.. code:: python


    terminator_genisys = bechdel.getMovieByImdbId('1340138')

Disclaimer
~~~~~~~~~~

This package and its author are unaffiliated with
`bechdeltest.com <http://bechdeltest.com>`__. Please don't abuse the API
with unnecessary requests.

.. |Travis-CI Build Status| image:: https://travis-ci.org/expersso/bechdel.svg?branch=master
   :target: https://travis-ci.org/expersso/bechdel
.. |codecov.io| image:: https://codecov.io/github/expersso/bechdel/coverage.svg?branch=master
   :target: https://codecov.io/github/expersso/bechdel?branch=master
