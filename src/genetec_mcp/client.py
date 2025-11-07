"""HTTP client for Genetec Security Center Web SDK API."""

import httpx
from typing import Dict, Any, Optional
from .config import GENETEC_CONFIG, API_TIMEOUT


class GenetecAPIClient:
    """HTTP client for Genetec API with authentication and error handling."""
    
    def __init__(self):
        """Initialize the Genetec API client with credentials from config."""
        self.base_url = GENETEC_CONFIG["server_url"].rstrip("/")
        # Format: {username};{application_id}
        self.username = f"{GENETEC_CONFIG['username']};{GENETEC_CONFIG['app_id']}"
        self.password = GENETEC_CONFIG["password"]
        self.timeout = API_TIMEOUT
        self.verify_ssl = GENETEC_CONFIG["verify_ssl"]
    
    async def make_request(
        self,
        endpoint: str,
        method: str = "POST",
        data: Optional[Dict[str, Any]] = None,
        params: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """Make authenticated request to Genetec API.
        
        Args:
            endpoint: API endpoint path (e.g., 'EntityManagement.svc/SearchEntities')
            method: HTTP method (default: POST)
            data: JSON data for POST/PUT requests
            params: Query parameters for GET requests
            
        Returns:
            Dict containing the API response
            
        Raises:
            httpx.HTTPStatusError: For HTTP error responses
            httpx.TimeoutException: For request timeouts
            httpx.ConnectError: For connection failures
        """
        url = f"{self.base_url}/{endpoint}"
        
        async with httpx.AsyncClient(
            timeout=self.timeout,
            verify=self.verify_ssl
        ) as client:
            response = await client.request(
                method=method,
                url=url,
                json=data,
                params=params,
                auth=(self.username, self.password),
                headers={
                    "Accept": "text/json",
                    "Content-Type": "application/json"
                }
            )
            
            # Raise exception for HTTP error responses
            response.raise_for_status()
            
            return response.json()
    
    async def search_entities(
        self,
        entity_type: str,
        search_query: Optional[str] = None,
        limit: int = 20,
        offset: int = 0
    ) -> Dict[str, Any]:
        """Search for entities of a specific type.
        
        Args:
            entity_type: Type of entity to search for
            search_query: Optional search text to filter by name
            limit: Maximum number of results to return
            offset: Number of results to skip (for pagination)
            
        Returns:
            Dict containing search results and pagination info
        """
        data = {
            "QueryContext": {
                "EntityType": entity_type,
                "PageInfo": {
                    "Limit": limit,
                    "Offset": offset
                }
            }
        }
        
        if search_query:
            data["QueryContext"]["SearchName"] = search_query
        
        return await self.make_request("EntityManagement.svc/SearchEntities", data=data)
    
    async def get_entity(self, entity_guid: str) -> Dict[str, Any]:
        """Get detailed information about a specific entity.
        
        Args:
            entity_guid: GUID of the entity to retrieve
            
        Returns:
            Dict containing entity details
        """
        data = {
            "EntityGuid": entity_guid
        }
        
        return await self.make_request("EntityManagement.svc/GetEntity", data=data)
    
    async def execute_access_control(
        self,
        command: str,
        door_guid: str,
        cardholder_guid: Optional[str] = None,
        duration_seconds: Optional[int] = None,
        reason: Optional[str] = None
    ) -> Dict[str, Any]:
        """Execute an access control command on a door.
        
        Args:
            command: Command to execute ('GrantAccess', 'Lock', 'Unlock')
            door_guid: GUID of the door
            cardholder_guid: GUID of the cardholder (for GrantAccess)
            duration_seconds: Duration in seconds (optional)
            reason: Reason for the action (optional)
            
        Returns:
            Dict containing command result
        """
        data = {
            "Command": command,
            "DoorGuid": door_guid
        }
        
        if cardholder_guid:
            data["CardholderGuid"] = cardholder_guid
        
        if duration_seconds is not None:
            data["DurationSeconds"] = duration_seconds
        
        if reason:
            data["Reason"] = reason
        
        return await self.make_request("AccessControlManagement.svc/ExecuteAccessControl", data=data)
    
    async def query_events(
        self,
        event_type: Optional[str] = None,
        door_guid: Optional[str] = None,
        cardholder_guid: Optional[str] = None,
        start_time: Optional[str] = None,
        end_time: Optional[str] = None,
        limit: int = 50,
        offset: int = 0
    ) -> Dict[str, Any]:
        """Query access events with filters.
        
        Args:
            event_type: Type of event to filter ('AccessGranted', 'AccessRefused', 'All')
            door_guid: Filter by specific door GUID
            cardholder_guid: Filter by specific cardholder GUID
            start_time: Start time filter (ISO 8601 format)
            end_time: End time filter (ISO 8601 format)
            limit: Maximum number of events to return
            offset: Number of events to skip (for pagination)
            
        Returns:
            Dict containing events and pagination info
        """
        data = {
            "QueryContext": {
                "PageInfo": {
                    "Limit": limit,
                    "Offset": offset
                }
            }
        }
        
        # Add filters
        filters = {}
        
        if event_type and event_type != "All":
            filters["EventType"] = event_type
        
        if door_guid:
            filters["DoorGuid"] = door_guid
        
        if cardholder_guid:
            filters["CardholderGuid"] = cardholder_guid
        
        if start_time:
            filters["StartTime"] = start_time
        
        if end_time:
            filters["EndTime"] = end_time
        
        if filters:
            data["QueryContext"]["Filters"] = filters
        
        return await self.make_request("EventManagement.svc/QueryReports", data=data)
    
    async def create_visitor(
        self,
        first_name: str,
        last_name: str,
        company: Optional[str] = None,
        email: Optional[str] = None,
        start_date: str = "",
        end_date: str = "",
        access_areas: list = [],
        credential_format: str = "card",
        escort_required: bool = False
    ) -> Dict[str, Any]:
        """Create a temporary visitor with credentials.
        
        Args:
            first_name: Visitor's first name
            last_name: Visitor's last name
            company: Visitor's company name (optional)
            email: Visitor's email address (optional)
            start_date: Visit start date/time (ISO 8601 format)
            end_date: Visit end date/time (ISO 8601 format)
            access_areas: List of area GUIDs to grant access
            credential_format: Credential format ('card', 'badge', 'pin')
            escort_required: Whether an escort is required
            
        Returns:
            Dict containing visitor details
        """
        data = {
            "FirstName": first_name,
            "LastName": last_name,
            "StartDate": start_date,
            "EndDate": end_date,
            "AccessAreas": access_areas,
            "CredentialFormat": credential_format,
            "EscortRequired": escort_required
        }
        
        if company:
            data["Company"] = company
        
        if email:
            data["Email"] = email
        
        return await self.make_request("CardholderManagement.svc/CreateVisitor", data=data)


def handle_api_error(e: Exception) -> str:
    """Convert API errors to user-friendly, actionable error messages.
    
    Args:
        e: The exception that occurred
        
    Returns:
        str: User-friendly error message with guidance on how to proceed
    """
    if isinstance(e, httpx.HTTPStatusError):
        status = e.response.status_code
        
        if status == 401:
            return (
                "Error: Authentication failed. Please check your credentials.\n"
                "Verify GENETEC_USERNAME, GENETEC_PASSWORD, and GENETEC_APP_ID in your .env file."
            )
        elif status == 403:
            return (
                "Error: Access denied. You don't have permission to access this resource.\n"
                "Check that your user account has the 'Log on using the SDK' privilege enabled."
            )
        elif status == 404:
            return (
                "Error: Resource not found. The requested entity or endpoint doesn't exist.\n"
                "Verify that the GUID is correct and the entity exists in Security Center."
            )
        elif status == 429:
            return (
                "Error: Rate limit exceeded. Too many requests in a short period.\n"
                "Wait a moment before making more requests."
            )
        elif status == 500:
            return (
                "Error: Internal server error. The Security Center server encountered an error.\n"
                "Contact your system administrator or check server logs."
            )
        elif status == 503:
            return (
                "Error: Service unavailable. The Security Center server is not responding.\n"
                "Check that the Web SDK role is running and the server is online."
            )
        
        return (
            f"Error: API request failed with HTTP {status}.\n"
            f"Response: {e.response.text[:200]}"
        )
    
    elif isinstance(e, httpx.TimeoutException):
        return (
            "Error: Request timeout. The server took too long to respond.\n"
            "Try again or increase GENETEC_TIMEOUT in your .env file."
        )
    
    elif isinstance(e, httpx.ConnectError):
        return (
            "Error: Cannot connect to Genetec server.\n"
            "Check that GENETEC_SERVER_URL is correct and the server is reachable.\n"
            f"Current URL: {GENETEC_CONFIG['server_url']}"
        )
    
    elif isinstance(e, httpx.RequestError):
        return (
            f"Error: Network request failed - {type(e).__name__}\n"
            "Check your network connection and server configuration."
        )
    
    # Generic error for unexpected exceptions
    return (
        f"Error: Unexpected error occurred - {type(e).__name__}\n"
        f"Details: {str(e)[:200]}"
    )
