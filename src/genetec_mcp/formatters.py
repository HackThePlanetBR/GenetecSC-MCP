"""Response formatting utilities for Genetec MCP server."""

import json
from typing import Dict, Any, List, Optional
from datetime import datetime
from .config import CHARACTER_LIMIT


def format_timestamp(timestamp: Optional[str]) -> str:
    """Convert timestamp to human-readable format.
    
    Args:
        timestamp: ISO 8601 timestamp string or None
        
    Returns:
        Formatted timestamp string or 'N/A' if None
    """
    if not timestamp:
        return "N/A"
    
    try:
        dt = datetime.fromisoformat(timestamp.replace('Z', '+00:00'))
        return dt.strftime("%Y-%m-%d %H:%M:%S UTC")
    except (ValueError, AttributeError):
        return str(timestamp)


def format_guid_with_name(name: str, guid: str) -> str:
    """Format entity with name and GUID in parentheses.
    
    Args:
        name: Entity name
        guid: Entity GUID
        
    Returns:
        Formatted string like "Entity Name (guid-here)"
    """
    return f"{name} ({guid})"


def format_entity_markdown(entities: List[Dict[str, Any]], total: int, offset: int) -> str:
    """Format entity list as Markdown.
    
    Args:
        entities: List of entity dictionaries
        total: Total number of entities available
        offset: Current pagination offset
        
    Returns:
        Markdown-formatted entity list
    """
    if not entities:
        return "# No Results\n\nNo entities found matching your criteria."
    
    count = len(entities)
    has_more = total > offset + count
    
    lines = [
        "# Search Results",
        "",
        f"**Total Results:** {total}",
        f"**Showing:** {count} results (offset: {offset})",
        "",
        "## Entities",
        ""
    ]
    
    for i, entity in enumerate(entities, 1):
        name = entity.get("Name", "Unnamed")
        guid = entity.get("Guid", "N/A")
        entity_type = entity.get("Type", "Unknown")
        logical_id = entity.get("LogicalId", "N/A")
        
        lines.append(f"### {i}. {name}")
        lines.append(f"- **GUID:** {guid}")
        lines.append(f"- **Type:** {entity_type}")
        lines.append(f"- **Logical ID:** {logical_id}")
        lines.append("")
    
    if has_more:
        next_offset = offset + count
        lines.append("---")
        lines.append(f"**Pagination:** Has more results. Use `offset={next_offset}` to see the next page.")
    
    return "\n".join(lines)


def format_entity_details_markdown(entity: Dict[str, Any]) -> str:
    """Format single entity details as Markdown.
    
    Args:
        entity: Entity dictionary with details
        
    Returns:
        Markdown-formatted entity details
    """
    name = entity.get("Name", "Unnamed")
    entity_type = entity.get("Type", "Unknown")
    guid = entity.get("Guid", "N/A")
    logical_id = entity.get("LogicalId", "N/A")
    
    lines = [
        "# Entity Details",
        "",
        f"**Name:** {name}",
        f"**Type:** {entity_type}",
        f"**GUID:** {guid}",
        f"**Logical ID:** {logical_id}",
        ""
    ]
    
    # Add properties section if available
    if "Properties" in entity:
        lines.append("## Properties")
        for key, value in entity["Properties"].items():
            lines.append(f"- **{key}:** {value}")
        lines.append("")
    
    # Add custom fields if available
    if "CustomFields" in entity:
        lines.append("## Custom Fields")
        for key, value in entity["CustomFields"].items():
            lines.append(f"- **{key}:** {value}")
        lines.append("")
    
    return "\n".join(lines)


def format_access_event_markdown(events: List[Dict[str, Any]], total: int, offset: int) -> str:
    """Format access events as Markdown.
    
    Args:
        events: List of event dictionaries
        total: Total number of events available
        offset: Current pagination offset
        
    Returns:
        Markdown-formatted event list
    """
    if not events:
        return "# No Events\n\nNo access events found for the specified criteria."
    
    count = len(events)
    has_more = total > offset + count
    
    lines = [
        "# Access Events",
        "",
        f"**Total Events:** {total}",
        f"**Showing:** {count} events (offset: {offset})",
        "",
        "## Recent Events",
        ""
    ]
    
    for i, event in enumerate(events, 1):
        event_type = event.get("EventType", "Unknown")
        timestamp = format_timestamp(event.get("Timestamp"))
        door_name = event.get("DoorName", "Unknown")
        door_guid = event.get("DoorGuid", "N/A")
        cardholder_name = event.get("CardholderName", "Unknown")
        cardholder_guid = event.get("CardholderGuid", "N/A")
        
        lines.append(f"### {i}. {event_type}")
        lines.append(f"- **Time:** {timestamp}")
        lines.append(f"- **Door:** {format_guid_with_name(door_name, door_guid)}")
        lines.append(f"- **Cardholder:** {format_guid_with_name(cardholder_name, cardholder_guid)}")
        
        if "Reason" in event:
            lines.append(f"- **Reason:** {event['Reason']}")
        
        lines.append("")
    
    if has_more:
        next_offset = offset + count
        lines.append("---")
        lines.append(f"**Pagination:** Use `offset={next_offset}` to see more events.")
    
    return "\n".join(lines)


