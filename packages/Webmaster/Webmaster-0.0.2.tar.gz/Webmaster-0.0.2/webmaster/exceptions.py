from sqlalchemy.exc import SQLAlchemyError, OperationalError
from werkzeug.exceptions import HTTPException

# Generic Errors
class ApplicationError(Exception): pass
class ModelError(ApplicationError): pass
class UserError(ApplicationError): pass

#-------------------------------------------------------------------------------
# Abort Specific Error

class MailerMisconfiguredError(HTTPException):
    code = 500
    description = "MAILER is not configured properly"


class MailerMisconfiguredMissingContactEmailError(HTTPException):
    code = 500
    description = "MAILER missing contact email"


class SQLAlchemyError(OperationalError, HTTPException):
    code = 500
    description = "DB Error"

