import streamlit as st
import pandas as pd
import io
import matplotlib.pyplot as plt
from pandasai import SmartDataframe
from pandasai.llm import OpenAI
import os
from utils.config import API_KEY

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
</style>
""", unsafe_allow_html=True)

def initialize_llm():
    """Initialize the OpenAI LLM with API key"""
    try:
        llm = OpenAI(api_token=API_KEY)
        return llm
    except Exception as e:
        st.error(f"Error initializing AI model: {str(e)}")
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

def main():
    # Header
    st.markdown('<div class="main-header">📊 DataSense</div>', unsafe_allow_html=True)
    st.markdown("### Your No-Code Data Analysis Assistant")
    st.markdown("Upload your data and ask questions in plain English. Get instant insights and visualizations!")
    
    # Sidebar
    with st.sidebar:
        st.header("⚙️ Configuration")
        
        # API Key input (alternative to config file)
        api_key = st.text_input("OpenAI API Key", type="password", 
                               value=API_KEY if API_KEY else "",
                               help="Get your API key from https://platform.openai.com/api-keys")
        
        if not api_key:
            st.warning("⚠️ Please enter your OpenAI API key to continue")
            st.info("You can also set it in utils/config.py as API_KEY")
            return
        
        st.header("📁 Data Upload")
        uploaded_file = st.file_uploader(
            "Choose a CSV or Excel file",
            type=['csv', 'xlsx', 'xls'],
            help="Upload your structured data file"
        )
        
        st.header("💡 Example Questions")
        st.markdown("""
        - "Show me sales trends by month"
        - "Create a bar chart of top 10 products"
        - "What is the average salary by department?"
        - "Plot the correlation between age and salary"
        - "Show total revenue by category"
        - "What are the top 5 performing regions?"
        """)
    
    # Main content area
    if uploaded_file is not None:
        # Load and display data
        df = load_data(uploaded_file)
        if df is not None:
            display_data_overview(df)
            
            # Initialize LLM and SmartDataframe
            llm = OpenAI(api_token=api_key)
            smart_df = SmartDataframe(df, config={"llm": llm})
            
            st.markdown("---")
            st.markdown('<div class="sub-header">💬 Ask Questions About Your Data</div>', unsafe_allow_html=True)
            
            # Chat interface
            user_question = st.text_area(
                "Enter your question in plain English:",
                placeholder="e.g., 'Show me the total sales by month as a line chart'",
                height=100
            )
            
            if st.button("Analyze Data", type="primary"):
                if user_question:
                    with st.spinner("Analyzing your data... This may take a few seconds."):
                        try:
                            # Get response from PandasAI
                            response = smart_df.chat(user_question)
                            
                            # Display response
                            st.markdown("### 📈 Analysis Results")
                            
                            if response is not None:
                                # Check the type of response and display appropriately
                                if isinstance(response, (pd.DataFrame, pd.Series)):
                                    st.write("**Data Table:**")
                                    st.dataframe(response, use_container_width=True)
                                elif hasattr(response, 'figure') and response.figure is not None:
                                    # It's a plot
                                    st.pyplot(response.figure)
                                elif isinstance(response, (int, float, str)):
                                    st.markdown(f'<div class="success-box"><h4>Answer:</h4><p style="font-size: 1.2rem;">{response}</p></div>', 
                                                unsafe_allow_html=True)
                                else:
                                    st.write(response)
                            else:
                                st.info("The analysis was completed but no specific output was returned.")
                                
                        except Exception as e:
                            st.error(f"Error during analysis: {str(e)}")
                            st.info("Try rephrasing your question or check if your data has the required columns.")
                else:
                    st.warning("Please enter a question to analyze your data.")
            
            # Quick analysis suggestions
            st.markdown("---")
            st.markdown("### 🚀 Quick Analysis Suggestions")
            
            col1, col2, col3 = st.columns(3)
            
            quick_questions = [
                "Show basic statistics for numerical columns",
                "Create a correlation heatmap",
                "Show the distribution of categorical columns",
                "Display missing values summary"
            ]
            
            for i, question in enumerate(quick_questions):
                col = [col1, col2, col3][i % 3]
                if col.button(question, key=f"quick_{i}"):
                    with st.spinner("Generating analysis..."):
                        try:
                            response = smart_df.chat(question)
                            st.markdown(f"### Results for: '{question}'")
                            if response is not None:
                                if isinstance(response, (pd.DataFrame, pd.Series)):
                                    st.dataframe(response, use_container_width=True)
                                elif hasattr(response, 'figure') and response.figure is not None:
                                    st.pyplot(response.figure)
                                else:
                                    st.write(response)
                        except Exception as e:
                            st.error(f"Error: {str(e)}")
    
    else:
        # Welcome screen when no file is uploaded
        st.markdown("""
        <div class="info-box">
        <h3>🚀 Get Started in 3 Simple Steps:</h3>
        <ol>
            <li><b>Upload your data</b> - CSV or Excel file (use the sidebar)</li>
            <li><b>Ask questions</b> - Use plain English like "show me sales trends"</li>
            <li><b>Get insights</b> - Receive instant analysis and visualizations</li>
        </ol>
        </div>
        """, unsafe_allow_html=True)
        
        # Features section
        col1, col2, col3 = st.columns(3)
        
        with col1:
            st.markdown("### 📈 Visualizations")
            st.write("""
            - Bar charts
            - Line graphs  
            - Pie charts
            - Scatter plots
            - Histograms
            """)
            
        with col2:
            st.markdown("### 🔍 Analysis")
            st.write("""
            - Summary statistics
            - Trend analysis
            - Correlation studies
            - Group comparisons
            - Pattern detection
            """)
            
        with col3:
            st.markdown("### 💬 Natural Language")
            st.write("""
            - No coding required
            - Plain English queries
            - Intelligent responses
            - Context understanding
            """)

if __name__ == "__main__":
    main()
