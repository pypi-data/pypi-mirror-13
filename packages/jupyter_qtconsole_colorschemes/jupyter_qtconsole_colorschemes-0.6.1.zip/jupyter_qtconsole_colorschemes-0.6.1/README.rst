====================================
Color Schemes for Jupyter Qt Console
====================================

    :Author: Joon Ro
    :Contact: joon.ro@outlook.com
    :Date: Version 0.6.1, 2016-02-06 SAT

Various color schemes for `Jupyter <http://jupyter.org>`_ `Qt Console <http://jupyter.org/qtconsole>`_. It was originally for `IPython <http://ipython.org>`_ Qt
Console, but as of IPython 4.0, the qtconsole have moved to new project under
the name Jupyter. Each color scheme consists of a ``.py`` file for the pygments
style and a ``.css`` file for Qt Console specific color settings.

List of color schemes
---------------------

- `Base16 <https://github.com/chriskempson/base16>`_

  - Ocean Dark (``base16_ocean_dark``)

- `monokai <http://www.monokai.nl/blog/2006/07/15/textmate-color-theme/>`_ (``monokai``)

- `Solarized <http://ethanschoonover.com/solarized>`_ 

  - Light (``solarizedlight``)

  - Dark (``solarizeddark``)

- `Tomorrow <https://github.com/ChrisKempson/Tomorrow-Theme>`_: ``tomorrow``

- `Zenburn <http://kippura.org/zenburnpage/>`_: ``zenburn``

Installation
------------

Thanks to `Antony Lee <https://bitbucket.org/anntzer/>`_, now the color schemes are in a module called
``jupyter_qtconsole_colorschemes``. You can install it with ``pip``:

.. code-block:: sh

    pip install jupyter_qtconsole_colorschemes

Usage
-----

Jupyter Qt Console
~~~~~~~~~~~~~~~~~~

In ``~/.jupyter/jupyter_qtconsole_config.py``, add the following with the color
scheme name you want to use (the example shown with ``zenburn``):

.. code-block:: python

    color_theme = 'zenburn'  # specify color theme

    import pkg_resources
    c.JupyterQtConsoleApp.stylesheet = pkg_resources.resource_filename(
        "jupyter_qtconsole_colorschemes", "{}.css".format(color_theme))

    c.JupyterWidget.syntax_style = color_theme

IPython Qt Console
~~~~~~~~~~~~~~~~~~

If you are using older version of Qt Console, then add the following to 
``~/.ipython/profile_default/ipython_qtconsole_config.py``:

.. code-block:: python

    color_theme = 'zenburn'  # specify color theme

    import pkg_resources
    c.IPythonQtConsoleApp.stylesheet = pkg_resources.resource_filename(
        "jupyter_qtconsole_colorschemes", "{}.css".format(color_theme))

    c.IPythonWidget.syntax_style = color_theme

License
-------

Released under the `MIT License <https://bitbucket.org/joon/color-schemes-for-ipython-qt-console/src/master/LICENSE>`_
