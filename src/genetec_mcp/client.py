"""HTTP client for Genetec Security Center Web SDK API."""

import httpx
from typing import Dict, Any, Optional, List
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
            endpoint: API endpoint path (e.g., 'report/EntityConfiguration')
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
        """Search for entities of a specific type using correct Genetec API.
        
        Args:
            entity_type: Type of entity to search for
            search_query: Optional search text to filter by name
            limit: Maximum number of results to return
            offset: Number of results to skip (for pagination)
            
        Returns:
            Dict with 'Entities' list and 'TotalCount' compatible with server.py
        """
        # Build query string for Genetec API
        query_parts = [f"EntityTypes@{entity_type}"]
        
        if search_query:
            query_parts.append(f"Name={search_query}")
            query_parts.append("NameSearchMode=Contains")
        
        # Calculate page number from offset and limit
        page = (offset // limit) + 1
        query_parts.append(f"Page={page}")
        query_parts.append(f"PageSize={limit}")
        
        query_string = ",".join(query_parts)
        
        response = await self.make_request(
            f"report/EntityConfiguration?q={query_string}",
            method="GET"
        )
        
        # Process Genetec response format: {"Rsp": {"Status": "Ok/TooManyResults", "Result": [...]}}
        rsp = response.get("Rsp", {})
        status = rsp.get("Status", "Fail")
        result = rsp.get("Result", [])
        
        # Convert to format expected by server.py
        if isinstance(result, list):
            guid_list = result
        else:
            guid_list = []
        
        # Fetch names for all entities in a single request
        entities = []
        if guid_list:
            # Build multi-entity query: entity={guid1},Name,EntityType,entity={guid2},Name,EntityType,...
            entity_queries = []
            for item in guid_list:
                guid = item.get("Guid")
                if guid:
                    entity_queries.append(f"entity={guid},Name,EntityType,LogicalId")
            
            if entity_queries:
                multi_query = ",".join(entity_queries)
                details_response = await self.make_request(
                    f"entity?q={multi_query}",
                    method="GET"
                )
                
                details_rsp = details_response.get("Rsp", {})
                details_result = details_rsp.get("Result", [])
                
                # Result can be a single object or a list
                if isinstance(details_result, dict):
                    details_result = [details_result]
                
                # Match details with GUIDs
                for i, item in enumerate(guid_list):
                    guid = item.get("Guid")
                    if i < len(details_result):
                        detail = details_result[i]
                        entities.append({
                            "Guid": guid,
                            "Name": detail.get("Name", "Unnamed"),
                            "EntityType": detail.get("EntityType", entity_type),
                            "LogicalId": detail.get("LogicalId", "N/A")
                        })
                    else:
                        entities.append({
                            "Guid": guid,
                            "Name": "Unnamed",
                            "EntityType": entity_type,
                            "LogicalId": "N/A"
                        })
        
        return {
            "Entities": entities,
            "TotalCount": len(entities),
            "Status": status
        }
    
    async def get_entity(self, entity_guid: str) -> Dict[str, Any]:
        """Get detailed information about a specific entity.
        
        Args:
            entity_guid: GUID of the entity to retrieve
            
        Returns:
            Dict with 'Entity' containing the entity data, compatible with server.py
        """
        response = await self.make_request(
            f"entity?q=entity={entity_guid}",
            method="GET"
        )
        
        # Process Genetec response format: {"Rsp": {"Status": "Ok", "Result": {...}}}
        rsp = response.get("Rsp", {})
        status = rsp.get("Status", "Fail")
        result = rsp.get("Result", {})
        
        # Check for errors
        if status == "Fail":
            error_code = result.get("SdkErrorCode", "Unknown")
            error_msg = result.get("Message", "Unknown error")
            raise Exception(f"Genetec API Error ({error_code}): {error_msg}")
        
        # Convert to format expected by server.py
        return {
            "Entity": result,
            "Status": status
        }
    
    async def query_door_events(
        self,
        door_guid: Optional[str] = None,
        start_time: Optional[str] = None,
        end_time: Optional[str] = None,
        limit: int = 50,
        offset: int = 0
    ) -> Dict[str, Any]:
        """Query door activity/access events using Genetec report API.
        
        Args:
            door_guid: Optional specific door GUID to filter by
            start_time: Optional start time in ISO 8601 format
            end_time: Optional end time in ISO 8601 format
            limit: Maximum number of events to return
            offset: Number of events to skip (for pagination)
            
        Returns:
            Dict with 'Events' list and 'TotalCount'
        """
        # Build query string for door activity report
        query_parts = []
        
        if door_guid:
            query_parts.append(f"Doors@{door_guid}")
        
        # Add time range if specified
        if start_time and end_time:
            query_parts.append(f"TimeRange.SetTimeRange({start_time},{end_time})")
        elif start_time:
            # If only start time, query from start to now
            from datetime import datetime
            now = datetime.utcnow().strftime("%Y-%m-%dT%H:%M:%S")
            query_parts.append(f"TimeRange.SetTimeRange({start_time},{now})")
        
        # Add pagination
        page = (offset // limit) + 1
        query_parts.append(f"Page={page}")
        query_parts.append(f"PageSize={limit}")
        
        query_string = ",".join(query_parts) if query_parts else f"Page=1,PageSize={limit}"
        
        response = await self.make_request(
            f"report/DoorActivity?q={query_string}",
            method="GET"
        )
        
        # Process Genetec response
        rsp = response.get("Rsp", {})
        status = rsp.get("Status", "Fail")
        result = rsp.get("Result", [])
        
        # Check for errors
        if status == "Fail":
            error_msg = result.get("Message", "Unknown error") if isinstance(result, dict) else "Query failed"
            raise Exception(f"Genetec API Error: {error_msg}")
        
        # Convert to expected format
        events = []
        if isinstance(result, list):
            for event_data in result:
                events.append({
                    "EventType": event_data.get("EventType", "Unknown"),
                    "Timestamp": event_data.get("Timestamp"),
                    "DoorGuid": event_data.get("DoorGuid"),
                    "DoorName": event_data.get("DoorName", "Unknown"),
                    "CardholderGuid": event_data.get("CardholderGuid"),
                    "CardholderName": event_data.get("CardholderName", "Unknown"),
                    "Reason": event_data.get("Reason")
                })
        
        return {
            "Events": events,
            "TotalCount": len(events),
            "Status": status
        }
    
    async def create_visitor_entity(
        self,
        first_name: str,
        last_name: str,
        company: Optional[str] = None,
        email: Optional[str] = None,
        start_date: str = None,
        end_date: str = None,
        access_areas: List[str] = None,
        credential_format: str = "card",
        escort_required: bool = False
    ) -> Dict[str, Any]:
        """Create a visitor entity using Genetec entity API.
        
        Args:
            first_name: Visitor's first name
            last_name: Visitor's last name
            company: Optional company name
            email: Optional email address
            start_date: Visit start date/time (ISO 8601)
            end_date: Visit end date/time (ISO 8601)
            access_areas: List of area GUIDs to grant access
            credential_format: Credential type ('card', 'badge', 'pin')
            escort_required: Whether escort is required
            
        Returns:
            Dict with created visitor information
        """
        # Build properties for new visitor entity
        props = []
        props.append(f"FirstName={first_name}")
        props.append(f"LastName={last_name}")
        
        if company:
            props.append(f"Company={company}")
        if email:
            props.append(f"EmailAddress={email}")
        
        props.append(f"ActivationDate={start_date}")
        props.append(f"ExpirationDate={end_date}")
        
        # Add access areas if provided
        if access_areas:
            areas_str = "@".join(access_areas)
            props.append(f"AccessAreas={areas_str}")
        
        props.append(f"CredentialFormat={credential_format}")
        props.append(f"EscortRequired={str(escort_required).lower()}")
        
        # Add Guid to get the GUID back
        props.append("Guid")
        
        # Build entity creation query
        props_string = ",".join(props)
        query = f"entity=NewEntity(Visitor),{props_string}"
        
        response = await self.make_request(
            f"entity?q={query}",
            method="POST"
        )
        
        # Process response
        rsp = response.get("Rsp", {})
        status = rsp.get("Status", "Fail")
        result = rsp.get("Result", {})
        
        # Check for errors
        if status == "Fail":
            error_code = result.get("SdkErrorCode", "Unknown")
            error_msg = result.get("Message", "Unknown error")
            raise Exception(f"Genetec API Error ({error_code}): {error_msg}")
        
        # Return visitor information
        return {
            "Visitor": {
                "Guid": result.get("Guid"),
                "Name": f"{first_name} {last_name}",
                "FirstName": first_name,
                "LastName": last_name,
                "Company": company,
                "Email": email,
                "StartDate": start_date,
                "EndDate": end_date,
                "AccessAreas": access_areas,
                "CredentialFormat": credential_format,
                "EscortRequired": escort_required
            },
            "Status": status
        }


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
