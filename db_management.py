from tinydb import TinyDB, Query
from util import *

db = TinyDB('database.json')
user_db = TinyDB('user_database.json')

def cred_retriever():
  return user_db.all()

def db_cred_checker(given_username, given_password):
  # Check if the given credentials are valid
  user = Query()
  result = user_db.search((user.username == given_username) & (user.password == given_password))
  if result:
    return True
  else:
    return False

def get_db_usernames():
  return [item['username'] for item in user_db.all()]

def db_create_account(data):
  user_db.insert(
    {"username": data['username'], 
    "password": data['password'], 
    "email": data['email'],
    "hunter_applied_bounties": [],
    "hunter_in_progress_bounties": [],
    "hunter_completed_bounties": [],
    "poster_posted_bounties": [],
    "poster_in_progress_bounties": [],
    "poster_completed_bounties": [],
    "uploaded_resume": ""
    }
  )

def db_create_bounty(username, given_bounty_data):
  db.insert(
      {"status": "posted",
       "username": username, 
       "bounty_id": generate_bounty_id(), 
       "creation_date": get_current_datetime(), 
       "bounty_name": given_bounty_data["bounty_name"],
       "cash_reward": given_bounty_data["cash_reward"], 
       "requirements": given_bounty_data["requirements"],
       "due_date": given_bounty_data["due_date"],
       "applicants": []
      }
    )

def db_get_all_posted_bounties():
  filtered_bounties = db.search(Query().status == "posted")
  return filtered_bounties

def db_apply_for_bounty(applicant, bounty_id):
  bounty = db.get(Query().bounty_id == bounty_id)
  if not bounty:
    return "Error: bounty does not exist"
  elif applicant in bounty["applicants"]:
    return "Error: already applied"
  elif applicant == bounty["username"]:
    return "Error: posted this bounty"
  else:
    db.update({"applicants": bounty["applicants"] + [applicant]}, Query().bounty_id == bounty_id)
    return "Success"

def db_get_posted_bounties_by_username(username):
  filtered_bounties = db.search((Query().status == "posted") & (Query().username == username))
  return filtered_bounties

def db_get_post_active_bounties_by_username(username):
  filtered_bounties = db.search((Query().status == "active") & (Query().username == username))
  return filtered_bounties

def db_get_post_completed_bounties_by_username(username):
  filtered_bounties = db.search((Query().status == "completed") & (Query().username == username))
  return filtered_bounties

def db_get_hunt_applied_bounties_by_username(username):
  filtered_bounties = db.search((Query().status == "posted") & (Query().applicants.any([username])))
  return filtered_bounties

def db_get_hunt_active_bounties_by_username(username):
  filtered_bounties = db.search((Query().status == "active") & (Query().selected_hunter == username))
  return filtered_bounties

def db_get_hunt_completed_bounties_by_username(username):
  filtered_bounties = db.search((Query().status == "completed") & (Query().selected_hunter == username))
  return filtered_bounties

def db_delete_user_resume(username):
  filename = str(username + ".pdf")
  path = os.path.join("resumes", filename)
  os.remove(path)
  db.update({"uploaded_resume": ""}, Query().username == username)
  return True

def db_get_posted_bounty_by_bounty_id(bounty_id):
  bounty = db.get(Query().bounty_id == bounty_id)
  return bounty

def db_select_a_hunter(bounty_id, selected_hunter):
  this_bounty = db.get(Query().bounty_id == bounty_id)
  if this_bounty:
    db.update({"status": "active", "selected_hunter": selected_hunter}, Query().bounty_id == bounty_id)
    return True
  else:
    return False

def db_deselect_a_hunter(bounty_id, selected_hunter):
  this_bounty = db.get(Query().bounty_id == bounty_id)
  if this_bounty:
    db.update({"status": "posted", "selected_hunter": ""}, Query().bounty_id == bounty_id)
    return True
  else:
    return False

def db_complete_bounty(bounty_id):
  this_bounty = db.get(Query().bounty_id == bounty_id)
  completion_time = get_current_datetime()
  if this_bounty:
    db.update({"status": "completed", "completion_time": completion_time}, Query().bounty_id == bounty_id)
    return True
  else:
    return False

def db_revert_complete_bounty(bounty_id):
  this_bounty = db.get(Query().bounty_id == bounty_id)
  if this_bounty:
    db.update({"status": "active", "completion_time": ""}, Query().bounty_id == bounty_id)
    return True
  else:
    return False

def db_add_repo_link(bounty_ID, repo_link):
  # Add a the string value repo_link to a new key "repo_link" in bounty_ID in db
  db.update({"repo_link": repo_link}, Query().bounty_id == bounty_ID)
  return True

def db_get_repo_link(bounty_ID):
  # Return the repo link associated with the given bounty_ID in db. If it does not exist, return None.
  bounty = db.get(Query().bounty_id == bounty_ID)
  if bounty:
    try:
      if len(bounty["repo_link"]) > 1:
        return bounty["repo_link"]
      else:
        return None
    except KeyError:
      return None
  else:
    return None

def db_remove_repo_link(bounty_ID):
  # Remove the repo_link key and value from the associated bounty_ID in db. If it is successfully removed, return True.
  try:
    db.update({"repo_link": ""}, Query().bounty_id == bounty_ID)
    return True
  except:
    return False

def db_delete_completed_bounty(bounty_ID):
  # Delete the bounty from the database with the given bounty ID
  try:
    db.remove(Query().bounty_id == bounty_ID)
    return True
  except:
    return False