import streamlit as st
from src.backend_config import PSUChatBackend
import time

# App configuration
st.set_page_config(
    page_title="PSU Chatbot",
    page_icon="🎓",
    layout="centered",  # Changed to centered for Claude-like experience
) 

# Initialize backend if not already in session state
if 'backend' not in st.session_state:
    st.session_state.backend = PSUChatBackend()
    # Automatically initialize the system
    with st.spinner("Initializing system. Please Wait..."):
        success, message = st.session_state.backend.initialize_system()
        if success:
            st.session_state.initialized = True
        else:
            st.session_state.initialized = False
            st.session_state.init_error = message

# Initialize chat history in session state if it doesn't exist
if 'messages' not in st.session_state:
    st.session_state.messages = []
    # Add welcome message
    welcome_message = "Hello! I'm the ParSU Citicharbot. I can help you with information about Partido State University services and transactions. What would you like to know?"
    st.session_state.messages.append({"role": "assistant", "content": welcome_message})

# Initialize clicked example tracker
if 'clicked_example' not in st.session_state:
    st.session_state.clicked_example = None

# Custom CSS for Claude-like interface
st.markdown(
    """
    <style>
    /* Main container styling */
    .main .block-container {
        max-width: 800px;
        padding-top: 2rem;
        padding-bottom: 3rem;
    }
    
    /* Header styling */
    h1 {
        font-size: 2rem !important;
        font-weight: 600 !important;
        margin-bottom: 0.5rem !important;
        color: #111827;
    }
    
    /* Message styling */
    .stChatMessage {
        background-color: transparent !important;
        border-radius: 0 !important;
        padding: 1rem 0 !important;
        border-bottom: 1px solid rgba(0, 0, 0, 0.05);
    }
    
    /* User message styling */
    .stChatMessage[data-testid="stChatMessage-user"] {
        background-color: transparent !important;
    }
    
    /* Bot message styling */
    .stChatMessage[data-testid="stChatMessage-assistant"] {
        background-color: transparent !important;
    }
    
    /* Avatar styling */
    .stChatMessageAvatar {
        background-color: #f3f4f6 !important;
        border-radius: 50% !important;
    }
    
    /* Input area styling */
    .stChatInputContainer {
        padding-top: 1rem !important;
        border-top: 1px solid rgba(0, 0, 0, 0.05) !important;
    }
    
    /* Chat input styling */
    .stChatInput {
        border: 1px solid #e5e7eb !important;
        border-radius: 8px !important;
        padding: 0.75rem 1rem !important;
    }
    
    /* Remove default Streamlit padding */
    .css-18e3th9 {
        padding-top: 0 !important;
        padding-bottom: 0 !important;
    }
    
    /* Thinking animation */
    @keyframes pulse {
        0% { opacity: 0.5; }
        50% { opacity: 1; }
        100% { opacity: 0.5; }
    }
    
    .thinking-dots {
        display: inline-block;
        animation: pulse 1.5s infinite;
    }
        /* Sidebar styling - Orange background (unchanged) */
    [data-testid="stSidebar"] {
        background-color: #fd7e14 !important; /* Dark Orange */
        color: #000000 !important; /* Black text */
        padding: 1rem;
    }
    
    /* Example question buttons */
    [data-testid="stSidebar"] button {
        background-color: #fd7e14 !important;
        color: #000000 !important;
        border: 1px solid #000000 !important;
    }
    
    [data-testid="stSidebar"] button:hover {
        background-color: #FFD700 !important; /* Gold for hover state */
        color: #000000 !important;
    }
    /* Footer styling */
    .footer {
        text-align: center;
        margin-top: 2rem;
        padding-top: 1rem;
        border-top: 1px solid rgba(0, 0, 0, 0.05);
        color: #6b7280;
        font-size: 0.875rem;
    }
    </style>
    """,
    unsafe_allow_html=True,
)

