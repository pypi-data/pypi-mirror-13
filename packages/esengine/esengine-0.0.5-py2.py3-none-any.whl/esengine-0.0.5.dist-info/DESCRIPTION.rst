|PyPI| |versions| |Travis CI| |Coverage Status| |Code Health|

ESEngine - ElasticSearch ODM
============================

.. raw:: html

   <p align="left" style="float:left" >


.. raw:: html

   </p>

What is esengine?
=================

(Object Document Mapper) inspired by MongoEngine
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

ESengine is ODM, you map elasticsearch indices in to Python objects,
those objects are defined using the **Document**, **EmbeddedDocument**
and **< type >Field** classes provided by ESEngine.

modeling
~~~~~~~~

Out of the box ESengine takes care only of the Document Modeling, this
includes Fields and its types and coercion, data mapping and the
generation of the basic CRUD operations (Create, Read, Update, Delete).

Communication
~~~~~~~~~~~~~

ESengine does not communicate direct with ElasticSearch, it only creates
the basic structure, to communicate it relies on an ES client providing
the transport methods (index, delete, update etc).

ES client
~~~~~~~~~

ESengine does not enforce the use of the official ElasticSearch client,
but you are encouraged to use it because it is well maintained and has
the support to **bulk** operations. Bu you are free to use another
client or create your own.

Querying the data
~~~~~~~~~~~~~~~~~

ESengine does not enforce or encourage you to use a DSL language for
queries, out of the box you have to write the elasticsearch **payload**
representation as a raw Python dictionary. However ESEngine comes with a
**utils.payload** helper module to help you building payloads in a less
verbose way.

Why not elasticsearch\_dsl?
~~~~~~~~~~~~~~~~~~~~~~~~~~~

ElasticSearch DSL is an excellent tool, a very nice effort by the
maintainers of the official ES library, it is handy in most of the
cases, but its DSL objects leads to a confuse query building, sometimes
it is better to write raw\_queries or use a simpler payload builder
having more control and visibility of what os being generated. DSL
enforce you to use the official ES client and there are cases when a
different client implementation perform better or you need to run tests
using a Mock. Also, to make things really easy, all the synrax sugar in
DSL can lead in to performance problems.

Project Stage
~~~~~~~~~~~~~

It is in beta-Release, working in production, but missing a lot of
features, you can help using, testing,, discussing or coding!

Getting started
===============

install
-------

ESengine needs a client to communicate with E.S, you can use one of the
following:

-  ElasticSearch-py (official)
-  Py-Elasticsearch (unofficial)
-  Create your own implementing the same api-protocol
-  Use the MockES provided as py.test fixture (only for tests)

Because of bulk operations you are recommendded to use
**elasticsearch-py** (Official E.S Python library) so the instalation
depends on the version of elasticsearch you are using.

Elasticsearch 2.x
~~~~~~~~~~~~~~~~~

.. code:: bash

    pip install esengine[es2]

Elasticsearch 1.x
~~~~~~~~~~~~~~~~~

.. code:: bash

    pip install esengine[es1]

Elasticsearch 0.90.x
~~~~~~~~~~~~~~~~~~~~

.. code:: bash

    pip install esengine[es0]

The above command will install esengine and the elasticsearch library
specific for you ES version.

    Alternatively you can only install elasticsearch library before
    esengine

pip install ``<version-specific-es>``

-  for 2.0 + use "elasticsearch>=2.0.0,<3.0.0"
-  for 1.0 + use "elasticsearch>=1.0.0,<2.0.0"
-  under 1.0 use "elasticsearch<1.0.0"

Then install esengine

.. code:: bash

    pip install esengine

Usage
=====

.. code:: python

    from elasticsearch import ElasticSearch
    from esengine import Document, StringField

    es = ElasticSearch(host='host', port=port)

Defining a document
-------------------

