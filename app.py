import os
import streamlit as st

from hindsight import HindsightEmbedded

from agent.agent_runner import run_agent_with_memory


# ============================================================
# PAGE CONFIG
# ============================================================

st.set_page_config(
    page_title="ResolveIQ",
    page_icon="🧠",
    layout="wide",
)


# ============================================================
# SECRETS
# ============================================================

def get_secret(name, default=""):
    try:
        value = st.secrets.get(name)
        if value:
            return value
    except Exception:
        pass

    return os.getenv(name, default)


GROQ_API_KEY = get_secret("GROQ_API_KEY")
HINDSIGHT_MODEL = get_secret(
    "HINDSIGHT_API_LLM_MODEL",
    "openai/gpt-oss-20b",
)

BANK_ID = "resolveiq"


# ============================================================
# HINDSIGHT EMBEDDED CLIENT
# ============================================================

@st.cache_resource
def get_hindsight_client():
    if not GROQ_API_KEY:
        raise RuntimeError(
            "GROQ_API_KEY is missing from Streamlit Secrets."
        )

    return HindsightEmbedded(
        profile="resolveiq",
        llm_provider="groq",
        llm_model=HINDSIGHT_MODEL,
        llm_api_key=GROQ_API_KEY,
    )


def get_hindsight():
    return get_hindsight_client()


# ============================================================
# HINDSIGHT HELPERS
# ============================================================

def recall_memories(query):
    client = get_hindsight()

    response = client.recall(
        bank_id=BANK_ID,
        query=query,
    )

    results = response.results

    normalized = []

    for result in results:
        normalized.append({
            "id": getattr(result, "id", None),
            "text": getattr(result, "text", str(result)),
            "type": getattr(result, "type", "unknown"),
            "context": getattr(result, "context", ""),
            "metadata": getattr(result, "metadata", {}),
            "entities": getattr(result, "entities", []),
            "mentioned_at": getattr(result, "mentioned_at", None),
        })

    return normalized

    for result in results:
        if isinstance(result, dict):
            normalized.append(result)
            continue

        normalized.append({
            "id": getattr(result, "id", None),
            "text": getattr(result, "text", str(result)),
            "type": getattr(result, "type", "unknown"),
            "context": getattr(result, "context", ""),
            "metadata": getattr(result, "metadata", {}),
            "entities": getattr(result, "entities", []),
            "mentioned_at": getattr(
                result,
                "mentioned_at",
                None,
            ),
        })

    return normalized


def save_memory(memory):
    client = get_hindsight()

    return client.retain(
        bank_id=BANK_ID,
        content=memory,
    )


# ============================================================
# HEADER
# ============================================================

st.title("🧠 ResolveIQ")

st.subheader(
    "Escalation Intelligence powered by organizational memory"
)

st.caption(
    "Remember → Recall → Decide → Resolve → Learn"
)

if GROQ_API_KEY:
    st.success(
        "🟢 Hindsight Embedded + Groq configured"
    )
else:
    st.error(
        "🔴 GROQ_API_KEY is missing."
    )


# ============================================================
# CASE INPUT
# ============================================================

st.header("🎫 Customer Escalation")

col1, col2 = st.columns(2)

with col1:
    customer_id = st.text_input(
        "Customer ID",
        value="C205",
    )

with col2:
    issue = st.text_input(
        "Issue",
        value="Payment failed",
    )

description = st.text_area(
    "Customer description",
    value=(
        "Customer says their payment has failed multiple times "
        "despite retrying the transaction."
    ),
    height=110,
)


# ============================================================
# ANALYZE CASE
# ============================================================

if st.button(
    "🔍 Analyze Case",
    type="primary",
    use_container_width=True,
):

    query = f"""
Customer ID: {customer_id}

Current issue:
{issue}

Customer description:
{description}

Find organizational memories relevant to this case.

Prioritize:
- similar payment failures
- previous troubleshooting attempts
- failed troubleshooting attempts
- successful resolutions
- recurring failure patterns
- previous escalations
- teams involved
- lessons learned
- cases where repeating the same approach failed

The goal is to determine whether historical experience
supports continued troubleshooting or escalation.
"""

    with st.spinner(
        "🧠 Recalling organizational experience..."
    ):
        try:
            results = recall_memories(query)

        except Exception as error:
            st.error(
                "Hindsight Embedded could not start or recall memory."
            )
            st.code(str(error))
            st.stop()

    ticket = {
        "customer_id": customer_id,
        "issue": issue,
        "description": description,
    }

    def recall_historical_cases(
        customer_id,
        issue,
        description,
    ):
        return results

    with st.spinner(
        "🤖 ResolveIQ is reasoning over the experience..."
    ):
        agent_result = run_agent_with_memory(
            ticket,
            recall_historical_cases,
        )

    st.session_state["analysis_complete"] = True
    st.session_state["results"] = results
    st.session_state["agent_result"] = agent_result
    st.session_state["customer_id"] = customer_id
    st.session_state["issue"] = issue
    st.session_state["description"] = description


# ============================================================
# RESULTS
# ============================================================

