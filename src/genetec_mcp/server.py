"""Main Genetec MCP server with tool implementations."""

from mcp.server.fastmcp import FastMCP
from .models import *
from .client import GenetecAPIClient, handle_api_error
from .formatters import *
from .config import CHARACTER_LIMIT

# Initialize FastMCP server
mcp = FastMCP("genetec_mcp")

# Initialize API client
api_client = GenetecAPIClient()


# =====================================================
# GRUPO 1: Core Entity Management
# =====================================================

@mcp.tool(
    name="genetec_search_entities",
    annotations={
        "title": "Search Genetec Entities",
        "readOnlyHint": True,
        "destructiveHint": False,
        "idempotentHint": True,
        "openWorldHint": True
    }
)
async def genetec_search_entities(params: SearchEntitiesInput) -> str:
    """Search for entities in Genetec Security Center by type and filters.
    
    This tool searches for entities of a specific type (Cardholder, Door, Camera, etc.)
    with optional name filtering and pagination support. Use this to find entities before
    performing operations on them or to get an overview of available resources.
    
    Common entity types:
    - Cardholder: People with access credentials
    - Door: Physical doors with access control
    - Camera: Video surveillance cameras
    - Area: Zones or areas in the facility
    - User: System users
    - Credential: Access cards/badges
    - AccessRule: Access control rules
    - Schedule: Time-based schedules
    
    Args:
        params (SearchEntitiesInput): Search parameters containing:
            - entity_type (str): Type of entity to search for
            - search_query (Optional[str]): Text to filter by name (partial match)
            - limit (int): Maximum results (1-100, default: 20)
            - offset (int): Pagination offset (default: 0)
            - response_format (str): 'markdown' or 'json'
    
    Returns:
        str: Formatted list of matching entities with pagination info
        
    Examples:
        - Search for all doors: entity_type='Door'
        - Find cardholders named John: entity_type='Cardholder', search_query='John'
        - Get cameras in area: entity_type='Camera', search_query='Building A'
    """
    try:
        # Make API request using client helper
        response = await api_client.search_entities(
            entity_type=params.entity_type,
            search_query=params.search_query,
            limit=params.limit,
            offset=params.offset
        )
        
        # Extract entities from response
        entities = response.get("Entities", [])
        total = response.get("TotalCount", len(entities))
        
        # Format response based on requested format
        if params.response_format == ResponseFormat.JSON:
            result = format_json(create_pagination_response(
                items=entities,
                total=total,
                offset=params.offset,
                limit=params.limit
            ))
        else:
            result = format_entity_markdown(entities, total, params.offset)
        
        # Apply character limit and return
        return truncate_response(result, CHARACTER_LIMIT)
        
    except Exception as e:
        return handle_api_error(e)


@mcp.tool(
    name="genetec_get_entity_details",
    annotations={
        "title": "Get Entity Details",
        "readOnlyHint": True,
        "destructiveHint": False,
        "idempotentHint": True,
        "openWorldHint": True
    }
)
async def genetec_get_entity_details(params: GetEntityInput) -> str:
    """Get detailed information about a specific entity by GUID.
    
    This tool retrieves comprehensive details about a single entity including its
    properties, relationships, and metadata. Use this after finding an entity's GUID
    through search to get complete information.
    
    Args:
        params (GetEntityInput): Parameters containing:
            - entity_guid (str): GUID of the entity (format: xxxxxxxx-xxxx-xxxx-xxxx-xxxxxxxxxxxx)
            - response_format (str): 'markdown' or 'json'
    
    Returns:
        str: Detailed entity information including properties and relationships
        
    Examples:
        - Get door details: entity_guid='a1b2c3d4-e5f6-7890-abcd-ef1234567890'
        - Get cardholder info: entity_guid='f1e2d3c4-b5a6-9870-dcba-fe0987654321'
    """
    try:
        # Get entity details from API
        response = await api_client.get_entity(entity_guid=params.entity_guid)
        
        entity = response.get("Entity", {})
        
        if not entity:
            return f"Error: Entity with GUID {params.entity_guid} not found."
        
        # Format response
        if params.response_format == ResponseFormat.JSON:
            result = format_json(entity)
        else:
            result = format_entity_details_markdown(entity)
        
        return truncate_response(result, CHARACTER_LIMIT)
        
    except Exception as e:
        return handle_api_error(e)


