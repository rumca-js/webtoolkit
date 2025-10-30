"""
"""

# fmt: off

HTTP_STATUS_UNKNOWN = 0

# 2xx Success
HTTP_STATUS_OK = 200
HTTP_STATUS_CREATED = 201                       # Resource created
HTTP_STATUS_ACCEPTED = 202                      # Request accepted, processing pending
HTTP_STATUS_NO_CONTENT = 204                    # No content to return

# 3xx Redirection
HTTP_STATUS_MOVED_PERMANENTLY = 301             # Resource moved permanently
HTTP_STATUS_FOUND = 302                         # Resource found (temporary redirect)
HTTP_STATUS_NOT_MODIFIED = 304                  # Resource not modified

# 4xx Client Errors
HTTP_STATUS_BAD_REQUEST = 400                   # Bad request syntax or invalid data
HTTP_STATUS_UNAUTHORIZED = 401                  # Authentication required
HTTP_STATUS_USER_AGENT = 403
HTTP_STATUS_NOT_FOUND = 404                     # Resource not found
HTTP_STATUS_METHOD_NOT_ALLOWED = 405            # Method not allowed on resource
HTTP_STATUS_TOO_MANY_REQUESTS = 429
HTTP_STATUS_SSL_CERTIFICATE_ERROR = 495

# 5xx Server Errors
HTTP_STATUS_INTERNAL_SERVER_ERROR = 500         # Generic server error
HTTP_STATUS_NOT_IMPLEMENTED = 501               # Not implemented on server
HTTP_STATUS_BAD_GATEWAY = 502                   # Invalid response from upstream server
HTTP_STATUS_SERVICE_UNAVAILABLE = 503           # Server temporarily overloaded or down
HTTP_STATUS_GATEWAY_TIMEOUT = 504               # Upstream server timeout

# Non-standard / NGINX-specific (unofficial)
HTTP_STATUS_SSL_HANDSHAKE_FAILED = 496          # SSL Handshake Failed (NGINX)
HTTP_STATUS_CLIENT_CLOSED_REQUEST = 499         # Client closed request before server response (NGINX)

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
    status_texts = {
        0: "HTTP_STATUS_UNKNOWN(0)",

        200: "HTTP_STATUS_OK(200)",
        201: "HTTP_STATUS_CREATED(201)",
        202: "HTTP_STATUS_ACCEPTED(202)",
        204: "HTTP_STATUS_NO_CONTENT(204)",

        301: "HTTP_STATUS_MOVED_PERMANENTLY(301)",
        302: "HTTP_STATUS_FOUND(302)",
        304: "HTTP_STATUS_NOT_MODIFIED(304)",

        400: "HTTP_STATUS_BAD_REQUEST(400)",
        401: "HTTP_STATUS_UNAUTHORIZED(401)",
        403: "HTTP_STATUS_USER_AGENT(403)",
        404: "HTTP_STATUS_NOT_FOUND(404)",
        405: "HTTP_STATUS_METHOD_NOT_ALLOWED(405)",
        429: "HTTP_STATUS_TOO_MANY_REQUESTS(429)",

        495: "HTTP_STATUS_SSL_CERTIFICATE_ERROR(495)",   # Non-standard
        496: "HTTP_STATUS_SSL_HANDSHAKE_FAILED(496)",    # Non-standard
        499: "HTTP_STATUS_CLIENT_CLOSED_REQUEST(499)",   # Non-standard

        500: "HTTP_STATUS_INTERNAL_SERVER_ERROR(500)",
        501: "HTTP_STATUS_NOT_IMPLEMENTED(501)",
        502: "HTTP_STATUS_BAD_GATEWAY(502)",
        503: "HTTP_STATUS_SERVICE_UNAVAILABLE(503)",
        504: "HTTP_STATUS_GATEWAY_TIMEOUT(504)",

        # non-standard
        600: "HTTP_STATUS_CODE_EXCEPTION(600)",
        603: "HTTP_STATUS_CODE_CONNECTION_ERROR(603)",
        604: "HTTP_STATUS_CODE_TIMEOUT(604)",
        612: "HTTP_STATUS_CODE_FILE_TOO_BIG(612)",
        613: "HTTP_STATUS_CODE_PAGE_UNSUPPORTED(613)",
        614: "HTTP_STATUS_CODE_SERVER_ERROR(614)",
        615: "HTTP_STATUS_CODE_SERVER_TOO_MANY_REQUESTS(615)",
    }

    return status_texts.get(status_code, f"STATUS_CODE({status_code})")
# fmt: on


def is_status_code_valid(status_code):
    if status_code is None:
        return False

    return status_code >= 200 and status_code < 400


def is_status_code_invalid(status_code):
    """
    This function informs that status code is so bad, that further communication does not make any sense
    """
    if status_code is None:
        return True

    if status_code == HTTP_STATUS_UNKNOWN:
        # we do not know status of page yet
        return False

    if status_code == HTTP_STATUS_USER_AGENT:
        # if current agent is rejected, does not mean page (source) is invalid
        return False

    if status_code == HTTP_STATUS_TOO_MANY_REQUESTS:
        # too many requests - we don't know what the page is
        return False

    if status_code == HTTP_STATUS_CODE_SERVER_ERROR:
        # server error - we don't know what the page is
        return False

    if status_code == HTTP_STATUS_CODE_SERVER_TOO_MANY_REQUESTS:
        # too many requests - we don't know what the page is
        return False

    if status_code < 200:
        return True

    if status_code >= 400:
        return True


def is_status_code_uncertain(status_code):
    """
    Uncertain in a way that we do not know if page is valid, invalid.
    Maybe it is valid with other use agent, etc.
    """
    if status_code == HTTP_STATUS_USER_AGENT:
        return True

    if status_code == HTTP_STATUS_CODE_SERVER_ERROR:
        # server error might be on one crawler, but does not have to be in another
        return True

    if status_code == HTTP_STATUS_CODE_EXCEPTION:
        # server error might be on one crawler, but does not have to be in another
        return True

    if status_code == HTTP_STATUS_TOO_MANY_REQUESTS:
        return True

    if status_code == HTTP_STATUS_CODE_SERVER_TOO_MANY_REQUESTS:
        return True

    return False
