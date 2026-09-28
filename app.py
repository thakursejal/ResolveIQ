import os
import textwrap
import requests
import streamlit as st
from agent.agent_runner import run_agent_with_memory
def render_html(markup, unsafe_allow_html=True):
    st.markdown(
        textwrap.dedent(markup),
        unsafe_allow_html=unsafe_allow_html,
    )

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
# CONFIG — HINDSIGHT CLOUD
# ============================================================

def get_secret(name, default=""):
    """
    Read a value from Streamlit Secrets first,
    then fall back to environment variables.
    """
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

HINDSIGHT_API_KEY = get_secret(
    "HINDSIGHT_API_KEY",
    "",
)

BANK_ID = get_secret(
    "HINDSIGHT_BANK_ID",
    "ResolveIQ",
)


# ============================================================
# HINDSIGHT API HELPERS
# ============================================================

def hindsight_headers():
    """
    Authentication headers for Hindsight Cloud.
    """
    return {
        "Authorization": f"Bearer {HINDSIGHT_API_KEY}",
        "Content-Type": "application/json",
        "Accept": "application/json",
    }


def recall_memories(query):
    """
    Recall relevant organizational memories from Hindsight.
    """

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
        json={
            "query": query
        },
        timeout=30,
    )

    response.raise_for_status()

    return response.json()


def save_memory(memory):
    """
    Store a new organizational memory in Hindsight.
    """

    if not HINDSIGHT_API_KEY:
        raise RuntimeError(
            "HINDSIGHT_API_KEY is missing from Streamlit Secrets."
        )

    url = (
        f"{HINDSIGHT_BASE_URL}"
        f"/v1/default/banks/{BANK_ID}/memories"
    )

    body = {
        "items": [
            {
                "content": memory
            }
        ],
        "async": True,
    }

    response = requests.post(
        url,
        headers=hindsight_headers(),
        json=body,
        timeout=20,
    )

    response.raise_for_status()

    return response.json()


# ============================================================
# CUSTOM STYLING
# ============================================================

