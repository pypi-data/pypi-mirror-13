=============================
 metapensiero.sphinx.patchdb
=============================

Collects and applies scripts embedded in a reST document
========================================================

:version: 1.1.0
:author: Lele Gaifax <lele@metapensiero.it>
:license: GPLv3

Building and maintaining the schema of a database is always a challenge. It may quickly become
a nightmare when dealing with even moderately complex databases, in a distribuited development
environment. You have new features going in, and fixes here and there, that keeps accumulating
in the development `branch`. You also have several already deployed instances of the database
you wanna upgrade now and then.

In my experience, it's very difficult to impossible to come up with a completely automated
solution, for several reasons:

* comparison between different releases of a database schema is tricky

* actual contents of the database must be preserved

* some changes require specific recipes to upgrade the data

* any automated solution hide some detail, by definition: I need complete control, to be able
  to create temporary tables and/or procedures for example

I tried, and wrote myself, several different approaches to the problem, and this package is my
latest and most satisfying effort: it builds on top of `docutils`_ and `Sphinx`_, with the side
advantage that you get a quite nice and good documentation of the whole architecture: `literate
database scheming`!

.. _docutils: http://docutils.sourceforge.net/
.. _sphinx: http://sphinx.pocoo.org/intro.html

How it works
------------

The package contains two distinct pieces: a `Sphinx`_ extension and the ``patchdb`` command
line tool.

The extension implements a new `ReST` directive able to embed a `script` in the document: when
processed by the ``sphinx-build`` tool, all the scripts will be collected in an external file,
configurable.

The ``patchdb`` tool takes that script collection and determines which scripts need to be
applied to some database, and the right order.

It keeps and maintains a single very simple table within the database, where it records the
last version of each script it successfully execute, so that it won't reexecute the same script
(actually, a particular `revision` of it) twice.

So, on the development side you simply write (and document!) each piece, and when it comes the
time of deploying current state you distribute just the script collection (a single file,
usually in `AXON`_, `JSON`_ or `YAML`_ format, or a ``pickle`` archive) to the end points where
the database instances live, and execute ``patchdb`` against each one.

.. _yaml: http://yaml.org/
.. _json: http://json.org/
.. _axon: http://intellimath.bitbucket.org/axon/

Scripts
~~~~~~~

The basic building block is a `script`, an arbitrary sequence of statements written in some
language (currently, either ``Python``, ``SQL`` or ``Shell``), augmented with some metadata
such as the `scriptid`, possibly a longer `description`, its `revision` and so on.

As a complete example of the syntax, consider the following::

  .. patchdb:script:: My first script
     :description: Full example of a script
     :revision: 2
     :depends: Other script@4
     :preceeds: Yet another
     :language: python
     :conditions: python_2_x

     print "Yeah!"

This will introduce a script globally identified by `My first script`, written in ``Python``:
this is its second release, and its execution must be constrained such that it happens
**after** the execution of the fourth revision of `Other script` and **before** `Yet another`.

The example shows also an usage of the conditions, allowing more than one variant of a script
like::

  .. patchdb:script:: My first script (py3)
     :description: Full example of a script
     :revision: 2
     :depends: Other script@4
     :preceeds: Yet another
     :language: python
     :conditions: python_3_x

     print("Yeah!")

The dependencies may be a comma separated list of script ids, such as::

  .. patchdb:script:: Create master table

     CREATE TABLE some_table (id INTEGER PRIMARY KEY, tt_id INTEGER)

  .. patchdb:script:: Create target table

     CREATE TABLE target_table (id INTEGER PRIMARY KEY)

  .. patchdb:script:: Add foreign key to some_table
     :depends: Create master table, Create target table

     ALTER TABLE some_table
           ADD CONSTRAINT fk_master_target
               FOREIGN KEY (tt_id) REFERENCES target_table (id)

Independently from the order these scripts appear in the documentation, the third script will
execute only after the first two get successfully applied to the database. As you can notice,
most of the options are optional: by default, ``:language:`` is ``sql``, ``:revision:`` is
``1``, the ``:description:`` is taken from the title (that is, the script ID), while
``:depends:`` and ``:preceeds:`` are empty.

Just for illustration purposes, the same effect could be achieved with::

  .. patchdb:script:: Create master table
     :preceeds: Add foreign key to some_table

     CREATE TABLE some_table (id INTEGER PRIMARY KEY, tt_id INTEGER)

  .. patchdb:script:: Create target table

     CREATE TABLE target_table (id INTEGER PRIMARY KEY)

  .. patchdb:script:: Add foreign key to some_table
     :depends: Create target table

     ALTER TABLE some_table
           ADD CONSTRAINT fk_master_target
               FOREIGN KEY (tt_id) REFERENCES target_table (id)

Patches
~~~~~~~

A `patch` is a particular flavour of script, one that specify a `brings` dependency
list. Imagine that the example above was the first version of the database, and that the
current version looks like the following::

  .. patchdb:script:: Create master table
     :revision: 2

     CREATE TABLE some_table (
       id INTEGER PRIMARY KEY,
       description VARCHAR(80),
       tt_id INTEGER
     )

