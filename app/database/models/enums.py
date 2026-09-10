from enum import StrEnum


class RequestStatus(StrEnum):
    NEW = "NEW"
    IN_PROGRESS = "IN_PROGRESS"
    CONTACTED = "CONTACTED"
    CALCULATING = "CALCULATING"
    APPROVED = "APPROVED"
    REJECTED = "REJECTED"
    COMPLETED = "COMPLETED"


class UserRole(StrEnum):
    CLIENT = "CLIENT"
    MANAGER = "MANAGER"
    ADMIN = "ADMIN"
