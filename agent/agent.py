import os

from groq import Groq
from dotenv import load_dotenv

from .decision import analyze_escalation, get_escalation_action
from .prompts import SYSTEM_PROMPT, build_agent_prompt

from .memory_parser import prepare_historical_context


load_dotenv()


def run_agent(ticket, historical_cases):
    """
    Run the ResolveIQ AI escalation agent.
    """

    # Build context from current ticket and historical memory
    historical_context = prepare_historical_context(
    historical_cases
)

agent_prompt = build_agent_prompt(
    ticket,
    historical_context
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

        ai_reasoning = response.choices[0].message.content

        # Structured escalation decision
        decision = analyze_escalation(
            ticket,
            historical_cases
        )

        return {
    **decision,
    "escalation_action": action,
    "agent": "ResolveIQ",
    "status": "success",
    "prompt_version": "v3",
    "ai_reasoning": ai_reasoning
}
   except Exception as error:
    # Fallback to the rule-based decision engine
    decision = analyze_escalation(
        ticket,
        historical_cases
    )

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
