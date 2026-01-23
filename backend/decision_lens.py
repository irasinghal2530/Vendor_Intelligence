# # backend/decision_lens.py

# VENDOR_SELECTION_LENS = {
#     "non_negotiables": [
#         "Regulatory and compliance requirements must be met",
#         "Minimum quality certifications are required for critical components"
#     ],
#     "strong_preferences": [
#         "Operational continuity over marginal cost savings",
#         "Established vendors for mission-critical parts",
#         "Predictable lead times over faster but volatile delivery"
#     ],
#     "tradeable_factors": [
#         "Unit price differences under ~3–4%",
#         "Payment terms within standard ranges",
#         "Incumbent vs new supplier if onboarding risk is low"
#     ],
#     "risk_sensitivities": [
#         "Single-source dependency for critical components",
#         "Late-stage quality failures",
#         "Price escalation over long contracts"
#     ],
#     "typical_assumptions": [
#         "Quality parity unless evidence suggests otherwise",
#         "Demand remains stable over the contract period"
#     ]
# }


# backend/decision_lens.py

VENDOR_SELECTION_LENS = {
    "non_negotiables": [
        # Existing
        "Regulatory and compliance requirements must be met",
        "Minimum quality certifications are required for critical components",

        # Tata-style mandatory eligibility rules
        "Valid PAN and GSTIN must be provided and successfully verified",
        "Vendor must pass internal registration and review before consideration",
        "Mandatory legal, tax, and compliance documents must be uploaded",
        "Incomplete or failed government/API validations block eligibility",
        "Bank details must be available for commercial engagement"
    ],

    "strong_preferences": [
        # Existing
        "Operational continuity over marginal cost savings",
        "Established vendors for mission-critical parts",
        "Predictable lead times over faster but volatile delivery",

        # From Tata registration logic
        "Vendors with complete and verified profiles over partially registered vendors",
        "Suppliers with demonstrated compliance history and documentation discipline",
        "Vendors capable of accepting and managing POs digitally"
    ],

    "tradeable_factors": [
        # Existing
        "Unit price differences under ~3–4%",
        "Payment terms within standard ranges",
        "Incumbent vs new supplier if onboarding risk is low",

        # Clarified tradeables
        "MSME status when operational capability is otherwise equivalent",
        "Minor variations in documentation format once core compliance is met",
        "New vendor consideration if onboarding and approval risk is low"
    ],

    "risk_sensitivities": [
        # Existing
        "Single-source dependency for critical components",
        "Late-stage quality failures",
        "Price escalation over long contracts",

        # Added from Tata process risks
        "Incomplete registration or delayed approval in vendor onboarding",
        "Missing quality or statutory certifications",
        "Address or legal entity mismatches across documents",
        "Inability to digitally accept POs or contractual documents"
    ],

    "typical_assumptions": [
        # Existing
        "Quality parity unless evidence suggests otherwise",
        "Demand remains stable over the contract period",

        # Procurement reality assumptions
        "Submitted documents are current unless flagged otherwise",
        "Vendor-provided information reflects actual operational readiness",
        "Compliance status remains valid through the contract period"
    ]
}
