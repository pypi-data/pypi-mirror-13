==================
web.dispatch.route
==================

    © 2009-2016 Alice Bevan-McGregor and contributors.

..

    https://github.com/marrow/web.dispatch.route

..

    |latestversion| |ghtag| |downloads| |masterstatus| |mastercover| |masterreq| |ghwatch| |ghstar|



Introduction
============

Dispatch is the process of taking some starting point and a path, then resolving the object that path refers to. This
process is common to almost every web application framework (transforming URLs into controllers), RPC system, and even
filesystem shell. Other terms for this process include: "traversal", "routing", or "lookup".

Route-based dispatch is the variant of dispatch that uses handlers for explicitly registered paths, optionally with
regular expression (regex)-based path elements. This implementation exposes an API that particularly benefits from the
use of mix-ins as traits. This gives a clean flexability to routes that are difficult to beat.

Most implementations of regex-based routing do so in a naïve way, often iterating lists of all routes at O(n)
worst-case. Others allow you to manually partition the space with sub-routers, or optimize by declaration or
manual lexicographical order. Some produce monolithic regular expressions that can cause instability when an
application grows beyond a certain size. Some even iterate the whole list even after finding an endpoint.

This dispatcher does not. It builds a tree, and descends the tree preferring static elements to dynamic ones,
with a controllalbe presedence at declaration. It optionally handles binding matched dynamic elements to arguments on
the resulting endpoint. Performance is O(depth) worst-case.

This package speaks a standardized `dispatch protocol <https://github.com/marrow/WebCore/wiki/Dispatch-Protocol>`_ and
is not entirely intended for direct use by most developers. The target audience is instead the authors of frameworks
that may require such modular dispatch for use by their own users.


Installation
============

Installing ``web.dispatch.route`` is easy, just execute the following in a terminal::

    pip install web.dispatch.route

**Note:** We *strongly* recommend always using a container, virtualization, or sandboxing environment of some kind when
developing using Python; installing things system-wide is yucky (for a variety of reasons) nine times out of ten.  We
prefer light-weight `virtualenv <https://virtualenv.pypa.io/en/latest/virtualenv.html>`_, others prefer solutions as
robust as `Vagrant <http://www.vagrantup.com>`_.

If you add ``web.dispatch.route`` to the ``install_requires`` argument of the call to ``setup()`` in your
application's ``setup.py`` file, this dispatcher will be automatically installed and made available when your own
application or library is installed.  We recommend using "less than" version numbers to ensure there are no
unintentional side-effects when updating.  Use ``web.dispatch.route<1.1`` to get all bugfixes for the current release,
and ``web.dispatch.route<2.0`` to get bugfixes and feature updates while ensuring that large breaking changes are not
installed.


Development Version
-------------------

    |developstatus| |developcover| |ghsince| |issuecount| |ghfork|

Development takes place on `GitHub <https://github.com/>`_ in the 
`web.dispatch.route <https://github.com/marrow/web.dispatch.route/>`_ project.  Issue tracking, documentation, and
downloads are provided there.

Installing the current development version requires `Git <http://git-scm.com/>`_, a distributed source code management
system.  If you have Git you can run the following to download and *link* the development version into your Python
runtime::

    git clone https://github.com/marrow/web.dispatch.route.git
    (cd web.dispatch.route; python setup.py develop)

You can then upgrade to the latest version at any time::

    (cd web.dispatch.route; git pull; python setup.py develop)

If you would like to make changes and contribute them back to the project, fork the GitHub project, make your changes,
and submit a pull request.  This process is beyond the scope of this documentation; for more information see
`GitHub's documentation <http://help.github.com/>`_.


Usage
=====

This section is split between framework authors who will be integrating the overall protocol into their systems, and
the "producers" using the system to register routes according to the API.

Framework Use
-------------

To begin resolving paths against routes registered in objects, first instantiate the dispatcher::

    from web.dispatch.route import RouteDispatch
    
    dispatch = RouteDispatch()

