import os
import requests
import streamlit as st

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
# HINDSIGHT CONFIG
# ============================================================

def get_secret(name, default=""):
    try:
        if name in st.secrets:
            return st.secrets[name]
    except Exception:
        pass
    return os.getenv(name, default)


HINDSIGHT_BASE_URL = get_secret(
    "HINDSIGHT_BASE_URL",
    "https://api.hindsight.vectorize.io",
)
HINDSIGHT_API_KEY = get_secret("HINDSIGHT_API_KEY", "")
BANK_ID = get_secret("HINDSIGHT_BANK_ID", "ResolveIQ")


def hindsight_headers():
    return {
        "Authorization": f"Bearer {HINDSIGHT_API_KEY}",
        "Content-Type": "application/json",
        "Accept": "application/json",
    }


def recall_memories(query):
    if not HINDSIGHT_API_KEY:
        raise RuntimeError(
            "HINDSIGHT_API_KEY is missing from Streamlit Secrets."
        )

    url = (
        f"{HINDSIGHT_BASE_URL}"
        f"/v1/default/banks/{BANK_ID}/memories/recall"
    )

    response = requests.post(
        url,
        headers=hindsight_headers(),
        json={"query": query},
        timeout=30,
    )
    response.raise_for_status()
    return response.json()


def save_memory(memory):
    if not HINDSIGHT_API_KEY:
        raise RuntimeError(
            "HINDSIGHT_API_KEY is missing from Streamlit Secrets."
        )

    url = (
        f"{HINDSIGHT_BASE_URL}"
        f"/v1/default/banks/{BANK_ID}/memories"
    )

    response = requests.post(
        url,
        headers=hindsight_headers(),
        json={
            "items": [{"content": memory}],
            "async": True,
        },
        timeout=20,
    )
    response.raise_for_status()
    return response.json()


# ============================================================
# HEADER
# ============================================================

st.title("🧠 ResolveIQ")
st.subheader("Escalation Intelligence powered by organizational memory")
st.caption("Remember → Recall → Decide → Resolve → Learn")

if HINDSIGHT_API_KEY:
    st.success("🟢 Connected to Hindsight Cloud")
else:
    st.warning("Hindsight API key is not configured in Streamlit Secrets.")


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
    value="Customer says their payment has failed multiple times.",
    height=110,
)


# ============================================================
# ANALYZE
# ============================================================

if st.button("🔍 Analyze Case", type="primary", use_container_width=True):

    query = f"""
Customer ID: {customer_id}

Issue: {issue}

Description:
{description}

Find relevant historical organizational memory.

Identify:
- previous similar cases
- troubleshooting attempts
- failed attempts
- successful resolutions
- recurring patterns
- escalation lessons
- teams that previously resolved the issue

Use the historical memory to help decide whether this case
should be escalated or continue troubleshooting.
"""

    with st.spinner("🧠 Recalling organizational memory..."):
        try:
            data = recall_memories(query)
        except requests.exceptions.HTTPError as error:
            status_code = (
                error.response.status_code
                if error.response is not None
                else "unknown"
            )
            st.error(f"Hindsight request failed (HTTP {status_code}).")

            if status_code == 401:
                st.info("The Hindsight API key is invalid, expired, or unauthorized.")
            elif status_code == 404:
                st.info(f"The Hindsight bank '{BANK_ID}' was not found.")
            elif status_code == 402:
                st.info("Hindsight reports insufficient credits.")
            st.stop()
        except Exception as error:
            st.error(f"Could not connect to Hindsight Cloud: {error}")
            st.stop()

    results = data.get("results", [])
    if not isinstance(results, list):
        results = []

    ticket = {
        "customer_id": customer_id,
        "issue": issue,
        "description": description,
    }

    def recall_historical_cases(customer_id, issue, description):
        return results

    with st.spinner("🤖 ResolveIQ is analyzing the case..."):
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

