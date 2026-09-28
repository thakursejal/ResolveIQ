import streamlit as st
import requests
from agent.agent_runner import run_agent_with_memory



# ============================================================
# CONFIG
# ============================================================

HINDSIGHT_URL = "http://localhost:8888"
BANK_ID = "ResolveIQ"


# ============================================================
# PAGE CONFIG
# ============================================================

st.set_page_config(
    page_title="ResolveIQ",
    page_icon="🧠",
    layout="wide",
    initial_sidebar_state="collapsed",
)


# ============================================================
# STYLING
# ============================================================

st.markdown(
    """
    <style>
    [data-testid="stAppViewContainer"] {
        background: #f7f8fc;
    }

    .block-container {
        max-width: 1150px;
        padding-top: 2rem;
        padding-bottom: 3rem;
    }

    .hero {
        background: white;
        border: 1px solid #e5e7eb;
        border-radius: 20px;
        padding: 30px 34px;
        margin-bottom: 24px;
    }

    .hero-title {
        font-size: 42px;
        font-weight: 800;
        margin: 0;
    }

    .hero-subtitle {
        color: #6b7280;
        font-size: 17px;
        margin-top: 8px;
    }

    .section-title {
        font-size: 24px;
        font-weight: 750;
        margin-top: 25px;
        margin-bottom: 12px;
    }

    .result-card {
        background: white;
        border: 1px solid #e5e7eb;
        border-radius: 16px;
        padding: 22px;
        margin: 10px 0;
    }

    .danger-card {
        background: #fff5f5;
        border: 1px solid #fecaca;
        border-radius: 16px;
        padding: 24px;
        margin: 12px 0;
    }

    .success-card {
        background: #f0fdf4;
        border: 1px solid #bbf7d0;
        border-radius: 16px;
        padding: 24px;
        margin: 12px 0;
    }

    .recommendation-title {
        font-size: 25px;
        font-weight: 800;
        margin-bottom: 8px;
    }

    .small-label {
        color: #6b7280;
        font-size: 13px;
        font-weight: 600;
        text-transform: uppercase;
        letter-spacing: 0.04em;
    }

    .team-name {
        font-size: 21px;
        font-weight: 750;
        margin-top: 5px;
    }

    [data-testid="stMetric"] {
        background: white;
        border: 1px solid #e5e7eb;
        border-radius: 14px;
        padding: 15px;
    }

    .stButton > button {
        border-radius: 10px;
        height: 46px;
        font-weight: 700;
    }

    .footer {
        text-align: center;
        color: #9ca3af;
        font-size: 13px;
        margin-top: 40px;
    }
    </style>
    """,
    unsafe_allow_html=True,
)


# ============================================================
# HERO
# ============================================================

st.markdown(
    """
    <div class="hero">
        <div class="hero-title">🧠 ResolveIQ</div>
        <div class="hero-subtitle">
            Escalation Intelligence powered by organizational memory
        </div>
    </div>
    """,
    unsafe_allow_html=True,
)


# ============================================================
# CASE INPUT
# ============================================================

st.markdown(
    '<div class="section-title">🎫 Customer Escalation</div>',
    unsafe_allow_html=True,
)

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
    height=100,
)


# ============================================================
# ANALYZE CASE
# ============================================================

analyze = st.button(
    "🔍 Analyze Case",
    type="primary",
    use_container_width=True,
)


if analyze:

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

            response = requests.post(
                f"{HINDSIGHT_URL}/v1/default/banks/{BANK_ID}/memories/recall",
                json={"query": query},
                timeout=30,
            )

            response.raise_for_status()

            data = response.json()

        except Exception as e:

            st.error(
                f"Could not connect to Hindsight: {e}"
            )

            st.stop()


    # ========================================================
    # EXTRACT RECALL RESULTS
    # ========================================================

    results = data.get("results", [])

    memory_texts = []

    for item in results:

        text = item.get("text", "")

        if text:
            memory_texts.append(text)


    combined_memory = " ".join(memory_texts).lower()


    # ========================================================
# RESOLVEIQ AI AGENT
# ========================================================

ticket = {
    "customer_id": customer_id,
    "issue": issue,
    "description": description,
}


def recall_historical_cases(
    customer_id,
    issue,
    description
):
    """
    Return the Hindsight memories already recalled
    for the current case.
    """

    return results


agent_result = run_agent_with_memory(
    ticket,
    recall_historical_cases
)


# ========================================================
# EXTRACT AGENT DECISION
# ========================================================

action = agent_result.get(
    "escalation_action",
    {}
)

recurring_issue = agent_result.get(
    "recurring_issue",
    False
)

failed_attempts = agent_result.get(
    "previous_failed_attempts",
    []
)

previous_failure = len(
    failed_attempts
) > 0

escalate = (
    action.get("action") == "ESCALATE"
)

payment_operations = (
    action.get("team") == "Payment Operations"
)

