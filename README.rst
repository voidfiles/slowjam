Slowjam: Application Tracing For Python
=======================================

Slowjam is an easy to use application tracer for python.

Listen to this:

.. code-block:: python

    >>> import requests

    >>> from slowjam.trace import jam
    >>> from slowjam.context import slowjam_context

    >>> slowjam_context.start('my_application', extras={'http': True})

    >>> with jam('listen', extras={'deylay': 3}):
    >>>     resp = requests.get('https://httpbin.org/delay/3')

    >>>     with jam('request.origin'):
    >>>         origin = resp.json().get('origin')
    >>>         origin.split('.')

    >>> profile = slowjam_context.stop()
    >>> if profile:
    >>>     print ''
    >>>     print unicode(profile)
    >>>     print ''

           time   exec time event
    ----------- ----------- ------------------------------
           0 ms             + my_application [http=True]
           0 ms             | + listen [deylay=3]
        8039 ms (+    0 ms) | | = request.decode
                (+ 8039 ms) | +
                (+ 8039 ms) +


Slowjam makes it easy to start getting feedback quick, but with some extra
effort it seamlessly integrates with other monitoring tools such as statsd,
graphite, and logstash.

Feature Support
---------------

- Application Tracing
- Function timing
- Usable output
- Graphite Integration

Installation
------------

To install Slowjam, simply:

.. code-block:: bash

    $ pip install slowjam
    ✨🍰✨

Satisfaction, guaranteed.