if st.session_state.get("analysis_complete", False):

    results = st.session_state.get("results", [])
    agent_result = st.session_state.get("agent_result", {})

    action = agent_result.get("escalation_action", {})
    failed_attempts = agent_result.get("previous_failed_attempts", [])
    previous_escalations = agent_result.get("previous_escalations", [])
    successful_resolutions = agent_result.get("successful_resolutions", [])

    recurring_issue = agent_result.get("recurring_issue", False)
    escalate = action.get("action") == "ESCALATE"
    recommended_team = action.get("team", "Customer Support")

    st.divider()
    st.header("📊 Case Analysis")

    m1, m2, m3, m4 = st.columns(4)

    with m1:
        st.metric("Historical Matches", len(results))

    with m2:
        st.metric("Recurring Issue", "Yes" if recurring_issue else "No")

    with m3:
        st.metric("Failed Attempts", len(failed_attempts))

    with m4:
        st.metric("Previous Escalations", len(previous_escalations))

    st.header("🚨 ResolveIQ Recommendation")

    if escalate:
        st.error("🔴 ESCALATION RECOMMENDED")
        st.write(f"**Recommended Team:** 🏢 {recommended_team}")
        st.write(
            "ResolveIQ recalled repeated unsuccessful troubleshooting "
            "and recommends avoiding the same ineffective approach."
        )
    else:
        st.success("🟢 CONTINUE TROUBLESHOOTING")
        st.write(
            "Hindsight did not provide enough historical evidence "
            "to justify escalation."
        )

    st.header("🧠 What ResolveIQ Remembered")

    if results:
        for i, memory in enumerate(results[:5], start=1):
            with st.expander(f"Historical memory #{i}", expanded=(i == 1)):
                if isinstance(memory, dict):
                    st.write(memory.get("text", memory))
                else:
                    st.write(memory)
    else:
        st.info("No relevant historical memory was found.")

    st.header("🤖 AI Agent Reasoning")
    st.info(
        agent_result.get(
            "ai_reasoning",
            "No AI reasoning was returned.",
        )
    )

    st.header("📚 Learning Signal")
    st.info(
        agent_result.get(
            "learning_signal",
            "No learning signal available.",
        )
    )

    st.header("💡 Why this decision?")

    if escalate:
        st.write(
            f"**Recurring issue:** {recurring_issue}"
        )
        st.write(
            f"**Historical failed attempts:** {len(failed_attempts)}"
        )
        st.write(
            f"**Recommended team:** {recommended_team}"
        )
        st.write(
            "ResolveIQ connected the current case with organizational "
            "memory and avoided repeating ineffective troubleshooting."
        )
    else:
        st.write(
            "The recalled organizational memory does not indicate "
            "a strong reason for escalation."
        )

    if successful_resolutions:
        st.header("✅ Previously Successful Resolutions")
        for resolution in successful_resolutions[:5]:
            st.write(f"• {resolution}")

    st.divider()
    st.header("🧠 Record Resolution")
    st.caption(
        "Save the outcome so future cases can learn from this experience."
    )

    resolution = st.text_area(
        "What resolved the issue?",
        value="Payment Operations fixed the payment gateway configuration.",
        height=100,
        key="resolution_input",
    )

    if st.button(
        "🧠 Save Resolution to Hindsight",
        use_container_width=True,
    ):
        customer_id_saved = st.session_state.get("customer_id", customer_id)
        issue_saved = st.session_state.get("issue", issue)
        description_saved = st.session_state.get("description", description)

        memory = f"""
Customer: {customer_id_saved}

Issue: {issue_saved}

Description:
{description_saved}

Resolution:
{resolution}

Lesson learned:
Store this outcome as organizational memory so future similar cases
can use the successful resolution instead of repeating failed troubleshooting.
"""

        with st.spinner("🧠 Saving resolution to Hindsight..."):
            try:
                save_memory(memory)
                st.success(
                    "🧠 Resolution saved successfully! "
                    "ResolveIQ can now learn from this outcome."
                )
            except requests.exceptions.HTTPError as error:
                status_code = (
                    error.response.status_code
                    if error.response is not None
                    else "unknown"
                )
                st.error(f"Could not save memory (HTTP {status_code}).")
            except Exception as error:
                st.error(f"Could not save resolution: {error}")


st.divider()
st.caption(
    "ResolveIQ · Remember → Recall → Decide → Resolve → Learn · "
    "AI-powered escalation intelligence using Hindsight memory"
)
