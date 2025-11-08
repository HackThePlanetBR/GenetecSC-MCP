"""Pydantic models for input validation in Genetec MCP server."""

from enum import Enum
from typing import Optional, List
from pydantic import BaseModel, Field, field_validator, ConfigDict


class ResponseFormat(str, Enum):
    """Output format for tool responses."""
    MARKDOWN = "markdown"
    JSON = "json"


# =====================================================
# Entity Management Models
# =====================================================

class SearchEntitiesInput(BaseModel):
    """Input model for searching entities."""

    model_config = ConfigDict(
        str_strip_whitespace=True,
        validate_assignment=True,
        extra='forbid'
    )

    entity_type: str = Field(
        ...,
        description=(
            "Type of entity to search for. Common types: 'Cardholder', 'Door', 'Camera', "
            "'Area', 'User', 'Credential', 'AccessRule', 'Schedule', 'Alarm', 'Visitor'"
        ),
        min_length=1,
        max_length=50
    )
    search_query: Optional[str] = Field(
        default=None,
        description="Optional search text to filter entities by name (partial match supported)",
        max_length=200
    )
    limit: int = Field(
        default=20,
        ge=1,
        le=100,
        description="Maximum number of results to return (1-100)"
    )
    offset: int = Field(
        default=0,
        ge=0,
        description="Number of results to skip for pagination"
    )
    response_format: ResponseFormat = Field(
        default=ResponseFormat.MARKDOWN,
        description="Output format: 'markdown' for human-readable or 'json' for machine-readable"
    )


class GetEntityInput(BaseModel):
    """Input model for getting entity details."""

    model_config = ConfigDict(
        str_strip_whitespace=True,
        validate_assignment=True,
        extra='forbid'
    )

    entity_guid: str = Field(
        ...,
        description=(
            "GUID of the entity to retrieve. "
            "Format: 'xxxxxxxx-xxxx-xxxx-xxxx-xxxxxxxxxxxx' (e.g., 'a1b2c3d4-e5f6-7890-abcd-ef1234567890')"
        ),
        min_length=36,
        max_length=36,
        pattern=r'^[0-9a-fA-F]{8}-[0-9a-fA-F]{4}-[0-9a-fA-F]{4}-[0-9a-fA-F]{4}-[0-9a-fA-F]{12}$'
    )
    response_format: ResponseFormat = Field(
        default=ResponseFormat.MARKDOWN,
        description="Output format: 'markdown' or 'json'"
    )


class ListCardholdersInput(BaseModel):
    """Input model for listing cardholders."""

    model_config = ConfigDict(
        str_strip_whitespace=True,
        validate_assignment=True,
        extra='forbid'
    )

    name_filter: Optional[str] = Field(
        default=None,
        description="Filter by cardholder name (partial match, case-insensitive)",
        max_length=200
    )
    status_filter: Optional[str] = Field(
        default=None,
        description="Filter by status: 'Active', 'Inactive', or None for all",
        pattern=r'^(Active|Inactive)?$'
    )
    limit: int = Field(
        default=20,
        ge=1,
        le=100,
        description="Maximum results to return"
    )
    offset: int = Field(
        default=0,
        ge=0,
        description="Pagination offset"
    )
    response_format: ResponseFormat = Field(
        default=ResponseFormat.MARKDOWN,
        description="Output format"
    )


class GetCardholderInput(BaseModel):
    """Input model for getting cardholder details."""

    model_config = ConfigDict(
        str_strip_whitespace=True,
        validate_assignment=True,
        extra='forbid'
    )

    cardholder_guid: str = Field(
        ...,
        description="GUID of the cardholder",
        min_length=36,
        max_length=36,
        pattern=r'^[0-9a-fA-F]{8}-[0-9a-fA-F]{4}-[0-9a-fA-F]{4}-[0-9a-fA-F]{4}-[0-9a-fA-F]{12}$'
    )
    include_credentials: bool = Field(
        default=True,
        description="Include credential information in the response"
    )
    include_access_rules: bool = Field(
        default=True,
        description="Include access rule information in the response"
    )
    response_format: ResponseFormat = Field(
        default=ResponseFormat.MARKDOWN,
        description="Output format"
    )