that is, ``some_table`` now contains one more field, ``description``.

We need an upgrade path from the first revision of the table to the second::

  .. patchdb:script:: Add a description to the master table
     :depends: Create master table@1
     :brings: Create master table@2

     ALTER TABLE some_table ADD COLUMN description VARCHAR(80)

When ``patchdb`` examines the database status, it will execute one *or* the other. If the
script `Create master table` isn't executed yet (for example when operating on a new database),
it will take the former script (the one that creates the table from scratch).  Otherwise, if
the database "contains" revision 1 (and not higher than 1) of the script, it will execute the
latter, bumping up the revision number.

Run-always scripts
~~~~~~~~~~~~~~~~~~

Yet another variant of scripts, which gets applied always, every time ``patchdb`` is executed.
This kind may be used to perform arbitrary operations, either at the start or at the end of the
``patchdb`` session::

    .. patchdb:script:: Say hello
       :language: python
       :always: first

       print("Hello!")

    .. patchdb:script:: Say goodbye
       :language: python
       :always: last

       print("Goodbye!")

Usage
-----

Collecting patches
~~~~~~~~~~~~~~~~~~

To use it, first of all you must register the extension within the Sphinx environment, adding
the full name of the package to the ``extensions`` list in the file ``conf.py``, for example::

    # Add any Sphinx extension module names here, as strings.
    extensions = ['metapensiero.sphinx.patchdb']

If you want to take advantage of the augmented ``DataDocumenter``, add also
``metapensiero.sphinx.patchdb.autodoc_sa`` to that list.

The other required bit of customization is the location of the `on disk scripts storage`,
i.e. the path of the file that will contain the information about every found script: this is
kept separated from the documentation itself because you will probably deploy it on production
servers just to update their database.

.. topic:: Storage format

   If the filename ends with ``.json`` it will contain a ``JSON`` formatted array, if it ends
   with ``.yaml`` the information will be dumped in ``YAML``, if it ends with ``.axon`` the
   dump will be formatted using ``AXON``, otherwise it will be a Python ``pickle``. I usually
   prefer ``AXON``, ``JSON`` or ``YAML``, because those formats are more VCs friendly and open
   to human inspection. ``AXON`` is slightly more readable than ``JSON``, while ``YAML`` is
   very slow.

The location may be set in the same ``conf.py`` as above, like::

    # Location of the external storage
    patchdb_storage = '…/dbname.json'

Otherwise, you can set it using the ``-D`` option of the ``sphinx-build`` command, so that you
can easily share its definition with other rules in a ``Makefile``. I usually put the following
snippet at the beginning of the ``Makefile`` created by ``sphinx-quickstart``::

    TOPDIR ?= ..
    STORAGE ?= $(TOPDIR)/database.json

    SPHINXOPTS = -D patchdb_storage=$(STORAGE)

At this point, executing the usual ``make html`` will update the scripts archive: that file
contains everything is needed to update the database either local or remote; in other words,
running Sphinx (or even having it installed) is **not** required to update a database.

Updating the database
~~~~~~~~~~~~~~~~~~~~~

The other side of the coin is managed by the ``patchdb`` tool, that digests the scripts archive
and is able to determine which of the scripts are not already applied and eventually does that,
in the right order.

When your database does already exist and you are just starting using ``patchdb`` you may need
to force the initial state with the following command::

    patchdb --assume-already-applied --postgres "dbname=test" --patch-storage database.json

that will just update the `patchdb` table registering current revision of all the missing
scripts, without executing them.

You can inspect what will be done, that is obtain the list of not already applied patches, with
a command like::

    patchdb --dry-run --postgres "dbname=test" -s database.json

The `database.json` archive can be sent to the production machines (in some cases I put it in a
*production* branch of the repository and use the version control tool to update the remote
machines, in other I simply used ``scp`` or ``rsync`` based solutions).

Example development Makefile snippet
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

The following is a snippet that I usually put in my outer ``Makefile``::

    export TOPDIR := $(CURDIR)
    DBHOST := localhost
    DBPORT := 5432
    DBNAME := dbname
    DROPDB := dropdb --host=$(DBHOST) --port=$(DBPORT)
    CREATEDB := createdb --host=$(DBHOST) --port=$(DBPORT) --encoding=UTF8
    STORAGE := $(TOPDIR)/$(DBNAME).json
    DSN := host=$(DBHOST) port=$(DBPORT) dbname=$(DBNAME)
    PUP := $(PATCHDB) --patch-storage=$(STORAGE) \
                      --postgres="$(DSN)" --log-file=$(DBNAME).log

    # Build the Sphinx documentation
    doc:
            $(MAKE) -C doc STORAGE=$(STORAGE) html

    $(STORAGE): doc

    # Show what is missing
    missing-patches: $(STORAGE)
            $(PUP) --dry-run

    # Upgrade the database to the latest revision
    database: $(STORAGE)
            $(PUP)

    # Remove current database and start from scratch
    scratch-database:
            -$(DROPDB) $(DBNAME)
            $(CREATEDB) $(DBNAME)
            $(MAKE) database
