from rest_framework.views import exception_handler


def custom_exception_handler(exc, context):
    response = exception_handler(exc, context)

    if response is None:
        return None

    error_map = {
        400: ('validation_error', 'Invalid input.'),
        401: ('authentication_required', 'Authentication credentials were not provided or are invalid.'),
        403: ('permission_denied', 'You do not have permission to perform this action.'),
        404: ('not_found', 'The requested resource was not found.'),
        405: ('method_not_allowed', 'Method not allowed.'),
        429: ('rate_limit_exceeded', 'Too many requests. Please try again later.'),
    }

    error_code, message = error_map.get(response.status_code, ('server_error', 'An unexpected error occurred.'))

    payload = {'success': False, 'error': error_code, 'message': message}

    if response.status_code == 400:
        payload['details'] = response.data

    response.data = payload
    return response