class ListDoorsInput(BaseModel):
    """Input model for listing doors."""

    model_config = ConfigDict(
        str_strip_whitespace=True,
        validate_assignment=True,
        extra='forbid'
    )

    name_filter: Optional[str] = Field(
        default=None,
        description="Filter by door name (partial match)",
        max_length=200
    )
    area_filter: Optional[str] = Field(
        default=None,
        description="Filter by area/zone name",
        max_length=200
    )
    limit: int = Field(
        default=20,
        ge=1,
        le=100,
        description="Maximum results"
    )
    offset: int = Field(
        default=0,
        ge=0,
        description="Pagination offset"
    )
    response_format: ResponseFormat = Field(
        default=ResponseFormat.MARKDOWN,
        description="Output format"
    )


class ListCamerasInput(BaseModel):
    """Input model for listing cameras."""

    model_config = ConfigDict(
        str_strip_whitespace=True,
        validate_assignment=True,
        extra='forbid'
    )

    name_filter: Optional[str] = Field(
        default=None,
        description="Filter by camera name (partial match)",
        max_length=200
    )
    area_filter: Optional[str] = Field(
        default=None,
        description="Filter by area/zone name",
        max_length=200
    )
    status_filter: Optional[str] = Field(
        default=None,
        description="Filter by status: 'Online', 'Offline', 'Recording'",
        pattern=r'^(Online|Offline|Recording)?$'
    )
    limit: int = Field(
        default=20,
        ge=1,
        le=100,
        description="Maximum results"
    )
    offset: int = Field(
        default=0,
        ge=0,
        description="Pagination offset"
    )
    response_format: ResponseFormat = Field(
        default=ResponseFormat.MARKDOWN,
        description="Output format"
    )


# =====================================================
# Access Control Models
# =====================================================

class GrantDoorAccessInput(BaseModel):
    """Input model for granting temporary door access."""

    model_config = ConfigDict(
        str_strip_whitespace=True,
        validate_assignment=True,
        extra='forbid'
    )

    door_guid: str = Field(
        ...,
        description="GUID of the door to grant access to",
        min_length=36,
        max_length=36,
        pattern=r'^[0-9a-fA-F]{8}-[0-9a-fA-F]{4}-[0-9a-fA-F]{4}-[0-9a-fA-F]{4}-[0-9a-fA-F]{12}$'
    )
    cardholder_guid: str = Field(
        ...,
        description="GUID of the cardholder to grant access to",
        min_length=36,
        max_length=36,
        pattern=r'^[0-9a-fA-F]{8}-[0-9a-fA-F]{4}-[0-9a-fA-F]{4}-[0-9a-fA-F]{4}-[0-9a-fA-F]{12}$'
    )
    duration_seconds: int = Field(
        default=30,
        ge=5,
        le=300,
        description="Access duration in seconds (5-300 seconds, default: 30)"
    )
    reason: Optional[str] = Field(
        default=None,
        description="Optional reason for granting access (for audit trail)",
        max_length=500
    )
    response_format: ResponseFormat = Field(
        default=ResponseFormat.MARKDOWN,
        description="Output format"
    )


class DoorAction(str, Enum):
    """Door action types."""
    LOCK = "lock"
    UNLOCK = "unlock"


class LockUnlockDoorInput(BaseModel):
    """Input model for locking or unlocking a door."""

    model_config = ConfigDict(
        str_strip_whitespace=True,
        validate_assignment=True,
        extra='forbid'
    )

    door_guid: str = Field(
        ...,
        description="GUID of the door",
        min_length=36,
        max_length=36,
        pattern=r'^[0-9a-fA-F]{8}-[0-9a-fA-F]{4}-[0-9a-fA-F]{4}-[0-9a-fA-F]{4}-[0-9a-fA-F]{12}$'
    )
    action: DoorAction = Field(
        ...,
        description="Action to perform: 'lock' or 'unlock'"
    )
    duration_seconds: Optional[int] = Field(
        default=None,
        ge=5,
        le=3600,
        description="For unlock: duration in seconds (5-3600). None = permanent until manually locked"
    )
    reason: Optional[str] = Field(
        default=None,
        description="Optional reason for the action (for audit trail)",
        max_length=500
    )
    response_format: ResponseFormat = Field(
        default=ResponseFormat.MARKDOWN,
        description="Output format"
    )


