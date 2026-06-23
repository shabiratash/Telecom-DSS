"""Rule-based retention recommendation engine."""


def generate_recommendations(features: dict, probability: float):
    """
    Given a feature dict and churn probability, return a list of
    recommendation cards: {title, action, severity, icon}.
    """
    recs = []

    complaints = features.get("complaint_count", 0) or 0
    inactive = features.get("inactive_days", 0) or 0
    rfreq = features.get("recharge_frequency", 0) or 0
    competitor = str(features.get("competitor_offer_exposure", "No"))
    discount = str(features.get("discount_usage", "No"))
    drop = features.get("call_drop_rate", 0) or 0
    network = str(features.get("network_quality", "Good"))
    tenure = features.get("tenure_months", 0) or 0
    recharge = features.get("recharge_amount", 0) or 0

    if complaints >= 3:
        recs.append({
            "title": "High Complaint Volume",
            "action": "Assign a priority support agent and resolve open tickets within 24h.",
            "severity": "high", "icon": "bi-headset",
        })
    if inactive >= 30:
        recs.append({
            "title": "High Inactivity",
            "action": "Launch a re-engagement campaign with bonus minutes and free data.",
            "severity": "high", "icon": "bi-activity",
        })
    if rfreq <= 3:
        recs.append({
            "title": "Low Recharge Frequency",
            "action": "Offer a discounted bundle package to encourage regular top-ups.",
            "severity": "medium", "icon": "bi-wallet2",
        })
    if competitor == "Yes":
        recs.append({
            "title": "Exposed to Competitor Offers",
            "action": "Provide a personalised loyalty offer and price-match guarantee.",
            "severity": "high", "icon": "bi-shield-shaded",
        })
    if drop >= 10 or network in ("Poor", "Average"):
        recs.append({
            "title": "Network Quality Issues",
            "action": "Prioritise tower optimisation in the customer's area and notify of upgrades.",
            "severity": "medium", "icon": "bi-broadcast-pin",
        })
    if discount == "No":
        recs.append({
            "title": "No Discount Engagement",
            "action": "Enroll the customer in a tailored discount / cashback program.",
            "severity": "low", "icon": "bi-tag",
        })
    if tenure <= 6:
        recs.append({
            "title": "Early-Tenure Customer",
            "action": "Strengthen onboarding with a welcome reward and check-in call.",
            "severity": "medium", "icon": "bi-stars",
        })
    if recharge < 100:
        recs.append({
            "title": "Low Spend Profile",
            "action": "Recommend an affordable value plan matching the customer's usage.",
            "severity": "low", "icon": "bi-cash-coin",
        })

    if not recs:
        recs.append({
            "title": "Healthy Customer",
            "action": "Maintain service quality and offer periodic loyalty rewards.",
            "severity": "low", "icon": "bi-emoji-smile",
        })

    # If overall risk is very high, escalate
    if probability >= 0.7:
        recs.insert(0, {
            "title": "Critical Churn Risk",
            "action": "Trigger immediate VIP retention outreach within 48 hours.",
            "severity": "high", "icon": "bi-exclamation-octagon",
        })
    return recs
