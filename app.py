import streamlit as st
from src.backend_config import PSUChatBackend
import time

# App configuration
st.set_page_config(
    page_title="PSU Chatbot",
    page_icon="🎓",
    layout="centered", 
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
    /* Setting base fonts and colors */
    [data-testid="stAppViewContainer"] {
        background-color: #ebf6f7 !important;
        color: #111827;
    }
    [data-testid="stquery"] {
        background-color: #000080 !important;
    }
        [data-testid="stChatInput"] {
        position: fixed;
        bottom: 5rem;
        left: 30%;
        width: 40%;
        background-color: white;
        padding: 1rem;
        z-index: 1000;
        box-shadow: 0 -2px 5px rgba(0, 0, 0, 0.1);
    }
    [data-testid="stChatMessageContainer"] {
        padding-bottom: 50px; /* Adjust this value based on the height of your input bar */
    }

    
    /* Chat container styling */
    .chat-header h1 {
        font-size: 1.8rem !important;
        font-weight: 600 !important;
        color: #111827;
        background-color: transparent !important;
        margin-bottom: 0.5rem !important;
        text-align: left;
    }
    
    /* Message container height control */
   [data-testid="stChatMessageContainer"] {
        position: fixed;
        top: 50%;
        left: 50%;
        transform: translate(-50%, -50%);
        width: 90%;
        height: 70%;
        border: 5px;
        border-radius: 10px;
        padding: 1rem;
    }

    
    /* User message styling */
    .stChatMessage[data-testid="stChatMessage-user"] {
        background-color: #fd7e14 !important;
        border-radius: 25%; !important;
        padding: 1.5rem 0 !important;
        border-bottom: 1px solid rgba(0, 0, 0, 0.05);
        margin-bottom: 0 !important;
    }
    
    /* Bot message styling */
   [data-testid="stChatMessage-assistant"] {
        background-color: black !important;
        border:5px blue;
        border-bottom: 1px solid rgba(0, 0, 0, 0.05);
    }
    
    /* Force all text in messages to be black */
    .stChatMessage p, .stChatMessage span, .stChatMessage div {
        color: #374151 !important;
        font-size: 1rem !important;
        line-height: 1.5 !important;
    }       
    /* Chat input styling */
    .stChatInput, [data-testid="stChatInput"] {
        background-color: #fd7e14 !important;
        color: #111827 !important;
        font-size: 1rem !important;
        border: 5px solid #0d6efd; !important;
        border-radius: 8px !important;
        padding: 0.75rem !important;
        box-shadow: 0 1px 2px rgba(0, 0, 0, 0.05) !important;
    }
    .stcontainer{
        border: 3px !important;
        border-radius: 8px !important;
    }
    /* Thinking animation */
    @keyframes typing {
        0% { width: 0; }
        20% { width: 1ch; }
        40% { width: 2ch; }
        60% { width: 3ch; }
        80% { width: 4ch; }
        100% { width: 5ch; }
    }
    
    .thinking-dots {
        display: inline-block;
        overflow: hidden;
        white-space: nowrap;
        animation: typing 1.5s steps(5) infinite;
        border-right: 2px solid #374151;
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
        border-radius: 4px !important;
        margin-bottom: 0.5rem !important;
        text-align: left !important;
        transition: background-color 0.2s !important;
        width: 100%;
        overflow: hidden;
        text-overflow: ellipsis;
        white-space: nowrap;
    }
    
    [data-testid="stSidebar"] button:hover {
        background-color: #001b4c !important;
        color: white !important;
    }
    [data-testid="stsession_state"] {
        background-color: #000080 !important; /* Navy blue */
    }
    
    /* Additional styles for sidebar elements */
    [data-testid="stSidebar"] h3 {
        font-size: 1.2rem !important;
        margin-top: 1.5rem !important;
        margin-bottom: 1rem !important;
    }
    
    /* Create space at the bottom to ensure footer doesn't overlap content */
    .content-wrapper {
        margin-bottom: 10px;
        padding-bottom: 40px;
    }
    
    /* Message spacing */
    .stChatMessage {
        margin-bottom: 1rem !important;
    }
    </style>

    <!-- Chat Container with Header -->
    <div class="chat-header">
        <h1>Welcome!</h1>
    </div>
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
        "How can I enroll?",
        "How do I request for documents for scholarship?",
    ]
    
    # Define function to set clicked example in session state
    def set_example_question(question):
        st.session_state.clicked_example = question
    
    # Create buttons with the callback
    for q in example_questions:
        st.button(q, key=f"example_{q}", on_click=set_example_question, args=(q,))

