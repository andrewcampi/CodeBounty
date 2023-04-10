# PyWebIO imports
from pywebio import *
from pywebio.input import *
from pywebio.output import *
from pywebio.pin import *
# General Imports
import time, os
from functools import partial
# My Imports
from util import *
from db_management import *

@config(theme="sketchy")
def cred_manager():
  clear()
  put_markdown("# Code Bounty")
  put_text("Have an account?")
  put_button("Login", onclick=lambda: login())
  put_text("New to Code Bounty?")
  put_button("Create an Account", onclick=lambda: create_account())
  
def login():
  clear()
  put_markdown("# Code Bounty")
  data = input_group("Login", [
    input('Username', name='username'),
    input('Password', name='password', type=PASSWORD)
    ])
  given_creds = [data['username'], data['password']]
  # check if the given username and password are valid
  valid_creds = db_cred_checker(given_creds[0], given_creds[1])
  if valid_creds:
    clear()
    main(data['username'])
  else:
    clear()
    put_markdown("### Login failed!")
    time.sleep(3)
    login()
  return True

def create_account():
  clear()
  existing_usernames = get_db_usernames()
  put_markdown("# Code Bounty")
  data = input_group("Create Account", [
    input('Username', name='username'),
    input('Password', name='password', type=PASSWORD),
    input('Email', name='email')
    ])
  if data['username'] in existing_usernames:
    put_text("Username already exists!")
    time.sleep(3)
    create_account()
  else:
    db_create_account(data)
    put_markdown("### Account created!")
    time.sleep(2)
    clear()
    main(data['username'])

def main(username):
  session.set_env(title='Code Bounty', output_max_width='80%')
  put_column([put_scope('top-navbar'), None, put_scope('main')], size='50px 50px 85%')
  find_a_bounty(username)

def display_nav_bar(username):
  with use_scope('top-navbar'):
    clear()
    put_grid([[
      put_text('Code Bounty').style('background:#000000; color:#ffffff; text-align: center; font-weight: bold; font-size: 20pt'),
      put_text(" "),
      #put_markdown('## Menu'),
      put_button('Find a Bounty', onclick=lambda:find_a_bounty(username)),
      put_button('Post a Bounty', onclick=lambda:post_a_bounty(username)),
      #put_markdown(str('## ' + username)),
      put_button('Account', onclick=lambda:account(username)),
    ]], direction='row')
    put_markdown("---")

def hide_nav_bar(username):
  with use_scope('top-navbar'):
    clear()
    put_text('Code Bounty').style('background:#000000; color:#ffffff; text-align: center; font-weight: bold; font-size: 20pt')
    put_markdown("---")
    
def find_a_bounty(username):
  display_nav_bar(username)
  with use_scope("main"):
    clear()
    put_markdown("# Latest Open Bounties")
    all_posted_bounties = db_get_all_posted_bounties()
    for bounty in reversed(all_posted_bounties): 
      put_markdown(str("## " + bounty["bounty_name"] + " - " + "$" + str(bounty["cash_reward"]) + " REWARD"))
      put_markdown(str("#### " + "Posted @ " + bounty["creation_date"]))
      this_bounty_id = bounty["bounty_id"]
      put_markdown(str("#### Bounty " + this_bounty_id + " by user " + bounty["username"]))
      put_markdown(str("#### Requirements:"))
      put_markdown(str(bounty["requirements"]))
      put_markdown(str("#### Due Date:"))
      put_markdown(str(bounty["due_date"]))
      put_markdown(str("#### Applicants: " + str(len(bounty["applicants"]))))
      if (username in bounty["applicants"]):
        put_markdown("#### Alread applied!")
      elif (username == bounty["username"]):
        put_markdown("#### You cannot apply for your own bounty.")
      else:
        put_button("Apply for this bounty", onclick=lambda bounty_id=this_bounty_id: apply_for_bounty(username, bounty_id))
      put_text(" ")
      
def apply_for_bounty(username, bounty_id):
  apply_message = db_apply_for_bounty(username, bounty_id)
  with use_scope("main"):
    clear()
    if "Error" not in apply_message:
      put_markdown("#### Success!")
      put_text(str("You hae applied for bounty " + str(bounty_id) + "."))
    else:
      put_markdown("#### Invalid application")
      if apply_message == "Error: already applied":
        put_text("You already applied for this bounty.")
      elif apply_message == "Error: posted this bounty":
        put_text("You cannot apply for a bounty you posted.")
      elif apply_message == "Error: bounty does not exist":
        put_text("The bounty you applied for does not exist.")
      else:
        put_text("Something went wrong.")
    put_button("OK", onclick=lambda:find_a_bounty(username))
  