@mcp.tool(
    name="genetec_list_cardholders",
    annotations={
        "title": "List Cardholders",
        "readOnlyHint": True,
        "destructiveHint": False,
        "idempotentHint": True,
        "openWorldHint": True
    }
)
async def genetec_list_cardholders(params: ListCardholdersInput) -> str:
    """List cardholders (people with access credentials) with optional filters.
    
    This tool retrieves a list of cardholders from the system, which are individuals
    who have been granted access credentials. Useful for finding specific people,
    reviewing access lists, or managing credentials.
    
    Cardholders can be filtered by:
    - Name (partial match, case-insensitive)
    - Status (Active/Inactive)
    
    Args:
        params (ListCardholdersInput): Parameters containing:
            - name_filter (Optional[str]): Filter by cardholder name
            - status_filter (Optional[str]): 'Active', 'Inactive', or None for all
            - limit (int): Maximum results (1-100, default: 20)
            - offset (int): Pagination offset
            - response_format (str): 'markdown' or 'json'
    
    Returns:
        str: List of cardholders with their details and credentials
        
    Examples:
        - List all active cardholders: status_filter='Active'
        - Find cardholder: name_filter='John Doe'
        - Get first 50 cardholders: limit=50
    """
    try:
        # Build search query for cardholders
        response = await api_client.search_entities(
            entity_type="Cardholder",
            search_query=params.name_filter,
            limit=params.limit,
            offset=params.offset
        )
        
        entities = response.get("Entities", [])
        total = response.get("TotalCount", len(entities))
        
        # Apply status filter if specified
        if params.status_filter:
            entities = [
                e for e in entities 
                if e.get("Status", "").lower() == params.status_filter.lower()
            ]
            total = len(entities)  # Update total after filtering
        
        # Format response
        if params.response_format == ResponseFormat.JSON:
            result = format_json(create_pagination_response(
                items=entities,
                total=total,
                offset=params.offset,
                limit=params.limit
            ))
        else:
            result = format_entity_markdown(entities, total, params.offset)
        
        return truncate_response(result, CHARACTER_LIMIT)
        
    except Exception as e:
        return handle_api_error(e)


@mcp.tool(
    name="genetec_get_cardholder_details",
    annotations={
        "title": "Get Cardholder Details",
        "readOnlyHint": True,
        "destructiveHint": False,
        "idempotentHint": True,
        "openWorldHint": True
    }
)
async def genetec_get_cardholder_details(params: GetCardholderInput) -> str:
    """Get comprehensive details about a specific cardholder.
    
    This tool retrieves detailed information about a cardholder including their
    personal information, active credentials, assigned access rules, and access history.
    Use this to review a person's access configuration or troubleshoot access issues.
    
    Args:
        params (GetCardholderInput): Parameters containing:
            - cardholder_guid (str): GUID of the cardholder
            - include_credentials (bool): Include credential information (default: True)
            - include_access_rules (bool): Include access rules (default: True)
            - response_format (str): 'markdown' or 'json'
    
    Returns:
        str: Comprehensive cardholder information with credentials and access rights
        
    Examples:
        - Get full cardholder info: cardholder_guid='xxx', include_credentials=True
        - Basic info only: cardholder_guid='xxx', include_credentials=False
    """
    try:
        # Get cardholder entity details
        response = await api_client.get_entity(entity_guid=params.cardholder_guid)
        
        entity = response.get("Entity", {})
        
        if not entity:
            return f"Error: Cardholder with GUID {params.cardholder_guid} not found."
        
        # Verify it's actually a cardholder
        if entity.get("Type") != "Cardholder":
            return (
                f"Error: Entity {params.cardholder_guid} is not a Cardholder. "
                f"It is a {entity.get('Type', 'Unknown')}."
            )
        
        # TODO: In a real implementation, we would fetch additional data:
        # - Credentials if include_credentials is True
        # - Access rules if include_access_rules is True
        # For now, we return the basic entity information
        
        # Format response
        if params.response_format == ResponseFormat.JSON:
            result = format_json(entity)
        else:
            result = format_entity_details_markdown(entity)
        
        return truncate_response(result, CHARACTER_LIMIT)
        
    except Exception as e:
        return handle_api_error(e)


