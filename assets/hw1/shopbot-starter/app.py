from __future__ import annotations

import streamlit as st

from chatbot import MODEL, ask_shopbot
from db import ensure_database, list_customers

st.set_page_config(page_title="ShopBot", page_icon="🛍️")
ensure_database()

st.title("ShopBot")
st.caption("A demonstration customer-service chatbot using synthetic data.")

customers = list_customers()
customer_by_label = {
    f"{c['name']} (customer {c['customer_id']})": c for c in customers
}

with st.sidebar:
    st.header("Demo login")
    selected_label = st.selectbox("Logged-in customer", list(customer_by_label))
    selected_customer = customer_by_label[selected_label]
    st.caption(f"Model: {MODEL}")
    if st.button("Clear conversation"):
        st.session_state.messages = []
        st.session_state.last_customer_id = selected_customer["customer_id"]
        st.rerun()

if "messages" not in st.session_state:
    st.session_state.messages = []
if "last_customer_id" not in st.session_state:
    st.session_state.last_customer_id = selected_customer["customer_id"]

# Treat switching the demo identity like logging out and logging in as another user.
if st.session_state.last_customer_id != selected_customer["customer_id"]:
    st.session_state.messages = []
    st.session_state.last_customer_id = selected_customer["customer_id"]

for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

prompt = st.chat_input("Ask about your purchases")
if prompt:
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.markdown(prompt)

    try:
        api_key = st.secrets["OPENAI_API_KEY"]
    except Exception:
        st.error(
            "OPENAI_API_KEY is not configured. Add it to "
            ".streamlit/secrets.toml locally or to your deployment secrets."
        )
        st.stop()

    with st.chat_message("assistant"):
        with st.spinner("Thinking..."):
            answer, _trace = ask_shopbot(
                api_key=api_key,
                customer=selected_customer,
                conversation=st.session_state.messages,
            )
        st.markdown(answer)

    st.session_state.messages.append({"role": "assistant", "content": answer})