def post_a_bounty(username):
  hide_nav_bar(username)
  # Get the bounty data from the user
  with use_scope("main"):
    clear()
    put_text(str("Signed in as " + username))
    put_text("Post a new bounty! (To escape, submit a blank form.)")
    given_bounty_data = input_group("Bounty Information", [
      input('Bounty Name', name='bounty_name'),
      input('Cash Reward', name='cash_reward', type=NUMBER),
      textarea("Requirements", name='requirements', rows=4), 
      textarea("Due Date", name="due_date", rows=2)
      ])
  if (len(given_bounty_data["bounty_name"]) < 2):
    # Return to the "Find a Bounty" page
    find_a_bounty(username)
  else:
    # Add it to the database
    db_create_bounty(username, given_bounty_data)
    # Inform the user that the bounty was successfully posted
    with use_scope("main"):
      clear()
      put_markdown("### Bounty Posted!")
      time.sleep(3)
    # Return to the "Find a Bounty" page
    find_a_bounty(username)

def upload_resume(username):
  hide_nav_bar(username)
  # Get the bounty data from the user
  with use_scope("main"):
    clear()
    put_text(str("Signed in as " + username))
    put_text(" ")
    # prompt the user to upload a pdf file
    resume = file_upload(label="Upload your resume as a pdf", accept=".pdf")
    if resume is not None:
      with open(str("resumes/" + username + ".pdf"), "wb") as f:
        f.write(resume['content'])
      # display a success message
      put_markdown("#### Success!")
      time.sleep(2)
    # Return to the account page
    account(username)

def delete_resume(username):
  hide_nav_bar(username)
  with use_scope("main"):
    clear()
    success = db_delete_user_resume(username)
    if success:
      put_markdown("#### Success!")
      time.sleep(2)
    else:
      put_markdown("#### Error.")
      put_text("Could not delete the resume.")
    put_text(" ")
  # Return to account page
  account(username)

def add_repo_link(username, bounty_ID):
  hide_nav_bar(username)
  with use_scope("main"):
    clear()
    repo_link = input(str("Provide a repo link for bounty " + bounty_ID))
    success = db_add_repo_link(bounty_ID, repo_link)
    if success:
      put_markdown("#### Success!")
      time.sleep(2)
    else:
      put_markdown("#### Error.")
      put_text("Could not add the repo link.")
      time.sleep(2)
    put_text(" ")
  # Return to account page
  account(username)

def remove_repo_link(username, bounty_ID):
  hide_nav_bar(username)
  with use_scope("main"):
    clear()
    success = db_remove_repo_link(bounty_ID)
    if success:
      put_markdown("#### Success!")
      time.sleep(2)
    else:
      put_markdown("#### Error.")
      put_text("Could not remove the repo link.")
      time.sleep(2)
    put_text(" ")
  # Return to account page
  account(username)
    
