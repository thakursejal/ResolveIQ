def _issue_is_similar(ticket, memory_text):
    """
    Check whether a historical memory is related to the
    current ticket.
    """

    ticket_text = (
        f"{ticket.get('issue', '')} "
        f"{ticket.get('description', '')}"
    ).lower()

    memory_text = memory_text.lower()

    keywords = [
        "payment",
        "transaction",
        "failed",
        "failure",
        "declined",
        "gateway",
        "refund",
        "card",
    ]

    return any(
        keyword in ticket_text and keyword in memory_text
        for keyword in keywords
    )


def analyze_escalation(
    severity,
    recurring_issue,
    failed_attempts,
    previous_escalations=None
):
    """
    Decide whether the current issue needs escalation.
    """

    previous_escalations = previous_escalations or []

    if recurring_issue and len(failed_attempts) >= 2:
        return {
            "action": "ESCALATE",
            "team": "Payment Operations",
            "priority": "HIGH",
            "reason": (
                "The issue is recurring and multiple "
                "troubleshooting attempts have failed."
            )
        }

    if previous_escalations and severity.lower() == "high":
        return {
            "action": "REVIEW",
            "team": "Support Lead",
            "priority": "HIGH",
            "reason": (
                "A previous escalation exists and the "
                "current issue has high severity."
            )
        }

    return {
        "action": "TROUBLESHOOT",
        "team": "Customer Support",
        "priority": "NORMAL",
        "reason": (
            "There is not enough historical evidence "
            "to justify escalation."
        )
    }


def get_escalation_action(
    severity,
    recurring_issue,
    failed_attempts,
    previous_escalations=None
):
    """
    Return the operational escalation decision.
    """

    return analyze_escalation(
        severity=severity,
        recurring_issue=recurring_issue,
        failed_attempts=failed_attempts,
        previous_escalations=previous_escalations
    )


def analyze_hindsight_memories(ticket, memory_records):
    """
    Analyze historical Hindsight memories to identify:

    - recurring issues
    - failed attempts
    - previous escalations
    - successful resolutions
    """

    if not memory_records:
        return {
            "memory_count": 0,
            "recurring_issue": False,
            "failed_attempts": [],
            "previous_escalations": [],
            "successful_resolutions": []
        }

    failed_attempts = []
    previous_escalations = []
    successful_resolutions = []

    for memory in memory_records:

        if not isinstance(memory, dict):
            continue

        text = memory.get("text", "")

        if not text:
            continue

        text_lower = text.lower()

        # Detect failed troubleshooting attempts
        failure_keywords = [
            "failed",
            "failure",
            "did not resolve",
            "didn't resolve",
            "unsuccessful",
            "not resolved"
        ]

        sentences = [
            sentence.strip()
            for sentence in (
                text
                .replace("!", ".")
                .replace("?", ".")
                .split(".")
            )
            if sentence.strip()
        ]

        matched_failures = [
            sentence
            for sentence in sentences
            if any(
                keyword in sentence.lower()
                for keyword in failure_keywords
            )
        ]

        if matched_failures:
            failed_attempts.extend(
                matched_failures
            )

        # Detect previous escalations
        escalation_keywords = [
            "escalated",
            "escalation",
            "payment operations",
            "support lead"
        ]

        if any(
            keyword in text_lower
            for keyword in escalation_keywords
        ):
            previous_escalations.append(text)

        # Detect successful resolutions
        resolution_keywords = [
            "resolved",
            "resolution",
            "fixed",
            "successfully"
        ]

        if any(
            keyword in text_lower
            for keyword in resolution_keywords
        ):
            successful_resolutions.append(text)

    return {
        "memory_count": len(memory_records),
        "recurring_issue": (
            len(failed_attempts) >= 2
            or len(previous_escalations) >= 1
            or len(memory_records) >= 2
        ),
        "failed_attempts": failed_attempts,
        "previous_escalations": previous_escalations,
        "successful_resolutions": successful_resolutions
    }
