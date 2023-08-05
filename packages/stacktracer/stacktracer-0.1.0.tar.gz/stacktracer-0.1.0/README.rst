stacktracer
===========

Stack tracer for multi-threaded applications.

Installation
------------

You can install ``stacktracer`` simply using ``pip``:

.. code:: bash

    pip install stacktracer

Usage
-----

.. code:: python

    import stacktracer

    stacktracer.start_trace("trace.html", interval=5, auto=True)
    # Set auto flag to always update file!

    // Do something with multi-threading here

    stacktracer.stop_trace()
