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

        # Apply status filter if specified (client-side filtering)
        # Note: This reduces the result set, so we keep track of both totals
        original_total = total
        if params.status_filter:
            entities = [
                e for e in entities
                if e.get("Status", "").lower() == params.status_filter.lower()
            ]
            # Update total to reflect filtered count
            # The original_total from API is lost, but this is the count user sees
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
        if entity.get("EntityType") != "Cardholder":
            return (
                f"Error: Entity {params.cardholder_guid} is not a Cardholder. "
                f"It is a {entity.get('EntityType', 'Unknown')}."
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
        # Note: Area filter is applied after API call, reducing result set
        if params.area_filter:
            entities = [
                e for e in entities
                if params.area_filter.lower() in e.get("Area", "").lower()
            ]
            # Update total after filtering to reflect actual count shown to user
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
        # Note: Filters are applied after API call, reducing result set
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

        # Update total after filtering to reflect actual count shown to user
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
# GRUPO 2: Access Control Operations (Conservative Implementation)
# =====================================================

@mcp.tool(
    name="genetec_list_access_events",
    annotations={
        "title": "List Access Events",
        "readOnlyHint": True,
        "destructiveHint": False,
        "idempotentHint": True,
        "openWorldHint": True
    }
)
async def genetec_list_access_events(params: ListAccessEventsInput) -> str:
    """List access control events with optional filters.

    This tool retrieves access events (granted/refused) from the Genetec Security Center.
    Use this to review access history, investigate security incidents, or monitor
    door activity.

    Events can be filtered by:
    - Door (specific door GUID)
    - Cardholder (specific person)
    - Event type (AccessGranted, AccessRefused, or All)
    - Time range (start_time and end_time in ISO 8601 format)

    Args:
        params (ListAccessEventsInput): Parameters containing:
            - door_guid (Optional[str]): Filter by specific door
            - cardholder_guid (Optional[str]): Filter by specific cardholder
            - event_type (EventType): 'AccessGranted', 'AccessRefused', or 'All'
            - start_time (Optional[str]): Start time filter (ISO 8601)
            - end_time (Optional[str]): End time filter (ISO 8601)
            - limit (int): Maximum events to return (1-500, default: 50)
            - offset (int): Pagination offset
            - response_format (str): 'markdown' or 'json'

    Returns:
        str: List of access events with details

    Examples:
        - Recent events: (no filters returns last 50)
        - Failed access: event_type='AccessRefused'
        - Door activity: door_guid='xxx'
        - Time range: start_time='2025-11-01T00:00:00Z', end_time='2025-11-07T23:59:59Z'
    """
    try:
        # Query door activity events
        response = await api_client.query_door_events(
            door_guid=params.door_guid,
            start_time=params.start_time,
            end_time=params.end_time,
            limit=params.limit,
            offset=params.offset
        )

        events = response.get("Events", [])
        total = response.get("TotalCount", len(events))

        # Apply event type filter if not "All" (client-side filtering)
        # Note: This reduces the result set after API call
        if params.event_type != EventType.ALL:
            events = [
                e for e in events
                if e.get("EventType", "").lower() == params.event_type.value.lower()
            ]
            total = len(events)

        # Apply cardholder filter if specified (client-side filtering)
        # Note: Applied after event_type filter, further reducing results
        if params.cardholder_guid:
            events = [
                e for e in events
                if e.get("CardholderGuid") == params.cardholder_guid
            ]
            total = len(events)

        # Format response
        if params.response_format == ResponseFormat.JSON:
            result = format_json(create_pagination_response(
                items=events,
                total=total,
                offset=params.offset,
                limit=params.limit
            ))
        else:
            result = format_access_event_markdown(events, total, params.offset)

        return truncate_response(result, CHARACTER_LIMIT)

    except Exception as e:
        return handle_api_error(e)


@mcp.tool(
    name="genetec_create_visitor",
    annotations={
        "title": "Create Visitor",
        "readOnlyHint": False,
        "destructiveHint": False,
        "idempotentHint": False,
        "openWorldHint": True
    }
)
async def genetec_create_visitor(params: CreateVisitorInput) -> str:
    """Create a temporary visitor with time-limited access credentials.

    This tool creates a new visitor entity in Genetec Security Center with:
    - Personal information (name, company, email)
    - Visit period (start and end dates)
    - Access rights to specific areas
    - Temporary credential (auto-deactivates after end date)
    - Optional escort requirement

    Use this for:
    - Contractor access management
    - Guest credentials
    - Temporary employees
    - Vendor access

    Args:
        params (CreateVisitorInput): Parameters containing:
            - first_name (str): Visitor's first name
            - last_name (str): Visitor's last name
            - company (Optional[str]): Company name
            - email (Optional[str]): Email address
            - start_date (str): Visit start (ISO 8601)
            - end_date (str): Visit end (ISO 8601)
            - access_areas (List[str]): Area GUIDs to grant access
            - credential_format (CredentialFormat): 'card', 'badge', or 'pin'
            - escort_required (bool): Whether escort is required
            - response_format (str): 'markdown' or 'json'

    Returns:
        str: Created visitor details including GUID and credential info

    Examples:
        - Create visitor: first_name='John', last_name='Smith',
          start_date='2025-11-08T09:00:00Z', end_date='2025-11-08T17:00:00Z',
          access_areas=['area-guid-1', 'area-guid-2']
    """
    try:
        # Create visitor entity
        response = await api_client.create_visitor_entity(
            first_name=params.first_name,
            last_name=params.last_name,
            company=params.company,
            email=params.email,
            start_date=params.start_date,
            end_date=params.end_date,
            access_areas=params.access_areas,
            credential_format=params.credential_format.value,
            escort_required=params.escort_required
        )

        visitor = response.get("Visitor", {})

        if not visitor.get("Guid"):
            return "Error: Failed to create visitor. No GUID returned."

        # Format response
        if params.response_format == ResponseFormat.JSON:
            result = format_json(visitor)
        else:
            result = format_visitor_created_markdown(visitor)

        return truncate_response(result, CHARACTER_LIMIT)

    except Exception as e:
        return handle_api_error(e)


# Entry point for running the server


# =====================================================
# System Status and Health Monitoring Tools
# =====================================================

@mcp.tool(
    name="genetec_list_entity_status_by_type",
    annotations={
        "title": "List Entity Status by Type",
        "readOnlyHint": True,
        "destructiveHint": False,
        "idempotentHint": True,
        "openWorldHint": True
    }
)
async def genetec_list_entity_status_by_type(params: ListEntityStatusByTypeInput) -> str:
    """List entities of a specific type with their operational status.
    
    This tool retrieves all entities of a specified type (Camera, Door, etc.) and
    includes their operational status information (online, offline, maintenance).
    Use this to monitor system health, identify offline devices, or find entities
    requiring attention.
    
    Status information includes:
    - IsOnline: Whether the entity is currently online
    - RunningState: Current operational state
    - IsInMaintenance: Whether entity is in maintenance mode
    
    Args:
        params (ListEntityStatusByTypeInput): Parameters containing:
            - entity_type (str): Type of entity ('Camera', 'Door', 'Area', etc.)
            - status_filter (str): Filter by status ('All', 'Online', 'Offline', 'InMaintenance')
            - limit (int): Maximum results per page (1-100, default: 20)
            - offset (int): Pagination offset (default: 0)
            - response_format (str): 'markdown' or 'json'
    
    Returns:
        str: Formatted list of entities with status information and statistics
    
    Examples:
        - List all cameras: entity_type='Camera', status_filter='All'
        - Find offline doors: entity_type='Door', status_filter='Offline'
        - Cameras in maintenance: entity_type='Camera', status_filter='InMaintenance'
        - All online areas: entity_type='Area', status_filter='Online'
    """
    try:
        # Step 1: Search for entities of the specified type
        search_result = await api_client.search_entities(
            entity_type=params.entity_type,
            search_query=None,  # Get all entities of this type
            limit=100,  # Get more entities to filter
            offset=params.offset
        )
        
        entities_basic = search_result.get("Entities", [])
        
        if not entities_basic:
            return f"No {params.entity_type} entities found in the system."
        
        # Step 2: Get status information for these entities
        entity_guids = [e.get("Guid") for e in entities_basic if e.get("Guid")]
        
        # Batch fetch status in groups to avoid overwhelming the API
        batch_size = 20
        all_entities_with_status = []
        
        for i in range(0, len(entity_guids), batch_size):
            batch_guids = entity_guids[i:i + batch_size]
            batch_entities = await api_client.get_entities_with_status(batch_guids)
            all_entities_with_status.extend(batch_entities)
        
        # Step 3: Apply status filter (client-side)
        filtered_entities = []
        
        for entity in all_entities_with_status:
            is_online = entity.get("IsOnline")
            is_in_maintenance = entity.get("IsInMaintenance", False)
            
            # Apply filter
            if params.status_filter == EntityStatusFilter.ALL:
                filtered_entities.append(entity)
            elif params.status_filter == EntityStatusFilter.ONLINE:
                if is_online is True and not is_in_maintenance:
                    filtered_entities.append(entity)
            elif params.status_filter == EntityStatusFilter.OFFLINE:
                if is_online is False and not is_in_maintenance:
                    filtered_entities.append(entity)
            elif params.status_filter == EntityStatusFilter.IN_MAINTENANCE:
                if is_in_maintenance:
                    filtered_entities.append(entity)
        
        # Step 4: Apply pagination to filtered results
        total_filtered = len(filtered_entities)
        start_idx = 0  # We already applied offset in the search
        end_idx = min(params.limit, total_filtered)
        paginated_entities = filtered_entities[start_idx:end_idx]
        
        # Step 5: Format response
        if params.response_format == ResponseFormat.JSON:
            result = format_json({
                "entity_type": params.entity_type,
                "status_filter": params.status_filter.value,
                "total": total_filtered,
                "count": len(paginated_entities),
                "offset": params.offset,
                "limit": params.limit,
                "has_more": total_filtered > params.offset + len(paginated_entities),
                "entities": paginated_entities
            })
        else:
            result = format_entity_status_markdown(
                entities=paginated_entities,
                entity_type=params.entity_type,
                status_filter=params.status_filter.value,
                total=total_filtered,
                offset=params.offset,
                limit=params.limit
            )
        
        return truncate_response(result, CHARACTER_LIMIT)
        
    except Exception as e:
        return handle_api_error(e)


@mcp.tool(
    name="genetec_system_health_dashboard",
    annotations={
        "title": "System Health Dashboard",
        "readOnlyHint": True,
        "destructiveHint": False,
        "idempotentHint": True,
        "openWorldHint": True
    }
)
async def genetec_system_health_dashboard(params: SystemHealthDashboardInput) -> str:
    """Get comprehensive system health dashboard across multiple entity types.
    
    This tool provides an aggregated view of system health across different entity
    types (Cameras, Doors, Areas, etc.). It returns statistics on online/offline
    status, entities in maintenance, and optionally lists entities requiring attention.
    
    Perfect for:
    - System-wide health monitoring
    - Identifying infrastructure problems
    - Daily operational reports
    - Preventive maintenance planning
    
    The dashboard includes:
    - Overall health score and status
    - Statistics per entity type (total, online, offline, maintenance)
    - List of entities with problems (optional)
    - Visual indicators for quick assessment
    
    Args:
        params (SystemHealthDashboardInput): Parameters containing:
            - entity_types (List[str]): Entity types to monitor (default: ['Camera', 'Door'])
            - include_problem_details (bool): Include list of problematic entities (default: True)
            - max_problems_per_type (int): Max problem entities to show per type (1-50, default: 10)
            - response_format (str): 'markdown' or 'json'
    
    Returns:
        str: Comprehensive health dashboard with statistics and problem entities
    
    Examples:
        - Monitor cameras and doors: entity_types=['Camera', 'Door']
        - Full system check: entity_types=['Camera', 'Door', 'Area', 'User']
        - Quick overview: entity_types=['Camera'], include_problem_details=False
    """
    try:
        from datetime import datetime
        
        # Initialize result structure
        health_data = {
            "timestamp": datetime.utcnow().strftime("%Y-%m-%d %H:%M:%S UTC"),
            "entity_types": {},
            "problems": {}
        }
        
        # Process each entity type
        for entity_type in params.entity_types:
            try:
                # Step 1: Get all entities of this type
                search_result = await api_client.search_entities(
                    entity_type=entity_type,
                    search_query=None,
                    limit=100,  # Get up to 100 entities per type
                    offset=0
                )
                
                entities_basic = search_result.get("Entities", [])
                entity_guids = [e.get("Guid") for e in entities_basic if e.get("Guid")]
                
                if not entity_guids:
                    # No entities of this type
                    health_data["entity_types"][entity_type] = {
                        "total": 0,
                        "online": 0,
                        "offline": 0,
                        "in_maintenance": 0,
                        "unknown": 0
                    }
                    health_data["problems"][entity_type] = []
                    continue
                
                # Step 2: Get status for these entities (in batches)
                batch_size = 20
                all_entities_with_status = []
                
                for i in range(0, len(entity_guids), batch_size):
                    batch_guids = entity_guids[i:i + batch_size]
                    batch_entities = await api_client.get_entities_with_status(batch_guids)
                    all_entities_with_status.extend(batch_entities)
                
                # Step 3: Calculate statistics
                total = len(all_entities_with_status)
                online = 0
                offline = 0
                in_maintenance = 0
                unknown = 0
                problem_entities = []
                
                for entity in all_entities_with_status:
                    is_online = entity.get("IsOnline")
                    is_in_maintenance = entity.get("IsInMaintenance", False)
                    
                    if is_in_maintenance:
                        in_maintenance += 1
                        if params.include_problem_details and len(problem_entities) < params.max_problems_per_type:
                            problem_entities.append({
                                "Name": entity.get("Name", "Unknown"),
                                "Guid": entity.get("Guid"),
                                "ProblemType": "InMaintenance"
                            })
                    elif is_online is True:
                        online += 1
                    elif is_online is False:
                        offline += 1
                        if params.include_problem_details and len(problem_entities) < params.max_problems_per_type:
                            problem_entities.append({
                                "Name": entity.get("Name", "Unknown"),
                                "Guid": entity.get("Guid"),
                                "ProblemType": "Offline"
                            })
                    else:
                        unknown += 1
                
                # Store results
                health_data["entity_types"][entity_type] = {
                    "total": total,
                    "online": online,
                    "offline": offline,
                    "in_maintenance": in_maintenance,
                    "unknown": unknown
                }
                
                health_data["problems"][entity_type] = problem_entities
                
            except Exception as type_error:
                # Log error for this type but continue with others
                print(f"Error processing {entity_type}: {str(type_error)}")
                health_data["entity_types"][entity_type] = {
                    "total": 0,
                    "online": 0,
                    "offline": 0,
                    "in_maintenance": 0,
                    "unknown": 0,
                    "error": str(type_error)
                }
                health_data["problems"][entity_type] = []
        
        # Format response
        if params.response_format == ResponseFormat.JSON:
            result = format_json(health_data)
        else:
            result = format_system_health_dashboard_markdown(
                health_data=health_data,
                include_problem_details=params.include_problem_details
            )
        
        return truncate_response(result, CHARACTER_LIMIT)
        
    except Exception as e:
        return handle_api_error(e)


if __name__ == "__main__":
    mcp.run()