def account(username):
  display_nav_bar(username)
  with use_scope("main"):
    clear()
    put_markdown(str("# " + username + "'s Account"))
    put_button("Logout", onclick=lambda:cred_manager())
    has_resume = check_for_resume(username)
    if has_resume:
      put_markdown("#### View your resume:")
      with open(str("resumes/" + username + ".pdf"), "rb") as f:
        content = f.read()
      put_file("resume.pdf", content)
      put_button("Delete your resume", onclick=lambda:delete_resume(username))
    else:
      put_button("Upload a Resume", onclick=lambda:upload_resume(username))
    put_markdown(("# Bounties"))
    put_tabs([
        {'title': 'Post', 'content': put_tabs([
            {'title': 'Posted', 'content': put_scope('subtab1')},
            {'title': 'Active', 'content': put_scope('subtab2')},
            {'title': 'Completed', 'content': put_scope('subtab3')}
        ])},
        {'title': 'Hunt', 'content': put_tabs([
            {'title': 'Applied', 'content': put_scope('subtab4')},
            {'title': 'Active', 'content': put_scope('subtab5')},
            {'title': 'Completed', 'content': put_scope('subtab6')}
        ])}
    ])
    # Content for subtab 1 (Post - Posted)
    posted_bounties = db_get_posted_bounties_by_username(username)
    posted_bounty_ids = [bounty['bounty_id'] for bounty in posted_bounties]
    with use_scope("subtab1"):
        for x, bounty in list(enumerate(posted_bounties)):
            put_collapse(str(bounty["bounty_name"] + " - " + "$" + str(bounty["cash_reward"]) + " REWARD"), put_scope(str("subtab1-" + bounty["bounty_id"])))
            with use_scope(str("subtab1-" + bounty["bounty_id"])):
                put_markdown(str("#### " + "Posted @ " + bounty["creation_date"]))
                put_markdown(str("#### Bounty " + posted_bounty_ids[x] + " by " + bounty["username"]))
                put_collapse("Requirements", str(bounty["requirements"]))
                put_markdown(str("#### Due Date:"))
                put_markdown(str(bounty["due_date"]))
                if (len(bounty["applicants"]) >= 1):
                    table_content = []
                    for applicant in bounty["applicants"]:
                        this_applicant_row = []
                        this_applicant_row.append(put_text(applicant))
                        this_applicant_resume_file_path = str("resumes/" + applicant + ".pdf")
                        if os.path.exists(this_applicant_resume_file_path):
                            this_applicant_row.append(put_file(str(applicant + ".pdf"), open(str("resumes/" + applicant + ".pdf"), 'rb').read(), "Download Resume"))
                        else:
                            this_applicant_row.append(put_text("No Resume Available"))
                        this_applicant_row.append(put_button(str("Chat with " + applicant), onclick=lambda:chat_view(username, applicant)))
                        table_content.append(this_applicant_row)
                    put_collapse("Applicants", put_table(table_content, header=[put_markdown("#### Applicant"), put_markdown("#### Resume"), put_markdown("#### Chat")]))
                    put_button(str("Select a hunter for " + posted_bounty_ids[x]), onclick=partial(select_a_hunter, username, posted_bounty_ids[x], bounty["applicants"]))
                else:
                    put_markdown(str("#### Applicants: no applicants yet"))     
    # Get content for subtab2 (Post - Active)
    posted_active_bounties = db_get_post_active_bounties_by_username(username)
    posted_active_bounty_ids = [bounty['bounty_id'] for bounty in posted_active_bounties]
    with use_scope("subtab2"):
      for x, bounty in list(enumerate(posted_active_bounties)): 
        put_collapse(str(bounty["bounty_name"] + " - " + "$" + str(bounty["cash_reward"]) + " REWARD"), put_scope(str("subtab2-" + bounty["bounty_id"])))
        with use_scope(str("subtab2-" + posted_active_bounty_ids[x])):
          put_markdown(str("#### " + "Posted @ " + bounty["creation_date"]))
          put_markdown(str("#### Bounty " + posted_active_bounty_ids[x] + " by " + bounty["username"]))
          put_collapse("Requirements", str(bounty["requirements"]))
          put_markdown(str("#### Due Date:"))
          put_markdown(str(bounty["due_date"]))
          table_content = [[put_markdown("#### Selected Hunter"), put_markdown("#### Resume"), put_markdown("#### Chat"), put_markdown("#### Repo Link"), put_markdown("#### Add/Remove Repo Link")], []]
          table_content[1].append(put_text(bounty["selected_hunter"]))
          # Get resume
          selected_hunter_resume_file_path = str("resumes/" + bounty["selected_hunter"] + ".pdf")
          if os.path.exists(selected_hunter_resume_file_path):
            table_content[1].append(put_file(str(bounty["selected_hunter"] + ".pdf"), open(str("resumes/" + bounty["selected_hunter"] + ".pdf"), 'rb').read(), "Download Resume"))
          else:
            table_content[1].append(put_text("No Resume Available"))
          # Chat
          table_content[1].append(put_button(str("Chat with " + bounty["selected_hunter"]), onclick=lambda:chat_view(username, bounty["selected_hunter"])))
          # Repo link
          repo_link = db_get_repo_link(posted_active_bounty_ids[x])
          if repo_link:
            table_content[1].append(put_link("Link to repo", url=repo_link, new_window=True))
            table_content[1].append(put_button("Remove repo link", onclick=lambda:remove_repo_link(username, posted_active_bounty_ids[x])))  
          else:
            table_content[1].append(put_text("No repo linked yet"))
            table_content[1].append(put_button("Add a repo link", onclick=lambda:add_repo_link(username, posted_active_bounty_ids[x])))     
          # Show the table
          put_table(table_content)
          put_button(str("Deselect a hunter for " + posted_active_bounty_ids[x]), onclick=partial(deselect_hunter, username, posted_active_bounty_ids[x], bounty["selected_hunter"]))
          put_button(f"Mark bounty {posted_active_bounty_ids[x]} as complete", onclick=partial(complete_bounty, username, posted_active_bounty_ids[x]))
    # Get content for subtab3 (Post - Completed)
    posted_completed_bounties = db_get_post_completed_bounties_by_username(username)
    posted_completed_bounty_ids = [bounty['bounty_id'] for bounty in posted_completed_bounties]
    with use_scope("subtab3"):
      for x, bounty in list(enumerate(posted_completed_bounties)): 
        put_collapse(str(bounty["bounty_name"] + " - " + "$" + str(bounty["cash_reward"]) + " REWARD"), put_scope(str("subtab3-" + bounty["bounty_id"])))
        with use_scope(str("subtab3-" + posted_completed_bounty_ids[x])):
          put_markdown(str("#### " + "Posted @ " + bounty["creation_date"]))
          try:
            put_markdown(str("#### Completed @ " + bounty["completion_time"]))
          except:
            no_completion_time_errors = 1
          put_markdown(str("#### Bounty " + posted_completed_bounty_ids[x] + " by " + bounty["username"]))
          put_collapse("Requirements", str(bounty["requirements"]))
          put_markdown(str("#### Due Date:"))
          put_markdown(str(bounty["due_date"]))
          table_content = [[put_markdown("#### Selected Hunter"), put_markdown("#### Resume"), put_markdown("#### Chat"), put_markdown("#### Repo Link"), put_markdown("#### Add/Remove Repo Link")], []]
          table_content[1].append(put_text(bounty["selected_hunter"]))
          # Get resume
          selected_hunter_resume_file_path = str("resumes/" + bounty["selected_hunter"] + ".pdf")
          if os.path.exists(selected_hunter_resume_file_path):
            table_content[1].append(put_file(str(bounty["selected_hunter"] + ".pdf"), open(str("resumes/" + bounty["selected_hunter"] + ".pdf"), 'rb').read(), "Download Resume"))
          else:
            table_content[1].append(put_text("No Resume Available"))
          # Chat
          table_content[1].append(put_button(str("Chat with " + bounty["selected_hunter"]), onclick=lambda:chat_view(username, bounty["selected_hunter"])))
          # Repo link
          repo_link = db_get_repo_link(posted_completed_bounty_ids[x])
          if repo_link:
            table_content[1].append(put_link("Link to repo", url=repo_link, new_window=True))
            table_content[1].append(put_button("Remove repo link", onclick=lambda:remove_repo_link(username, posted_completed_bounty_ids[x])))  
          else:
            table_content[1].append(put_text("No repo linked yet"))
            table_content[1].append(put_button("Add a repo link", onclick=lambda:add_repo_link(username, posted_completed_bounty_ids[x])))     
          # Show the table
          put_table(table_content)
          put_button(str("Delete bounty " + posted_completed_bounty_ids[x] + " from completion history"), onclick=partial(delete_completed_bounty, username, posted_completed_bounty_ids[x]))
          put_button(str('Revert bounty ' + posted_completed_bounty_ids[x] + ' to "active" status'), onclick=partial(revert_completed_bounty, username, posted_completed_bounty_ids[x]))
    # Get content for subtab4 (Hunt - Applied)
    hunt_applied_bounties = db_get_hunt_applied_bounties_by_username(username)
    with use_scope("subtab4"):
      for bounty in hunt_applied_bounties:
        put_collapse(str(bounty["bounty_name"] + " - " + "$" + str(bounty["cash_reward"]) + " REWARD"), put_scope(str("subtab4-" + bounty["bounty_id"])))
        with use_scope(str("subtab4-" + bounty["bounty_id"])):
          put_markdown(str("#### " + "Posted @ " + bounty["creation_date"]))
          put_markdown(str("#### Bounty " + bounty["bounty_id"] + " by " + bounty["username"]))
          put_button(str("Chat with " + bounty["username"]), onclick=lambda:chat_view(username, bounty["username"]))
          put_collapse("Requirements", str(bounty["requirements"]))
          put_markdown(str("#### Due Date:"))
          put_markdown(str(bounty["due_date"]))
          put_markdown(str("#### Applicants: " + str(len(bounty["applicants"]))))
    # Get content for subtab5 (Hunt - Active)
    hunt_active_bounties = db_get_hunt_active_bounties_by_username(username)
    with use_scope("subtab5"):
      for bounty in hunt_active_bounties: 
        put_collapse(str(bounty["bounty_name"] + " - " + "$" + str(bounty["cash_reward"]) + " REWARD"), put_scope(str("subtab5-" + bounty["bounty_id"])))
        with use_scope(str("subtab5-" + bounty["bounty_id"])):
          put_markdown(str("#### " + "Posted @ " + bounty["creation_date"]))
          put_markdown(str("#### Bounty " + bounty["bounty_id"] + " by " + bounty["username"]))
          put_collapse("Requirements", str(bounty["requirements"]))
          put_markdown(str("#### Due Date:"))
          put_markdown(str(bounty["due_date"]))
          table_content = [[put_markdown("#### Poster"), put_markdown("#### Chat"), put_markdown("#### Repo Link"), put_markdown("#### Add/Remove Repo Link")], []]
          table_content[1].append(bounty["username"])
          # Chat
          table_content[1].append(put_button(str("Chat with " + bounty["username"]), onclick=lambda:chat_view(username, bounty["username"])))
          # Repo link
          repo_link = db_get_repo_link(bounty["bounty_id"])
          if repo_link:
            table_content[1].append(put_link("Link to repo", url=repo_link, new_window=True))
            table_content[1].append(put_button("Remove repo link", onclick=lambda:remove_repo_link(username, bounty["bounty_id"])))  
          else:
            table_content[1].append(put_text("No repo linked yet"))
            table_content[1].append(put_button("Add a repo link", onclick=lambda:add_repo_link(username, bounty["bounty_id"])))
          # Show the table
          put_table(table_content)
    # Get content for subtab6 (Hunt - Completed)
    hunt_completed_bounties = db_get_hunt_completed_bounties_by_username(username)
    with use_scope("subtab6"):
      for bounty in hunt_completed_bounties: 
        put_collapse(str(bounty["bounty_name"] + " - " + "$" + str(bounty["cash_reward"]) + " REWARD"), put_scope(str("subtab6-" + bounty["bounty_id"])))
        with use_scope(str("subtab6-" + bounty["bounty_id"])):
          put_markdown(str("#### " + "Posted @ " + bounty["creation_date"]))
          try:
            put_markdown(str("#### " + "Completed @ " + bounty["completion_date"] ))
          except:
            hunt_completed_bounty_completion_time_error = 1
          put_markdown(str("#### Bounty " + bounty["bounty_id"] + " by " + bounty["username"]))
          put_collapse("Requirements", str(bounty["requirements"]))
          put_markdown(str("#### Due Date:"))
          put_markdown(str(bounty["due_date"]))
          table_content = [[put_markdown("#### Poster"), put_markdown("#### Chat"), put_markdown("#### Repo Link"), put_markdown("#### Add/Remove Repo Link")], []]
          table_content[1].append(bounty["username"])
          # Chat
          table_content[1].append(put_button(str("Chat with " + bounty["username"]), onclick=lambda:chat_view(username, bounty["username"])))
          # Repo link
          repo_link = db_get_repo_link(bounty["bounty_id"])
          if repo_link:
            table_content[1].append(put_link("Link to repo", url=repo_link, new_window=True))
            table_content[1].append(put_button("Remove repo link", onclick=lambda:remove_repo_link(username, bounty["bounty_id"])))  
          else:
            table_content[1].append(put_text("No repo linked yet"))
            table_content[1].append(put_button("Add a repo link", onclick=lambda:add_repo_link(username, bounty["bounty_id"])))
          # Show the table
          put_table(table_content)


