from datetime import datetime

import requests
import streamlit as st

# Configure page
st.set_page_config(page_title="Prompt Security Chat", layout="wide")

# Initialize session state for conversation history
if "messages" not in st.session_state:
    st.session_state.messages = []

# Orchestrator URL
ORCHESTRATOR_URL = "http://orchestrator:7000/process"

st.title("Prompt Security Chat >>")

# Display chat history
for msg in st.session_state.messages:
    if msg["role"] == "user":
        with st.chat_message("user"):
            st.markdown(msg["content"])
            st.caption(msg["timestamp"])
    else:
        with st.chat_message("assistant"):
            if msg["error"]:
                st.error(f"{msg['content']}")
            else:
                st.markdown("**LLM Response:**")
                st.info(msg["content"])
                
                if msg.get("sanitized_prompt"):
                    with st.expander("📋 Details"):
                        st.markdown("**Sanitized Prompt:**")
                        st.text(msg["sanitized_prompt"])

# Input section - at the bottom
user_input = st.chat_input("Type your prompt here...")


# Handle user input
if user_input:
    # Add user message to history
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    st.session_state.messages.append({
        "role": "user",
        "content": user_input,
        "timestamp": timestamp
    })
    
    # Make request to orchestrator
    with st.spinner("Processing..."):
        try:
            payload = {"prompt": user_input.strip()}
            response = requests.post(
                ORCHESTRATOR_URL,
                json=payload,
                timeout=15.0
            )
            
            if response.status_code == 200:
                data = response.json()
                st.session_state.messages.append({
                    "role": "assistant",
                    "content": data.get("llm_response", "No response"),
                    "sanitized_prompt": data.get("sanitized_prompt", ""),
                    "error": False,
                    "status_code": 200
                })
            else:
                error_detail = response.json().get("detail", "Unknown error")
                st.session_state.messages.append({
                    "role": "assistant",
                    "content": error_detail,
                    "error": True,
                    "status_code": response.status_code
                })
                
        except requests.exceptions.Timeout:
            st.session_state.messages.append({
                "role": "assistant",
                "content": "Request timeout. The Orchestrator took too long to respond.",
                "error": True,
                "status_code": 504
            })
        except requests.exceptions.ConnectionError:
            st.session_state.messages.append({
                "role": "assistant",
                "content": f"Connection error. Make sure the Orchestrator service is running at {ORCHESTRATOR_URL}",
                "error": True,
                "status_code": 503
            })
        except Exception as e:
            st.session_state.messages.append({
                "role": "assistant",
                "content": f"Unexpected error: {str(e)}",
                "error": True,
                "status_code": 500
            })
    
    st.rerun()

# Footer
st.divider()
