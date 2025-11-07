"""Configuration and constants for Genetec MCP server."""

import os
from typing import Dict, Any
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

# =====================================================
# API Configuration
# =====================================================

GENETEC_CONFIG: Dict[str, Any] = {
    "server_url": os.getenv("GENETEC_SERVER_URL", "https://localhost:4590/WebSdk"),
    "username": os.getenv("GENETEC_USERNAME", "admin"),
    "password": os.getenv("GENETEC_PASSWORD", ""),
    "app_id": os.getenv(
        "GENETEC_APP_ID",
        "KxsD11z743Hf5Gq9mv3+5ekxzemlCiUXkTFY5ba1NOGcLCmGstt2n0zYE9NsNimv"
    ),
    "timeout": int(os.getenv("GENETEC_TIMEOUT", "30")),
    "verify_ssl": os.getenv("GENETEC_VERIFY_SSL", "true").lower() == "true"
}

# =====================================================
# Response Configuration
# =====================================================

# Maximum response size in characters to prevent overwhelming LLM context
CHARACTER_LIMIT: int = 25000

# Default pagination limits
DEFAULT_LIMIT: int = 20
MAX_LIMIT: int = 100

# API request timeout in seconds
API_TIMEOUT: float = float(GENETEC_CONFIG["timeout"])

# =====================================================
# Genetec API Endpoints
# =====================================================

ENDPOINTS = {
    # Entity Management
    "search_entities": "EntityManagement.svc/SearchEntities",
    "get_entity": "EntityManagement.svc/GetEntity",
    
    # Access Control
    "execute_access_control": "AccessControlManagement.svc/ExecuteAccessControl",
    "grant_access": "AccessControlManagement.svc/GrantAccess",
    "lock_door": "AccessControlManagement.svc/LockDoor",
    "unlock_door": "AccessControlManagement.svc/UnlockDoor",
    
    # Event Management
    "query_reports": "EventManagement.svc/QueryReports",
    "get_events": "EventManagement.svc/GetEvents",
    
    # Cardholder Management
    "create_visitor": "CardholderManagement.svc/CreateVisitor",
    "get_cardholder": "CardholderManagement.svc/GetCardholder",
}

# =====================================================
# Entity Types
# =====================================================

ENTITY_TYPES = [
    "Cardholder",
    "Credential",
    "Door",
    "Camera",
    "Area",
    "User",
    "UserGroup",
    "CardholderGroup",
    "AccessRule",
    "Schedule",
    "Alarm",
    "Visitor",
    "Reader",
    "AccessControlUnit",
]

# =====================================================
# Event Types
# =====================================================

EVENT_TYPES = {
    "access_granted": "AccessGranted",
    "access_refused": "AccessRefused",
    "door_forced": "DoorForced",
    "door_held_open": "DoorHeldOpen",
    "camera_motion": "CameraMotion",
    "camera_motion_off": "CameraMotionOff",
    "cardholder_entry": "CardholderEntryDetected",
    "antipassback": "CardholderAntipassback",
}

# =====================================================
# Validation
# =====================================================

def validate_config() -> None:
    """Validate that required configuration is present."""
    required_fields = ["server_url", "username", "password", "app_id"]
    missing = [field for field in required_fields if not GENETEC_CONFIG.get(field)]
    
    if missing:
        raise ValueError(
            f"Missing required environment variables: {', '.join(missing)}. "
            f"Please create a .env file based on .env.example"
        )

# Validate configuration on import
validate_config()