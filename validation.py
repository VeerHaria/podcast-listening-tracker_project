"""Input checks. Each function returns clean data or raises ValueError."""
import re
from datetime import date, datetime

CATEGORIES = ["Technology", "Science", "Education", "News", "History",
              "Business", "Comedy", "Health", "Arts", "Other"]


def check_text(text, label):
    text = " ".join(text.split())          # remove extra spaces
    if not re.fullmatch(r"[A-Za-z0-9][A-Za-z0-9 .,'&:!?()-]{1,59}", text):
        raise ValueError(f"{label} must be 2 to 60 characters (letters, numbers, spaces, . , ' & : ! ? ( ) -).")
    return text


def check_category(text):
    if text not in CATEGORIES:
        raise ValueError("Choose a category from the list.")
    return text


def check_date(text):
    text = text.strip()
    if not re.fullmatch(r"[0-9]{4}-[0-9]{2}-[0-9]{2}", text):
        raise ValueError("Date must look like 2026-09-30.")
    try:
        day = datetime.strptime(text, "%Y-%m-%d").date()
    except ValueError:
        raise ValueError("That date does not exist.")
    if day > date.today():
        raise ValueError("Date cannot be in the future.")
    return text


def check_number(text, label, low, high):
    text = text.strip()
    if not re.fullmatch(r"[0-9]+", text):
        raise ValueError(f"{label} must be a whole number.")
    number = int(text)
    if not low <= number <= high:
        raise ValueError(f"{label} must be between {low} and {high}.")
    return number
