from typing import Dict, List, Any, Optional, TypeVar, Tuple

# Loader Data Types
T = TypeVar("T", bound=Dict[str, Any])

UserDataType = Dict[str, Any]
IdeaDataType = Dict[str, Any]
StepDataType = Dict[str, Any]

IDEA_DOMAIN_CATEGORIES = {
    "Technology": [
        "Artificial Intelligence",
        "Software",
        "Hardware",
        "Data Analytics",
        "Information Technology",
        "Mobile",
        "Apps",
        "Platforms",
        "Internet Services",
        "Robotics",
    ],
    "Business Services": [
        "Corporate Services",
        "Professional Services",
        "Administrative Services",
        "Consulting",
        "Sales and Marketing",
        "Financial Services",
    ],
    "Consumer": [
        "Consumer Goods",
        "Consumer Electronics",
        "Commerce and Shopping",
        "Clothing and Apparel",
        "Food and Beverage",
        "Consumer Services",
        "Retail",
    ],
    "Health & Science": [
        "Biotechnology",
        "Health Care",
        "Science and Engineering",
        "Medical Devices",
        "Pharmaceuticals",
    ],
    "Media & Entertainment": [
        "Media and Entertainment",
        "Content and Publishing",
        "Entertainment",
        "Music and Audio",
        "Gaming",
    ],
    "Education": ["Education", "E-Learning", "EdTech"],
    "Sustainability": ["Climate Tech", "Sustainability", "Energy", "Renewable Energy"],
    "Finance": [
        "Financial Services",
        "Lending and Investments",
        "Payments",
        "Insurance",
        "Banking",
        "Cryptocurrency",
        "Venture Capital",
        "Private Equity",
    ],
    "Other": [],  # Catch-all for others
}