st.markdown(
    """
    <style>

    /* ---------- GLOBAL ---------- */

    .stApp {
        background: #f5f7fb;
        color: #172033;
    }

    [data-testid="stAppViewContainer"] {
        background: #f5f7fb;
    }

    .block-container {
        max-width: 1180px;
        padding-top: 2rem;
        padding-bottom: 4rem;
    }

    /* ---------- TEXT VISIBILITY ---------- */

    p,
    label,
    .stMarkdown,
    .stText,
    .stCaption,
    div[data-testid="stMetricLabel"] {
        color: #172033;
    }

    /* ---------- HERO ---------- */

    .hero {
        background: linear-gradient(
            135deg,
            #ffffff 0%,
            #f8f1ff 100%
        );

        border: 1px solid #e4d8f2;
        border-radius: 24px;

        padding: 32px 36px;
        margin-bottom: 30px;

        box-shadow:
            0 10px 30px rgba(40, 20, 70, 0.08);
    }

    .hero-title {
        color: #171321;
        font-size: 42px;
        font-weight: 850;
        letter-spacing: -1px;
        margin: 0;
    }

    .hero-subtitle {
        color: #5d6070;
        font-size: 17px;
        margin-top: 8px;
    }

    .hero-flow {
        margin-top: 18px;
        color: #7b3fe4;
        font-size: 14px;
        font-weight: 700;
    }

    /* ---------- SECTION TITLES ---------- */

    .section-title {
        color: #171321;
        font-size: 24px;
        font-weight: 800;
        margin-top: 28px;
        margin-bottom: 14px;
    }

    /* ---------- CARDS ---------- */

    .result-card {
        background: #ffffff;
        color: #172033;

        border: 1px solid #e1e5ed;
        border-radius: 16px;

        padding: 22px;
        margin: 10px 0;

        box-shadow:
            0 5px 18px rgba(30, 40, 60, 0.05);
    }

    .result-card b {
        color: #171321;
    }

    .danger-card {
        background: #fff4f4;
        color: #541313;

        border: 1px solid #f4bcbc;
        border-radius: 18px;

        padding: 24px;
        margin: 12px 0;

        box-shadow:
            0 6px 18px rgba(150, 20, 20, 0.06);
    }

    .danger-card div {
        color: #541313;
    }

    .success-card {
        background: #f0fbf4;
        color: #124b28;

        border: 1px solid #bce8c9;
        border-radius: 18px;

        padding: 24px;
        margin: 12px 0;

        box-shadow:
            0 6px 18px rgba(20, 120, 60, 0.05);
    }

    .success-card div {
        color: #124b28;
    }

    .recommendation-title {
        font-size: 25px;
        font-weight: 850;
        margin-bottom: 8px;
    }

    .small-label {
        color: #687083;
        font-size: 12px;
        font-weight: 750;
        text-transform: uppercase;
        letter-spacing: 0.06em;
    }

    .team-name {
        color: #171321;
        font-size: 21px;
        font-weight: 800;
        margin-top: 6px;
    }

    /* ---------- METRICS ---------- */

    [data-testid="stMetric"] {
        background: #ffffff;

        border: 1px solid #e1e5ed;
        border-radius: 16px;

        padding: 18px;

        box-shadow:
            0 5px 18px rgba(30, 40, 60, 0.05);
    }

    [data-testid="stMetricLabel"] {
        color: #687083 !important;
    }

    [data-testid="stMetricValue"] {
        color: #171321 !important;
        font-weight: 800;
    }

    /* ---------- INPUTS ---------- */

    div[data-baseweb="input"] > div,
    div[data-baseweb="textarea"] {
        background: #ffffff;
        border-radius: 10px;
    }

    input,
    textarea {
        color: #171321 !important;
        background: #ffffff !important;
    }

    /* ---------- BUTTON ---------- */

    .stButton > button {
        border-radius: 12px;
        min-height: 48px;

        font-weight: 800;
        font-size: 15px;

        border: 1px solid #d8dce5;
    }

    /* ---------- EXPANDERS ---------- */

    div[data-testid="stExpander"] {
        background: #ffffff;
        border: 1px solid #e1e5ed;
        border-radius: 14px;
        margin-bottom: 10px;
    }

    /* ---------- FOOTER ---------- */

    .footer {
        text-align: center;
        color: #7c8392;

        font-size: 13px;
        margin-top: 45px;

        padding-top: 20px;
        border-top: 1px solid #e1e5ed;
    }

    /* ---------- STATUS ---------- */

    .status-card {
        background: #ffffff;
        border: 1px solid #e1e5ed;
        border-radius: 14px;
        padding: 14px 18px;
        margin-bottom: 20px;
    }

    .status-label {
        color: #687083;
        font-size: 12px;
        font-weight: 750;
        text-transform: uppercase;
    }

    .status-value {
        color: #171321;
        font-size: 15px;
        font-weight: 750;
        margin-top: 3px;
    }

    </style>
    """,
    unsafe_allow_html=True,
)


# ============================================================
# HERO
# ============================================================

render_html(
    """
    <div class="hero">

        <div class="hero-title">
            🧠 ResolveIQ
        </div>

        <div class="hero-subtitle">
            Escalation Intelligence powered by organizational memory
        </div>

        <div class="hero-flow">
            Remember → Recall → Decide → Resolve → Learn
        </div>

    </div>
    """,
    unsafe_allow_html=True,
)


# ============================================================
# CONNECTION STATUS
# ============================================================

if HINDSIGHT_API_KEY:

    render_html(
        """
        <div class="status-card">

            <div class="status-label">
                Hindsight Memory
            </div>

            <div class="status-value">
                🟢 Connected to Hindsight Cloud
            </div>

        </div>
        """,
        unsafe_allow_html=True,
    )

else:

    st.warning(
        "Hindsight API key is not configured in Streamlit Secrets."
    )


# ============================================================
# CASE INPUT
# ============================================================

render_html(
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
    value=(
        "Customer says their payment has failed multiple times."
    ),
    height=110,
)


# ============================================================
# ANALYZE BUTTON
# ============================================================

analyze = st.button(
    "🔍 Analyze Case",
    type="primary",
    use_container_width=True,
)