class EventType(str, Enum):
    """Access event types."""
    ACCESS_GRANTED = "AccessGranted"
    ACCESS_REFUSED = "AccessRefused"
    ALL = "All"


class ListAccessEventsInput(BaseModel):
    """Input model for listing access events."""

    model_config = ConfigDict(
        str_strip_whitespace=True,
        validate_assignment=True,
        extra='forbid'
    )

    door_guid: Optional[str] = Field(
        default=None,
        description="Filter by specific door GUID",
        pattern=r'^[0-9a-fA-F]{8}-[0-9a-fA-F]{4}-[0-9a-fA-F]{4}-[0-9a-fA-F]{4}-[0-9a-fA-F]{12}$'
    )
    cardholder_guid: Optional[str] = Field(
        default=None,
        description="Filter by specific cardholder GUID",
        pattern=r'^[0-9a-fA-F]{8}-[0-9a-fA-F]{4}-[0-9a-fA-F]{4}-[0-9a-fA-F]{4}-[0-9a-fA-F]{12}$'
    )
    event_type: EventType = Field(
        default=EventType.ALL,
        description="Filter by event type: 'AccessGranted', 'AccessRefused', or 'All'"
    )
    start_time: Optional[str] = Field(
        default=None,
        description="Start time filter (ISO 8601 format: 'YYYY-MM-DDTHH:MM:SSZ')",
        pattern=r'^\d{4}-\d{2}-\d{2}T\d{2}:\d{2}:\d{2}Z$'
    )
    end_time: Optional[str] = Field(
        default=None,
        description="End time filter (ISO 8601 format: 'YYYY-MM-DDTHH:MM:SSZ')",
        pattern=r'^\d{4}-\d{2}-\d{2}T\d{2}:\d{2}:\d{2}Z$'
    )
    limit: int = Field(
        default=50,
        ge=1,
        le=500,
        description="Maximum events to return (1-500)"
    )
    offset: int = Field(
        default=0,
        ge=0,
        description="Pagination offset"
    )
    response_format: ResponseFormat = Field(
        default=ResponseFormat.MARKDOWN,
        description="Output format"
    )


class CredentialFormat(str, Enum):
    """Credential format types."""
    CARD = "card"
    BADGE = "badge"
    PIN = "pin"


class CreateVisitorInput(BaseModel):
    """Input model for creating a visitor."""

    model_config = ConfigDict(
        str_strip_whitespace=True,
        validate_assignment=True,
        extra='forbid'
    )

    first_name: str = Field(
        ...,
        min_length=1,
        max_length=50,
        description="Visitor's first name"
    )
    last_name: str = Field(
        ...,
        min_length=1,
        max_length=50,
        description="Visitor's last name"
    )
    company: Optional[str] = Field(
        default=None,
        max_length=100,
        description="Visitor's company name"
    )
    email: Optional[str] = Field(
        default=None,
        description="Visitor's email address",
        pattern=r'^[\w\.-]+@[\w\.-]+\.\w+$'
    )
    start_date: str = Field(
        ...,
        description="Visit start date/time (ISO 8601 format: 'YYYY-MM-DDTHH:MM:SSZ')",
        pattern=r'^\d{4}-\d{2}-\d{2}T\d{2}:\d{2}:\d{2}Z$'
    )
    end_date: str = Field(
        ...,
        description="Visit end date/time (ISO 8601 format: 'YYYY-MM-DDTHH:MM:SSZ')",
        pattern=r'^\d{4}-\d{2}-\d{2}T\d{2}:\d{2}:\d{2}Z$'
    )
    access_areas: List[str] = Field(
        ...,
        description="List of area GUIDs to grant access to",
        min_items=1,
        max_items=20
    )
    credential_format: CredentialFormat = Field(
        default=CredentialFormat.CARD,
        description="Credential format: 'card', 'badge', or 'pin'"
    )
    escort_required: bool = Field(
        default=False,
        description="Whether an escort is required for this visitor"
    )
    response_format: ResponseFormat = Field(
        default=ResponseFormat.MARKDOWN,
        description="Output format"
    )

    @field_validator('access_areas')
    @classmethod
    def validate_area_guids(cls, v: List[str]) -> List[str]:
        """Validate that all area GUIDs have correct format."""
        guid_pattern = r'^[0-9a-fA-F]{8}-[0-9a-fA-F]{4}-[0-9a-fA-F]{4}-[0-9a-fA-F]{4}-[0-9a-fA-F]{12}$'
        import re

        for guid in v:
            if not re.match(guid_pattern, guid):
                raise ValueError(f"Invalid GUID format: {guid}")

        return v

    @field_validator('end_date')
    @classmethod
    def validate_end_after_start(cls, v: str, info) -> str:
        """Validate that end_date is after start_date."""
        if 'start_date' in info.data:
            from datetime import datetime
            start = datetime.fromisoformat(info.data['start_date'].replace('Z', '+00:00'))
            end = datetime.fromisoformat(v.replace('Z', '+00:00'))

            if end <= start:
                raise ValueError("end_date must be after start_date")

        return v

