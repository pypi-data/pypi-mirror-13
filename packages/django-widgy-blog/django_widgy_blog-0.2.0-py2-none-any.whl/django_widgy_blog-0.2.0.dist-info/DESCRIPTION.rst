Django Widgy Blog
=================

This is reusable blog app designed for use with django-widgy_. It can
be utilized as a drop-in addition to a widgy project for creating a
quick, run-of-the-mill blog or as an abstract guide to building your
own custom app that takes advantage of all the wonderful features that
widgy offers.

Quickstart
----------

(This guide assumes that your project is already using widgy. Please see
this tutorial_ if this is not the case.)

1.  Install the package

        $ pip install django-widgy-blog

2.  Add ``widgy_blog`` to your ``INSTALLED_APPS``.

3.  Run ``python manage.py migrate`` in
    order to generate the relevant models in the database.

4.  Configure the urls:

    a.  If you're using widgy's ``contrib.urlconf_include`` package, you can
        opt to use widgy_blog as a plugin. This allows admin users of the site
        to take advantage of plugin-specific features, such as editing the url
        route of the blog and customizing its addition to menus. See
        urlconf_include_ for more information.

    b.  Alternatively, you can include the widgy_blog urls within your urls.py
        file as you normally would. Just remember to add them before the
        included Mezzanine urls if you're editing the root conf!

5.  That's it. Log in to the admin center and start adding blog posts!

.. _django-widgy: https://github.com/fusionbox/django-widgy
.. _tutorial: http://docs.wid.gy/en/latest/tutorials/widgy-mezzanine-tutorial.html
.. _urlconf_include: http://docs.wid.gy/en/latest/tutorials/widgy-mezzanine-tutorial.html#urlconf-include


CHANGES
=======

0.2.0 (2016-01-14)
------------------

- Support for Django 1.8
- Blog archives are now shown in reverse chronological order.
- Blogs now have date and time rather than just date published.
- Tags are now supported
- Various small bugfixes.
- Blog views with a page querystring equal to 1 will now have a canonical_url
  in the template context pointing to the same page without that querystring.

0.1.0 (release 2014-12-03)
--------------------------

- Add model attributes to AbstractBlogLayout and BlogAdmin
  that make them easier to subclass. Update AbstractBlogLayout
  published queryset function to use fewer queries [Scott Clark, #18]
- **Backwards Incompatible:** Registered the ``BlogLayout`` model with widgy.
  If you weren't using this as your Blog layout, you will need to unregister
  it::

      import widgy
      from widgy_blog.models import BlogLayout

      widgy.unregister(BlogLayout)

  If you were already registering the ``BlogLayout`` yourself, you can just
  remove that code.


