import os
from pathlib import Path
from dotenv import load_dotenv

# Load environment variables from .env
load_dotenv()

# Project paths
BASE_DIR = Path(__file__).resolve().parent.parent  # backend folder
CSV_PATH = str(BASE_DIR / "doctor_availability.csv")

# OpenAI Config
MODEL_NAME = os.getenv("MODEL_NAME", "gpt-4o-mini")
TEMPERATURE = float(os.getenv("TEMPERATURE", "0"))

# Valid Data
VALID_SPECIALIZATIONS = [
    "general_dentist",
    "oral_surgeon",
    "orthodontist",
    "cosmetic_dentist",
    "prosthodontist",
    "pediatric_dentist",
    "emergency_dentist",
]

VALID_DOCTORS = [
    "john doe",
    "emily johnson",
    "sarah wilson",
    "jane smith",
    "michael green",
    "robert martinez",
    "lisa brown",
    "susan davis",
    "daniel miller",
    "kevin anderson",
]

DATE_FORMAT = "%m/%d/%Y %H:%M"