.. _install:


Installation guide
==================

Before installing django-soapbox, you'll need to have a copy of
`Django <https://www.djangoproject.com>`_ already installed. For
information on obtaining and installing Django, consult the `Django
download page <https://www.djangoproject.com/download/>`_, which offers
convenient packaged downloads and installation instructions.

The |version| release of django-soapbox supports Django 1.8 and 1.9,
on any of Python 2.7, 3.3, 3.2, 3.4 or 3.5. Older versions of Django
and/or Python may work, but are not tested or officially supported.

Note that Django 1.9 drops support for Python 3.2 and 3.3, and Python
3.2 will reach end-of-life in February 2016. The next released version
of ``django-soapbox`` will therefore, drop support for Python 3.2.


Normal installation
-------------------

The preferred method of installing django-soapbox is via
``pip``, the standard Python package-installation tool. If you don't
have ``pip``, instructions are available for `how to obtain and
install it <https://pip.pypa.io/en/latest/installing.html>`_.

Once you have ``pip``, simply type::

    pip install django-soapbox


Manual installation
-------------------

It's also possible to install django-soapbox manually. To do
so, obtain the latest packaged version from `the listing on the Python
Package Index
<https://pypi.python.org/pypi/django-soapbox/>`_. Unpack the
``.tar.gz`` file, and run::

    python setup.py install

Once you've installed django-soapbox, you can verify successful
installation by opening a Python interpreter and typing ``import
soapbox``.

If the installation was successful, you'll simply get a fresh Python
prompt. If you instead see an ``ImportError``, check the configuration
of your install tools and your Python import path to ensure
django-soapbox installed into a location Python can import from.


Installing from a source checkout
---------------------------------

The development repository for ``django-soapbox`` is at
<https://github.com/ubernostrum/django-soapbox>. Presuming you have `git
<http://git-scm.com/>`_ installed, you can obtain a copy of the
repository by typing::

    git clone https://github.com/ubernostrum/django-soapbox.git

From there, you can use normal git commands to check out the specific
revision you want, and install it using ``python setup.py install``.

