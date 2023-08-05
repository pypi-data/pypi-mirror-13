import base64
import datetime
import time
import urllib

from google.appengine.api import app_identity

import storage

GOOGLE_ACCESS_ID = app_identity.get_service_account_name()


def sign_url(resource, expires):
    method = 'GET'
    content_md5, content_type = None, None

    expiration = datetime.datetime.utcnow() + \
                 datetime.timedelta(seconds=expires)
    expiration = int(time.mktime(expiration.timetuple()))

    # Generate the string to sign.
    signature_string = '\n'.join([
        method,
        content_md5 or '',
        content_type or '',
        str(expiration),
        resource])

    _, signature_bytes = app_identity.sign_blob(signature_string)
    signature = base64.b64encode(signature_bytes)

    # Set the right query parameters.
    query_params = {'GoogleAccessId': GOOGLE_ACCESS_ID,
                    'Expires': str(expiration),
                    'Signature': signature}

    # Return the download URL.
    return '{endpoint}{resource}?{querystring}'.format(
            endpoint=storage.API_ACCESS_ENDPOINT, resource=resource,
            querystring=urllib.urlencode(query_params))