def chat_view(username, user_to_chat_with):
  hide_nav_bar(username)
  names = [username, user_to_chat_with]
  names.sort() # sort it in alphabetical order
  chat_thread_file_name = str(names[0] + "___" + names[1] + ".txt")
  # Check if chat file exists. If not, the users have never chatted.
  if not os.path.exists(str("chat_threads/" + chat_thread_file_name)):
    chat_thread_file = open(str("chat_threads/" + chat_thread_file_name), "w")
  with use_scope("main"):
    clear()
    put_scrollable(put_scope('msg-box'), height=300, keep_bottom=True)
    # Display chat history
    chat_history = open(str("chat_threads/" + chat_thread_file_name), "r").readlines()
    with use_scope("msg-box"):
      for line in chat_history:
        put_markdown(line.strip())
    # Get input
    while True:
      data = input_group('Send message', [
              input(name='msg'),
              actions(name='cmd', buttons=['Send', {'label': 'Exit', 'type': 'cancel'}])
          ])
      if data is None:
        break
      time_of_message = get_current_datetime()
      put_markdown(str("###### _" + time_of_message + "_"), scope='msg-box')
      put_markdown('`%s`: %s' % (username, data['msg']), sanitize=True, scope='msg-box')
      chat_thread_file = open(str("chat_threads/" + chat_thread_file_name), "a")
      chat_thread_file.write(str("###### _" + time_of_message + "_" + "\n"))
      chat_thread_file.write(str('`%s`: %s' % (username, data['msg']) + "\n"))
      chat_thread_file.close()
    # Done with chat
    clear()
  find_a_bounty(username)