Currently the route dispatcher has no configuration options.  With a prepared dispatcher, and supposing you have some
object to dispatch against, you'll need to prepare the path according to the protocol::

    path = "/foo/bar/baz"  # Initial path, i.e. an HTTP request's PATH_INFO.
    path = path.split('/')  # Find the path components.
    path = path[1:]  # Skip the singular leading slash; see the API specification.
    path = deque(path)  # Provide the path as a deque instance, allowing popleft.

Of course, the above is rarely split apart like that. We split apart the invidiual steps of path processing here to
more clearly illustrate. In a web framework the above would happen once per request that uses dispatch. This, of
course, frees your framework to use whatever internal or public representation of path you want: choices of
separators, and the ability for deque to consume arbitrary iterables. An RPC system might ``split`` on a period and
simply not have the possibility of leading separators. Etc.

You can now call the dispatcher and iterate the dispatch events::

    for segment, handler, endpoint, *meta in dispatch(None, some_object, path):
        print(segment, handler, endpoint)  # Do something with this information.

The initial ``None`` value there represents the "context" to pass along to initializers of classes encountered during
dispatch.  If the value ``None`` is provided, classes won't be instantiated with any arguments. If a context is
provided it will be passed as the first positional argument to instantiation.

After completing iteration, check the final ``endpoint``. If it is ``True`` then the path was successfully mapped to
the object referenced by the ``handler`` variable. If dispatch is unsuccessful, a ``LookupError`` is raised with an
explanation referencing the path element that caused the erorr.

You can always just skip straight to the answer if you so choose::

    try:
        segment, handler, endpoint, *meta = list(dispatch(None, some_object, path))[-1]
    except LookupError:
        ... # Dispatch failed.

However, providing some mechanism for callbacks or notifications of dispatch is often far more generally useful.

**Note:** It is entirely permissable for dispatchers to return ``None`` as a processed path segment. Route-based
dispatch will do this to announce the starting point of dispatch. This is especially useful if you need to know if the
initial object was a class that was instantiated.  (In that event ``handler`` will be an instance of ``some_object``
during the first iteration instead of being literally ``some_object``.)  Other dispatchers may return ``None`` at
other times, such as to indicate multiple steps of intermediate processing.

Python 2 & 3 Compatibility
~~~~~~~~~~~~~~~~~~~~~~~~~~

The dispatch protocol is designed to be extendable in the future by using ``namedtuple`` subclasses, however this has
an impact on usage as you may have noticed the ``*meta`` in there. This syntax, introduced in Python 3, will gather
any extraneous tuple elements into a separate list. If you actually care about the metadata do not unpack the tuple
this way.  Instead::

    for meta in dispatch(None, some_object, path):
        segment, handler, endpoint = step[:3]  # Unpack, but preserve.
        print(segment, handler, endpoint, meta)  # Do something with this information.

This document is written from the perspective of modern Python 3, and throwing away the metadata within the ``for``
statement itself provides more compact examples. The above method of unpacking the first three values is the truly
portable way to do this across versions.


Basic Routable Objects
----------------------

The simplest routable object is one that has some attribute with a ``__route__`` attribute of its own::

    class Root:
        def hello(self, name):
            return "Hello " + name
        
        hello.__route__ = '/{name}'

This defines a method capable of handling any single path element. Because this is a common pattern, and having such
annotations after the method body, divorced from the method's definition, is ugly, a decorator is provided::

    from web.dispatch.route import route

    class Root:
        @route('/{name}')
        def hello(self, name):
            return "Hello " + name

Now an attempt to access a path such as ``/world`` will result in version of the method with that argument already
bound to it. The syntax allows for customization of the default expression, which is simply "any single path element".
To do so, after the name add a colon (``:``) followed by the custom expression. Be careful not to use any forward
slashes within your expression::

    class Root:
        @route('/{name:[a-zA-Z ]+}/{age:[1-9][0-9]*}')
        def hello(self, name, age):
            return name + " is " + age + " years old"

Now access to ``/dad/27`` is valid, returning a callable that when executed will return ``dad is 27 years old``, but
``/42/dad`` is invalid, and won't match any routes. When using the ``route`` decorator declaration order is preserved
via the ``__index__`` annotation.


Version History
===============

Version 1.0
-----------

* Initial extract from WebCore 2.


License
=======

web.dispatch.route has been released under the MIT Open Source license.

The MIT License
---------------

