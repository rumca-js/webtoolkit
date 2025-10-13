"""
"""

HTTP_STATUS_UNKNOWN = 0
HTTP_STATUS_OK = 200
HTTP_STATUS_USER_AGENT = 403
HTTP_STATUS_TOO_MANY_REQUESTS = 429
HTTP_STATUS_SSL_CERTIFICATE_ERROR = 495

# standard HTTP status codes are up to 600
# we define our own internal error types

HTTP_STATUS_CODE_EXCEPTION = 600
HTTP_STATUS_CODE_CONNECTION_ERROR = 603
HTTP_STATUS_CODE_TIMEOUT = 604
HTTP_STATUS_CODE_FILE_TOO_BIG = 612
HTTP_STATUS_CODE_PAGE_UNSUPPORTED = 613
HTTP_STATUS_CODE_SERVER_ERROR = 614
HTTP_STATUS_CODE_SERVER_TOO_MANY_REQUESTS = 615 # this server too many requests


def status_code_to_text(status_code):
    if not status_code:
        return "UNKNOWN(0)"

    if status_code == 200:
        return "HTTP_STATUS_OK(200)"
    elif status_code == 401:
        return "HTTP_STATUS_UNAUTHORIZED(401)"
    elif status_code == 403:
        return "HTTP_STATUS_USER_AGENT(403)"
    elif status_code == 404:
        return "HTTP_STATUS_NOT_FOUND(404)"
    elif status_code == 406:
        return "HTTP_STATUS_NOT_ACCEPTABLE(406)"
    elif status_code == 409:
        return "HTTP_STATUS_CONFLICT(409)"
    elif status_code == 410:
        return "HTTP_STATUS_GONE(410)"
    elif status_code == 418:
        return "HTTP_STATUS_IM_A_TEAPOT(418)"
    elif status_code == 429:
        return "HTTP_STATUS_TOO_MANY_REQUESTS(419)"
    elif status_code == 451:
        return "HTTP_STATUS_UNAVAILABLE_LEGAL_REASONS(451)"
    elif status_code == 500:
        return "HTTP_STATUS_INTERNAL_SERVER(500)"
    elif status_code == 501:
        return "HTTP_STATUS_NOT_IMPLEMENTED(501)"
    elif status_code == 502:
        return "HTTP_STATUS_BAD_GATEWAY(502)"
    elif status_code == 503:
        return "HTTP_STATUS_SERVICE_UNAVAILABLE(503)"
    elif status_code == 521:
        return "HTTP_STATUS_WEB_SERVER_IS_DOWN(521)"
    elif status_code == 600:
        return "HTTP_STATUS_CODE_EXCEPTION(600)"
    elif status_code == 603:
        return "HTTP_STATUS_CODE_CONNECTION_ERROR(603)"
    elif status_code == 604:
        return "HTTP_STATUS_CODE_TIMEOUT(604)"
    elif status_code == 612:
        return "HTTP_STATUS_CODE_FILE_TOO_BIG(612)"
    elif status_code == 613:
        return "HTTP_STATUS_CODE_PAGE_UNSUPPORTED(613)"
    elif status_code == 614:
        return "HTTP_STATUS_CODE_SERVER_ERROR(614)"
    elif status_code == 615:
        return "HTTP_STATUS_CODE_SERVER_TOO_MANY_REQUESTS(615)"
    else:
        return str(status_code)
