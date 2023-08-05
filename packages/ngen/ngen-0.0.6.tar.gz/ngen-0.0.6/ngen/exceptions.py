

class Error(Exception):
    "General error class for inheritance purposes"
    pass


class ParserError(Error):
    pass


class FieldError(ParserError, TypeError):
    pass


class ValidationError(Error):
    pass


class ImproperlyConfigured(Error):
    pass
