import datetime

def get_date_suffix(day):
    """Returns the suffix for a given day (st, nd, rd, or th)."""
    if 4 <= day <= 20 or 24 <= day <= 30:
        return "th"
    else:
        return ["st", "nd", "rd"][day % 10 - 1]

def handle_datetime_message(message, speak):
    """
    Checks if the message asks for the time or date and responds.
    Returns True if handled, False otherwise.
    """
    lower_message = message.lower()
    now = datetime.datetime.now()

    if "time" in lower_message:
        current_time = now.strftime("%I:%M %p") # e.g., "01:22 PM"
        response = f"The current time is {current_time}."
        speak(response)
        return True

    if "date" in lower_message:
        day = now.day
        suffix = get_date_suffix(day)
        current_date = now.strftime(f"%B {day}{suffix}, %Y") # e.g., "September 30th, 2025"
        response = f"Today's date is {current_date}."
        speak(response)
        return True

    return False