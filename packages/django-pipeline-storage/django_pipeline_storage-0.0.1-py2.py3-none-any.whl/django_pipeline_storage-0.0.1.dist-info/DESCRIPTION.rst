=====
Pipeline Storage
=====

A simple Storage finder for files when django-pipeline is develop mode.

Installation
------------

To install it, simply: ::

    pip install django-pipeline-storage


Quick start
-----------

1. Replace:

.. code-block:: python

  STATICFILES_STORAGE = 'pipeline.storage.PipelineStorage'

  by:

  STATICFILES_STORAGE = 'pipeline_storage.PipelineStorage'

2. Add to Pipeline settings:

.. code-block:: python

    PIPELINE = {
      ...
      'PIPELINE_COLLECTOR_ENABLED': False,
      ...
    }


Todo
----

1. add more storages support
2. add test

