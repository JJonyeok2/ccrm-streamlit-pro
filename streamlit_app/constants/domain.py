"""Domain value mappings used by the CRM prediction payload."""

CHURN_MAP = {
    "Existing Customer": 0,
    "Attrited Customer": 1,
}

EDUCATION_MAP = {
    "Uneducated": 1,
    "High School": 2,
    "College": 3,
    "Graduate": 4,
    "Post-Graduate": 5,
    "Doctorate": 6,
    "Unknown": 7,
}

MARITAL_MAP = {
    "Single": 1,
    "Married": 2,
    "Divorced": 3,
    "Unknown": 4,
}

INCOME_MAP = {
    "Less than $40K": 1,
    "$40K - $60K": 2,
    "$60K - $80K": 3,
    "$80K - $120K": 4,
    "$120K +": 5,
    "Unknown": 6,
}

CARD_TYPE_MAP = {
    "Blue": 1,
    "Silver": 2,
    "Gold": 3,
    "Platinum": 4,
}

GENDER_MAP = {
    "F": 0,
    "M": 1,
}
