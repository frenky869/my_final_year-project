import streamlit as st
import pandas as pd
# IMPORTANT: Use the core pandasai components for clarity
# The error means the environment can't find this library.
# We will fix this by providing the correct requirements below.

from pandasai.smart_dataframe import SmartDataframe

from pandasai.llm import OpenAI 
import os 
# We remove the import 'from utils.config import API_KEY' as that file does not exist here.

# --- LLM Setup ---
# Initialize API Key
# This function is defined globally to handle the API key check
def get_openai_api_key():
    """Retrieves API key from Streamlit secrets or sidebar input."""
    # 1. Try Streamlit Secrets (Recommended for deployment)
    if "OPENAI_API_KEY" in st.secrets:
        return st.secrets["OPENAI_API_KEY"]
    
    # 2. Use Sidebar Input (Fallback for local testing)
    with st.sidebar:
        api_key = st.text_input("OpenAI API Key", type="password",
                                help="Get your API key from https://platform.openai.com/api-keys")
        if api_key:
            return api_key
    return None

# --- Main Functions ---

def load_data(uploaded_file):
    """Load data from uploaded CSV or Excel file"""
    try:
        if uploaded_file.name.endswith('.csv'):
            df = pd.read_csv(uploaded_file)
        elif uploaded_file.name.endswith(('.xlsx', '.xls')):
            df = pd.read_excel(uploaded_file)
        else:
            st.error("Unsupported file format. Please upload CSV or Excel files.")
            return None
        return df
    except Exception as e:
        st.error(f"Error loading file: {str(e)}")
        return None

def display_data_overview(df):
    """Display basic information about the dataset"""
    st.subheader("📋 Data Overview")
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.metric("Number of Rows", df.shape[0])
    with col2:
        st.metric("Number of Columns", df.shape[1])
    with col3:
        st.metric("Memory Usage", f"{df.memory_usage(deep=True).sum() / 1024**2:.2f} MB")
    
    # Data preview
    st.write("**Data Preview (First 5 rows):**")
    st.dataframe(df.head(), use_container_width=True)
    
    # Column information
    st.write("**Column Information:**")
    col_info = pd.DataFrame({
        'Column Name': df.columns,
        'Data Type': df.dtypes,
        'Non-Null Count': df.count(),
        'Null Count': df.isnull().sum()
    })
    st.dataframe(col_info, use_container_width=True)

def safe_chat(smart_df, question):
    """Safely handle chat responses and convert to Streamlit components"""
    try:
        # Use simple chat method
        response = smart_df.chat(question)
        return response
    except Exception as e:
        return f"Error: {str(e)}"

