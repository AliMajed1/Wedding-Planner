""" Reservation API wrapper

This class implements a simple wrapper around the reservation API. It
provides automatic retries for server-side errors, delays to prevent
server overloading, and produces sensible exceptions for the different
types of client-side error that can be encountered.
"""

# This file contains areas that need to be filled in with your own
# implementation code. They are marked with "Your code goes here".
# Comments are included to provide hints about what you should do.

import requests
import simplejson
import warnings
import time
import sys

from exceptions import (
    BadRequestError, InvalidTokenError, BadSlotError, NotProcessedError,
    SlotUnavailableError,ReservationLimitError, UnexpectedError, RetriesExhaustedError)

class ReservationApi:
    def __init__(self, base_url: str, token: str, retries: int, delay: float):
        """ Create a new ReservationApi to communicate with a reservation
        server.

        Args:
            base_url: The URL of the reservation API to communicate with.
            token: The user's API token obtained from the control panel.
            retries: The maximum number of attempts to make for each request.
            delay: A delay to apply to each request to prevent server overload.
        """
        self.base_url = base_url
        self.token    = token
        self.retries  = retries
        self.delay    = delay


    # NOTE: I kept getting an error when trying to use this method from "reason = json['message']" which I didn't know how to deal with.
    # So I decided leaving it and using requests. commands separately. 
    def _reason(self, req: requests.Response) -> str:
        """Obtain the reason associated with a response"""
        reason = ''

        # Try to get the JSON content, if possible, as that may contain a
        # more useful message than the status line reason
     
        try:
            json = req.json()
            reason = json['message']

        # A problem occurred while parsing the body - possibly no message
        # in the body (which can happen if the API really does 500,
        # rather than generating a "fake" 500), so fall back on the HTTP
        # status line reason
        except simplejson.errors.JSONDecodeError:
            if isinstance(req.reason, bytes):
                try:
                    reason = req.reason.decode('utf-8')
                except UnicodeDecodeError:
                    reason = req.reason.decode('iso-8859-1')
            else:
                reason = req.reason

        return reason


    def _headers(self) -> dict:
        """Create the authorization token header needed for API requests"""
        auth =  {'Authorization': 'Bearer ' + self.token}
        return auth




    def _send_request(self, method: str, endpoint: str) -> dict:
        """Send a request to the reservation API and convert errors to
           appropriate exceptions"""
        # Your code goes here
        headers = self._headers()
        url = self.base_url + endpoint
        num_retries = self.retries + 1
        # Allow for multiple retries if needed
        for i in range(num_retries):
            # Perform the request.
            if (method == "GET"):
                response = requests.get(url, headers = headers)
            elif(method == "DELETE"):
                response = requests.delete(url, headers = headers)
            elif(method == "POST"):
                response = requests.post(url, headers = headers)

            # Delay before processing the response to avoid swamping server.
            # This way whenever a new request or a retry is happening...there will always be 1 second delay.
            time.sleep(self.delay)

            # 200 response indicates all is well - send back the json data.
            if (response.status_code == 200):
                return response.json()

            # 5xx responses indicate a server-side error, show a warning
            # (including the try number).
            elif (response.status_code > 499 and response.status_code < 510):
                if (response.status_code == 500):
                    print("Error (500) : Internal Server Error")

                elif (response.status_code == 501):
                    print("Error (501) : Not Implemented")

                elif (response.status_code == 502):
                    print("Error (502) : Bad Gateway")

                elif (response.status_code == 503):
                    print("Error (503) : Service Unavailable")

                elif (response.status_code == 504):
                    print("Error (504) : Gateway Timeout")

                #The only error with a number between 500 and 510 we haven't listed yet is this.    
                else:
                    print("Error (505) : 505 HTTP Version Not Supported")


            # 400 errors are client problems that are meaningful, so convert
            # them to separate exceptions that can be caught and handled by
            # the caller.
            elif(response.status_code == 400):
                raise BadRequestError
            elif(response.status_code == 401):
                raise InvalidTokenError
            elif(response.status_code == 403):
                raise BadSlotError
            elif(response.status_code == 404):
                raise NotProcessedError
            elif(response.status_code == 409):
                raise SlotUnavailableError
            elif(response.status_code == 451):
                raise ReservationLimitError
            # Anything else is unexpected and may need to kill the client.
            else:
                raise UnexpectedError
                sys.exit()
        # Get here and retries have been exhausted, throw an appropriate
        # exception.
        raise RetriesExhaustedError
    def get_slots_available(self):
        """Obtain the list of slots currently available in the system"""
        return self._send_request("GET", "/available")

    def get_slots_held(self):
        """Obtain the list of slots currently held by the client"""
        return self._send_request("GET", "")

    def release_slot(self, slot_id):
        """Release a slot currently held by the client"""
        return self._send_request("DELETE", "/" + str(slot_id))

    def reserve_slot(self, slot_id):
        """Attempt to reserve a slot for the client"""
        return self._send_request("POST", "/" + str(slot_id))