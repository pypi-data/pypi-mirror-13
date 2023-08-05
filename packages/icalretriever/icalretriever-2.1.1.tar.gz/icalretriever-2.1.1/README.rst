ICalRetriever
=============

|build status|

ICalRetriever is a HTTP ICS retriever. It is designed to be called by a
crontab each hour in order to download an ICalendar file from a designed
HTTP location, eventually apply filters on it, and then write it to the
disk.

Then, you can serve the ICal to WebDAV clients (using Radicale WebDAV
server for example) in readonly mode, so that their synchronised ICal
file is updated each hour conforming to the ICS HTTP source.

Installing
----------

ICalRetriever is available on PyPI as ``icalretriever``.

Usage
-----

Simply call the retriever with the configuration file as parameter.

::

    $ icalretriever-retrieve.py myConfig.yml

Configuration file
------------------

Configuration is written in YAML.

You can sync multiple calendar using one configuration file. Here is an
example of configuration file you may want to copy and adapt to your
needs:

::

    calendars:
     - name: Fake calendar (filtered)
       file: output_filtered.ics
       url: http://perdu.com/fake.ics
       filters:
         - name: remove_days
           args: [5, 6]
         - name: remove_name
           args: ["Boring event I dont want", "Another boring event"]

     - name: Fake calendar (not filtered)
       file: output.ics
       url: http://perdu.com/fake.ics

License
-------

This program is brought to you under MIT license. For further
informations, please read the provided LICENSE file.

.. |build status| image:: https://git.microjoe.org/ci/projects/1/status.png?ref=master
   :target: https://git.microjoe.org/ci/projects/1?ref=master