# Side container for logo and info
with st.sidebar:
    st.image("https://via.placeholder.com/150x150.png?text=PSU+Logo", width=120)
    st.title("ParSU Citicharbot")
    st.markdown("---")
    st.markdown("### About")
    st.write("This chatbot provides information about Partido State University services, procedures, and transactions.")
    st.markdown("---")
    
    # Example questions section
    st.markdown("### Example Questions")
    example_questions = [
        "How do I apply for admission?",
        "How to get a Student ID?",
        "How can i Enroll?",
        "How do I request for documents for scholarship?",
    ]
    
    # Define function to set clicked example in session state
    def set_example_question(question):
        st.session_state.clicked_example = question
    
    # Create buttons with the callback
    for q in example_questions:
        st.button(q, key=f"example_{q}", on_click=set_example_question, args=(q,))

# Main chat area
st.markdown("<h1>Partido State University Assistant</h1>", unsafe_allow_html=True)

# Check if system is initialized
if not st.session_state.get('initialized', True):
    st.error(f"System initialization failed: {st.session_state.get('init_error', 'Unknown error')}")
    st.button("Retry Initialization", on_click=lambda: st.session_state.pop('backend', None))
else:
    # Display chat history
    for message in st.session_state.messages:
        with st.chat_message(message["role"], avatar="🎓" if message["role"] == "assistant" else "👤"):
            st.write(message["content"])

    # Process example question if one was clicked
    if st.session_state.clicked_example:
        query = st.session_state.clicked_example
        
        # Add user message to chat history
        st.session_state.messages.append({"role": "user", "content": query})
        
        # Display user message
        with st.chat_message("user", avatar="👤"):
            st.write(query)
        
        # Generate response
        if st.session_state.backend.chain:
            with st.chat_message("assistant", avatar="🎓"):
                message_placeholder = st.empty()
                message_placeholder.markdown('<span class="thinking-dots">Thinking...</span>', unsafe_allow_html=True)
                
                success, response = st.session_state.backend.generate_response(query)
                
                # Simulating typing effect
                if success:
                    time.sleep(0.5)  # Brief pause to simulate thinking
                    message_placeholder.markdown(response, unsafe_allow_html=True)
                else:
                    message_placeholder.error("Sorry, I encountered an error. Please try asking something else.")
                    response = "Sorry, I encountered an error. Please try asking something else."
                
                # Add assistant response to chat history
                st.session_state.messages.append({"role": "assistant", "content": response})
        
        # Clear the clicked example to prevent it from being processed again
        st.session_state.clicked_example = None
        
        # Rerun the app to update the chat display
        if hasattr(st, 'rerun'):
            st.rerun()
        else:
            st.experimental_rerun()

    # Chat input
    query = st.chat_input("Ask a question about Partido State University")

    # Process user query
    if query:
        # Add user message to chat history
        st.session_state.messages.append({"role": "user", "content": query})
        
        # Display user message
        with st.chat_message("user", avatar="👤"):
            st.write(query)
        
        # Generate response
        if st.session_state.backend.chain:
            with st.chat_message("assistant", avatar="🎓"):
                message_placeholder = st.empty()
                message_placeholder.markdown('<span class="thinking-dots">Thinking...</span>', unsafe_allow_html=True)
                
                success, response = st.session_state.backend.generate_response(query)
                
                # Simulating typing effect
                if success:
                    time.sleep(0.5)  # Brief pause to simulate thinking
                    message_placeholder.markdown(response, unsafe_allow_html=True)
                else:
                    message_placeholder.error("Sorry, I encountered an error. Please try asking something else.")
                    response = "Sorry, I encountered an error. Please try asking something else."
                
                # Add assistant response to chat history
                st.session_state.messages.append({"role": "assistant", "content": response})
        else:
            with st.chat_message("assistant", avatar="🎓"):
                message = "The system initialization failed. Please reload the app and try again."
                st.write(message)
                
                # Add assistant response to chat history
                st.session_state.messages.append({"role": "assistant", "content": message})

    # Footer
    st.markdown(
        """
        <div class="footer">
            <p>Partido State University Chatbot - Powered by Mistral</p>
            <p>© 2025 ParSU. All rights reserved.</p>
        </div>
        """, 
        unsafe_allow_html=True
    )