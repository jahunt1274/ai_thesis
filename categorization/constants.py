from enum import Enum

# Define available OpenAI models as an enum for type safety
class OpenAIModels(Enum):
    GPT4 = "gpt-4"
    GPT4o = "gpt-4o"
    GPT4oMini = "gpt-4o-mini"
    GPT4Turbo = "gpt-4-turbo"
    GPT35Turbo = "gpt-3.5-turbo"
    
    def __str__(self):
        return self.value

# Define rate limits by model
# 999999 is a standin for no-limit on the model
# tpm = Tokens per Minute
# rpm = Requests per Minute
# rpd = Requests per Day
OPENAI_API_RATE_LIMITS = {
    OpenAIModels.GPT4:          {"tpm": 10000, "rpm": 500, "rpd": 10000},
    OpenAIModels.GPT4o:         {"tpm": 30000, "rpm": 500, "rpd": 999999},
    OpenAIModels.GPT4oMini:     {"tpm": 200000, "rpm": 500, "rpd": 10000},
    OpenAIModels.GPT4Turbo:     {"tpm": 30000, "rpm": 500, "rpd": 999999},
    OpenAIModels.GPT35Turbo:    {"tpm": 200000, "rpm": 500, "rpd": 10000}
}

# Define costs by model (per 1000 tokens)
OPENAI_API_COSTS = {
    OpenAIModels.GPT4:          {"input": 0.03, "output": 0.06, "delim":1000},
    OpenAIModels.GPT4o:         {"input": 0.01, "output": 0.03, "delim":1000},
    OpenAIModels.GPT4oMini:     {"input": 0.01, "output": 0.03, "delim":1000},
    OpenAIModels.GPT4Turbo:     {"input": 0.01, "output": 0.03, "delim":1000},
    OpenAIModels.GPT35Turbo:    {"input": 0.0015, "output": 0.002, "delim":1000}
}

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
