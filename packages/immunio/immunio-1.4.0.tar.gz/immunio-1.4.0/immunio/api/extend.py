from __future__ import (
    absolute_import,
    division,
    print_function,
    unicode_literals,
)


from immunio.singleton import run_hook


def custom_threat(threat_name, message, metadata=None):
    """
    Inform Immunio of custom threat for your app.
    """
    if not (isinstance(threat_name, str) or isinstance(threat_name, unicode)):
        raise ValueError(
            "`threat_name` must be str or unicode, not %r" % threat_name)

    if not (isinstance(message, str) or isinstance(message, unicode)):
        raise ValueError(
            "`message` must be str or unicode, not %r" % message)

    if metadata is None:
        metadata = {}

    if not isinstance(metadata, dict):
        raise ValueError("`metadata` must be a dict, not %r" % metadata)

    return run_hook("custom_threat", {
        "threat_name": threat_name,
        "message": message,
        "display_meta": metadata,
    })
