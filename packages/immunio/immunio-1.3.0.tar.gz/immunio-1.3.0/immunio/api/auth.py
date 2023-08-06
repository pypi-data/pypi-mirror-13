from __future__ import (
    absolute_import,
    division,
    print_function,
    unicode_literals,
)


from immunio.singleton import run_hook


def _parse_auth_args(user_id, username, email, other_meta=None):
    """
    Helper function to take the provided user_id, username, and email
    and create the required meta dict.
    """
    if other_meta is None:
        other_meta = {}
    if user_id is not None:
        user_id = str(user_id)
    other_meta["user_id"] = user_id or username or email
    other_meta["username"] = username or email or user_id
    other_meta["email"] = email
    return other_meta


def set_current_user(user_id=None, username=None, email=None):
    """
    Inform Immunio of the current user for the current request. This function
    should be called for every request made to the App.

    The `user_id` should be a unique un-changing reference for the user.
    Typically this should be a database primary key. If no id is available
    you can use the username as a user_id.


    """
    return run_hook("framework_user",
                    _parse_auth_args(user_id, username, email))


def login_success(user_id=None, username=None, email=None):
    """
    Inform Immunio of a successful login.  This function should be called
    during the request which actually logs in an existing user.
    """
    return run_hook("framework_login",
                    _parse_auth_args(user_id, username, email))


def login_failure(user_id=None, username=None, email=None, reason=None):
    """
    Inform Immunio of a failed login attempt.
    """
    return run_hook("authenticate", {
        "is_valid": False,
        "username": _parse_auth_args(user_id, username, email)["username"],
        "reason": reason,
    })


def password_reset_request_accepted(user_id=None, username=None, email=None):
    """
    Inform Immunio of a request to reset a user's password that was
    accepted by your system. Call this if someone requests a password reset
    and your system found a matching account and initiated the reset.
    """
    return run_hook(
        "framework_password_reset",
        _parse_auth_args(user_id, username, email, {"is_valid": True}))


def password_reset_request_failed(search_value):
    """
    Inform Immunio of a request to reset a user's password that did not
    match a known account.
    """
    return run_hook("framework_password_reset", {
        "is_valid": False,
        "search_value": search_value,
    })


def account_created(user_id=None, username=None, email=None):
    """
    Inform Immunio of a newly created account.
    """
    return run_hook("framework_account_created",
                    _parse_auth_args(user_id, username, email))