# =====================================================
# System Status and Health Monitoring
# =====================================================

class EntityStatusFilter(str, Enum):
    """Filter options for entity status."""
    ALL = "All"
    ONLINE = "Online"
    OFFLINE = "Offline"
    IN_MAINTENANCE = "InMaintenance"


class ListEntityStatusByTypeInput(BaseModel):
    """Input model for listing entity status by type.
    
    This model validates parameters for querying entities of a specific type
    and retrieving their operational status (online, offline, maintenance).
    """
    
    model_config = ConfigDict(
        str_strip_whitespace=True,
        validate_assignment=True,
        extra='forbid'
    )
    
    entity_type: str = Field(
        ...,
        description=(
            "Type of entity to query. Common types: 'Cardholder', 'Door', 'Camera', "
            "'Area', 'User', 'Credential', 'AccessRule', 'Schedule', 'Alarm'"
        ),
        min_length=1,
        max_length=50
    )
    status_filter: EntityStatusFilter = Field(
        default=EntityStatusFilter.ALL,
        description=(
            "Filter entities by operational status: "
            "'All' (all entities), "
            "'Online' (online entities only), "
            "'Offline' (offline entities only), "
            "'InMaintenance' (entities in maintenance mode)"
        )
    )
    limit: int = Field(
        default=20,
        description="Maximum number of results to return (1-100)",
        ge=1,
        le=100
    )
    offset: int = Field(
        default=0,
        description="Number of results to skip for pagination",
        ge=0
    )
    response_format: ResponseFormat = Field(
        default=ResponseFormat.MARKDOWN,
        description="Output format: 'markdown' for human-readable or 'json' for machine-readable"
    )


class SystemHealthDashboardInput(BaseModel):
    """Input model for system health dashboard.
    
    This model validates parameters for retrieving a comprehensive system health
    overview across multiple entity types with aggregated statistics.
    """
    
    model_config = ConfigDict(
        str_strip_whitespace=True,
        validate_assignment=True,
        extra='forbid'
    )
    
    entity_types: List[str] = Field(
        default=["Camera", "Door"],
        description=(
            "List of entity types to include in dashboard. "
            "Common types: 'Camera', 'Door', 'Area', 'User', 'Credential'. "
            "Maximum 10 types."
        ),
        min_items=1,
        max_items=10
    )
    include_problem_details: bool = Field(
        default=True,
        description=(
            "Include detailed list of entities with problems "
            "(offline, in maintenance, etc.)"
        )
    )
    max_problems_per_type: int = Field(
        default=10,
        description="Maximum number of problem entities to show per type (1-50)",
        ge=1,
        le=50
    )
    response_format: ResponseFormat = Field(
        default=ResponseFormat.MARKDOWN,
        description="Output format: 'markdown' or 'json'"
    )
    
    @field_validator('entity_types')
    @classmethod
    def validate_entity_types(cls, v: List[str]) -> List[str]:
        """Validate that all entity types are non-empty strings."""
        for entity_type in v:
            if not entity_type or not entity_type.strip():
                raise ValueError("Entity type cannot be empty")
        return v
