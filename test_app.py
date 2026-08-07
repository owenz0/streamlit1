import streamlit as st

with st.form("calculator"):
    num1 = st.number_input("First number")
    num2 = st.number_input("Second number")
    submitted = st.form_submit_button("add+ballons")
    if (submitted):
        st.write(num1+num2)
        st.balloons()
