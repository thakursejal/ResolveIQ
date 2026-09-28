from .agent import run_agent
from .decision import analyze_hindsight_memories, get_escalation_action
from .memory_parser import prepare_historical_context
from .output_schema import validate_agent_output


def run_agent_with_memory(ticket, recall_historical_cases):
    """
    Run ResolveIQ using historical memories recalled by Hindsight.

    Flow:
    Hindsight Recall
        ↓
    Memory Preparation
        ↓
    Memory Analysis
        ↓
    AI Reasoning
        ↓
    Operational Decision
        ↓
    Output Validation
    """

    # 1. Recall relevant memories from Hindsight
    memory_records = recall_historical_cases(
        customer_id=ticket.get("customer_id", ""),
        issue=ticket.get("issue", ""),
        description=ticket.get("description", "")
    )
    
    if memory_records is None:
    memory_records = []

    # 2. Prepare Hindsight memories for the AI agent
    historical_context = prepare_historical_context(
        memory_records
    )

    # 3. Analyze the recalled memories
    memory_analysis = analyze_hindsight_memories(
        ticket,
        historical_context
    )

    # 4. Run the AI reasoning layer
    ai_result = run_agent(
        ticket,
        historical_context
    )

    # 5. Determine operational action from memory evidence
   action = get_escalation_action(
    "high"
    if (
        memory_analysis["recurring_issue"]
        and len(memory_analysis["failed_attempts"]) >= 2
    )
    else ai_result.get("severity", "medium"),
    memory_analysis["recurring_issue"],
    memory_analysis["failed_attempts"],
    memory_analysis["previous_escalations"]
)

    # 6. Determine final severity
    severity = (
        "high"
        if action["priority"] == "HIGH"
        else "medium"
    )

    # 7. Build a consistent recommendation
  if action["action"] == "ESCALATE":

    recommendation = (
        f"Escalate to {action['team']}"
    )

    reason = (
        "Hindsight recalled a recurring issue with "
        f"{len(memory_analysis['failed_attempts'])} "
        "unsuccessful troubleshooting attempts. "
        "Repeating the same failed approach is not recommended."
    )

    elif memory_analysis["successful_resolutions"]:

        recommendation = (
            "Try a previously successful resolution"
        )

        reason = (
            "Hindsight recalled a previous successful "
            "resolution for a related case."
        )

    else:

        recommendation = (
            "Continue standard troubleshooting"
        )

        reason = (
            "Hindsight did not provide enough evidence "
            "of repeated failure to justify escalation."
        )

    # 8. Construct final agent result
    result = {
        "agent": "ResolveIQ",
        "status": ai_result.get("status", "success"),
        "severity": severity,
        "recurring_issue": memory_analysis["recurring_issue"],
        "previous_failed_attempts": memory_analysis[
            "failed_attempts"
        ],
        "previous_escalations": memory_analysis[
            "previous_escalations"
        ],
        "successful_resolutions": memory_analysis[
            "successful_resolutions"
        ],
        "escalation_action": action,
        "memory_count": memory_analysis["memory_count"],
        "learning_signal": (
    "Repeated failures detected from historical cases."
    if len(memory_analysis["failed_attempts"]) >= 2
    else
    "Previous experience recalled, but repeated failure "
    "was not established."
),
        "recommendation": recommendation,
        "reason": reason,
        "ai_reasoning": ai_result.get(
            "ai_reasoning",
            "No AI reasoning was returned."
        )
    }

    # 9. Validate final output structure
    validation = validate_agent_output(result)

    result["output_valid"] = validation["valid"]

    if not validation["valid"]:
        result["missing_output_fields"] = (
            validation["missing_fields"]
        )

    return result
