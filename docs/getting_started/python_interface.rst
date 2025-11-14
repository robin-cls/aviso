Python Interface
================

The ``altimetry_downloader_aviso`` tool provides a simple Python API to programmatically interact
with the Aviso catalog.

It exposes the same three core operations as the CLI: ``summary``, ``details``, and ``get``.

.. code-block:: python

    from altimetry_downloader_aviso import summary, details, get

Basic Usage
-----------

List available products
~~~~~~~~~~~~~~~~~~~~~~~

Retrieve a summary of the available products in Aviso catalog using :func:`aviso_client.summary()` function. Retrieve an :class:`aviso_client.AvisoCatalog` object.

.. code-block:: pycon

    >>> catalog = summary()
    >>> catalog
    AvisoCatalog(products=[AvisoProduct(id='d1f06620-d11c-4945-b53d-6769e909be01', title='Wind & Wave product SWOT Level-3 WindWave - Extended'), ...])

To list available products in the catalog, use the :attr:`aviso_client.AvisoCatalog.products` attribute, that is a list of :class:`aviso_client.AvisoProduct` objects.

.. code-block:: pycon

    >>> for product in catalog.products:
    >>>     print(f"{product.id}  {product.title}")
    SWOT_L3_LR_WIND_WAVE_Extended  Wind & Wave product SWOT Level-3 WindWave - Extended
    SWOT_L3_LR_SSH_Basic  Altimetry product SWOT Level-3 Low Rate SSH - Basic
    ...


View product details
~~~~~~~~~~~~~~~~~~~~

Get detailed metadata for a given product using :func:`aviso_client.details()` function. It returns an :class:`aviso_client.AvisoProduct` object.

.. code-block:: pycon

    >>> product = aviso_client.details("SWOT_L3_LR_SSH_Basic")
    >>> print(product.abstract)
    The SWOT L3_LR_SSH product provides ocean topography measurements obtained from the SWOT KaRIn and nadir altimeter instruments,...


Download a product
~~~~~~~~~~~~~~~~~~

Download a product using :func:`aviso_client.get()` function.

.. code-block:: pycon

    >>> local_files = get("SWOT_L3_LR_SSH_Basic", output_dir="aviso_dir", cycle_number=7, pass_number=[12, 13])
    >>> print(local_files)
    ['aviso_dir/SWOT_L3_LR_SSH_Basic_007_012_20231123T193011_20231123T202137_v2.0.1.nc',
     'aviso_dir/SWOT_L3_LR_SSH_Basic_007_013_20231123T202138_20231123T211304_v2.0.1.nc']

.. caution::

    By default, already existing files are not re-downloaded. Use ``--overwrite`` option to force re-download.
    

Further Reading
---------------

- :doc:`../basic_usage/advanced_usage`
