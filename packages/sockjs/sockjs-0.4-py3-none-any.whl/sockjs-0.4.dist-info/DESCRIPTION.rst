SockJS server based on Asyncio (PEP 3156)
=========================================

.. image :: https://secure.travis-ci.org/aio-libs/sockjs.png
  :target:  https://secure.travis-ci.org/aio-libs/sockjs

`aiosockjs` is a `SockJS <http://sockjs.org>`_ server
based on `aiohttp <https://github.com/KeepSafe/aiohttp/>`_ 
`PEP 3156 <http://www.python.org/dev/peps/pep-3156/>`_ asyncio module.

`aiosockjs` is a `SockJS <http://sockjs.org>`_ integration for 
`aiohttp <https://github.com/KeepSafe/aiohttp/>`_.  SockJS interface is implemented as a 
`aiohttp route. Its possible to create any number of different sockjs routes, ie 
`/sockjs/*` or `/mycustom-sockjs/*`. You can provide different session implementation 
and management for each sockjs route.

Simple aiohttp web server is required::

   [server:main]
   use = egg:gunicorn#main
   host = 0.0.0.0
   port = 8080
   worker = aiohttp.worker.GunicornWebWorker


Example of sockjs route::

   def main(global_settings, **settings):
       app = web.Application(loop=loop)
       app.router.add_route('GET', '/', index)
       sockjs.add_endpoint(app, prefix='/sockjs', handler=chatSession)

       handler = app.make_handler()
       srv = loop.run_until_complete(
           loop.create_server(handler, '127.0.0.1', 8080))
       print("Server started at http://127.0.0.1:8080")
       try:
           loop.run_forever()
        except KeyboardInterrupt:
           srv.close()
           loop.run_until_complete(handler.finish_connections())


Client side code::

  <script src="//cdn.jsdelivr.net/sockjs/0.3.4/sockjs.min.js"></script>
  <script>
      var sock = new SockJS('http://localhost:8080/sockjs');

      sock.onopen = function() {
        console.log('open');
      };

      sock.onmessage = function(obj) {
        console.log(obj);
      };

      sock.onclose = function() {
        console.log('close');
      };
  </script>


Installation
------------

1. Install virtualenv::

    $ wget https://raw.github.com/pypa/virtualenv/master/virtualenv.py
    $ python3.4 ./virtualenv.py --no-site-packages sockjs

3. Clone aiosockjs from github and then install::

    $ git clone https://github.com/aio-libs/sockjs.git
    $ cd sockjs
    $ ../sockjs/bin/python setup.py develop

To run chat example use following command::

    $ ./sockjs/bin/python ./aiosockjs/examples/chat.py


Supported transports
--------------------

* websocket `hybi-10 <http://tools.ietf.org/html/draft-ietf-hybi-thewebsocketprotocol-10>`_
* `xhr-streaming <https://secure.wikimedia.org/wikipedia/en/wiki/XMLHttpRequest#Cross-domain_requests>`_
* `xhr-polling <https://secure.wikimedia.org/wikipedia/en/wiki/XMLHttpRequest#Cross-domain_requests>`_
* `iframe-xhr-polling <https://developer.mozilla.org/en/DOM/window.postMessage>`_
* iframe-eventsource (`EventSource <http://dev.w3.org/html5/eventsource/>`_ used from an 
  `iframe via postMessage <https://developer.mozilla.org/en/DOM/window.postMessage>`_)
* iframe-htmlfile (`HtmlFile <http://cometdaily.com/2007/11/18/ie-activexhtmlfile-transport-part-ii/>`_
  used from an `iframe via postMessage <https://developer.mozilla.org/en/DOM/window.postMessage>`_.)
* `jsonp-polling <https://secure.wikimedia.org/wikipedia/en/wiki/JSONP>`_


Not supported transports
------------------------
  * websocket `hixie-76 <http://tools.ietf.org/html/draft-hixie-thewebsocketprotocol-76>`_


Requirements
------------

- Python 3.4

- gunicorn 19.2.0

- aiohttp https://github.com/KeepSafe/aiohttp


Examples
--------

You can find several `examples` in the aiosockjs repository at github.

https://github.com/aio-libs/sockjs/tree/master/examples


License
-------

aiosockjs is offered under the Apache 2 license.

=======
CHANGES
=======

0.4 (02/03/2016)
----------------

- Fixed lost event-loop argument in `sockjs.transports.websocket.WebSocketTransport`
- Fixed lost event-loop argument in `sockjs.transports.rawwebsocket.RawWebSocketTransport`
- Fixed RawRequestMessage. Add raw_header argument (aiohttp 0.21+)
- Fixed many warnings
- Fixed `sockjs.route` add_endpoint without name bug

0.3 (08/07/2015)
----------------

- Fixed calls of ``SessionManager.aquire()`` - was removed the unnecessary second argument.
- Fixed the incorrect argument in one call of ``cors_headers()``.
- Fixed many errors. The code is not perfect, but at least it was working as it should.

0.2 (07/07/2015)
----------------

- Fixed packaging

0.1.0 (06/21/2015)
------------------

- Initial release