.. code:: python

    class Person(Document):
        _doctype = "person"
        _index = "universe"

        name = StringField()


    If you do not specify an "id" field, ESEngine will automatically add
    "id" as StringField. It is recommended that when specifying you use
    StringField for ids.

Indexing
--------

.. code:: python

    person = Person(id=1234, name="Gonzo")
    person.save(es=es)

Getting by id
-------------

.. code:: python

    Person.get(id=1234, es=es)

filtering by IDS
----------------

.. code:: python

    ids = [1234, 5678, 9101]
    power_trio = Person.filter(ids=ids)

filtering by fields
-------------------

.. code:: python

    Person.filter(name="Gonzo", es=es)

Searching
---------

ESengine does not try to create abstraction for query building, by
default ESengine only implements search transport receiving a raw ES
query in form of a Python dictionary.

.. code:: python

    query = {
        "query": {
            "filtered": {
                "query": {
                    "match_all": {}
                },
                "filter": {
                    "ids": {
                        "values": [1, 2]
                    }
                }
            }
        }
    }
    Person.search(query, size=10, es=es)

Getting all documents
---------------------

.. code:: python

    Person.all(es=es)

    # with more arguments

    Person.all(size=20, es=es)

Counting
--------

.. code:: python

    Person.count(name='Gonzo', es=es)

Using a default connection
--------------------------

By default ES engine does not try to implicit create a connection for
you, so you have to pass in **es=es** argument.

You can easily achieve this overwriting the **get\_es** method and
returning a default connection or using any kind of technique as
RoundRobin or Mocking for tests Also you can set the \*\*\_es\*\*
attribute pointing to a function generating the connection client or the
client instance as the following example:

.. code:: python


    from elasticsearch import ElasticSearch
    from esengine import Document, StringField
    from esengine.utils import validate_client


    class Person(Document):
        _doctype = "person"
        _index = "universe"
        _es = Elasticsearch(host='10.0.0.0')

        name = StringField()


Now you can use the document transport methods ommiting ES instance
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

.. code:: python

    person = Person(id=1234, name="Gonzo")
    person.save()

    Person.get(id=1234)

    Person.filter(name="Gonzo")

Updating
--------

A single document
~~~~~~~~~~~~~~~~~

A single document can be updated simply using the **.save()** method

.. code:: python


    person = Person.get(id=1234)
    person.name = "Another Name"
    person.save()

Updating a Resultset
~~~~~~~~~~~~~~~~~~~~

The Document methods **.get**, **.filter** and **.search** will return
an instance of **ResultSet** object. This object is an Iterator
containing the **hits** reached by the filtering or search process and
exposes some CRUD methods[ **update**, **delete** and **reload** ] to
deal with its results.

.. code:: python

    people = Person.filter(field='value')
    people.update(another_field='another_value')

    When updating documents sometimes you need the changes done in the
    E.S index reflected in the objects of the **ResultSet** iterator, so
    you can use **.reload** method to perform that action.

The use of **reload** method
~~~~~~~~~~~~~~~~~~~~~~~~~~~~

.. code:: python

    people = Person.filter(field='value')
    print people
    ... <Resultset: [{'field': 'value', 'another_field': None}, 
                     {'field': 'value', 'another_field': None}]>

    # Updating another field on both instances
    people.update(another_field='another_value')
    print people
    ... <Resultset: [{'field': 'value', 'another_field': None}, {'field': 'value', 'another_field': None}]>

    # Note that in E.S index the values weres changed but the current ResultSet is not updated by defaul
    # you have to fire an update
    people.reload()

    print people
    ... <Resultset: [{'field': 'value', 'another_field': 'another_value'},
                     {'field': 'value', 'another_field': 'another_value'}]>

Deleting documents
~~~~~~~~~~~~~~~~~~

A ResultSet
^^^^^^^^^^^

.. code:: python

    people = Person.all()
    people.delete()

A single document
^^^^^^^^^^^^^^^^^

.. code:: python

    Person.get(id=123).delete()

Bulk operations
---------------