def select_a_hunter(username, bounty_id, applicants):
  hide_nav_bar(username)
  with use_scope("main"):
    clear()
    selected_hunter = radio(str("Select a hunter for bounty " + bounty_id), options=applicants)
    success = db_select_a_hunter(bounty_id, selected_hunter)
    clear()
    if success:
      put_markdown("### Success!")
      put_markdown(str("##### " + selected_hunter + " is now hunting bounty " + bounty_id))
    else:
      put_markdown("### Error.")
      put_markdown(str("#### Cound not select " + selected_hunter + " as the hunter."))
  time.sleep(3)
  account(username)

def deselect_hunter(username, bounty_id, selected_hunter):
  hide_nav_bar(username)
  with use_scope("main"):
    clear()
    put_markdown(f"#### You are about to deselect {selected_hunter} from hunting bounty {bounty_id}.")
    choice = radio("Are you sure you want to do this?", options=["Yes. Deselect the hunter.", "No. Go back!"])
    if "Yes" in choice:
      db_deselect_a_hunter(bounty_id, selected_hunter)
      clear()
      put_markdown("### Success!")
      put_markdown(f"##### Bounty {bounty_id} is now re-opened to applicants.")
      time.sleep(3)
  account(username)

def complete_bounty(username, bounty_id):
  hide_nav_bar(username)
  with use_scope("main"):
    clear()
    put_markdown(f"#### You are about to mark bounty {bounty_id} as complete.")
    choice = radio("Are you sure you want to do this?", options=["Yes. Mark as complete.", "No. Go back!"])
    if "Yes" in choice:
      db_complete_bounty(bounty_id)
      clear()
      put_markdown("### Success!")
      put_markdown(f"##### Bounty {bounty_id} has been marked as completed.")
      time.sleep(3)
  account(username)

def delete_completed_bounty(username, bounty_id):
  hide_nav_bar(username)
  with use_scope("main"):
    clear()
    put_markdown(f"#### You are about to delete bounty {bounty_id} from the completion history.")
    choice = radio("Are you sure you want to do this?", options=["Yes. Delete it.", "No. Go back!"])
    if "Yes" in choice:
      db_delete_completed_bounty(bounty_id)
      clear()
      put_markdown("### Success!")
      put_markdown(f"##### Bounty {bounty_id} has been deleted.")
      time.sleep(3)
  account(username)

def revert_completed_bounty(username, bounty_id):
  hide_nav_bar(username)
  with use_scope("main"):
    clear()
    put_markdown(str('#### You are about to revert bounty ' + bounty_id + ' back to "active" status.'))
    choice = radio("Are you sure you want to do this?", options=["Yes. Revert it.", "No. Go back!"])
    if "Yes" in choice:
      db_revert_complete_bounty(bounty_id)
      clear()
      put_markdown("### Success!")
      put_markdown(f"##### Bounty {bounty_id} has been reverted.")
      time.sleep(3)
  account(username)

if __name__ == '__main__':
  start_server(cred_manager, port=80, debug=True)
