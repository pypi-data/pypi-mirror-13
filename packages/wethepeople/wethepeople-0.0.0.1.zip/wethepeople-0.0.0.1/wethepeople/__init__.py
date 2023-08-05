try:
    from objects import (Petition, Metadata,
                         ResponseInfo, RequestInfo,
                         ResultSet, PetitionResponse,
                         Signature, SignatureResponse)
    import url
    from core import RequestObject
except ImportError:
    from . import url
    from .core import RequestObject
    from .objects import (Petition, Metadata,
                          ResponseInfo, RequestInfo,
                          ResultSet, PetitionResponse,
                          Signature, SignatureResponse)


class Api(object):

    def __init__(self, apikey=None, apiversion="1"):
        """Creates Api Instance"""

        self.r = RequestObject()
        self.version = apiversion
        self.apikey = apikey

    @property
    def apiendpoint(self):
        return url.Url(
            "https://api.whitehouse.gov/v{v}".format(v=self.version)
        )

    def _gen_metadata(self, rjson):
        metadata = Metadata(
            ResponseInfo()._populate(self, **
                                     rjson["metadata"]
                                     .get("responseInfo", dict())),
            RequestInfo()._populate(self, **
                                    rjson["metadata"]
                                    .get("requestInfo", dict())),
            ResultSet()._populate(self, **
                                  rjson["metadata"]
                                  .get("resultset", dict())),
        )
        return metadata

    def get(self, pages=None, query=None):
        pages = pages if pages else list()
        query = query if query else dict()

        url = self.apiendpoint.page(*pages).query(**query)
        return self.r.get(str(url))

    def signature_handler(self, response):
        """
        Takes Petitions responses and creates the
        Petition Object
        """
        rjson = response.json()
        metadata = self._gen_metadata(rjson)
        generatedlist = list()
        for petition in rjson["results"]:
            generatedlist.append(Signature()._populate(self, **petition))
        return SignatureResponse(metadata, generatedlist, self)

    def petition_handler(self, response):
        """
        Takes Petitions responses and creates the
        Petition Object
        """
        rjson = response.json()
        metadata = self._gen_metadata(rjson)
        generatedlist = list()
        for petition in rjson["results"]:
            generatedlist.append(Petition()._populate(self, **petition))
        return PetitionResponse(metadata, generatedlist, self)

    def get_petitions(self, **kwargs):
        response = self.get(pages=["petitions.json"], query=kwargs)
        return self.petition_handler(response)

    def get_petition(self, id):
        response = self.get(
            pages=["petitions", str(id)+".json"], query=dict())
        return self.petition_handle(response)

    def get_signatures(self, petition_id, **kwargs):
        response = self.get(
            pages=["petitions", str(petition_id), "signatures.json"], query=kwargs)
        return self.signature_handler(response)
