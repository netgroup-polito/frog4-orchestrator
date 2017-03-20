class UserNotFound(Exception):
    def __init__(self, message):
        self.message = message
        # Call the base class constructor with the parameters it needs
        super(UserNotFound, self).__init__(message)
        
    def get_mess(self):
        return self.message


class TenantNotFound(Exception):
    def __init__(self, message):
        self.message = message
        # Call the base class constructor with the parameters it needs
        super(TenantNotFound, self).__init__(message)
        
    def get_mess(self):
        return self.message    


class UserLocationNotFound(Exception):
    def __init__(self, message):
        self.message = message
        # Call the base class constructor with the parameters it needs
        super(UserLocationNotFound, self).__init__(message)
        
    def get_mess(self):
        return self.message
    

class DeletionTimeout(Exception):
    def __init__(self, message):
        self.message = message
        # Call the base class constructor with the parameters it needs
        super(DeletionTimeout, self).__init__(message)
        
    def get_mess(self):
        return self.message
    

class NoUserNodeDefined(Exception):
    def __init__(self, message):
        self.message = message
        # Call the base class constructor with the parameters it needs
        super(NoUserNodeDefined, self).__init__(message)
        
    def get_mess(self):
        return self.message


class EndpointConnectionError(Exception):
    def __init__(self, message):
        self.message = message
        # Call the base class constructor with the parameters it needs
        super(EndpointConnectionError, self).__init__(message)
        
    def get_mess(self):
        return self.message


class NodeNotFound(Exception):
    def __init__(self, message):
        # Call the base class constructor with the parameters it needs
        super(NodeNotFound, self).__init__(message)

        self.message = message
        
    def get_mess(self):
        return self.message


class DomainNotFound(Exception):
    def __init__(self, message):
        # Call the base class constructor with the parameters it needs
        super(DomainNotFound, self).__init__(message)

        self.message = message
        
    def get_mess(self):
        return self.message    


class ControllerNotFound(Exception):
    def __init__(self, message):
        # Call the base class constructor with the parameters it needs
        super(ControllerNotFound, self).__init__(message)

        self.message = message
        
    def get_mess(self):
        return self.message


class StackError(Exception):
    def __init__(self, message):
        self.message = message
        # Call the base class constructor with the parameters it needs
        super(StackError, self).__init__(message)
        
    def get_mess(self):
        return self.message


class ResourceAlreadyExistsOnNode(Exception):
    def __init__(self, message):
        self.message = message
        # Call the base class constructor with the parameters it needs
        super(ResourceAlreadyExistsOnNode, self).__init__(message)
        
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


class NoHeatPortTranslationFound(Exception):
    def __init__(self, message):
        self.message = message
        # Call the base class constructor with the parameters it needs
        super(NoHeatPortTranslationFound, self).__init__(message)
        
    def get_mess(self):
        return self.message


class NoMacAddress(Exception):
    def __init__(self, message):
        self.message = message
        # Call the base class constructor with the parameters it needs
        super(NoMacAddress, self).__init__(message)
        
    def get_mess(self):
        return self.message


class NoPreviousDeviceFound(Exception):
    def __init__(self, message):
        self.message = message
        # Call the base class constructor with the parameters it needs
        super(NoPreviousDeviceFound, self).__init__(message)
        
    def get_mess(self):
        return self.message


class InfoNotFound(Exception): 
    def __init__(self, message):
        self.message = message
        # Call the base class constructor with the parameters it needs
        super(InfoNotFound, self).__init__(message)
        
    def get_mess(self):
        return self.message   


class sessionNotFound(Exception):
    def __init__(self, message):
        self.message = message
        # Call the base class constructor with the parameters it needs
        super(sessionNotFound, self).__init__(message)
        
    def get_mess(self):
        return self.message


class ingoingFlowruleMissing(Exception):
    def __init__(self, message):
        self.message = message
        # Call the base class constructor with the parameters it needs
        super(ingoingFlowruleMissing, self).__init__(message)
    
    def get_mess(self):
        return self.message


class maximumNumberOfVNFInGraph(Exception):
    def __init__(self, message):
        self.message = message
        # Call the base class constructor with the parameters it needs
        super(maximumNumberOfVNFInGraph, self).__init__(message)
    
    def get_mess(self):
        return self.message


class wrongRequest(Exception):
    def __init__(self, message):
        self.message = message
        # Call the base class constructor with the parameters it needs
        super(wrongRequest, self).__init__(message)
    
    def get_mess(self):
        return self.message


class unauthorizedRequest(Exception):
    def __init__(self, message):
        self.message = message
        # Call the base class constructor with the parameters it needs
        super(unauthorizedRequest, self).__init__(message)
    
    def get_mess(self):
        return self.message


class wrongConnectionBetweenEndpoints(Exception):
    def __init__(self, message):
        self.message = message
        # Call the base class constructor with the parameters it needs
        super(wrongConnectionBetweenEndpoints, self).__init__(message)
    
    def get_mess(self):
        return self.message


class WrongNumberOfPorts(Exception):
    def __init__(self, message):
        self.message = message
        # Call the base class constructor with the parameters it needs
        super(WrongNumberOfPorts, self).__init__(message)
    
    def get_mess(self):
        return self.message


class WrongPortID(Exception):
    def __init__(self, message):
        self.message = message
        # Call the base class constructor with the parameters it needs
        super(WrongPortID, self).__init__(message)
    
    def get_mess(self):
        return self.message


class PortLabelNotFound(Exception):
    def __init__(self, message):
        self.message = message
        # Call the base class constructor with the parameters it needs
        super(PortLabelNotFound, self).__init__(message)
    
    def get_mess(self):
        return self.message


class Wrong_ISP_Graph(Exception):
    def __init__(self, message):
        self.message = message
        # Call the base class constructor with the parameters it needs
        super(Wrong_ISP_Graph, self).__init__(message)
    
    def get_mess(self):
        return self.message


class GraphError(Exception):
    def __init__(self, message):
        self.message = message
        # Call the base class constructor with the parameters it needs
        super(GraphError, self).__init__(message)
    
    def get_mess(self):
        return self.message


class GraphNotFound(Exception):
    def __init__(self, message):
        self.message = message
        # Call the base class constructor with the parameters it needs
        super(GraphNotFound, self).__init__(message)
    
    def get_mess(self):
        return self.message


class PortNotFound(Exception):
    def __init__(self, message):
        self.message = message
        # Call the base class constructor with the parameters it needs
        super(PortNotFound, self).__init__(message)
    
    def get_mess(self):
        return self.message


class EndpointNotFound(Exception):
    def __init__(self, message):
        self.message = message
        # Call the base class constructor with the parameters it needs
        super(EndpointNotFound, self).__init__(message)
    
    def get_mess(self):
        return self.message


class ConnectionsError(Exception):
    def __init__(self, message):
        self.message = message
        # Call the base class constructor with the parameters it needs
        super(ConnectionsError, self).__init__(message)
    
    def get_mess(self):
        return self.message


class VNFRepositoryError(Exception):
    def __init__(self, message):
        self.message = message
        # Call the base class constructor with the parameters it needs
        super(VNFRepositoryError, self).__init__(message)

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

class TenantNotFound(Exception):
    def __init__(self, message):
        self.message = message
        # Call the base class constructor with the parameters it needs
        super(TenantNotFound, self).__init__(message)
        
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