# Check if system is initialized
if not st.session_state.get('initialized', True):
    st.error(f"System initialization failed: {st.session_state.get('init_error', 'Unknown error')}")
    st.button("Retry Initialization", on_click=lambda: st.session_state.pop('backend', None))
else:
    # Main content wrapper to add space for footer
    st.markdown('<div class="content-wrapper">', unsafe_allow_html=True)
    
    # Create a container for chat messages
    chat_container = st.container()
    
    with chat_container:
        # Display chat history
        for i, message in enumerate(st.session_state.messages):
            is_last = i == len(st.session_state.messages) - 1
            class_name = "last-message" if is_last else ""
            
            with st.chat_message(message["role"], avatar="🎓" if message["role"] == "assistant" else "👤"):
                st.markdown(f'<div class="{class_name}">{message["content"]}</div>', unsafe_allow_html=True)

    # Process example question if one was clicked
    if st.session_state.clicked_example:
        query = st.session_state.clicked_example
        
        # Add user message to chat history
        st.session_state.messages.append({"role": "user", "content": query})
        
        # Display user message
        with chat_container:
            with st.chat_message("user", avatar="👤"):
                st.markdown(f'<div class="last-message">{query}</div>', unsafe_allow_html=True)
        
        # Generate response
        if st.session_state.backend.chain:
            with chat_container:
                with st.chat_message("assistant", avatar="🎓"):
                    message_placeholder = st.empty()
                    message_placeholder.markdown('<div class="thinking-dots">Thinking</div>', unsafe_allow_html=True)
                    
                    success, response = st.session_state.backend.generate_response(query)
                    
                    # Simulating typing effect
                    if success:
                        time.sleep(0.5)  # Brief pause to simulate thinking
                        message_placeholder.markdown(f'<div class="last-message">{response}</div>', unsafe_allow_html=True)
                    else:
                        message_placeholder.error("Sorry, I encountered an error. Please try asking something else.")
                        response = "Sorry, I encountered an error. Please try asking something else."
                    
                    # Add assistant response to chat history
                    st.session_state.messages.append({"role": "assistant", "content": response})
        
        # Clear the clicked example to prevent it from being processed again
        st.session_state.clicked_example = None

    # Footer container for chat input
    footer_container = st.container() 
    with footer_container:
        st.markdown('<div class="chat-footer">', unsafe_allow_html=True)
        # Chat input - now properly contained in the footer
        query = st.chat_input("Ask a question about Partido State University Citizen Charter")
        st.markdown('</div>', unsafe_allow_html=True)
    
    # Process user query
    if query:
        # Add user message to chat history
        st.session_state.messages.append({"role": "user", "content": query})
        
        # Display user message
        with chat_container:
            with st.chat_message("user", avatar="👤"):
                st.markdown(f'<div class="last-message">{query}</div>', unsafe_allow_html=True)
        
        # Generate response
        if st.session_state.backend.chain:
            with chat_container:
                with st.chat_message("assistant", avatar="🎓"):
                    message_placeholder = st.empty()
                    message_placeholder.markdown('<div class="thinking-dots">Thinking</div>', unsafe_allow_html=True)
                    
                    success, response = st.session_state.backend.generate_response(query)
                    
                    # Simulating typing effect
                    if success:
                        time.sleep(0.5)  # Brief pause to simulate thinking
                        message_placeholder.markdown(f'<div class="last-message">{response}</div>', unsafe_allow_html=True)
                    else:
                        message_placeholder.error("Sorry, I encountered an error. Please try asking something else.")
                        response = "Sorry, I encountered an error. Please try asking something else."
                    
                    # Add assistant response to chat history
                    st.session_state.messages.append({"role": "assistant", "content": response})
        else:
            with chat_container:
                with st.chat_message("assistant", avatar="🎓"):
                    message = "The system initialization failed. Please reload the app and try again."
                    st.markdown(f'<div class="last-message">{message}</div>', unsafe_allow_html=True)
                    
                    # Add assistant response to chat history
                    st.session_state.messages.append({"role": "assistant", "content": message})