def main():
    api_key = get_openai_api_key()

    # --- Page Configuration and CSS ---
    st.set_page_config(
        page_title="DataSense - No-Code Data Analysis",
        page_icon="📊",
        layout="wide",
        initial_sidebar_state="expanded"
    )

    st.markdown("""
    <style>
        .main-header {
            font-size: 3rem;
            color: #1f77b4;
            text-align: center;
            margin-bottom: 2rem;
        }
        .sub-header {
            font-size: 1.5rem;
            color: #2e86ab;
            margin-bottom: 1rem;
        }
        .info-box {
            background-color: #f0f2f6;
            padding: 20px;
            border-radius: 10px;
            margin: 10px 0;
        }
        .success-box {
            background-color: #d4edda;
            padding: 15px;
            border-radius: 10px;
            margin: 10px 0;
        }
        .error-box {
            background-color: #f8d7da;
            padding: 15px;
            border-radius: 10px;
            margin: 10px 0;
        }
    </style>
    """, unsafe_allow_html=True)

    # Header
    st.markdown('<div class="main-header">📊 DataSense</div>', unsafe_allow_html=True)
    st.markdown("### Your No-Code Data Analysis Assistant")
    
    # Check for API Key early
    if not api_key:
        st.warning("⚠️ Please enter your OpenAI API key in the sidebar to activate the analysis engine.")
        st.info("The application requires an API key to communicate with the AI model.")
        return

    # Sidebar elements
    with st.sidebar:
        st.header("📁 Data Upload")
        uploaded_file = st.file_uploader(
            "Choose a CSV or Excel file",
            type=['csv', 'xlsx', 'xls'],
            help="Upload your structured data file"
        )
        
        st.header("💡 Example Questions")
        st.markdown("""
        - **"Show me sales trends by month"**
        - **"Create a bar chart of top 5 products by revenue"**
        - **"What is the average age of customers?"**
        - **"Filter rows where price is less than 100"**
        """)


    # Main content area
    if uploaded_file is not None:
        # Load and display data
        df = load_data(uploaded_file)
        if df is not None:
            display_data_overview(df)
            
            # Initialize LLM and SmartDataframe
            try:
                llm = OpenAI(api_token=api_key)
                # Ensure the cache is disabled so the model re-runs every time
                smart_df = SmartDataframe(df, config={"llm": llm, "enable_cache": False})
                
                st.markdown("---")
                st.markdown('<div class="sub-header">💬 Ask Questions About Your Data</div>', unsafe_allow_html=True)
                
                # Chat interface
                user_question = st.text_area(
                    "Enter your question in plain English:",
                    placeholder="e.g., 'What is the average age?', 'Show top 5 products by sales', 'Plot a histogram of the customer ages'",
                    height=100
                )
                
                col1, col2 = st.columns([1, 4])
                with col1:
                    analyze_btn = st.button("Analyze Data", type="primary", use_container_width=True)
                with col2:
                    # Added a hidden element to clear results if needed
                    st.empty() # Placeholder for the "Clear Results" button logic if you want to implement it later
                
                if analyze_btn and user_question:
                    st.markdown("---")
                    with st.spinner("🤔 Analyzing your data... This may take a few seconds."):
                        try:
                            # Get response from PandasAI
                            response = safe_chat(smart_df, user_question)
                            
                            # Display response
                            st.markdown("### 📈 Analysis Results")
                            
                            if response is not None:
                                if isinstance(response, (pd.DataFrame, pd.Series)):
                                    # Output is a table
                                    st.write("**Data Table:**")
                                    st.dataframe(response, use_container_width=True)
                                elif isinstance(response, (int, float)):
                                    # Output is a single number (e.g., average, sum)
                                    st.markdown(f'''
                                    <div class="success-box">
                                        <h4>📊 Numeric Result:</h4>
                                        <p style="font-size: 2rem; font-weight: bold; text-align: center;">{response:,.2f}</p>
                                    </div>
                                    ''', unsafe_allow_html=True)
                                elif isinstance(response, str) and response.startswith("Error:"):
                                    # Output is an error message
                                    st.markdown(f'<div class="error-box"><h4>❌ Error:</h4><p>{response}</p></div>', unsafe_allow_html=True)
                                else:
                                    # This handles text and matplotlib/seaborn plots generated by PandasAI
                                    st.write("**Analysis Output:**")
                                    st.write(response)
                            else:
                                st.info("The analysis was completed but no specific output was returned.")
                                
                        except Exception as e:
                            st.error(f"An unexpected error occurred during analysis: {str(e)}")
                            st.info("💡 Please try rephrasing your question or check the column names in your data.")
                
            except Exception as e:
                st.error(f"Error initializing AI model: {str(e)}")
                st.info("Please check your OpenAI API key and ensure it is valid.")
    
    else:
        # Welcome screen when no file is uploaded
        st.markdown("""
        <div class="info-box">
        <h3>🚀 Get Started in 3 Simple Steps:</h3>
        <ol>
            <li>**Enter your API Key** (in the sidebar, for the AI engine)</li>
            <li>**Upload your data** (CSV or Excel file)</li>
            <li>**Ask a question** (e.g., "Show sales by region as a bar chart")</li>
        </ol>
        </div>
        """, unsafe_allow_html=True)

if __name__ == "__main__":
    main()

