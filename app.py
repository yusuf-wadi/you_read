import streamlit as st
st.set_page_config(page_icon=":book:", page_title='YouRead')

from components.main import main
from components.sidebar import sidebar
# from components.app_auth import login_register
# from components.landing import landing
import subprocess

app_version = "0.0.1"
# session state

if "authentication_status" not in st.session_state:
    st.session_state['authentication_status'] = None
if "name" not in st.session_state:
    st.session_state['name'] = " "
if "username" not in st.session_state:
    st.session_state['username'] = " "
if "credits" not in st.session_state:
    st.session_state['credits'] = None

# start backend for stripe
# subprocess.Popen(["ruby" ,"src/server.rb"])

if __name__ == '__main__':
    
    st.title(f":book: YouRead v{app_version}")
    
    ## auth feature
    
    # if not st.session_state['authentication_status']:
    #     landing()
    #     login_register()
    # else:
    #     main()
    #     sidebar()
    
    ## ##
    
    main()
    sidebar()
