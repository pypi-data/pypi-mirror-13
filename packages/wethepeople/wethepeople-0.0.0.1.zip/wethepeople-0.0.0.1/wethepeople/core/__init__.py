from requests import Session
from . import exceptions


def ErrorProbe(response):
    """
    Probes the Response for errors
    """
    responsejson = response.json()["metadata"]["responseInfo"]
    if responsejson.get("status") is 400 or responsejson.get("status") is 404:
        # Yes, 400 is 404 for some reason
        # 404 In case they fix it
        raise exceptions.PetitionNotFound(
            "Error {errorCode}\nMessage: {message}".format(
                errorCode=responsejson.get("errorCode"),
                message=responsejson.get("developerMessage")
            ))
    if responsejson.get("status") is 599:
        raise exceptions.InternalServerError(
            "Error {errorCode}\nMessage: {message}".format(
                errorCode=responsejson.get("errorCode"),
                message=responsejson.get("developerMessage")
            ))


class SessionWrapper(object):

    """
    This Class Wraps around Request.Session
    """

    def __init__(self):
        self.session = Session()

    def get(self, url):
        return self.session.get(url, verify=True)

    def post(self):
        raise NotImplementedError


class RequestObject(object):

    """
    This class wraps around SessionWrapper
    """

    def __init__(self):
        self.session = SessionWrapper()

    def get(self, url):
        response = self.session.get(url)
        ErrorProbe(response)
        return response

    def post(self, url):
        raise NotImplementedError
