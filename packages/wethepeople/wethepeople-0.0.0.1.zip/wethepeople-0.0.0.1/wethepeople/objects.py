class WTPBaseObject(object):
    pass


class WTPResultObject(WTPBaseObject):

    def _populate(self, instance, **kwargs):
        self.api_instance = instance

        for args in kwargs.items():
            setattr(self, args[0], args[1])
        return self


class APIResponse(WTPBaseObject):

    """
    This the response object()
    """

    def __init__(self, metadata, results, apiinstance):
        self._metadata = metadata
        self._results = results
        self.instance = apiinstance

    @property
    def metadata(self):
        return self._metadata

    @property
    def results(self):
        return self._results


class SignatureResponse(APIResponse):

    def _id_generator(self):
        for signature in self.results:
            yield signature.id

    @property
    def ids(self):
        """
        Get the list of signature ids
        """
        return list(self._id_generator())


class PetitionResponse(APIResponse):

    def _id_generator(self):
        for petition in self.results:
            yield petition.id

    @property
    def ids(self):
        """
        Get the list of Petition ids
        """
        return list(self._id_generator())


class Metadata(WTPResultObject):

    def __init__(self, responseinfo, requestinfo, resultset):
        self.responseinfo = responseinfo
        self.requestinfo = requestinfo
        self.resultset = resultset


class ResponseInfo(WTPResultObject):
    pass


class RequestInfo(WTPResultObject):
    pass


class ResultSet(WTPResultObject):
    pass


class Petition(WTPResultObject):

    def __repr__(self):
        return "<petition:{id}>".format(id=self.id)

    def search_signatures(self, **kwargs):
        return self.api_instance.get_signatures(self.id, **kwargs)

    @property
    def signatures(self):
        return self.search_signatures().results


class Signature(WTPResultObject):

    def __repr__(self):
        return "<signatureFor:petition:{id}>".format(id=self.petitionId)

    @property
    def petition(self):
        return self.api_instance.get_petition(self.petitionId)
