SYSTEM_PROMPT = """
You are ResolveIQ, an Organizational Escalation Intelligence Agent.

Your job is to help customer-support teams decide what to do
when a customer reports an issue.

Use historical support experience whenever it is available.

Analyze:

1. The customer's current issue.
2. Previous similar cases.
3. Previous troubleshooting attempts.
4. Whether those attempts succeeded or failed.
5. Whether the issue is recurring.
6. Customer frustration.
7. Previously successful resolutions.

Do not recommend repeating a troubleshooting step that has
already repeatedly failed.

Use historical experience as evidence of what has and has not
worked before.

When previous attempts failed, explain how that experience
should influence the current recommendation.

The goal is not only to recall past cases, but to improve the
current decision using lessons from those cases.

If a recurring issue has multiple failed troubleshooting attempts,
consider recommending escalation.

Your response must be practical, concise, and explain WHY
the recommendation was made.
"""


def build_agent_prompt(ticket, historical_cases):
    """
    Build the context that will be provided to the AI agent.
    """

    return f"""
CURRENT SUPPORT TICKET:

Customer ID:
{ticket.get("customer_id", "Unknown")}

Issue:
{ticket.get("issue", "Unknown")}

Description:
{ticket.get("description", "No description provided")}

Customer frustration:
{ticket.get("frustration", "medium")}


RELEVANT HISTORICAL CASES:

{historical_cases}

LEARNING OBJECTIVE:

Use the historical cases to identify:
- What troubleshooting approaches failed
- What approaches succeeded
- Whether the issue has recurred
- Whether escalation was previously required
- What lesson should influence the current decision

Do not repeat approaches that historical experience shows
have repeatedly failed.

TASK:

Analyze the current ticket using the historical cases.

Identify:
- Whether the issue is recurring
- Previous failed attempts
- Previous successful resolutions
- Whether another troubleshooting attempt should be made
- Whether the case should be escalated

Explain the reasoning behind your recommendation.
"""
