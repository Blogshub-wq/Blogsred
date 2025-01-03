import streamlit as st
from pymongo import MongoClient
from datetime import datetime

# MongoDB Configuration
client = MongoClient("mongodb+srv://starbucks70707:a7xVRbpyRC7lmyrG@chat.yztnp.mongodb.net/?retryWrites=true&w=majority&appName=chat")
db = client["chat"]
users_collection = db["users"]
messages_collection = db["messages"]

# App State Management
if "logged_in" not in st.session_state:
    st.session_state.logged_in = False
if "current_user" not in st.session_state:
    st.session_state.current_user = None
if "chat_mode" not in st.session_state:
    st.session_state.chat_mode = False

# Functions
def register_user(username, password):
    """Register a new user."""
    if users_collection.find_one({"username": username}):
        return "Username already exists."
    users_collection.insert_one({"username": username, "password": password})
    return "Registration successful! Please log in."

def authenticate_user(username, password):
    """Authenticate user credentials."""
    user = users_collection.find_one({"username": username, "password": password})
    return user is not None

def handle_chat():
    """Chat interface for sending messages."""
    st.write("Disscussion Area")
    st.divider()
    
    # Display existing messages
    chat_logs = messages_collection.find({"chat_id": "secret_chat"}).sort("timestamp", 1)
    
    for msg in chat_logs:
        st.markdown(f"**{msg['user']}**: {msg['message']}")
        
        # Edit and delete options
        if msg['user'] == st.session_state.current_user:
            edit_button = st.button("Edit", key=f"edit_{msg['_id']}")
            delete_button = st.button("Delete", key=f"delete_{msg['_id']}")
            
            if edit_button:
                # Store the message ID to edit it
                st.session_state.editing_message_id = msg['_id']
                st.session_state.editing_message = msg['message']
            
            if delete_button:
                messages_collection.delete_one({"_id": msg["_id"]})
                st.rerun()
    
    # If editing a message, show the text input for editing
    if 'editing_message_id' in st.session_state:
        new_message = st.text_input("Edit message", value=st.session_state.editing_message)
        if st.button("Save"):
            messages_collection.update_one(
                {"_id": st.session_state.editing_message_id},
                {"$set": {"message": new_message, "timestamp": datetime.now()}}
            )
            del st.session_state.editing_message_id  # Clear the session state for editing
            del st.session_state.editing_message
            st.rerun()
    
    st.divider()
    
    # Message Input
    user_message = st.text_input("Your message")
    
    if st.button("Send"):
        message_data = {
            "user": st.session_state.current_user,
            "message": user_message,
            "timestamp": datetime.now(),
            "chat_id": "secret_chat"
        }
        messages_collection.insert_one(message_data)
        st.success("Message sent!")
    
    # Chat Refresh Button
    if st.button("Refresh Chat"):
        st.rerun()

    if st.button("SOS"):
        st.session_state.logged_in = False
        st.session_state.current_user = None
        st.session_state.chat_mode = False  # Reset chat mode when logging out
        st.write("Logging out...")
        st.rerun()
        st.redirect("https://www.youtube.com/watch?v=dQw4w9WgXcQ")


# App Logic
if not st.session_state.logged_in:
    st.title("Blog Writer")
    choice = st.radio("Choose an option:", ["Login", "Register"])
    
    if choice == "Register":
        username = st.text_input("Username")
        password = st.text_input("Password", type="password")
        if st.button("Register"):
            result = register_user(username, password)
            st.success(result)
    
    if choice == "Login":
        username = st.text_input("Username")
        password = st.text_input("Password", type="password")
        if st.button("Login"):
            if authenticate_user(username, password):
                st.session_state.logged_in = True
                st.session_state.current_user = username
                st.session_state.chat_mode = False  # Ensure chat_mode is False when logging in
                st.success(f"Welcome, {username}!")
            else:
                st.error("Invalid credentials.")
else:
    st.title(f"Welcome, {st.session_state.current_user}!")
    access_code = st.text_input("Enter Invitation Code:")
    
    if st.button("Submit Code"):
        if access_code == "ShwetaXSatwik":  # Secret Code
            st.session_state.chat_mode = True
        else:
            st.error("Correct code! Here is web link: https://bloggers.streamlit.app/")
    
    if st.session_state.chat_mode:
        handle_chat()

    # SOS Button - after the Refresh Chat button
