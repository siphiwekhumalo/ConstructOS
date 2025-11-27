"""
Domain Event Schemas for inter-service communication.

All microservices publish events to a shared message broker (Redis Streams/Kafka)
for asynchronous communication and eventual consistency.
"""
import json
import uuid
from datetime import datetime
from dataclasses import dataclass, field, asdict
from typing import Optional, Dict, Any


@dataclass
class DomainEvent:
    """Base class for all domain events."""
    event_id: str = field(default_factory=lambda: str(uuid.uuid4()))
    event_type: str = ""
    source_service: str = ""
    timestamp: str = field(default_factory=lambda: datetime.utcnow().isoformat())
    payload: Dict[str, Any] = field(default_factory=dict)
    correlation_id: Optional[str] = None
    
    def to_json(self) -> str:
        return json.dumps(asdict(self))
    
    @classmethod
    def from_json(cls, json_str: str) -> "DomainEvent":
        data = json.loads(json_str)
        return cls(**data)


@dataclass
class AccountCreatedEvent(DomainEvent):
    event_type: str = "account.created"
    source_service: str = "identity"


@dataclass
class AccountUpdatedEvent(DomainEvent):
    event_type: str = "account.updated"
    source_service: str = "identity"


@dataclass
class ContactCreatedEvent(DomainEvent):
    event_type: str = "contact.created"
    source_service: str = "identity"


@dataclass
class LeadConvertedEvent(DomainEvent):
    event_type: str = "lead.converted"
    source_service: str = "sales"


@dataclass
class OpportunityWonEvent(DomainEvent):
    event_type: str = "opportunity.won"
    source_service: str = "sales"


@dataclass
class InvoiceCreatedEvent(DomainEvent):
    event_type: str = "invoice.created"
    source_service: str = "finance"


@dataclass
class PaymentReceivedEvent(DomainEvent):
    event_type: str = "payment.received"
    source_service: str = "finance"


@dataclass
class ProjectCreatedEvent(DomainEvent):
    event_type: str = "project.created"
    source_service: str = "project"


@dataclass
class ProjectStatusChangedEvent(DomainEvent):
    event_type: str = "project.status_changed"
    source_service: str = "project"


@dataclass
class EmployeeCreatedEvent(DomainEvent):
    event_type: str = "employee.created"
    source_service: str = "hr"


@dataclass
class TicketCreatedEvent(DomainEvent):
    event_type: str = "ticket.created"
    source_service: str = "compliance"


@dataclass
class InspectionCompletedEvent(DomainEvent):
    event_type: str = "inspection.completed"
    source_service: str = "compliance"


@dataclass
class StockLevelChangedEvent(DomainEvent):
    event_type: str = "stock.level_changed"
    source_service: str = "inventory"


@dataclass
class DocumentUploadedEvent(DomainEvent):
    event_type: str = "document.uploaded"
    source_service: str = "document"


EVENT_TYPES = {
    "account.created": AccountCreatedEvent,
    "account.updated": AccountUpdatedEvent,
    "contact.created": ContactCreatedEvent,
    "lead.converted": LeadConvertedEvent,
    "opportunity.won": OpportunityWonEvent,
    "invoice.created": InvoiceCreatedEvent,
    "payment.received": PaymentReceivedEvent,
    "project.created": ProjectCreatedEvent,
    "project.status_changed": ProjectStatusChangedEvent,
    "employee.created": EmployeeCreatedEvent,
    "ticket.created": TicketCreatedEvent,
    "inspection.completed": InspectionCompletedEvent,
    "stock.level_changed": StockLevelChangedEvent,
    "document.uploaded": DocumentUploadedEvent,
}


def parse_event(json_str: str) -> DomainEvent:
    """Parse a JSON string into the appropriate event type."""
    data = json.loads(json_str)
    event_type = data.get("event_type", "")
    event_class = EVENT_TYPES.get(event_type, DomainEvent)
    return event_class(**data)
