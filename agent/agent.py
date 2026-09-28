import os

from groq import Groq
from dotenv import load_dotenv

from .prompts import SYSTEM_PROMPT, build_agent_prompt

from .memory_parser import format_historical_context


load_dotenv()

ESCALATION_TOOL = {
    "type": "function",
    "function": {
        "name": "evaluate_escalation",
        "description": (
            "Evaluate whether a support issue should be escalated "
            "using historical failure and escalation evidence."
        ),
        "parameters": {
            "type": "object",
            "properties": {
                "recurring_issue": {
                    "type": "boolean",
                    "description": "Whether the issue appears recurring."
                },
                "failed_attempts": {
                    "type": "integer",
                    "description": "Number of failed historical attempts."
                },
                "previous_escalations": {
                    "type": "integer",
                    "description": "Number of previous escalations recalled."
                }
            },
            "required": [
                "recurring_issue",
                "failed_attempts",
                "previous_escalations"
            ]
        }
    }
}


def run_agent(ticket, historical_cases):
    """
    Run the ResolveIQ AI escalation agent.
    """

    # Build context from current ticket and historical memory
  formatted_context = format_historical_context(
    historical_cases
)

agent_prompt = build_agent_prompt(
    ticket,
    formatted_context
)

    # Get API key
    api_key = os.getenv("GROQ_API_KEY")

    if not api_key:
        return {
            "agent": "ResolveIQ",
            "status": "error",
            "error": "GROQ_API_KEY is not configured."
        }

    try:
        client = Groq(api_key=api_key)

        response = client.chat.completions.create(
            model="llama-3.3-70b-versatile",
                        tools=[ESCALATION_TOOL],
            messages=[
                {
                    "role": "system",
                    "content": SYSTEM_PROMPT
                },
                {
                    "role": "user",
                    "content": agent_prompt
                }
            ],
            temperature=0.2,
        )

        message = response.choices[0].message

if getattr(message, "tool_calls", None):
    tool_call = message.tool_calls[0]

    if tool_call.function.name != "evaluate_escalation":
        raise ValueError(
            f"Unsupported tool requested: "
            f"{tool_call.function.name}"
        )

    ai_reasoning = (
        "ResolveIQ requested escalation analysis using "
        "historical evidence before producing its recommendation."
    )

else:
    ai_reasoning = message.content

              return {
            "agent": "ResolveIQ",
            "status": "success",
            "prompt_version": "v3",
            "ai_reasoning": ai_reasoning
              }
       except Exception as error:

        return {
            "agent": "ResolveIQ",
            "status": "fallback",
            "prompt_version": "v3",
            "ai_reasoning": (
                "LLM unavailable. "
                "ResolveIQ will rely on Hindsight memory "
                "and its structured escalation logic."
            ),
            "error": str(error)
        }

    action = get_escalation_action(
        decision["severity"],
        decision["recurring_issue"],
        decision["previous_failed_attempts"]
    )

    return {
        **decision,
        "escalation_action": action,
        "agent": "ResolveIQ",
        "status": "fallback",
        "prompt_version": "v3",
        "ai_reasoning": (
            "LLM unavailable. "
            "ResolveIQ used its structured escalation logic."
        ),
        "error": str(error)
    }
