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
        entity_type = entity.get("EntityType", "Unknown")
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
    entity_type = entity.get("EntityType", "Unknown")
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
    status_emoji = "âœ…" if success else "âŒ"
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
        "# Visitor Created âœ…",
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
        "âš ï¸ **Response Truncated**\n\n"
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

# =====================================================
# System Status and Health Formatters
# =====================================================

def format_entity_status_markdown(
        entities: List[Dict[str, Any]],
        entity_type: str,
        status_filter: str,
        total: int,
        offset: int,
        limit: int
) -> str:
    """Format entity status list as Markdown.
    
    Args:
        entities: List of entity dictionaries with status information
        entity_type: Type of entities being displayed
        status_filter: Filter applied (All, Online, Offline, InMaintenance)
        total: Total number of entities (after filtering)
        offset: Current pagination offset
        limit: Items per page
        
    Returns:
        Formatted Markdown string
    """
    # Header
    lines = [
        f"# {entity_type} Status Report",
        ""
    ]
    
    # Filter info
    if status_filter != "All":
        lines.append(f"**Filter:** {status_filter}")
    
    # Summary statistics
    lines.extend([
        f"**Total Results:** {total}",
        f"**Showing:** {len(entities)} entities (offset: {offset}, limit: {limit})",
        ""
    ])
    
    # Count by status
    if entities:
        online_count = sum(1 for e in entities if e.get("IsOnline") is True)
        offline_count = sum(1 for e in entities if e.get("IsOnline") is False)
        maintenance_count = sum(1 for e in entities if e.get("IsInMaintenance") is True)
        unknown_count = len(entities) - (online_count + offline_count)
        
        lines.extend([
            "## Status Summary",
            "",
            f"- ✅ **Online:** {online_count}",
            f"- ❌ **Offline:** {offline_count}",
            f"- 🔧 **In Maintenance:** {maintenance_count}",
            f"- ❓ **Unknown:** {unknown_count}",
            ""
        ])
    
    # Entity list
    if not entities:
        lines.extend([
            "## Entities",
            "",
            "*No entities found matching the criteria.*"
        ])
    else:
        lines.extend([
            "## Entities",
            ""
        ])
        
        for entity in entities:
            name = entity.get("Name", "Unknown")
            guid = entity.get("Guid", "N/A")
            logical_id = entity.get("LogicalId", "N/A")
            is_online = entity.get("IsOnline")
            running_state = entity.get("RunningState", "Unknown")
            is_in_maintenance = entity.get("IsInMaintenance", False)
            
            # Status icon
            if is_in_maintenance:
                status_icon = "🔧"
                status_text = "Maintenance"
            elif is_online is True:
                status_icon = "✅"
                status_text = "Online"
            elif is_online is False:
                status_icon = "❌"
                status_text = "Offline"
            else:
                status_icon = "❓"
                status_text = "Unknown"
            
            lines.extend([
                f"### {status_icon} {name}",
                "",
                f"- **GUID:** `{guid}`",
                f"- **Logical ID:** {logical_id}",
                f"- **Status:** {status_text}",
                f"- **Running State:** {running_state}",
                ""
            ])
    
    # Pagination info
    count = len(entities)
    has_more = total > offset + count
    
    if has_more:
        next_offset = offset + count
        lines.extend([
            "---",
            "",
            f"📄 **Pagination:** Showing {offset + 1}-{offset + count} of {total} total results",
            f"➡️ Use `offset={next_offset}` to get the next page",
            ""
        ])
    
    return "\n".join(lines)


def format_system_health_dashboard_markdown(
        health_data: Dict[str, Any],
        include_problem_details: bool
) -> str:
    """Format system health dashboard as Markdown.
    
    Args:
        health_data: Dictionary with health data per entity type
        include_problem_details: Whether to include detailed problem list
        
    Returns:
        Formatted Markdown dashboard
    """
    lines = [
        "# 🏥 System Health Dashboard",
        "",
        f"**Generated:** {health_data.get('timestamp', 'Unknown')}",
        ""
    ]
    
    # Overall summary
    total_entities = 0
    total_online = 0
    total_offline = 0
    total_maintenance = 0
    total_unknown = 0
    
    entity_types_data = health_data.get("entity_types", {})
    
    for type_data in entity_types_data.values():
        total_entities += type_data.get("total", 0)
        total_online += type_data.get("online", 0)
        total_offline += type_data.get("offline", 0)
        total_maintenance += type_data.get("in_maintenance", 0)
        total_unknown += type_data.get("unknown", 0)
    
    # Calculate health percentage
    if total_entities > 0:
        health_percentage = (total_online / total_entities) * 100
        if health_percentage >= 95:
            health_icon = "🟢"
            health_status = "Excellent"
        elif health_percentage >= 80:
            health_icon = "🟡"
            health_status = "Good"
        elif health_percentage >= 60:
            health_icon = "🟠"
            health_status = "Warning"
        else:
            health_icon = "🔴"
            health_status = "Critical"
    else:
        health_icon = "⚪"
        health_status = "No Data"
        health_percentage = 0
    
    lines.extend([
        f"## {health_icon} Overall Status: {health_status}",
        "",
        f"**Health Score:** {health_percentage:.1f}% ({total_online}/{total_entities} entities online)",
        "",
        "### Quick Stats",
        "",
        f"- **Total Entities:** {total_entities}",
        f"- ✅ **Online:** {total_online}",
        f"- ❌ **Offline:** {total_offline}",
        f"- 🔧 **In Maintenance:** {total_maintenance}",
        f"- ❓ **Unknown Status:** {total_unknown}",
        ""
    ])
    
    # Per entity type breakdown
    lines.extend([
        "## 📊 Status by Entity Type",
        ""
    ])
    
    for entity_type, type_data in entity_types_data.items():
        total = type_data.get("total", 0)
        online = type_data.get("online", 0)
        offline = type_data.get("offline", 0)
        maintenance = type_data.get("in_maintenance", 0)
        unknown = type_data.get("unknown", 0)
        
        if total > 0:
            online_pct = (online / total) * 100
            type_health = "🟢" if online_pct >= 95 else "🟡" if online_pct >= 80 else "🟠" if online_pct >= 60 else "🔴"
        else:
            online_pct = 0
            type_health = "⚪"
        
        lines.extend([
            f"### {type_health} {entity_type}",
            "",
            f"- **Total:** {total}",
            f"- **Online:** {online} ({online_pct:.1f}%)",
            f"- **Offline:** {offline}",
            f"- **In Maintenance:** {maintenance}",
            f"- **Unknown:** {unknown}",
            ""
        ])
    
    # Problem entities details
    if include_problem_details:
        problems = health_data.get("problems", {})
        
        if problems:
            lines.extend([
                "## ⚠️ Entities Requiring Attention",
                ""
            ])
            
            for entity_type, problem_entities in problems.items():
                if problem_entities:
                    lines.append(f"### {entity_type}")
                    lines.append("")
                    
                    for entity in problem_entities:
                        name = entity.get("Name", "Unknown")
                        guid = entity.get("Guid", "N/A")
                        status = entity.get("ProblemType", "Unknown")
                        
                        if status == "Offline":
                            icon = "❌"
                        elif status == "InMaintenance":
                            icon = "🔧"
                        else:
                            icon = "❓"
                        
                        lines.extend([
                            f"- {icon} **{name}**",
                            f"  - GUID: `{guid}`",
                            f"  - Issue: {status}",
                            ""
                        ])
        else:
            lines.extend([
                "## ✅ No Issues Detected",
                "",
                "*All monitored entities are operating normally.*",
                ""
            ])
    
    return "\n".join(lines)
