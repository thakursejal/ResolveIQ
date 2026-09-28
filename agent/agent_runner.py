from .agent import run_agent
from .memory_parser import prepare_historical_context


def run_agent_with_memory(ticket, recall_historical_cases):
    """
    Connect ResolveIQ's AI agent with the Hindsight recall interface.

    Parameters:
        ticket: Current support ticket.
        recall_historical_cases: Member 1's Hindsight recall function.

    Returns:
        ResolveIQ escalation analysis.
    """

    memory_records = recall_historical_cases(
        customer_id=ticket.get("customer_id", ""),
        issue=ticket.get("issue", ""),
        description=ticket.get("description", "")
    )

    historical_context = prepare_historical_context(
        memory_records
    )

    return run_agent(
        ticket,
        historical_context
    )
