import streamlit as st
import hashlib

def check_password():
    if "password_correct" not in st.session_state:
        st.session_state["password_correct"] = False

    if st.session_state["password_correct"]:
        return True

    col1, col2 = st.columns([1, 2])
    with col1:
        st.image("attached_assets/image_1739823857967.png", width=150)
    with col2:
        st.title("VEGA")
        st.markdown("##### Vigilant Enterprise Guard Analytics")

    st.markdown("""
        <style>
        .stForm {
            background-color: #252525;
            padding: 30px;
            border-radius: 8px;
            box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
        }
        </style>
    """, unsafe_allow_html=True)

    with st.form("login_form"):
        username = st.text_input("Username")
        password = st.text_input("Password", type="password")
        submit = st.form_submit_button("Login")

        if submit:
            if (
                username.lower() == "admin" and
                password == "admin"
            ):
                st.session_state["password_correct"] = True
                st.switch_page("pages/execute_rules.py")
                return True
            else:
                st.error("😕 Invalid username or password")
                return False

    return False