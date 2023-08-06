import base64
import binascii
import json
import time

from pyramid import httpexceptions
from pyramid.security import forget
from six import text_type

from cliquet.errors import http_error, ERRORS, send_alert
from cliquet import utils
from syncclient.client import SyncClient, TokenserverClient

from syncto import (AUTHORIZATION_HEADER, CLIENT_STATE_HEADER,
                    CLIENT_STATE_LENGTH)
from syncto.crypto import encrypt, decrypt


def build_sync_client(request):
    # Get the BID assertion
    is_authorization_defined = AUTHORIZATION_HEADER in request.headers
    starts_with_browser_id = False
    if is_authorization_defined:
        authorization = request.headers[AUTHORIZATION_HEADER].lower()
        starts_with_browser_id = authorization.startswith("browserid ")

    if not is_authorization_defined or not starts_with_browser_id:
        msg = "Provide a BID assertion %s header." % AUTHORIZATION_HEADER
        response = http_error(httpexceptions.HTTPUnauthorized(),
                              errno=ERRORS.MISSING_AUTH_TOKEN,
                              message=msg)
        response.headers.extend(forget(request))
        raise response

    bucket_id = request.matchdict['bucket_id']
    is_client_state_header_defined = CLIENT_STATE_HEADER in request.headers

    if bucket_id == 'syncto':
        if not is_client_state_header_defined:
            msg = "Provide the tokenserver %s header." % CLIENT_STATE_HEADER
            response = http_error(httpexceptions.HTTPUnauthorized(),
                                  errno=ERRORS.MISSING_AUTH_TOKEN,
                                  message=msg)
            response.headers.extend(forget(request))
            raise response
        client_state = request.headers[CLIENT_STATE_HEADER]
    elif len(bucket_id) != CLIENT_STATE_LENGTH:
        msg = "The provided bucket ID is incorrect."
        response = http_error(httpexceptions.HTTPUnauthorized(),
                              errno=ERRORS.MISSING_AUTH_TOKEN,
                              message=msg)
        response.headers.extend(forget(request))
        raise response
    else:
        client_state = bucket_id

    if is_client_state_header_defined:
        send_alert(request,
                   "%s header is deprecated and should not be "
                   "provided anymore." % CLIENT_STATE_HEADER)

    authorization_header = request.headers[AUTHORIZATION_HEADER]
    bid_assertion = authorization_header.split(" ", 1)[1]

    settings = request.registry.settings
    cache = request.registry.cache
    statsd = request.registry.statsd
    token_server_url = settings['token_server_url']

    hmac_secret = settings['cache_hmac_secret']
    cache_key = 'credentials_%s' % utils.hmac_digest(hmac_secret,
                                                     bid_assertion)
    ca_bundle = settings['certificate_ca_bundle']

    encrypted_credentials = cache.get(cache_key)

    if not encrypted_credentials:
        settings_ttl = int(settings['cache_credentials_ttl_seconds'])
        bid_ttl = _extract_bid_assertion_ttl(bid_assertion)
        ttl = min(settings_ttl, bid_ttl or settings_ttl)

        tokenserver = TokenserverClient(bid_assertion, client_state,
                                        token_server_url, verify=ca_bundle)
        if statsd:
            statsd.watch_execution_time(tokenserver, prefix="tokenserver")
        credentials = tokenserver.get_hawk_credentials(duration=ttl)
        encrypted = encrypt(json.dumps(credentials), client_state, hmac_secret)
        cache.set(cache_key, encrypted, ttl)
    else:
        credentials = json.loads(
            decrypt(encrypted_credentials, client_state, hmac_secret))

    if statsd:
        timer = statsd.timer("syncclient.start_time")
        timer.start()

    sync_client = SyncClient(verify=ca_bundle, **credentials)

    if statsd:
        timer.stop()
        statsd.watch_execution_time(sync_client, prefix="syncclient")

    return sync_client


def base64url_decode(value):
    """Pad base64 value with == and decode from base64 using URL-safe
    alphabet substitutions.
    """
    if isinstance(value, text_type):
        value = value.encode('utf-8')
    rem = len(value) % 4
    if rem > 0:
        value += b'=' * (4 - rem)
    try:
        return base64.urlsafe_b64decode(value).decode('utf-8')
    except (binascii.Error, TypeError) as e:
        raise ValueError(str(e))


def _extract_bid_assertion_ttl(bid_assertion):
    """A BrowserID assertion is a list of base64 blocks separated with ``.``.
    Return the smallest ttl from the JSON block that contain an expiration
    timestamp.
    """
    ttl = None
    for fragment in bid_assertion.split('.'):
        try:
            decoded_fragment = base64url_decode(fragment)
            payload = json.loads(decoded_fragment)
        except ValueError:
            payload = {}
        if 'exp' in payload:
            exp = (payload['exp'] / 1000) - time.time()  # UTC
            ttl = min(exp, ttl or exp)
    return ttl
