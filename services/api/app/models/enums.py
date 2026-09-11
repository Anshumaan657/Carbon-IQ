from enum import Enum


class UserRole(str, Enum):
    BUYER = "buyer"
    CURATOR = "curator"
    ADMIN = "admin"


class ProjectCategory(str, Enum):
    AVOIDANCE = "avoidance"
    REDUCTION = "reduction"
    REMOVAL = "removal"
    MIXED = "mixed"


class ProjectStatus(str, Enum):
    DRAFT = "draft"
    ACTIVE = "active"
    INACTIVE = "inactive"
    COMPLETED = "completed"
    UNKNOWN = "unknown"


class VerificationStatus(str, Enum):
    VERIFIED = "verified"
    VALIDATION_PENDING = "validation_pending"
    VERIFICATION_PENDING = "verification_pending"
    UNVERIFIED = "unverified"
    UNKNOWN = "unknown"


class RiskTolerance(str, Enum):
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"


class RiskSeverity(str, Enum):
    INFO = "info"
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"


class DocumentStatus(str, Enum):
    PENDING = "pending"
    PROCESSING = "processing"
    READY = "ready"
    FAILED = "failed"


class PortfolioStatus(str, Enum):
    DRAFT = "draft"
    SAVED = "saved"
    ORDERED = "ordered"


class OrderStatus(str, Enum):
    SIMULATED = "simulated"
    CANCELLED = "cancelled"