# ============================================================
# ANALYZE CASE
# ============================================================

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

    with st.spinner(
        "🧠 Recalling organizational memory..."
    ):

        try:

            data = recall_memories(query)

        except requests.exceptions.HTTPError as error:

            status_code = (
                error.response.status_code
                if error.response is not None
                else "unknown"
            )

            st.error(
                f"Hindsight request failed "
                f"(HTTP {status_code})."
            )

            if status_code == 401:

                st.info(
                    "Your Hindsight API key is invalid, "
                    "expired, or not authorized."
                )

            elif status_code == 404:

                st.info(
                    f"The Hindsight bank '{BANK_ID}' "
                    "was not found."
                )

            elif status_code == 402:

                st.info(
                    "Hindsight reports insufficient credits."
                )

            st.stop()

        except Exception as error:

            st.error(
                f"Could not connect to Hindsight Cloud: {error}"
            )

            st.stop()


    # ========================================================
    # EXTRACT MEMORY RESULTS
    # ========================================================

    results = data.get(
        "results",
        []
    )


    memory_texts = []

    for item in results:

        if not isinstance(item, dict):
            continue

        text = item.get(
            "text",
            ""
        )

        if text:
            memory_texts.append(text)


    combined_memory = (
        " ".join(memory_texts)
        .lower()
    )


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
        description,
    ):
        """
        Return the memories already recalled from Hindsight.
        """
        return results


    agent_result = run_agent_with_memory(
        ticket,
        recall_historical_cases,
    )


    # ========================================================
    # EXTRACT AGENT DECISION
    # ========================================================

    action = agent_result.get(
        "escalation_action",
        {},
    )

    recurring_issue = agent_result.get(
        "recurring_issue",
        False,
    )

    failed_attempts = agent_result.get(
        "previous_failed_attempts",
        [],
    )

    previous_failure = (
        len(failed_attempts) > 0
    )

    escalate = (
        action.get("action") == "ESCALATE"
    )

    recommended_team = action.get(
        "team",
        "Customer Support",
    )

    gateway_fix = (
        "gateway configuration"
        in combined_memory
    )


    # ========================================================
    # SAVE ANALYSIS TO SESSION STATE
    # ========================================================

    st.session_state["analysis_complete"] = True

    st.session_state["results"] = results

    st.session_state["memory_texts"] = memory_texts

    st.session_state["agent_result"] = agent_result

    st.session_state["action"] = action

    st.session_state["recurring_issue"] = recurring_issue

    st.session_state["failed_attempts"] = failed_attempts

    st.session_state["previous_failure"] = previous_failure

    st.session_state["escalate"] = escalate

    st.session_state["recommended_team"] = recommended_team

    st.session_state["gateway_fix"] = gateway_fix

    st.session_state["customer_id"] = customer_id

    st.session_state["issue"] = issue

    st.session_state["description"] = description


# ============================================================
# DISPLAY ANALYSIS
# ============================================================

