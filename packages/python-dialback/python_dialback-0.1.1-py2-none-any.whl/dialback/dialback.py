# This file is part of python-dialback.
#
# python-dialback is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# python-dialback is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with python-dialback.  If not, see <http://www.gnu.org/licenses/>.

import os
import requests
import datetime
import locale

from six.moves.urllib import parse

from .exceptions import DialbackValidationError

CONTENT_TYPE_FORM_URLENCODED = "application/x-www-url-encoded"

class DialbackRequest(object):

    def __init__(self, headers, body=None):
        self.headers = headers
        self.body = body

        # Transform the headers to be case insensative - section 4.2 of HTTP 1.1
        # states they are, we don't want any mixups.
        self.headers = dict(((k.lower(), v) for k, v in self.headers.items()))

        # If there is a body parse and extract it.
        if self.body is not None:
            # decode the body.
            self.body = parse.parse_qs(self.body)

    def validate_headers(self):
        # Check the content type exists (section 4 specifies they MUST)
        if "content-type" not in self.headers:
            raise DialbackValidationError(
                error="Must specify a Content-Type",
                section=4
            )

        # Check the content type is correct
        if self.headers["content-type"] != CONTENT_TYPE_FORM_URLENCODED:
            err = "Must have the Content-type " + CONTENT_TYPE_FORM_URLENCODED
            raise DialbackValidationError(
                error=err,
                section=4
            )

        return True

    def validate_body(self):
        # Check "host" or "webfinger" exists (one must be provided - section 4)
        if not ("host" in self.body or "webfinger" in self.body):
            raise DialbackValidationError(
                error='MUST include exactly one of "host" or "webfinger"',
                section=4
            )

        # Should check both aren't listed (again in section 4.0)
        if "host" in self.body and "webfinger" in self.body:
            raise DialbackValidationError(
                error='MUST include exactly one of "host" or "webfinger"',
                section=4
            )

        # Lets extract this as ID for the generic name
        self.id = self.body.get("host", self.body["webfinger"])[0]

        # It must have the URL
        if "url" not in self.body:
            raise DialbackValidationError(
                error='MUST include the "url" parameter',
                section=4
            )
        self.url = self.body["url"][0]

        # It must have a token
        if "token" not in self.body:
            raise DialbackValidationError(
                error='MUST include the "token" parameter',
                section=4
            )
        self.token = self.body["token"][0]

        # Extract the date
        if "date" not in self.body:
            raise DialbackValidationError(
                error='Must have the HTTP "Date" header',
                section=4
            )

        return True

class DialbackEndpoint(object):
    """ Dialback authentication endpoint

    This provides a mechanism to validate a dialback request that is send to the
    dialback endpoint. This endpoint must response with either a HTTP 200 or 204
    for a valid request or 4xx or 5xx for an invalid request.

    You should subclass this and override `validate_unique` and `validate_token`
    and proivde code to validate those things, check the method specific docs
    for help defining those.

    Once you have subclassed this you should instantiate it and provide it with
    a dialback request to validate, this request should be an instance of
    DialbackRequest.

    Example:

    >>> dialback_endpoint = MyDialbackEndpoint()
    >>> dialback_request = DialbackRequest(
        headers=request.headers,
        body=request.body
    )
    >>> if dialback_endpoint.validate_request(dialback_request):
            return Response(status_code=200)
        else:
            return Response(status_code=401)
    """

    def __init__(self, date_boundry=300):
        self.date_boundry = datetime.timedelta(seconds=date_boundry)

    def validate_token(self, token):
        """ Takes in the token used and verifies it's valid

        This should verify that the token used is indeed a valid token. The
        dialback requester should ensure this token reaches you through some
        mechanism pre-defined between you and the client. You then are expected
        to verify that this token is correct. Return True if it is in fact
        correct and False if it isn't.
        """
        raise NotImplementedError("Need to implement this yourself")

    def validate_unique(self, id, url, token, date):
        """ Take in a tuple and verify it's unique (i.e. not been seen before)

        This takes in these arguments:

        id: The host or webfinger
        url: The URL the original request was made to
        token: The token provided in the original Authorization header
        date: The Date header on the original request

        The server must verify that it has not seen these four values together
        ergo they are a unique tuple. You should return True if it validates
        correctly and False if the tuple is not unique.
        """
        raise NotImplementedError("Need to implement this yourself")

    def validate_date(self, date):
        """ Takes in the date and checks it's in the specified window

        This takes the date as a python datetime object and validates that it's
        within the specified window. This defaults to 5 minutes (the time
        specified in the specification in 5.1 and 5.2). The method will return
        True if the request is within that time and raise
        DialbackValidationError if not.
        """
        now = datetime.datetime.now()
        future_limit = now + self.date_boundry
        past_limit = now - self.date_boundry

        # Check that it's within the window in the future
        if date > future_limit:
            raise DialbackValidationError(
                error="Date specified is past the accepted date window",
                section=(5.1, 5.2)
            )

        # Check that it's within the window for the past
        if date < past_limit:
            raise DialbackValidationError(
                error="Date specified is before the accepted date window",
                section=(5.1, 5.2)
            )

        # Looks like it's valid
        return True

    def validate_request(self, request):
        """ Validates that the request is valid """
        if not isinstance(request, DialbackRequest):
            raise DialbackExcpetion("Must be a DialbackRequest instance")


