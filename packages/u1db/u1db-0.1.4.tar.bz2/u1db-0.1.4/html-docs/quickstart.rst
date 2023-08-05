.. _quickstart:

Downloads and Quickstart guide
###############################

How to start working with the u1db Python implementation.

Getting u1db
------------

Download
^^^^^^^^

Download the latest release from `the U1DB download page <http://launchpad.net/u1db/+download>`_.

This is the recommended version of u1db to use for your Python application.

Use from source control
^^^^^^^^^^^^^^^^^^^^^^^

u1db is `maintained in bazaar in Launchpad <http://launchpad.net/u1db/>`_. To
fetch the latest version, `bzr branch lp:u1db`.

Starting u1db
-------------

.. testsetup ::

    import os, tempfile
    old_dir = os.path.realpath('.')
    tmp_dir = tempfile.mkdtemp()
    os.chdir(tmp_dir)

.. doctest ::

    >>> import u1db
    >>> db = u1db.open("mydb.u1db", create=True)

    >>> content = {"name": "Alan Hansen"} # create a document
    >>> doc = db.create_doc(content)
    >>> doc.content
    {'name': 'Alan Hansen'}
    >>> doc.content = {"name": "Alan Hansen", "position": "defence"} # update the document's content
    >>> rev = db.put_doc(doc)

    >>> content = {"name": "John Barnes", "position": "defence"} # create more documents
    >>> doc2 = db.create_doc(content)

    >>> doc2.content["position"] = "forward"
    >>> db.put_doc(doc2) #doctest:+ELLIPSIS
    '...'

    >>> content = {"name": "Ian Rush", "position": "forward"}
    >>> doc3 = db.create_doc(content)

    >>> db.create_index("by-position", "position") # create an index by passing a field name

    >>> results = db.get_from_index("by-position", "forward") # query that index by passing a value
    >>> len(results)
    2
    >>> data = [result.content for result in results]
    >>> names = [item["name"] for item in data]
    >>> sorted(names)
    [u'Ian Rush', u'John Barnes']

.. testcleanup ::

    os.chdir(old_dir)
    os.remove(os.path.join(tmp_dir, "mydb.u1db"))
    os.rmdir(tmp_dir)

Running a server
----------------

The reference implementation comes with a command-line client and a server. The
command-line client covers the basic operations on a database.

.. code-block:: bash

    ~/u1db/trunk$ ./u1db-client init-db example.u1db
    ~/u1db/trunk$ echo '{"key": "value"}' | ./u1db-client create example.u1db # add a document to our database
    id: D-cf8a96bea58b4b5ab2ce1ab9c1bfa053
    rev: f6657904254d474d9a333585928726df:1
    ~/u1db/trunk$ ./u1db-client get example.u1db D-cf8a96bea58b4b5ab2ce1ab9c1bfa053 # fetch it
    {"key": "value"}
    rev: f6657904254d474d9a333585928726df:1
    ~/u1db/trunk$ ./u1db-client delete example.u1db D-cf8a96bea58b4b5ab2ce1ab9c1bfa053 f6657904254d474d9a333585928726df:1 # and delete it
    rev: f6657904254d474d9a333585928726df:2

    ~/u1db/trunk$ ./u1db-serve --verbose # run the server, and you can now use http://127.0.0.1:43632/example.u1db as a sync URL
    listening on: 127.0.0.1:43632

Synchronising to other databases
--------------------------------

.. code-block:: python

    >>> import u1db
    >>> db = u1db.open("mydb", create=True)
    >>> generation = db.sync("http://127.0.0.1:43632/example.u1db")

or from the command line

.. code-block:: bash

    ~/u1db/trunk$ ./u1db-client init-db someother.u1db
    ~/u1db/trunk$ ./u1db-client sync someother.u1db http://127.0.0.1:43632/example.u1db


