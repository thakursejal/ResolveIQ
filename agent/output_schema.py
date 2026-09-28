REQUIRED_OUTPUT_FIELDS = [
    "agent",
    "status",
    "severity",
    "recurring_issue",
    "previous_failed_attempts",
    "previous_escalations",
    "successful_resolutions",
    "escalation_action",
    "memory_count",
    "recommendation",
    "reason",
    "ai_reasoning",
]

def validate_agent_output(result):
    """
    Validate the structure returned by ResolveIQ.
    """

    missing_fields = [
        field
        for field in REQUIRED_OUTPUT_FIELDS
        if field not in result
    ]

    if missing_fields:
        return {
            "valid": False,
            "missing_fields": missing_fields
        }

    return {
        "valid": True,
        "missing_fields": []
    }
