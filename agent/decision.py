def _issue_is_similar(current_issue, historical_issue):
    """
    Check whether the current issue is related to a historical issue.
    """

    current_words = set(current_issue.lower().split())
    historical_words = set(historical_issue.lower().split())

    if not current_words or not historical_words:
        return False

    common_words = current_words.intersection(historical_words)

    return len(common_words) >= 2


def analyze_escalation(ticket, historical_cases):
    """
    Analyze a new support ticket against relevant historical cases.
    """

    customer_id = ticket.get("customer_id")
    current_issue = ticket.get("issue", "")
    frustration = ticket.get("frustration", "medium").lower()

    relevant_cases = []

    # Find historical cases related to the current issue
    for case in historical_cases:

        historical_issue = case.get("issue", "")

        if _issue_is_similar(current_issue, historical_issue):
            relevant_cases.append(case)

    # No relevant history
    if not relevant_cases:
        return {
            "severity": "medium",
            "recurring_issue": False,
            "previous_failed_attempts": [],
            "successful_resolutions": [],
            "recommendation": "Standard troubleshooting",
            "reason": "No relevant historical cases were found."
        }

    failed_attempts = []
    successful_resolutions = []

    for case in relevant_cases:

        result = case.get("result", "").lower()

        if result == "failed":
            failed_attempts.append(
                case.get("attempted_solution", "Unknown")
            )

        elif result == "resolved":
            successful_resolutions.append(
                case.get("resolution", "Unknown")
            )

    recurring_issue = len(relevant_cases) >= 2

    # Multiple relevant failures → escalation
    if recurring_issue and len(failed_attempts) >= 2:

        recommendation = "Escalate to Payment Operations"

        reason = (
            f"Customer {customer_id} has a recurring issue. "
            f"Previous relevant troubleshooting attempts failed: "
            f"{', '.join(failed_attempts)}."
        )

        severity = "high"

    # A successful historical resolution exists
    elif successful_resolutions:

        recommendation = (
            f"Try previously successful resolution: "
            f"{successful_resolutions[-1]}"
        )

        reason = (
            "A relevant historical case contains a successful "
            "resolution that may apply to the current issue."
        )

        severity = "medium"

    else:

        recommendation = "Standard troubleshooting"

        reason = (
            "Relevant historical cases were found, but there is "
            "not enough evidence to recommend escalation."
        )

        severity = "medium"

    # High frustration increases severity
    if frustration == "high" and recurring_issue:
        severity = "high"

    return {
        "severity": severity,
        "recurring_issue": recurring_issue,
        "previous_failed_attempts": failed_attempts,
        "successful_resolutions": successful_resolutions,
        "recommendation": recommendation,
        "reason": reason
    }
    def get_escalation_action(severity, recurring_issue, failed_attempts):
    """
    Convert the analysis into a clear operational action.
    """

    if recurring_issue and len(failed_attempts) >= 2:
        return {
            "action": "ESCALATE",
            "team": "Payment Operations",
            "priority": "HIGH"
        }

    if severity == "high":
        return {
            "action": "REVIEW",
            "team": "Support Lead",
            "priority": "HIGH"
        }

    return {
        "action": "TROUBLESHOOT",
        "team": "Customer Support",
        "priority": "NORMAL"
    }
