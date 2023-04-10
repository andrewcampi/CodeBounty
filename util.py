import random, string, os
from datetime import datetime

def generate_bounty_id():
  # Define characters for the ID
  chars = string.ascii_uppercase + string.digits
  # Generate a random ID of length 12
  bounty_id = ''.join(random.choice(chars) for _ in range(12))
  return bounty_id

def get_current_datetime():
  # Get the current date and time
  now = datetime.utcnow()
  # Format the date and time as a string
  current_datetime = now.strftime("%Y-%m-%d %H:%M:%S UTC")
  return current_datetime

def check_for_resume(username):
  filename = username + ".pdf"
  filepath = os.path.join("resumes", filename)
  if os.path.exists(filepath) and os.path.isfile(filepath):
    return True
  else:
    return False
    