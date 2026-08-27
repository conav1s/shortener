class LinkError(Exception):
    """Base 'links' app exception"""


class InvalidURLError(LinkError):
    pass


class CodeGenerationError(LinkError):
    pass


class LinkNotFoundError(LinkError):
    pass


class LinkExpiredError(LinkError):
    pass
