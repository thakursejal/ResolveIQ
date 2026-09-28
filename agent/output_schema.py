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
    "learning_signal",
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

        if result.get("status") not in ["success", "fallback"]:
        return {
            "valid": False,
            "missing_fields": [],
            "error": "Invalid agent status."
        }

    return {
        "valid": True,
        "missing_fields": []
    }