Copyright © 2009-2016 Alice Bevan-McGregor and contributors.

Permission is hereby granted, free of charge, to any person obtaining a copy of this software and associated
documentation files (the “Software”), to deal in the Software without restriction, including without limitation the
rights to use, copy, modify, merge, publish, distribute, sublicense, and/or sell copies of the Software, and to permit
persons to whom the Software is furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all copies or substantial portions of the
Software.

THE SOFTWARE IS PROVIDED “AS IS”, WITHOUT WARRANTY OF ANY KIND, EXPRESS OR IMPLIED, INCLUDING BUT NOT LIMITED TO THE
WARRANTIES OF MERCHANTABILITY, FITNESS FOR A PARTICULAR PURPOSE AND NON-INFRINGEMENT. IN NO EVENT SHALL THE AUTHORS OR
COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR
OTHERWISE, ARISING FROM, OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE SOFTWARE.


.. |ghwatch| image:: https://img.shields.io/github/watchers/marrow/web.dispatch.route.svg?style=social&label=Watch
    :target: https://github.com/marrow/web.dispatch.route/subscription
    :alt: Subscribe to project activity on Github.

.. |ghstar| image:: https://img.shields.io/github/stars/marrow/web.dispatch.route.svg?style=social&label=Star
    :target: https://github.com/marrow/web.dispatch.route/subscription
    :alt: Star this project on Github.

.. |ghfork| image:: https://img.shields.io/github/forks/marrow/web.dispatch.route.svg?style=social&label=Fork
    :target: https://github.com/marrow/web.dispatch.route/fork
    :alt: Fork this project on Github.

.. |masterstatus| image:: http://img.shields.io/travis/marrow/web.dispatch.route/master.svg?style=flat
    :target: https://travis-ci.org/marrow/web.dispatch.route/branches
    :alt: Release build status.

.. |mastercover| image:: http://img.shields.io/codecov/c/github/marrow/web.dispatch.route/master.svg?style=flat
    :target: https://codecov.io/github/marrow/web.dispatch.route?branch=master
    :alt: Release test coverage.

.. |masterreq| image:: https://img.shields.io/requires/github/marrow/web.dispatch.route.svg
    :target: https://requires.io/github/marrow/web.dispatch.route/requirements/?branch=master
    :alt: Status of release dependencies.

.. |developstatus| image:: http://img.shields.io/travis/marrow/web.dispatch.route/develop.svg?style=flat
    :target: https://travis-ci.org/marrow/web.dispatch.route/branches
    :alt: Development build status.

.. |developcover| image:: http://img.shields.io/codecov/c/github/marrow/web.dispatch.route/develop.svg?style=flat
    :target: https://codecov.io/github/marrow/web.dispatch.route?branch=develop
    :alt: Development test coverage.

.. |developreq| image:: https://img.shields.io/requires/github/marrow/web.dispatch.route.svg
    :target: https://requires.io/github/marrow/web.dispatch.route/requirements/?branch=develop
    :alt: Status of development dependencies.

.. |issuecount| image:: http://img.shields.io/github/issues-raw/marrow/web.dispatch.route.svg?style=flat
    :target: https://github.com/marrow/web.dispatch.route/issues
    :alt: Github Issues

.. |ghsince| image:: https://img.shields.io/github/commits-since/marrow/web.dispatch.route/1.0.0.svg
    :target: https://github.com/marrow/web.dispatch.route/commits/develop
    :alt: Changes since last release.

.. |ghtag| image:: https://img.shields.io/github/tag/marrow/web.dispatch.route.svg
    :target: https://github.com/marrow/web.dispatch.route/tree/1.0.0
    :alt: Latest Github tagged release.

.. |latestversion| image:: http://img.shields.io/pypi/v/web.dispatch.route.svg?style=flat
    :target: https://pypi.python.org/pypi/web.dispatch.route
    :alt: Latest released version.

.. |downloads| image:: http://img.shields.io/pypi/dw/web.dispatch.route.svg?style=flat
    :target: https://pypi.python.org/pypi/web.dispatch.route
    :alt: Downloads per week.

.. |cake| image:: http://img.shields.io/badge/cake-lie-1b87fb.svg?style=flat
