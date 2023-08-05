Changelog
=========

Version 0.1.2 [2016-01-04]
--------------------------

- `19a1f6a <https://github.com/interop-dev/django-netjsongraph/commit/19a1f6a>`_:
  added ``NETJSONGRAPH_TIMEOUT``
- `365509c <https://github.com/interop-dev/django-netjsongraph/commit/365509c>`_:
  avoided possible *500 internal server error* when updating topology from admin action
- `7fa86db <https://github.com/interop-dev/django-netjsongraph/commit/7fa86db>`_:
  added failure message when updating topology from admin
- `56066e8 <https://github.com/interop-dev/django-netjsongraph/commit/56066e8>`_:
  added ``get_absolute_url()`` method to ``Topology`` model
- `f90c639 <https://github.com/interop-dev/django-netjsongraph/commit/f90c639>`_:
  added "Links to other nodes" section in ``Node`` admin
- `d6fff61 <https://github.com/interop-dev/django-netjsongraph/commit/d6fff61>`_:
  added ``NETJSONGRAPH_LINK_EXPIRATION`` days setting
- `#3 <https://github.com/interop-dev/django-netjsongraph/issues/3>`_,
  `b246669 <https://github.com/interop-dev/django-netjsongraph/commit/b246669>`_:
  minor improvements to visualizer

Version 0.1.1 [2015-12-27]
--------------------------

- added possibility to unpublish topologies
- added admin actions for topology admin: unpublish, publish and update
- update topology attributes (protocol, version, metric) when latest data is retrieved
- improved update method of ``Topology`` model

Version 0.1 [2015-12-23]
------------------------

- topology collector
- HTTP API
- visualizer
- admin
