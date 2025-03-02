from enum import Enum

# Define available OpenAI models as an enum for type safety
class OpenAIModels(Enum):
    GPT4o = "gpt-4o"
    GPT4Turbo = "gpt-4-turbo"
    GPT4 = "gpt-4" 
    GPT35Turbo = "gpt-3.5-turbo"
    
    def __str__(self):
        return self.value

IDEA_CATEGORIES = [
    "Administrative Services",
    "Agriculture and Farming",
    "Angel Investing",
    "Apps",
    "Artificial Intelligence",
    "Arts",
    "Biotechnology",
    "Climate Tech",
    "Clothing and Apparel",
    "Commerce and Shopping",
    "Community and Lifestyle",
    "Construction",
    "Consumer Electronics",
    "Consumer Goods",
    "Content and Publishing",
    "Corporate Services",
    "Data Analytics",
    "Design",
    "Education",
    "Energy",
    "Entertainment",
    "Events",
    "Financial Services",
    "Food and Beverage",
    "Gaming",
    "Government and Military",
    "Hardware",
    "Health Care",
    "Information Technology",
    "Internet Services",
    "Lending and Investments",
    "Manufacturing",
    "Media and Entertainment",
    "Mobile",
    "Music and Audio",
    "Natural Resources",
    "Navigation and Mapping",
    "Payments",
    "Platforms",
    "Privacy and Security",
    "Private Equity",
    "Professional Services",
    "Public Admin and Safety",
    "Real Estate",
    "Retail",
    "Sales and Marketing",
    "Science and Engineering",
    "Social and Non-Profit",
    "Software",
    "Sports",
    "Sustainability",
    "Transportation",
    "Travel and Tourism",
    "Venture Capital"
]

ADDITIOANL_IDEA_CATEGORIES = [
    "Advertising",
    "Aerospace",
    "Augmented Reality",
    "Automation Nexus",
    "Automotive",
    "Beauty",
    "Consulting",
    "Consumer Services",
    "Engineering",
    "Environmental Services",
    "Home Improvement",
    "Hospitality",
    "Human Resources",
    "Insurance",
    "Internet of Things (IoT)",
    "Legal",
    "Legal Services",
    "Logistics",
    "Productivity",
    "Robotics",
    "Safety",
    "Space",
    "Supply Chain",
    "Supply Chain Management",
    "Telecommunications",
    "Uncategorized",
    "Unknown",
    "Urban Planning",
    "Virtual Reality",
]

ALL_IDEA_CATEGORIES = IDEA_CATEGORIES + ADDITIOANL_IDEA_CATEGORIES