if st.session_state.get(
    "analysis_complete",
    False,
):

    results = st.session_state.get(
        "results",
        [],
    )

    memory_texts = st.session_state.get(
        "memory_texts",
        [],
    )

    agent_result = st.session_state.get(
        "agent_result",
        {},
    )

    action = st.session_state.get(
        "action",
        {},
    )

    recurring_issue = st.session_state.get(
        "recurring_issue",
        False,
    )

    failed_attempts = st.session_state.get(
        "failed_attempts",
        [],
    )

    previous_failure = st.session_state.get(
        "previous_failure",
        False,
    )

    escalate = st.session_state.get(
        "escalate",
        False,
    )

    recommended_team = st.session_state.get(
        "recommended_team",
        "Customer Support",
    )

    gateway_fix = st.session_state.get(
        "gateway_fix",
        False,
    )


    # ========================================================
    # CASE ANALYSIS
    # ========================================================

    st.divider()

    render_html(
        '<div class="section-title">📊 Case Analysis</div>',
        unsafe_allow_html=True,
    )


    metric1, metric2, metric3, metric4 = st.columns(4)


    with metric1:

        st.metric(
            "Historical Matches",
            len(results),
        )


    with metric2:

        st.metric(
            "Recurring Issue",
            "Yes" if recurring_issue else "No",
        )


    with metric3:

        st.metric(
            "Failed Attempts",
            len(failed_attempts),
        )


    with metric4:

        st.metric(
            "Previous Escalations",
            len(
                agent_result.get(
                    "previous_escalations",
                    [],
                )
            ),
        )


    # ========================================================
    # RECOMMENDATION
    # ========================================================

    render_html(
        '<div class="section-title">🚨 ResolveIQ Recommendation</div>',
        unsafe_allow_html=True,
    )


    if escalate:

        render_html(
            f"""
            <div class="danger-card">

                <div class="recommendation-title">
                    🔴 ESCALATION RECOMMENDED
                </div>

                <div>
                    ResolveIQ recalled historical evidence
                    of repeated unsuccessful troubleshooting.
                </div>

            </div>
            """,
            unsafe_allow_html=True,
        )


        team_col, signal_col = st.columns(2)


        with team_col:

            render_html(
                f"""
                <div class="result-card">

                    <div class="small-label">
                        Recommended Team
                    </div>

                    <div class="team-name">
                        🏢 {recommended_team}
                    </div>

                </div>
                """,
                unsafe_allow_html=True,
            )


        with signal_col:

            render_html(
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
                "Payment Operations fixed the payment "
                "gateway configuration."
            )


    else:

        render_html(
            """
            <div class="success-card">

                <div class="recommendation-title">
                    🟢 CONTINUE TROUBLESHOOTING
                </div>

                <div>
                    Hindsight did not provide enough
                    historical evidence to justify escalation.
                </div>

            </div>
            """,
            unsafe_allow_html=True,
        )


    # ========================================================
    # MEMORY
    # ========================================================

    st.divider()

    render_html(
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
    # AI REASONING
    # ========================================================

    st.divider()

    render_html(
        '<div class="section-title">🤖 AI Agent Reasoning</div>',
        unsafe_allow_html=True,
    )


    ai_reasoning = agent_result.get(
        "ai_reasoning",
        "No AI reasoning was returned.",
    )


    render_html(
        f"""
        <div class="result-card">

            <div>
                {ai_reasoning}
            </div>

        </div>
        """,
        unsafe_allow_html=True,
    )


    # ========================================================
    # LEARNING SIGNAL
    # ========================================================

    learning_signal = agent_result.get(
        "learning_signal",
        "No learning signal available.",
    )


    render_html(
        '<div class="section-title">📚 Learning Signal</div>',
        unsafe_allow_html=True,
    )


    st.info(
        learning_signal
    )


    # ========================================================
    # EXPLAINABILITY
    # ========================================================

    st.divider()

    render_html(
        '<div class="section-title">💡 Why this decision?</div>',
        unsafe_allow_html=True,
    )


    if escalate:

        render_html(
            f"""
            <div class="result-card">

                <b>ResolveIQ connected the current case
                with organizational memory.</b>

                <br><br>

                🔁 Recurring issue detected:
                <b>{recurring_issue}</b>

                <br><br>

                ❌ Historical failed attempts:
                <b>{len(failed_attempts)}</b>

                <br><br>

                🏢 Recommended team:
                <b>{recommended_team}</b>

                <br><br>

                ResolveIQ therefore avoids repeating
                ineffective troubleshooting.

            </div>
            """,
            unsafe_allow_html=True,
        )

    else:

        st.write(
            "The recalled organizational memory does not "
            "indicate a strong reason for escalation."
        )


    # ========================================================
    # RECORD RESOLUTION
    # ========================================================

    st.divider()

    render_html(
        '<div class="section-title">✅ Record Resolution</div>',
        unsafe_allow_html=True,
    )

    st.caption(
        "Save the outcome so future cases can learn "
        "from this experience."
    )


    resolution = st.text_area(
        "What resolved the issue?",
        value=(
            "Payment Operations fixed the payment "
            "gateway configuration."
        ),
        height=100,
        key="resolution_input",
    )


    save_resolution = st.button(
        "🧠 Save Resolution to Hindsight",
        use_container_width=True,
    )


    if save_resolution:

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
Customer: {customer_id_saved}

Issue: {issue_saved}

Description:
{description_saved}

Resolution:
{resolution}

Lesson learned:
Store this outcome as organizational memory so future
similar cases can use the successful resolution instead
of repeating failed troubleshooting.
"""


        with st.spinner(
            "🧠 Saving resolution to Hindsight..."
        ):

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

                st.error(
                    f"Could not save memory "
                    f"(HTTP {status_code})."
                )

            except Exception as error:

                st.error(
                    f"Could not save resolution: {error}"
                )


# ============================================================
# FOOTER
# ============================================================

render_html(
    """
    <div class="footer">

        ResolveIQ · Remember → Recall → Decide → Resolve → Learn

        <br><br>

        AI-powered escalation intelligence using Hindsight memory

    </div>
    """,
    unsafe_allow_html=True,
)
