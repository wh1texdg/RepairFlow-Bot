class RepairFlowError(Exception):
    """Base application error."""


class NotFoundError(RepairFlowError):
    pass


class AccessDeniedError(RepairFlowError):
    pass


class InvalidStatusTransitionError(RepairFlowError):
    pass


class ExternalServiceError(RepairFlowError):
    pass
