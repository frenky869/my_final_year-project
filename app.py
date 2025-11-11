import streamlit as st
import pandas as pd
import os

# Page configuration
st.set_page_config(
    page_title="DataSense - No-Code Data Analysis",
    page_icon="📊",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS for better styling
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

def analyze_with_pandasai(df, question, api_key):
    """Analyze data using PandasAI"""
    try:
        # Import inside function to handle potential errors
        from pandasai import SmartDataframe
        from pandasai.llm import OpenAI
        
        llm = OpenAI(api_token=api_key)
        smart_df = SmartDataframe(df, config={"llm": llm, "enable_cache": False})
        response = smart_df.chat(question)
        return response
    except Exception as e:
        return f"Error: {str(e)}"

def main():
    api_key = get_openai_api_key()

    # Header
    st.markdown('<div class="main-header">📊 DataSense</div>', unsafe_allow_html=True)
    st.markdown("### Your No-Code Data Analysis Assistant")
    
    # Check for API Key early
    if not api_key:
        st.warning("⚠️ Please enter your OpenAI API key in the sidebar to activate the analysis engine.")
        st.info("The application requires an API key to communicate with the AI model.")
        # Don't return here, let users still see the app structure

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
        - **"Show basic statistics for numerical columns"**
        """)

    # Main content area
    if uploaded_file is not None:
        # Load and display data
        df = load_data(uploaded_file)
        if df is not None:
            display_data_overview(df)
            
            if api_key:  # Only show analysis if API key is provided
                st.markdown("---")
                st.markdown('<div class="sub-header">💬 Ask Questions About Your Data</div>', unsafe_allow_html=True)
                
                # Chat interface
                user_question = st.text_area(
                    "Enter your question in plain English:",
                    placeholder="e.g., 'What is the average age?', 'Show top 5 products by sales', 'Plot a histogram of the customer ages'",
                    height=100
                )
                
                if st.button("Analyze Data", type="primary"):
                    if user_question:
                        with st.spinner("🤔 Analyzing your data... This may take a few seconds."):
                            try:
                                # Get response from PandasAI
                                response = analyze_with_pandasai(df, user_question, api_key)
                                
                                # Display response
                                st.markdown("### 📈 Analysis Results")
                                
                                if response is not None:
                                    if isinstance(response, (pd.DataFrame, pd.Series)):
                                        st.write("**Data Table:**")
                                        st.dataframe(response, use_container_width=True)
                                    elif isinstance(response, (int, float)):
                                        st.markdown(f'''
                                        <div class="success-box">
                                            <h4>📊 Numeric Result:</h4>
                                            <p style="font-size: 2rem; font-weight: bold; text-align: center;">{response:,.2f}</p>
                                        </div>
                                        ''', unsafe_allow_html=True)
                                    elif isinstance(response, str) and response.startswith("Error:"):
                                        st.markdown(f'<div class="error-box"><h4>❌ Error:</h4><p>{response}</p></div>', unsafe_allow_html=True)
                                    else:
                                        st.write("**Analysis Output:**")
                                        st.write(response)
                                else:
                                    st.info("The analysis was completed but no specific output was returned.")
                                    
                            except Exception as e:
                                st.error(f"An unexpected error occurred during analysis: {str(e)}")
                                st.info("💡 Please try rephrasing your question or check the column names in your data.")
                    else:
                        st.warning("Please enter a question to analyze.")
            else:
                st.warning("🔑 Please enter your OpenAI API key in the sidebar to enable data analysis.")
    
    else:
        # Welcome screen when no file is uploaded
        st.markdown("""
        <div class="info-box">
        <h3>🚀 Get Started in 3 Simple Steps:</h3>
        <ol>
            <li><b>Enter your API Key</b> (in the sidebar, for the AI engine)</li>
            <li><b>Upload your data</b> (CSV or Excel file)</li>
            <li><b>Ask a question</b> (e.g., "Show sales by region as a bar chart")</li>
        </ol>
        </div>
        """, unsafe_allow_html=True)
        
        # Show sample data preview
        st.markdown("### 📊 Sample Data Preview")
        col1, col2 = st.columns(2)
        
        with col1:
            st.write("**Sample Sales Data:**")
            sample_sales = pd.DataFrame({
                'Date': ['2024-01-01', '2024-01-01', '2024-01-02'],
                'Product': ['Product A', 'Product B', 'Product A'],
                'Sales': [15000, 8000, 16000],
                'Region': ['North', 'South', 'North']
            })
            st.dataframe(sample_sales)
            
        with col2:
            st.write("**Sample Employee Data:**")
            sample_employees = pd.DataFrame({
                'Name': ['John Smith', 'Sarah Johnson', 'Mike Brown'],
                'Department': ['Engineering', 'Marketing', 'Engineering'],
                'Salary': [85000, 65000, 95000],
                'Age': [32, 28, 35]
            })
            st.dataframe(sample_employees)

if __name__ == "__main__":
    main()