def format_door_action_markdown(
    action: str,
    door_name: str,
    door_guid: str,
    success: bool,
    details: Optional[Dict[str, Any]] = None
) -> str:
    """Format door action result as Markdown.
    
    Args:
        action: Action performed (e.g., 'Lock', 'Unlock', 'Grant Access')
        door_name: Name of the door
        door_guid: GUID of the door
        success: Whether the action was successful
        details: Optional additional details
        
    Returns:
        Markdown-formatted action result
    """
    status_emoji = "✅" if success else "❌"
    status_text = "successful" if success else "failed"
    
    lines = [
        f"# Door {action} {status_emoji}",
        "",
        f"**Door:** {format_guid_with_name(door_name, door_guid)}",
        f"**Action:** {action}",
        f"**Status:** {status_text.capitalize()}",
        f"**Timestamp:** {format_timestamp(datetime.utcnow().isoformat())}",
        ""
    ]
    
    if details:
        lines.append("## Details")
        for key, value in details.items():
            lines.append(f"- **{key}:** {value}")
        lines.append("")
    
    return "\n".join(lines)


def format_visitor_created_markdown(visitor: Dict[str, Any]) -> str:
    """Format visitor creation result as Markdown.
    
    Args:
        visitor: Dictionary containing visitor information
        
    Returns:
        Markdown-formatted visitor details
    """
    name = visitor.get("Name", "Unknown")
    guid = visitor.get("Guid", "N/A")
    company = visitor.get("Company", "N/A")
    email = visitor.get("Email", "N/A")
    start_date = format_timestamp(visitor.get("StartDate"))
    end_date = format_timestamp(visitor.get("EndDate"))
    
    lines = [
        "# Visitor Created ✅",
        "",
        f"**Name:** {name}",
        f"**Company:** {company}",
        f"**Email:** {email}",
        f"**Visitor GUID:** {guid}",
        "",
        "## Visit Details",
        f"- **Start:** {start_date}",
        f"- **End:** {end_date}",
        ""
    ]
    
    if "AccessAreas" in visitor:
        lines.append("## Access Rights")
        for area in visitor["AccessAreas"]:
            lines.append(f"- {area}")
        lines.append("")
    
    if "Credential" in visitor:
        cred = visitor["Credential"]
        lines.append("## Credential")
        lines.append(f"- **Type:** {cred.get('Type', 'N/A')}")
        lines.append(f"- **Number:** {cred.get('Number', 'N/A')}")
        lines.append(f"- **Status:** {cred.get('Status', 'N/A')}")
        lines.append("")
    
    return "\n".join(lines)


def format_json(data: Dict[str, Any]) -> str:
    """Format data as pretty-printed JSON.
    
    Args:
        data: Dictionary to format
        
    Returns:
        JSON-formatted string
    """
    return json.dumps(data, indent=2, ensure_ascii=False)


def truncate_response(response: str, limit: int = CHARACTER_LIMIT) -> str:
    """Truncate response if it exceeds character limit.
    
    Args:
        response: Response string to potentially truncate
        limit: Maximum character limit (default from config)
        
    Returns:
        Truncated response with notice if limit exceeded
    """
    if len(response) <= limit:
        return response
    
    # Reserve space for truncation message
    truncation_msg = (
        "\n\n"
        "---\n"
        "⚠️ **Response Truncated**\n\n"
        f"The response exceeded the {limit:,} character limit and was truncated.\n"
        "Use more specific filters, reduce the limit parameter, or increase the offset "
        "to paginate through results.\n"
    )
    
    available_space = limit - len(truncation_msg)
    truncated = response[:available_space]
    
    # Try to truncate at a reasonable boundary (end of line)
    last_newline = truncated.rfind('\n')
    if last_newline > available_space * 0.8:  # If we're close to the end
        truncated = truncated[:last_newline]
    
    return truncated + truncation_msg


def create_pagination_response(
    items: List[Any],
    total: int,
    offset: int,
    limit: int
) -> Dict[str, Any]:
    """Create paginated response structure.
    
    Args:
        items: List of items for current page
        total: Total number of items available
        offset: Current pagination offset
        limit: Items per page
        
    Returns:
        Dictionary with pagination metadata
    """
    count = len(items)
    has_more = total > offset + count
    next_offset = offset + count if has_more else None
    
    return {
        "total": total,
        "count": count,
        "offset": offset,
        "limit": limit,
        "has_more": has_more,
        "next_offset": next_offset,
        "items": items
    }
