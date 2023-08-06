"""Postcodepy API ProxyView classes."""

from django.views.generic import View

from django.conf import settings
import postcodepy

USER_SETTINGS = getattr(settings, "POSTCODEPY", None)


class PostcodepyProxyView(View):
    """PostcodeProxyView - base View class to render a postcode API response.

    derive your own View from this class to render postcode API responses.
    """

    def get(self, request, postcode=None, houseNumber=None,
            houseNumberAddition=None):
        """get - fetch 'adres-info' by 'postcode/huisnummer'.

        Parameters
        ----------
        request : request
            the django request object

        postcode : str
            postcode formatted as 4 digits 2 characters (no space), ex: 7514BP

        houseNumber : int
            housenumber without additions

        houseNumberAddition : str (optional)
            the housenumber addition as a string. Mostly one character
            (7514BP,129,A), but also numerical additions may apply
            (8651AP,1,41).
        """
        access_key = USER_SETTINGS['AUTH']['API_ACCESS_KEY']
        access_secret = USER_SETTINGS['AUTH']['API_ACCESS_SECRET']
        api = postcodepy.API(environment='live',
                             access_key=access_key,
                             access_secret=access_secret)

        pcat = (postcode, houseNumber)
        if houseNumberAddition:
            pcat = pcat + (houseNumberAddition,)

        retValue = api.get_postcodedata(*pcat)
        return retValue


class SignalProxyView(View):
    """SignalProxyView - base View class to render a signal API response.

    derive your own View from this class to render signal API responses.
    """

    def get(self, request, sar):
        """get - fetch 'signal-info' based on specified set of parameters.

        Parameters
        ----------
        sar : dict
            the signal-api-request (sar), being a dictionary of parameters
            relevant for the request. Since all parameters are optional,
            please take a look at the API documentation:
            https://api.postcode.nl/documentation
        """
        access_key = USER_SETTINGS['AUTH']['API_ACCESS_KEY']
        access_secret = USER_SETTINGS['AUTH']['API_ACCESS_SECRET']
        api = postcodepy.API(environment='live',
                             access_key=access_key,
                             access_secret=access_secret)

        retValue = api.get_signalcheck(sar)
        return retValue
