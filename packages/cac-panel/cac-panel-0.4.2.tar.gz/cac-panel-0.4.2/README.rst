==================
python-cloudatcost
==================

``cac-panel`` is a python wrapper for `panel.cloudatcost.com`_


---------
usage CLI
---------
CACpy Provides a cli for panel and api:

::

    cac-panel --help

-------------
usage Library
-------------


::

    from cacpanel import CACpanel
    panel = CACpanel('email@example.com','password')
    print(panel.settings())

More details and the latest updates can be found on the `GitHub Project Page`_.

.. _GitHub Project Page: https://github.com/makefu/cac-panel
