from . import constants


class PICUException(Exception):
    pass

class IllegalArgument(PICUException):
    pass

class PropertyNotFound(PICUException):
    pass


class IDNAException(PICUException, UnicodeError):
    ERROR_MESSAGES = dict((getattr(constants, e), e) for e in dir(constants) if e.startswith('UIDNA_ERROR_'))

    def __init__(self, idna_errors, msgprefix, *args):
        self.idna_errors = idna_errors

        # parse IDNA error codes
        err_labels = []
        for ecode, elabel in self.ERROR_MESSAGES.iteritems():
            if (idna_errors & ecode):
                err_labels.append(elabel)
                idna_errors = idna_errors & ~ecode
        if idna_errors:
            err_labels.append("UNKNOWN_ERROR-%s" % idna_errors)

        super(IDNAException, self).__init__("%s%s" % (msgprefix, ', '.join(err_labels)), *args)

