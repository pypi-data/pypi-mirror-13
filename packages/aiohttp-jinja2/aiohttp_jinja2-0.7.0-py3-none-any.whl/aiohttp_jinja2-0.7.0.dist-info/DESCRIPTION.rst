aiohttp_jinja2
==============

jinja2_ template renderer for `aiohttp.web`__.


.. _jinja2: http://jinja.pocoo.org

.. _aiohttp_web: http://aiohttp.readthedocs.org/en/latest/web.html

__ aiohttp_web_


Usage
-----

Before template rendering you have to setup *jinja2 environment* first::

    app = web.Application()
    aiohttp_jinja2.setup(app,
        loader=jinja2.FileSystemLoader('/path/to/templates/folder'))


After that you may to use template engine in your *web-handlers*. The
most convinient way is to decorate *web-handler*::

    @aiohttp_jinja2.template('tmpl.jinja2')
    def handler(request):
        return {'name': 'Andrew', 'surname': 'Svetlov'}

On handler call the ``aiohttp_jinja2.template`` decorator will pass
returned dictionary ``{'name': 'Andrew', 'surname': 'Svetlov'}`` into
template named ``tmpl.jinja2`` for getting resulting HTML text.

If you need more complex processing (set response headers for example)
you may call ``render_template`` function::

    @asyncio.coroutine
    def handler(request):
        context = {'name': 'Andrew', 'surname': 'Svetlov'}
        response = aiohttp_jinja2.render_template('tmpl.jinja2',
                                                  request,
                                                  context)
        response.headers['Content-Language'] = 'ru'
        return response

License
-------

``aiohttp_jinja2`` is offered under the Apache 2 license.

CHANGES
=======

0.7.0 (2015-12-30)
------------------

- Add ability to decorate class based views (available in aiohttp 0.20) #18

- Upgrade aiohttp requirement to version 0.20.0+

0.6.2 (2015-11-22)
------------------

- Make app_key parameter from render_string coroutine optional

0.6.0 (2015-10-29)
------------------

- Fix a bug in middleware (missed coroutine decorator) #16

- Drop Python 3.3 support (switched to aiohttp version v0.18.0)

- Simplify context processors initialization by adding parameter to `setup()`

0.5.0 (2015-07-09)
------------------

- Introduce context processors #14

- Bypass StreamResponse #15

0.4.3 (2015-06-01)
------------------

- Fix distribution building: add manifest file

0.4.2 (2015-05-21)
------------------

- Make HTTPInternalServerError exceptions more verbose on console
  output

0.4.1 (2015-04-05)
------------------

- Documentation update

0.4.0 (2015-04-02)
------------------

- Add `render_string` method

0.3.1 (2015-04-01)
------------------

- Don't allow non-mapping context

- Fix tiny documentation issues

- Change the library logo

0.3.0 (2015-03-15)
------------------

- Documentation release

0.2.1 (2015-02-15)
------------------

- Fix `render_template` function

0.2.0 (2015-02-05)
------------------

- Migrate to aiohttp 0.14

- Add `status` parameter to template decorator

- Drop optional `response` parameter

0.1.0 (2015-01-08)
------------------

- Initial release

