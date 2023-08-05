==========================
tt, our ablog/sphinx theme
==========================
:version: 0.3.1

a Sphinx / ablog theme built on top of `alabaster <https://github.com/bitprophet/alabaster>`_

Install
----------

To install, run::

    python3 setup install

This will make available the package ``tibas.tt``.
You can then, in your ``config.py`` import and use::

    import tibas.tt as tt

    ...

    templates_path = [
        tt.get_path(), ablog.get_html_templates_path()
    ]

    ...

    html_theme = 'tt'

    ...

    html_theme_path = [ tt.get_path() ]
