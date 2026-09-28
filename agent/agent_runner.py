from .agent import run_agent
from .decision import analyze_hindsight_memories, get_escalation_action
from .memory_parser import prepare_historical_context


def run_agent_with_memory(ticket, recall_historical_cases):
    """
    Run ResolveIQ using historical memories recalled by Hindsight.
    """

    # 1. Recall relevant memories from Hindsight
    memory_records = recall_historical_cases(
        customer_id=ticket.get("customer_id", ""),
        issue=ticket.get("issue", ""),
        description=ticket.get("description", "")
    )

    # 2. Prepare memories for the AI prompt
    historical_context = prepare_historical_context(
        memory_records
    )

    # 3. Analyze Hindsight memories for escalation signals
    memory_analysis = analyze_hindsight_memories(
        ticket,
        historical_context
    )

    # 4. Run the AI reasoning layer
    ai_result = run_agent(
        ticket,
        historical_context
    )

    # 5. Determine operational escalation action
    severity = "high" if (
        memory_analysis["recurring_issue"]
        and len(memory_analysis["failed_attempts"]) >= 2
    ) else ai_result.get("severity", "medium")

    action = get_escalation_action(
        severity,
        memory_analysis["recurring_issue"],
        memory_analysis["failed_attempts"]
    )

    return {
        **ai_result,
        "severity": severity,
        "recurring_issue": memory_analysis["recurring_issue"],
        "previous_failed_attempts": memory_analysis["failed_attempts"],
        "previous_escalations": memory_analysis["previous_escalations"],
        "successful_resolutions": memory_analysis["successful_resolutions"],
        "escalation_action": action,
        "memory_count": memory_analysis["memory_count"]
    }
