Configuration
=============

LIVEWATCH_EXTENSIONS
--------------------

If you want to use it with ``cache`` or ``django-celery`` or ``django-rq`` you have to update the ``LIVEWATCH_EXTENSIONS`` setting.

cache
`````

Make sure that you have a ``cache`` installed and configured.

.. code-block:: python

    # Example with cache support
    LIVEWATCH_EXTENSIONS = (
        'livewatch.extensions.cache:CacheExtension',
    )

django-celery
`````````````

Make sure that you have ``celery`` installed. You can use the ``celery`` extra target for that.

.. code-block:: bash

    $ pip install django-livewatch[celery]

.. code-block:: python

    # Example with celery support
    LIVEWATCH_EXTENSIONS = (
        'livewatch.extensions.rq:CeleryExtension',
    )

Celery has to be configured in your ``project.celery`` module that defines the celery app. For more details see the
official :ref:`celery documentation <celery:django-first-steps>`.

Please make sure to load tasks from ``INSTALLED_APPS``:

.. code-block:: python

    app.autodiscover_tasks(lambda: settings.INSTALLED_APPS)

If you don't load all tasks from the ``INSTALLED_APPS`` setting, please use ``CELERY_IMPORTS`` to register the livewatch tasks.

.. code-block:: python

    # In settings.py
    # Activate livewatch.tasks
    CELERY_IMPORTS = (
        'livewatch.tasks',
    )


django-rq
`````````

Make sure that you have ``rq`` installed. You can use the ``rq`` extra target for that.

.. code-block:: bash

    $ pip install django-livewatch[rq]

.. code-block:: python

    # Example with rq support
    LIVEWATCH_EXTENSIONS = (
        'livewatch.extensions.rq:RqExtension',
    )

.. hint::

    If you use ``celery`` or ``rq``, you have to ensure that a ``cache`` is running!

For details on writing your own extensions, please see the :ref:`extending-livewatch` section.