@mcp.tool(
    name="genetec_list_doors",
    annotations={
        "title": "List Doors",
        "readOnlyHint": True,
        "destructiveHint": False,
        "idempotentHint": True,
        "openWorldHint": True
    }
)
async def genetec_list_doors(params: ListDoorsInput) -> str:
    """List doors in the access control system with optional filters.
    
    This tool retrieves a list of doors (access points) configured in Security Center.
    Doors are the physical entry/exit points that are controlled by the access control
    system. Use this to find specific doors, review door configurations, or identify
    doors in a particular area.
    
    Doors can be filtered by:
    - Name (partial match)
    - Area/Zone
    
    Args:
        params (ListDoorsInput): Parameters containing:
            - name_filter (Optional[str]): Filter by door name (e.g., 'Main Entrance')
            - area_filter (Optional[str]): Filter by area/zone name
            - limit (int): Maximum results (1-100, default: 20)
            - offset (int): Pagination offset
            - response_format (str): 'markdown' or 'json'
    
    Returns:
        str: List of doors with their status and location information
        
    Examples:
        - List all doors: (no filters)
        - Find entrance doors: name_filter='entrance'
        - Doors in building: area_filter='Building A'
    """
    try:
        # Search for door entities
        response = await api_client.search_entities(
            entity_type="Door",
            search_query=params.name_filter,
            limit=params.limit,
            offset=params.offset
        )
        
        entities = response.get("Entities", [])
        total = response.get("TotalCount", len(entities))
        
        # Apply area filter if specified (client-side filtering)
        if params.area_filter:
            entities = [
                e for e in entities 
                if params.area_filter.lower() in e.get("Area", "").lower()
            ]
            total = len(entities)
        
        # Format response
        if params.response_format == ResponseFormat.JSON:
            result = format_json(create_pagination_response(
                items=entities,
                total=total,
                offset=params.offset,
                limit=params.limit
            ))
        else:
            result = format_entity_markdown(entities, total, params.offset)
        
        return truncate_response(result, CHARACTER_LIMIT)
        
    except Exception as e:
        return handle_api_error(e)


@mcp.tool(
    name="genetec_list_cameras",
    annotations={
        "title": "List Cameras",
        "readOnlyHint": True,
        "destructiveHint": False,
        "idempotentHint": True,
        "openWorldHint": True
    }
)
async def genetec_list_cameras(params: ListCamerasInput) -> str:
    """List surveillance cameras in the system with optional filters.
    
    This tool retrieves a list of cameras configured in Security Center. Cameras
    provide video surveillance and can be linked to access control events. Use this
    to find specific cameras, review camera coverage, or identify cameras in an area.
    
    Cameras can be filtered by:
    - Name (partial match)
    - Area/Zone
    - Status (Online, Offline, Recording)
    
    Args:
        params (ListCamerasInput): Parameters containing:
            - name_filter (Optional[str]): Filter by camera name
            - area_filter (Optional[str]): Filter by area/zone
            - status_filter (Optional[str]): 'Online', 'Offline', 'Recording'
            - limit (int): Maximum results (1-100, default: 20)
            - offset (int): Pagination offset
            - response_format (str): 'markdown' or 'json'
    
    Returns:
        str: List of cameras with their status and location
        
    Examples:
        - List all cameras: (no filters)
        - Find offline cameras: status_filter='Offline'
        - Cameras in lobby: area_filter='Lobby'
        - Find specific camera: name_filter='CAM-101'
    """
    try:
        # Search for camera entities
        response = await api_client.search_entities(
            entity_type="Camera",
            search_query=params.name_filter,
            limit=params.limit,
            offset=params.offset
        )
        
        entities = response.get("Entities", [])
        total = response.get("TotalCount", len(entities))
        
        # Apply filters (client-side filtering)
        if params.area_filter:
            entities = [
                e for e in entities 
                if params.area_filter.lower() in e.get("Area", "").lower()
            ]
        
        if params.status_filter:
            entities = [
                e for e in entities 
                if e.get("Status", "").lower() == params.status_filter.lower()
            ]
        
        # Update total after filtering
        if params.area_filter or params.status_filter:
            total = len(entities)
        
        # Format response
        if params.response_format == ResponseFormat.JSON:
            result = format_json(create_pagination_response(
                items=entities,
                total=total,
                offset=params.offset,
                limit=params.limit
            ))
        else:
            result = format_entity_markdown(entities, total, params.offset)
        
        return truncate_response(result, CHARACTER_LIMIT)
        
    except Exception as e:
        return handle_api_error(e)


# =====================================================
# GRUPO 2: Access Control Operations
# =====================================================

# Tools will be implemented in Phase 3


# Entry point for running the server
if __name__ == "__main__":
    mcp.run()
