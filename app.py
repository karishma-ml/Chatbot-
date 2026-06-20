import streamlit as st
import requests
import json 

# AI (Ollama)---------------------
def ask_ollama(prompt):
    try:
        response= requests.post(
            "http://localhost:11434/api/generate",
            json={"model": "llama3.2","prompt": prompt }, 
            stream=True 
        )
        output= ""
        for line in response.iter_lines():
            if line:
                output += json.loads(line.decode()).get("response", "")
        return output.strip()
    except Exception as e:
        return f"Ollama Error: {e}"
    
# session setup ---------------------------

defaults = {
    "users": {},
    "current_user": None,
    "active_sidebar": None,
    "show_help": False,
    "started": False,
    "history": {},
    "show_history": False,
    "answer": None
}
for key, val in defaults.items():
    if key not in st.session_state:
        st.session_state[key]= val

# page config --------------

st.set_page_config(page_title='AI Personal Assistent', layout='wide', initial_sidebar_state='collapsed')

st.markdown("""
    <style>
    .stApp {background-color: #071023; color: white;}
    .stButton > button {
    background-color: #1a3c6e; color: white;
    padding: 8px, 20px; border-radius: 6px; font-weight: 600;
    }
    .stButton> button:hover { background-color: #244c8a;}
    </style>
    """, unsafe_allow_html=True,
)

# SIDEBAR SECTION  -----------------------------
st.sidebar.title("User Account")

if st.sidebar.button("Login", key="sb_login"):
    st.session_state.active_sidebar= "login"

if st.sidebar.button("Sign Up", key="sb_signup"):
    st.session_state.active_sidebar= "signup"

st.sidebar.markdown("---")

# LOGIN FORM -----------------------------
if st.session_state.active_sidebar == "login":
    st.sidebar.subheader("🔐 Login")
    user= st.sidebar.text_input("Username", key="lg_user")
    pwd= st.sidebar.text_input("Password", type="password", key="lg_pwd")
    if st.sidebar.button("Login", key="lg_submit"):
        if user in st.session_state.users and st.session_state.users[user]==pwd:
            st.session_state.current_user= user
            st.sidebar.success(f"Logged in as {user}")
            st.session_state.active_sidebar= None  
        else:
            st.sidebar.error("Invalid username or password")

# SIGNUP FORM ------------------------------------
elif st.session_state.active_sidebar== "signup":
    st.sidebar.subheader("📝 Create Account")
    new_user= st.sidebar.text_input("Create Username", key="su_user")
    new_pwd= st.sidebar.text_input("Create Password", type="password", key="su_pwd")
    if st.sidebar.button("Sign Up", key= "sidebar_signup"):
        if new_user in st.session_state.users:
            st.sidebar.error("Username already exists!")
        else:
            st.session_state.users[new_user]= new_pwd
            st.sidebar.success("Account created! Now login.")
            st.session_state.active_sidebar= None 

# SHOW LOGGED-IN USERNAME ------------------------
if st.session_state.current_user:
    st.markdown(
        f"<div style='text-align:right; font-size:18px; color:#8ab4f8;'>"
        f"Logged in as <b>{st.session_state.current_user}</b></div>",
        unsafe_allow_html=True
    )                

# MAIN TITLE --------------------
st.title("**AI-Powered chatbot for Insant Support & Solution**")

# TOP BUTTONS ---------------------
col1, col2, col3= st.columns([1,2,1])
with col2:
    start_btn, help_btn = st.columns([1,1])
    if start_btn.button("Get Started", use_container_width= True):
        st.session_state.started= True
        st.session_state.show_help= False
        st.session_state.show_history= False 
    if help_btn.button("Need Help", use_container_width=True):
        st.session_state.show_help= not st.session_state.show_help
        st.session_state.started= False
        st.session_state.show_history=False 

# HELP SECTION  ------------------

if st.session_state.show_help:
    st.info("How to use this AI Assistant")

    with st.expander("How to ask questions?"):
        st.write("""
        - Click Get Started
        - Type your question in the input box
        - Click Ask
        - The AI will answer using the local Ollama model
        """)
    with st.expander("What can this chatbot do?"):
        st.write("""
        - Explain topics  
        - Solve doubts  
        - Write summaries  
        - Answer general questions  
        - Help with coding  
        """)

    with st.expander("How to check history?"):
        st.write("""
        - You must **login or signup** to view your chat history  
        - After logging in, click the **History** button  
        - Your previously asked questions and answers will be shown  
        - Each user has their **own separate history**  
        - History helps you revisit old queries anytime  
        """)

    with st.expander("Troubleshooting"):
        st.write("""
        - Ensure Ollama is running  
        - Ensure model is downloaded  
        - Ask clear questions  
        """)

# CHAT INPUT SECTION -----------------------------------
if st.session_state.started:
    user_query= st.text_input("Ask me anything...", placeholder="Type your question here...")

    ask_col, history_col, empty= st.columns([1, 1, 5])
    with ask_col:
        ask_btn= st.button("Ask")
    with history_col:
        history_btn= st.button("History")

    # hISTORY BUTTON ----------------------
    if history_btn:
        st.session_state.answer= None 
        st.session_state.show_help= False

        if not st.session_state.current_user:
            st.warning("You must login first. You can login or SignUp from the sidebar.")
            st.session_state.show_history= False
        else:
            st.session_state.show_history= True

# ASK BUTTON ----------------------------
    if ask_btn:
        st.session_state.show_history= False
        if user_query.strip():        #strip will remove extra spaces
            answer= ask_ollama(user_query)
            st.session_state.answer= answer

            if st.session_state.current_user:
                user= st.session_state.current_user
                st.session_state.history.setdefault(user, [])  #if user does not have any history then set default history i.e. empty list.
                st.session_state.history[user].append({
                    "q": user_query,
                    "a": answer
                })
        else:
            st.warning("Please enter a question.")

    # SHOW ANSWERS ----------------------------------
    if st.session_state.answer and not st.session_state.show_history:
        st.write("Answer:")
        st.write(st.session_state.answer)

# HISTORY SECTION ---------------------------------
if st.session_state.show_history and st.session_state.current_user:
    st.subheader("Your chat history")

    user = st.session_state.current_user
    data= st.session_state.history.get(user, [])

    if data:
        for item in data:
            with st.expander(item["q"]):
                st.write(item["a"])
    else:
        st.info("No history yet.")

# FOOTER ---------------
st.markdown("<div style= 'position: fixed; left:18px; bottom:12px;'> Made with ❤️ -- Streamlit</div>", unsafe_allow_html=True)