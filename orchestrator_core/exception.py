class UserNotFound(Exception):
    def __init__(self, message):
        self.message = message
        # Call the base class constructor with the parameters it needs
        super(UserNotFound, self).__init__(message)
        
    def get_mess(self):
        return self.message


class DomainNotFound(Exception):
    def __init__(self, message):
        # Call the base class constructor with the parameters it needs
        super(DomainNotFound, self).__init__(message)

        self.message = message
        
    def get_mess(self):
        return self.message


class WrongConfigurationFile(Exception):
    def __init__(self, message):
        self.message = message
        # Call the base class constructor with the parameters it needs
        super(WrongConfigurationFile, self).__init__(message)
        
    def get_mess(self):
        return self.message


class LoginError(Exception):
    def __init__(self, message):
        self.message = message
        # Call the base class constructor with the parameters it needs
        super(LoginError, self).__init__(message)
        
    def get_mess(self):
        return self.message    


class SessionNotFound(Exception):
    def __init__(self, message):
        self.message = message
        # Call the base class constructor with the parameters it needs
        super(SessionNotFound, self).__init__(message)
        
    def get_mess(self):
        return self.message


class WrongRequest(Exception):
    def __init__(self, message):
        self.message = message
        # Call the base class constructor with the parameters it needs
        super(WrongRequest, self).__init__(message)
    
    def get_mess(self):
        return self.message


class UnauthorizedRequest(Exception):
    def __init__(self, message):
        self.message = message
        # Call the base class constructor with the parameters it needs
        super(UnauthorizedRequest, self).__init__(message)
    
    def get_mess(self):
        return self.message


class WrongNumberOfPorts(Exception):
    def __init__(self, message):
        self.message = message
        # Call the base class constructor with the parameters it needs
        super(WrongNumberOfPorts, self).__init__(message)
    
    def get_mess(self):
        return self.message


class GraphError(Exception):
    def __init__(self, message):
        self.message = message
        # Call the base class constructor with the parameters it needs
        super(GraphError, self).__init__(message)
    
    def get_mess(self):
        return self.message


class NoFunctionalCapabilityFound(Exception):
    def __init__(self, message):
        self.message = message
        # Call the base class constructor with the parameters it needs
        super(NoFunctionalCapabilityFound, self).__init__(message)

    def get_mess(self):
        return self.message


class FunctionalCapabilityAlreadyInUse(Exception):
    def __init__(self, message):
        self.message = message
        # Call the base class constructor with the parameters it needs
        super(FunctionalCapabilityAlreadyInUse, self).__init__(message)

    def get_mess(self):
        return self.message


class IncoherentDomainInformation(Exception):
    def __init__(self, message):
        self.message = message
        # Call the base class constructor with the parameters it needs
        super(IncoherentDomainInformation, self).__init__(message)

    def get_mess(self):
        return self.message


class FeasibleDomainNotFoundForNFFGElement(Exception):
    def __init__(self, message):
        self.message = message
        # Call the base class constructor with the parameters it needs
        super(FeasibleDomainNotFoundForNFFGElement, self).__init__(message)

    def get_mess(self):
        return self.message


class FeasibleSolutionNotFoundForNFFG(Exception):
    def __init__(self, message):
        self.message = message
        # Call the base class constructor with the parameters it needs
        super(FeasibleSolutionNotFoundForNFFG, self).__init__(message)

    def get_mess(self):
        return self.message


class PathNotFeasible(Exception):
    def __init__(self, message):
        self.message = message
        # Call the base class constructor with the parameters it needs
        super(PathNotFeasible, self).__init__(message)

    def get_mess(self):
        return self.message


class UnsupportedLabelingMethod(Exception):
    def __init__(self, message):
        self.message = message
        # Call the base class constructor with the parameters it needs
        super(UnsupportedLabelingMethod, self).__init__(message)

    def get_mess(self):
        return self.message


class UserValidationError(Exception):
    def __init__(self, message):
        self.message = message
        # Call the base class constructor with the parameters it needs
        super(UserValidationError, self).__init__(message)

    def get_mess(self):
        return self.message


class TokenNotFound(Exception):
    def __init__(self, message):
        self.message = message
        # Call the base class constructor with the parameters it needs
        super(TokenNotFound, self).__init__(message)

    def get_mess(self):
        return self.message


class NoGraphFound(Exception):
    def __init__(self, message):
        self.message = message
        # Call the base class constructor with the parameters it needs
        super(NoGraphFound, self).__init__(message)

    def get_mess(self):
        return self.message


class UserTokenExpired(Exception):
    def __init__(self, message):
        self.message = message
        # Call the base class constructor with the parameters it needs
        super(UserTokenExpired, self).__init__(message)
