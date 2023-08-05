class WTPBaseException(Exception):
    pass

class PetitionNotFound(WTPBaseException):
    pass

class InternalServerError(WTPBaseException):
    pass