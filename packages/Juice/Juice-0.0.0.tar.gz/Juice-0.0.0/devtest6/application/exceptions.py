
from toucan import exceptions

class ApplicationError(exceptions.HTTPException):
    code = 500
    description = "Something happens"

class DBError(exceptions.HTTPException):
    code = 500
    description = "IDK What happenes"