ESEngine takes advantage of elasticsearch-py helpers for bulk actions,
the **ResultSet** object uses **bulk** melhod to **update** and
**delete** documents.

But you can use it in a explicit way using Document's **update\_all**,
\*\*save\_\_all\*\* and **delete\_all** methods.

Lets create a bunch of document instances
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

.. code:: python

    top_5_racing_bikers = []

    for name in ['Eddy Merckx', 
                 'Bernard Hinault', 
                 'Jacques Anquetil', 
                 'Sean Kelly', 
                 'Lance Armstrong']:
         top_5_racing_bikers.append(Person(name=name))

Save it all
^^^^^^^^^^^

.. code:: python

    Person.save_all(top_5_racing_bikers)

Using the **create** shortcut
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

The above could be achieved using **create** shortcut

A single
''''''''

.. code:: python

    Person.create(name='Eddy Merckx', active=False)

    Create will return the instance of the indexed Document

All using list comprehension
''''''''''''''''''''''''''''

.. code:: python

    top_5_racing_bikers = [
        Person.create(name=name, active=False)
        for name in ['Eddy Merckx', 
                     'Bernard Hinault', 
                     'Jacques Anquetil', 
                     'Sean Kelly', 
                     'Lance Armstrong']
    ]

    NOTE: **.create** method will automatically save the document to the
    index, and will not raise an error if there is a document with the
    same ID (if specified), it will update it acting as upsert.

Updating all
^^^^^^^^^^^^

Turning the field **active** to **True** for all documents

.. code:: python

    Person.update_all(top_5_racing_bikes, active=True)

Deleting all
^^^^^^^^^^^^

.. code:: python

    Person.delete_all(top_5_racing_bikes)

Chunck size
^^^^^^^^^^^

chunk\_size is number of docs in one chunk sent to ES (default: 500) you
can change using **meta** argument.

.. code:: python

    Person.update_all(
        top_5_racing_bikes, # the documents
        active=True,  # values to be changed
        metal={'chunk_size': 200}  # meta data passed to **bulk** operation    
    )

Utilities
^^^^^^^^^

Mapping
^^^^^^^

TODO:

Refreshing
^^^^^^^^^^

Sometimes you need to force indices-shards refresh for testing, you can
use

.. code:: python

    # Will refresh all indices
    Document.refresh()

Payload builder
===============

Sometimes queries turns in to complex and verbose data structures, to
help you (use with moderation) you can use Payload utils to build
queries.

Example using a raw query:
--------------------------

.. code:: python

    query = {
        "query": {
            "filtered": {
                "query": {
                    "match_all": {}
                },
                "filter": {
                    "ids": {
                        "values": [1, 2]
                    }
                }
            }
        }
    }

    Person.search(query=query, size=10)

Same example using payload utils
--------------------------------

.. code:: python

    from esengine.utils.payload import Payload, Query, Filter
    payload = Payload(
        query=Query.filtered(query=Query.match_all(), filter=Filter.ids([1, 2]))
    )
    Person.search(query=payload.dict, size=10)

    Payload utils exposes Payload, Query, Filter, Aggregate, Suggesters

Contribute
==========

ESEngine is OpenSource! join us!

.. |PyPI| image:: https://img.shields.io/pypi/v/esengine.svg
   :target: https://pypi.python.org/pypi/esengine
.. |versions| image:: https://img.shields.io/pypi/pyversions/esengine.svg
   :target: https://pypi.python.org/pypi/esengine
.. |Travis CI| image:: http://img.shields.io/travis/catholabs/esengine.svg
   :target: https://travis-ci.org/catholabs/esengine
.. |Coverage Status| image:: http://img.shields.io/coveralls/catholabs/esengine.svg
   :target: https://coveralls.io/r/catholabs/esengine
.. |Code Health| image:: https://landscape.io/github/catholabs/esengine/master/landscape.svg?style=flat
   :target: https://landscape.io/github/catholabs/esengine/master


