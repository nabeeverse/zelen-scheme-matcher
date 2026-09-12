from db import get_all_schemes, get_eligibility_rules


def is_allowed(value, allowed_values):
    if not allowed_values:
        return True

    allowed_values = str(allowed_values).strip()

    if allowed_values.upper() in ("ALL", "ANY"):
        return True

    allowed = [
        item.strip().lower()
        for item in allowed_values.split(",")
    ]

    return str(value).strip().lower() in allowed


def match_schemes(user):

    schemes = get_all_schemes()
    matches = []

    for scheme in schemes:

        rule = get_eligibility_rules(scheme["sch_id"])

        if not rule:
            continue

        gender_match = is_allowed(
            user.get("gender"),
            rule.get("allowed_genders")
        )

        caste_match = is_allowed(
            user.get("caste"),
            rule.get("allowed_caste")
        )

        business_match = is_allowed(
            user.get("business_type"),
            rule.get("allowed_business_type")
        )

        minimum_revenue = rule.get("min_annual_revenue")

        if minimum_revenue is None:
            revenue_match = True
        else:
            try:
                revenue_match = (
                    float(user.get("annual_revenue", 0))
                    >= float(minimum_revenue)
                )
            except (TypeError, ValueError):
                revenue_match = False

        requires_udyam = bool(rule.get("requires_udyam"))

        udyam_match = (
            not requires_udyam
            or bool(user.get("has_udyam_registration"))
        )

        # Score ALL schemes instead of removing partial matches
        matched_criteria = sum([
            gender_match,
            caste_match,
            business_match,
            revenue_match,
            udyam_match
        ])

        confidence = round(
            (matched_criteria / 5) * 100,
            2
        )

        # Don't show extremely poor matches
        if confidence < 40:
            continue

        reasons = []

        if gender_match:
            reasons.append(
                "Your gender fits the scheme's eligibility rule."
            )
        else:
            reasons.append(
                "Gender does not match the stated eligibility rule."
            )

        if caste_match:
            reasons.append(
                "Your category fits the scheme's eligibility rule."
            )
        else:
            reasons.append(
                "Category does not match the stated eligibility rule."
            )

        if business_match:
            reasons.append(
                "Your business type fits the scheme."
            )
        else:
            reasons.append(
                "Your business type is different from the listed business types."
            )

        if revenue_match:
            reasons.append(
                "Your annual revenue meets the listed revenue requirement."
            )
        else:
            reasons.append(
                "Your annual revenue is below the listed minimum."
            )

        if requires_udyam:
            if udyam_match:
                reasons.append(
                    "Udyam registration requirement is satisfied."
                )
            else:
                reasons.append(
                    "This scheme requires Udyam registration."
                )
        else:
            reasons.append(
                "Udyam registration is not required by this rule."
            )

        matches.append({
            "sch_id": scheme["sch_id"],
            "sch_name": scheme["sch_name"],
            "ministry_dept": scheme.get("ministry_dept"),
            "description": scheme.get("description"),
            "financial_benefit_details":
                scheme.get("financial_benefit_details"),
            "application_url":
                scheme.get("application_url"),
            "match_confidence_score": confidence,
            "match_reasons": reasons
        })

    matches.sort(
        key=lambda x: x["match_confidence_score"],
        reverse=True
    )

    return matches