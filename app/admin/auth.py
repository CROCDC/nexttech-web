import hmac

from flask import Response, current_app, request


def _unauthorized():
    return Response(
        'Acceso restringido.', 401,
        {'WWW-Authenticate': 'Basic realm="Next Tech Admin"'},
    )


def enforce_admin_auth():
    """Blueprint before_request guard: HTTP Basic Auth via ADMIN_USER / ADMIN_PASSWORD.

    Returns None to let the request through, or a Response to block it. With no
    ADMIN_PASSWORD configured the panel stays closed (503) instead of being
    silently public. Credentials use compare_digest to avoid length/timing leaks.
    """
    expected_user = current_app.config.get('ADMIN_USER') or ''
    expected_password = current_app.config.get('ADMIN_PASSWORD')
    if not expected_password:
        return Response('Admin deshabilitado: falta configurar ADMIN_PASSWORD.', 503)

    auth = request.authorization
    if not auth or not auth.username or auth.password is None:
        return _unauthorized()

    user_ok = hmac.compare_digest(auth.username, expected_user)
    password_ok = hmac.compare_digest(auth.password, expected_password)
    if not (user_ok and password_ok):
        return _unauthorized()

    return None
