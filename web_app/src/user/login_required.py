"""
Wrapper that ensures user authentication logging,
providing access to the application's content and functionality.
"""

from flask import session, redirect
from functools import wraps

BASE = "/diploma/fertilizer_recommendation"


def login_required(f):
    """
    Function that checks whether the user is logged in; if yes, grants access to the function,
    otherwise redirects to the login page.
    """

    @wraps(f)
    def decorated_function(*args, **kwargs):
        if not session.get("user_id"):
            return redirect(BASE + "/login")
        return f(*args, **kwargs)

    return decorated_function
