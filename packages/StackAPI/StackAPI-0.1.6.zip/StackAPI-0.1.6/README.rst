This is a Python wrappers for the `Stack Exchange API`_. This library
supports Stack Exchange API v2.2.

This library has support for:

-  The Stack Exchange backoff parameter. It will automatically force a
   delay to match the parameter.
-  Read and write functionality via the API.
-  Can retrieve multiple pages of results with a single call and merges
   all the results into a single response.
-  Throws exceptions returned by the API for easier troubleshooting.
-  Utilizes `Requests`_.

Example usage patterns:
-----------------------

Establish a connection to Stack Overflow and gather some comments
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

::

    from stackapi import StackAPI
    SITE = StackAPI('stackoverflow')
    comments = SITE.fetch('comments')

The above, will issue a call to the ```/comments```_ end point on Stack
Overflow.

If you wish to interact with the API’s ``write`` functions, you can pass
additional parameters to the ``SITE`` variable:

-  ``max_pages`` allows you to set the maximum number of pages to
   return. The wrapper attempts to return everything to you that it can,
   and setting this variable ensure that you don’t eat through your
   quota unintentionally. The default is 100 pages.
-  ``page_size`` allows you to set the maximum number of items on a
   page. The default is 100.
-  ``key`` is the site you are issuing queries to. (In the above
   example, it is ``stackoverflow``)
-  ``access_token`` is utilized if you wish to write data back to the
   network

These parameters can be passed during the initialization of the ``SITE``
variable

::

    SITE = StackAPI('stackoverflow', key=SETTINGS['API_KEY'], access_token=SETTINGS['API_TOKEN'])

or after initialization

::

    SITE.page_size = 10
    SITE.max_pages = 10

Interacting with the API
------------------------

Retrieving data
~~~~~~~~~~~~~~~

The ``fetch`` function takes an end point as an argument and attempts to
return data utilizing that end point. If you have set an
``access_token``, it will automatically attach that to your retrieval
attempt, so that your quota is increased. Other variables you can pass
``fetch`` include:

-  ``page`` - When there is more than 1 page of results, you may need to
   get data from something other than the first page. This parameter is
   utilized to get to those additional pages.
-  ``filter`` - If you have generated a non default filter to pull
   additional data elements, this field is utilized to pass that filter

``fetch`` will attempt to pull back multiple pages of data for you if
the API indicates there is more data and your ``max_pages`` hasn’t been
exceeded

Sending data
~~~~~~~~~~~~

The ``send_data`` function takes similar arguments to the ``fetch``
function. In addition, it will take the arguments for the end point as
the `API documentation`_ describes, and pass those along.

::

    flag = SITE.send_data('comments/%s/flags/add' % (comment_id), option_id=flag_option_id)

This example will add a flag to the ``comment_id``. The flag added is
specified by the value of

.. _Stack Exchange API: http://api.stackexchange.com/
.. _Requests: http://docs.python-requests.org/
.. _``/comments``: http://api.stackexchange.com/docs/comments
.. _API documentation: http://api.stackexchange.com/docs