from dataclasses import dataclass


@dataclass
class LeadAnalysis:
    lead_type: str
    intent: str
    commercial_value: str
    recommended_action: str


def analyze(
    title: str,
    company: str = "",
    category: str = "",
    kind: str = "",
    opportunity_type: str = "JOB",
    match_score: int = 0,
) -> LeadAnalysis:

    text = f"{title} {company} {category} {kind}".lower()

    # Ignore people offering their own services.
    if opportunity_type == "IGNORE":
        return LeadAnalysis(
            lead_type="IGNORE",
            intent="SELF_PROMOTION",
            commercial_value="NONE",
            recommended_action="IGNORE",
        )

    if opportunity_type == "CLIENT":
        return LeadAnalysis(
            lead_type="CLIENT",
            intent="SERVICE_REQUEST",
            commercial_value="HIGH" if match_score >= 60 else "MEDIUM",
            recommended_action="CONTACT",
        )

    if opportunity_type == "STARTUP":
        return LeadAnalysis(
            lead_type="STARTUP",
            intent="PRODUCT_BUILD",
            commercial_value="HIGH" if match_score >= 60 else "MEDIUM",
            recommended_action="PITCH",
        )

    if opportunity_type == "WEB3":
        return LeadAnalysis(
            lead_type="WEB3",
            intent="TALENT_REQUEST",
            commercial_value="HIGH" if match_score >= 60 else "MEDIUM",
            recommended_action="CONTACT",
        )

    if opportunity_type == "FREELANCE":
        return LeadAnalysis(
            lead_type="FREELANCE",
            intent="PROJECT_REQUEST",
            commercial_value="HIGH" if match_score >= 60 else "MEDIUM",
            recommended_action="APPLY",
        )

    # Generic employment opportunity.
    if "intern" in text or "internship" in text:
        value = "MEDIUM"
    elif match_score >= 70:
        value = "HIGH"
    else:
        value = "LOW"

    return LeadAnalysis(
        lead_type="JOB",
        intent="EMPLOYMENT",
        commercial_value=value,
        recommended_action="APPLY",
    )
