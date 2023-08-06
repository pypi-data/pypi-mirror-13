


==========
DjamBase
==========

.. image:: http://images.jambase.com/logos/jambase140x70.gif

**A Python Jambase API Client Library**

Getting Started
---------------
.. code::

    $ pip install DjamBase

Get a valid Developer API key at http://developer.jambase.com.

.. code:: python

    import DjamBase

    db = DjamBase.API("your_api_key")

Usage
---------

**db.artist_search(params)**
    'params' is a dictionary, with: ``{"id": <int>, "name": <str>}`` as valid key, value options. These will serve
    as the JamBase Artist search parameters.
**db.venue_search(params)**
    'params' is a dictionary, with: ``{"id": <int>, "zipCode": <int>, "radius"*: <int>}`` as valid key, value options.
    These are the JamBase Venue search parameters. * miles.
**db.event_list(params)**
    params' is a dictionary, with:

.. code:: python

    {
    "id": <int>,
    "artist": <str>,
    "artistId": <int>,
    "band": <str>,
    "bandId": <int>,
    "venueId": <int>,
    "zipCode": <int>,
    "radius": <int>,
    "startDate": <YYYY-MM-DD>,
    "endDate": <YYYY-MM-DD>
    }


as possible valid key, value options. These are the JamBase Event search parameters.

Use any combination of a functions' available parameters that you like, depending on the
desired results. Notice that all keys are written in "camelCase".



Use as below:

.. code:: python

    r = db.event_list( {"name": "the foobar fighters", "radius": 200} )


Response
--------


Of course, you can use whatever variable name you like, but the above variable "r" will contain a response object. It's that simple!
The ".body" attribute of this object contains the response in JSON format. If you would like XML, pass "xml"
as the optional 2nd argument when instantiating the client.

**r.body**
   -Use this response object property retrieve the content of the search response. JSON by default.
**r.status**
   -This property will give you access to the dialogues' HTTP status code, in case there are issues.
**r.text**
   -This property will give you a stringified version of the JSON/XML response.
**r.binary**
   -This property will get you binary version of the response.



.. code:: python

    json = r.body
    print json

Example
---------

.. code:: python

    import DjamBase

    db = DjamBase.API("your_api_key", "xml")

    r = db.event_list( {"name": "the foobar fighters", "radius": 200} )
    code = r.status
    print code      **<Response-200>**

    xml = r.body
    print xml