if st.session_state.get(
    "analysis_complete",
    False,
):

    results = st.session_state.get(
        "results",
        [],
    )

    agent_result = st.session_state.get(
        "agent_result",
        {},
    )

    action = agent_result.get(
        "escalation_action",
        {},
    )

    failed_attempts = agent_result.get(
        "previous_failed_attempts",
        [],
    )

    previous_escalations = agent_result.get(
        "previous_escalations",
        [],
    )

    successful_resolutions = agent_result.get(
        "successful_resolutions",
        [],
    )

    recurring_issue = agent_result.get(
        "recurring_issue",
        False,
    )

    escalate = (
        action.get("action") == "ESCALATE"
    )

    recommended_team = action.get(
        "team",
        "Customer Support",
    )


    # ========================================================
    # CASE ANALYSIS
    # ========================================================

    st.divider()

    st.header("📊 Case Analysis")

    m1, m2, m3, m4 = st.columns(4)

    with m1:
        st.metric(
            "Historical Matches",
            len(results),
        )

    with m2:
        st.metric(
            "Recurring Issue",
            "YES" if recurring_issue else "NO",
        )

    with m3:
        st.metric(
            "Failed Attempts",
            len(failed_attempts),
        )

    with m4:
        st.metric(
            "Previous Escalations",
            len(previous_escalations),
        )


    # ========================================================
    # RECOMMENDATION
    # ========================================================

    st.header(
        "🚨 ResolveIQ Recommendation"
    )

    if escalate:

        st.error(
            "🔴 ESCALATION RECOMMENDED"
        )

        st.write(
            f"### 🏢 Recommended Team: "
            f"{recommended_team}"
        )

        st.write(
            "ResolveIQ recalled repeated unsuccessful "
            "troubleshooting and recommends avoiding "
            "the same ineffective approach."
        )

    else:

        st.success(
            "🟢 CONTINUE TROUBLESHOOTING"
        )

        st.write(
            "Historical experience does not yet provide "
            "enough evidence to justify escalation."
        )


    # ========================================================
    # MEMORY
    # ========================================================

    st.header(
        "🧠 What Hindsight Remembered"
    )

    if results:

        for index, memory in enumerate(
            results[:5],
            start=1,
        ):

            with st.expander(
                f"Historical memory #{index}",
                expanded=(index == 1),
            ):

                st.write(
                    memory.get(
                        "text",
                        "No memory text available.",
                    )
                )

                memory_type = memory.get(
                    "type",
                    "unknown",
                )

                if memory_type:
                    st.caption(
                        f"Memory type: {memory_type}"
                    )

    else:

        st.info(
            "No relevant organizational memory was found."
        )


    # ========================================================
    # AI REASONING
    # ========================================================

    st.header(
        "🤖 AI Agent Reasoning"
    )

    st.info(
        agent_result.get(
            "ai_reasoning",
            "No AI reasoning was returned.",
        )
    )


    # ========================================================
    # LEARNING SIGNAL
    # ========================================================

    st.header(
        "📚 Learning Signal"
    )

    st.info(
        agent_result.get(
            "learning_signal",
            "No learning signal available.",
        )
    )


    # ========================================================
    # DECISION EXPLANATION
    # ========================================================

    st.header(
        "💡 Why this decision?"
    )

    st.write(
        f"**Recurring issue:** "
        f"{'Yes' if recurring_issue else 'No'}"
    )

    st.write(
        f"**Historical failed attempts:** "
        f"{len(failed_attempts)}"
    )

    st.write(
        f"**Previous escalations:** "
        f"{len(previous_escalations)}"
    )

    st.write(
        f"**Recommended team:** "
        f"{recommended_team}"
    )

    st.write(
        agent_result.get(
            "reason",
            "No additional reason was returned.",
        )
    )


    # ========================================================
    # SUCCESSFUL RESOLUTIONS
    # ========================================================

    if successful_resolutions:

        st.header(
            "✅ Previously Successful Resolutions"
        )

        for resolution in successful_resolutions[:5]:

            st.write(
                f"• {resolution}"
            )


    # ========================================================
    # SAVE NEW EXPERIENCE
    # ========================================================

    st.divider()

    st.header(
        "🧠 Teach ResolveIQ What Happened"
    )

    st.caption(
        "The outcome becomes organizational experience "
        "for future cases."
    )

    resolution = st.text_area(
        "What resolved the issue?",
        value=(
            "Payment Operations fixed the payment gateway "
            "configuration and successfully processed the transaction."
        ),
        height=100,
        key="resolution_input",
    )

    if st.button(
        "🧠 Save Resolution to Hindsight",
        use_container_width=True,
    ):

        customer_id_saved = st.session_state.get(
            "customer_id",
            customer_id,
        )

        issue_saved = st.session_state.get(
            "issue",
            issue,
        )

        description_saved = st.session_state.get(
            "description",
            description,
        )

        memory = f"""
Customer ID: {customer_id_saved}

Issue: {issue_saved}

Customer description:
{description_saved}

Resolution:
{resolution}

Organizational lesson:
This case should be remembered so future similar cases
can use the successful resolution and avoid repeating
previously unsuccessful troubleshooting.
"""

        with st.spinner(
            "🧠 Retaining new organizational experience..."
        ):

            try:

                save_memory(memory)

                st.success(
                    "✅ Experience retained in Hindsight."
                )

                st.info(
                    "Run the same type of case again to "
                    "demonstrate how ResolveIQ learns from it."
                )

            except Exception as error:

                st.error(
                    "Could not retain the new experience."
                )

                st.code(str(error))


# ============================================================
# FOOTER
# ============================================================

st.divider()

st.caption(
    "ResolveIQ · Remember → Recall → Decide → Resolve → Learn"
)
