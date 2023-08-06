from __future__ import (
    absolute_import,
    division,
    print_function,
    unicode_literals,
)

from immunio.logger import log
from immunio.patcher import monkeypatch


# Set name so plugin can be enabled and disabled.
NAME = "flask"


def add_hooks(run_hook, get_agent_func=None, timer=None):
    """
    Add our hooks into the flask library functions.
    """
    try:
        import flask
    except ImportError:
        return None

    # Install a hook to capture newly created wsgi apps and wrap them.
    hook_flask_app(run_hook, get_agent_func, timer)

    # Install a hook to capture the route name (use the url pattern)
    hook_flask_request_context(run_hook, timer)

    meta = {
        "version": flask.__version__,
    }

    return meta


def hook_flask_app(run_hook, get_agent_func, timer):
    """
    Wrap the `Flask()` __init__ function so we can wrap each WSGI
    app as it is produced. This also creates the Agent if it hasn't been
    created yet.
    """
    try:
        import flask
    except ImportError:
        return

    # If we don't have a `get_agent_func()` defined the app will be
    # wrapped elsewhere.
    if not get_agent_func:
        return

    # For new-style classes, special methods like __call__ are looked up
    # on the class directly, not the instance. This means it can't be
    # overridden normally. Instead, we have to override it on the class
    # to get it to check an instance method to allow us to override it
    # from the __init__ monkeypatch below.
    def immunio_call(self, *args, **kwargs):
        """
        Simply duplicate the behaviour of the original __call__ and proxy
        everything to the internal `wsgi_app` method. This stub will be
        wrapped by the Agent during the `__init__` monkeypatch below.
        """
        return self.wsgi_app(*args, **kwargs)
    flask.Flask._immunio_call = immunio_call

    @monkeypatch(flask.Flask, "__call__", timer=timer,
                 report_name="plugin.flask.app.__call__")
    def _call(orig, flask_self, *args, **kwargs):
        """
        We patch __call__ here because it is impossible to patch it on a
        per-instance basis. This mokeypatch on the class simply proxies
        through the stub `_immunio_call` defined above. Since the
        `_immunio_call` method is "normal", it can be overridden on the
        Flask instance during the __init__ monkeypatch below.
        """
        log.debug("Call to patched __call__(%(args)s, %(kwargs)s)", {
            "args": args,
            "kwargs": kwargs,
        })
        # Always call the immunio_call stub defined above. Since the stub
        # is not a special method, it can be overridden on the instance below.
        return flask_self._immunio_call(*args, **kwargs)


    @monkeypatch(flask.Flask, "__init__", timer=timer,
                 report_name="plugin.flask.app.__init__")
    def _flask_init(orig, flask_self, *args, **kwargs):
        """
        Here we patch the `__call__` method (via the _immunio_call stub) of
        every new Flask app. This ensures that when the app object is used
        as a WSGI callable, we already have it wrapped.
        """
        log.debug("Call to patched __init__(%(args)s, %(kwargs)s)", {
            "args": args,
            "kwargs": kwargs,
        })
        # Get the WSGI app (__init__ always returns None)
        orig(flask_self, *args, **kwargs)

        # Get or create the Immunio Agent singleton
        agent = get_agent_func()

        # Wrap the Flask app __call__ method (via _immunio_call) with Immunio.
        flask_self._immunio_call = agent.wrap_wsgi_app(flask_self._immunio_call)


def hook_flask_request_context(run_hook, timer=None):
    try:
        import flask
    except ImportError:
        return

    @monkeypatch(flask.Flask, "request_context", timer=timer,
                 report_name="plugin.flask.app.request_context")
    def _flask_request_context(orig, flask_self, *args, **kwargs):
        log.debug("Call to patched request_context"
                  "(%(args)s, %(kwargs)s)", {
            "args": args,
            "kwargs": kwargs,
        })

        request_context = orig(flask_self, *args, **kwargs)
        if request_context.request.routing_exception is None:
            # Rule a string URL path with placeholders in
            # the format ``<converter(arguments):name>`
            rule = request_context.request.url_rule.rule
            run_hook("framework_view", {
                "view_name": rule
            })
        return request_context