class DialbackAuth(requests.auth.AuthBase):
    """ Authorization client for python's request library.

    This provides an easy to use client that can be used with the request
    library used in python. It will generate the authorization header, to use
    this you must also provide the dialback authorization endpoint that the
    server will call back to to verify this request.

    To use this you should instantiate the DialbackAuth class with the webfinger
    or host, but not both or neither. You then should get the token to the HTTP
    authorization server where it can verify the token is indeed a valid token.
    You then just pass this in the "auth" parameter to the request function.

    Example:

    >>> dialback_auth = DialbackAuth(webfinger="tsyesika@io.tsyesika.se")
    >>> # Save the dialback.token somewhere accessable to auth server.
    >>> response = requests.post(
        "https://io.tsyesika.se/api/client/register",
        auth=dialback_auth,
        json=json_payload
    )
    >>>

    This would then return with either a 200 OK to tell me the request was
    successful or 4xx for confirmation failure or 5xx for a server failure.
    It would be prudent to check the status code and handling the error if one
    exists.

    NB: It is important to note that tokens must be cryptographically generated
        this process occurs using the `random_token` method on instantiation to
        store the token in the `token` attribute. You should not change this
        token without good reason and understanding of consiquence. The token
        also should not be reused.
    """

    def __init__(self, webfinger=None, host=None):
        self.webfinger = webfinger
        self.host = host
        self.token = self.random_token()

        if (webfinger and host) or (not (webfinger or host)):
            raise DialbackValidationError(
                error='MUST include exactly one of "host" or "webfinger"',
                section=4
            )

    def __call__(self, request):
        """ Adds dialback authorization to python's request library request """
        # Create the headers
        headers = {
            "Authorization": "Dialback ",
            "Content-Type": CONTENT_TYPE_FORM_URLENCODED
        }
        headers.update(request.headers)
        parameters = {}

        # Add the webfinger or host
        if self.webfinger:
            parameters["webfinger"] = '"{0}"'.format(self.webfinger)
        elif self.host:
            parameters["host"] = '"{0}"'.format(self.host)

        # Add a cryptographic token
        parameters["token"] = '"{0}"'.format(self.token)

        # Convert the header to the key=value, ... format
        headers["Authorization"] += self.dialback_encode(parameters)

        # Add the current date
        headers["Date"] = self.http_datetime()

        # Return constructed Authorization header
        request.prepare_headers(headers)
        return request

    def dialback_encode(self, dictionary):
        """ Takes a dictionary and encodes it to www-form like encoded form

        This takes in a dictionary which it will then encode to a string that
        is formatted as "key=value" where it is seperated by a ", ". This is
        used in the Authentication header of the dialback authentication
        protocol.
        """
        return ", ".join(["{0}={1}".format(k, v) for k,v in dictionary.items()])

    def random_token(self, length=8):
        """ Produces a cryptographically secure random base64 encoded string """
        return os.urandom(length).encode("base64")[:-2]

    def http_datetime(self):
        """ Produces a HTTP timestamp formatted as RFC7231

        This will return a string value for the current representation of the
        date in accordance with what is defined in HTTP Semantics and
        Content[RFC7231]. This sets the local as en_US as python by default will
        produce the datetime with host machine's locale's translation.

        [RFC7231] https://tools.ietf.org/html/rfc7231
        """
        # Get the current time in UTC
        now = datetime.datetime.utcnow()

        # Set the local the en_US which HTTP headers expect it in.
        locale.setlocale(locale.LC_TIME, 'en_US')

        return now.strftime('%a, %d %b %Y %H:%M:%S UTC')