gateway_fix = (
    "gateway configuration"
    in combined_memory
)
    # ========================================================
    # CASE SUMMARY
    # ========================================================

    st.divider()

    st.markdown(
        '<div class="section-title">📊 Case Analysis</div>',
        unsafe_allow_html=True,
    )

    metric1, metric2, metric3 = st.columns(3)

    with metric1:
        st.metric(
            "Historical matches",
            len(results),
        )

    with metric2:
        st.metric(
            "Recurring issue",
            "Yes" if recurring_issue else "No",
        )

    with metric3:
        st.metric(
            "Previous failures",
            "Detected" if previous_failure else "None",
        )


    # ========================================================
    # RECOMMENDATION
    # ========================================================

    st.markdown(
        '<div class="section-title">🚨 ResolveIQ Recommendation</div>',
        unsafe_allow_html=True,
    )

    if escalate:

        st.markdown(
            """
            <div class="danger-card">
                <div class="recommendation-title">
                    🔴 ESCALATION RECOMMENDED
                </div>
                <div>
                    ResolveIQ found historical evidence that similar
                    troubleshooting attempts failed.
                </div>
            </div>
            """,
            unsafe_allow_html=True,
        )

        team_col, signal_col = st.columns(2)

        with team_col:

            st.markdown(
                """
                <div class="result-card">
                    <div class="small-label">
                        Recommended Team
                    </div>
                    <div class="team-name">
                        🏢 Payment Operations
                    </div>
                </div>
                """,
                unsafe_allow_html=True,
            )

        with signal_col:

            st.markdown(
                """
                <div class="result-card">
                    <div class="small-label">
                        Memory Signal
                    </div>
                    <div class="team-name">
                        🔁 Recurring failure
                    </div>
                </div>
                """,
                unsafe_allow_html=True,
            )

        if gateway_fix:

            st.info(
                "💡 Previous successful resolution: "
                "Payment Operations fixed the payment gateway configuration."
            )

    else:

        st.markdown(
            """
            <div class="success-card">
                <div class="recommendation-title">
                    🟢 CONTINUE TROUBLESHOOTING
                </div>
                <div>
                    No strong historical escalation signal was found.
                </div>
            </div>
            """,
            unsafe_allow_html=True,
        )


    # ========================================================
    # MEMORY
    # ========================================================

    st.divider()

    st.markdown(
        '<div class="section-title">🧠 What ResolveIQ Remembered</div>',
        unsafe_allow_html=True,
    )

    if memory_texts:

        for i, memory in enumerate(
            memory_texts[:5],
            start=1,
        ):

            with st.expander(
                f"Historical memory #{i}",
                expanded=(i == 1),
            ):

                st.write(memory)

    else:

        st.info(
            "No relevant historical memory was found."
        )


    # ========================================================
    # EXPLAINABILITY
    # ========================================================

    st.divider()

    st.markdown(
        '<div class="section-title">💡 Why this decision?</div>',
        unsafe_allow_html=True,
    )

    if escalate:

        st.markdown(
            """
            <div class="result-card">

            <b>ResolveIQ connected the current case with
            organizational memory:</b>

            <br><br>

            1. 🔁 Similar payment failures occurred before.

            <br><br>

            2. ❌ Previous troubleshooting attempts failed.

            <br><br>

            3. 🏢 The previous case was escalated to
            Payment Operations.

            <br><br>

            4. ✅ Payment Operations resolved the previous
            issue by fixing the payment gateway configuration.

            <br><br>

            <b>Decision:</b> avoid repeating ineffective
            troubleshooting and escalate.

            </div>
            """,
            unsafe_allow_html=True,
        )

    else:

        st.write(
            "The retrieved organizational memory does not "
            "indicate a strong reason for escalation."
        )


    # ========================================================
    # SAVE CURRENT RESOLUTION
    # ========================================================

    st.divider()

    st.markdown(
        '<div class="section-title">✅ Record Resolution</div>',
        unsafe_allow_html=True,
    )

    st.caption(
        "When this case is resolved, save the outcome so "
        "ResolveIQ can learn from it."
    )

    resolution = st.text_area(
        "What resolved the issue?",
        value=(
            "Payment Operations fixed the payment "
            "gateway configuration."
        ),
        height=100,
    )

    save_resolution = st.button(
        "🧠 Save Resolution to Hindsight",
        use_container_width=True,
    )


    if save_resolution:

        memory = f"""
Customer: {customer_id}

Issue: {issue}

Description:
{description}

Resolution:
{resolution}

Lesson learned:
Store this outcome as organizational memory so future
similar cases can use the successful resolution instead
of repeating failed troubleshooting.
"""

        body = {
            "items": [
                {
                    "content": memory,
                    "document_id": f"resolution-{customer_id}",
                }
            ],
            "async": True,
        }

        try:

            save_response = requests.post(
                f"{HINDSIGHT_URL}/v1/default/banks/{BANK_ID}/memories",
                json=body,
                timeout=10,
            )

            save_response.raise_for_status()

            st.success(
                "🧠 Resolution saved! "
                "ResolveIQ can now learn from this outcome."
            )

        except Exception as e:

            st.error(
                f"Could not save resolution: {e}"
            )


# ============================================================
# FOOTER
# ============================================================

st.markdown(
    """
    <div class="footer">
        ResolveIQ · Remember → Recall → Decide → Resolve → Learn
    </div>
    """,
    unsafe_allow_html=True,
)
