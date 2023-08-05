Django-Mail-Templated Changelog
===============================

2.4.0
-----

- Fixed setup.py, added missing files to the package.

- Added more tests.

2.3.0
-----

- Made ``template_name`` argument required when ``render=True`` passed
  to ``__init__()``.
  
- Removed argument ``render`` of method ``send()``.

- Added public property ``is_rendered``.

- Added more tests.

2.2.0
-----

- Fixed compatibility with Python 3

2.1.0
-----

- Added full support of template inheritance.

- Added obligatory base email template.

- Fixed broken pickling/unpickling feature.

- ``render=True`` is now ignored on initialisation without template. Raised
  error before.

2.0.0
-----

*This is intermediate version with broken pickling/unpickling feature.*
Using of next or previous version is highly recommended.

- Slightly changed the list of arguments for ``EmailMessage.__init__()``.
  
- Replaced template and template\_name property setters with method
  ``load_template()``.
  
- Added method ``render()``.

- Added support for late initialisation.

- Improved tests.

1.0.0
-----

- Fixed the multilingual templates support for Django >= 1.8.
