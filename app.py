import streamlit as st
import pandas as pd
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
    .error-box {
        background-color: #f8d7da;
        padding: 15px;
        border-radius: 10px;
        margin: 10px 0;
    }
</style>
""", unsafe_allow_html=True)

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
        response = smart_df.chat(question)
        return response
    except Exception as e:
        return f"Error: {str(e)}"

def main():
    # Header
    st.markdown('<div class="main-header">📊 DataSense</div>', unsafe_allow_html=True)
    st.markdown("### Your No-Code Data Analysis Assistant")
    st.markdown("Upload your data and ask questions in plain English. Get instant insights and visualizations!")
    
    # Sidebar
    with st.sidebar:
        st.header("⚙️ Configuration")
        
        # API Key input
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
        - **Summary Questions:**
          - "Show basic statistics"
          - "What are the data types?"
          - "Show missing values"
        
        - **Analysis Questions:**
          - "What is the average of [column]?"
          - "Show top 10 [category]"
          - "Group by [column] and calculate average"
        
        - **Data Questions:**
          - "Filter where [column] > [value]"
          - "Sort by [column] descending"
          - "Show unique values in [column]"
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
                smart_df = SmartDataframe(df, config={"llm": llm, "enable_cache": False})
                
                st.markdown("---")
                st.markdown('<div class="sub-header">💬 Ask Questions About Your Data</div>', unsafe_allow_html=True)
                
                # Chat interface
                user_question = st.text_area(
                    "Enter your question in plain English:",
                    placeholder="e.g., 'What is the average age?', 'Show top 5 products by sales', 'Filter records where salary > 50000'",
                    height=100
                )
                
                col1, col2 = st.columns([1, 4])
                with col1:
                    analyze_btn = st.button("Analyze Data", type="primary", use_container_width=True)
                with col2:
                    clear_btn = st.button("Clear Results", use_container_width=True)
                
                if analyze_btn and user_question:
                    with st.spinner("🤔 Analyzing your data... This may take a few seconds."):
                        try:
                            # Get response from PandasAI
                            response = safe_chat(smart_df, user_question)
                            
                            # Display response
                            st.markdown("### 📈 Analysis Results")
                            
                            if response is not None:
                                if isinstance(response, (pd.DataFrame, pd.Series)):
                                    st.write("**Data Table:**")
                                    st.dataframe(response, use_container_width=True)
                                    
                                    # Auto-create basic charts for DataFrames
                                    if isinstance(response, pd.DataFrame) and len(response.columns) >= 2:
                                        try:
                                            # Try to create a simple chart if we have numeric data
                                            numeric_cols = response.select_dtypes(include=['number']).columns
                                            if len(numeric_cols) >= 1:
                                                st.write("**Quick Chart:**")
                                                if len(numeric_cols) == 1:
                                                    st.bar_chart(response[numeric_cols[0]])
                                                else:
                                                    st.line_chart(response[numeric_cols].set_index(response.index))
                                        except:
                                            pass  # Skip chart if it fails
                                    
                                elif isinstance(response, (int, float)):
                                    st.markdown(f'''
                                    <div class="success-box">
                                        <h4>📊 Result:</h4>
                                        <p style="font-size: 2rem; font-weight: bold; text-align: center;">{response:,.2f}</p>
                                    </div>
                                    ''', unsafe_allow_html=True)
                                elif isinstance(response, str):
                                    if response.startswith("Error:"):
                                        st.markdown(f'<div class="error-box"><h4>❌ Error:</h4><p>{response}</p></div>', unsafe_allow_html=True)
                                    else:
                                        st.markdown(f'<div class="success-box"><h4>💡 Answer:</h4><p style="font-size: 1.2rem;">{response}</p></div>', unsafe_allow_html=True)
                                else:
                                    st.write("**Analysis Output:**")
                                    st.write(response)
                            else:
                                st.info("The analysis was completed but no specific output was returned.")
                                
                        except Exception as e:
                            st.error(f"Error during analysis: {str(e)}")
                            st.info("💡 Try rephrasing your question or check if your data has the required columns.")
                
                # Quick analysis buttons
                st.markdown("---")
                st.markdown("### 🚀 Quick Analysis")
                
                quick_col1, quick_col2, quick_col3 = st.columns(3)
                
                quick_actions = [
                    ("📊 Basic Stats", "Show basic statistics for numerical columns"),
                    ("🔍 Data Info", "Show data types and missing values"),
                    ("📈 Top Values", "Show top 10 most frequent values for each categorical column")
                ]
                
                for i, (icon, question) in enumerate(quick_actions):
                    col = [quick_col1, quick_col2, quick_col3][i]
                    if col.button(icon, key=f"quick_{i}", use_container_width=True):
                        with st.spinner("Generating analysis..."):
                            try:
                                response = safe_chat(smart_df, question)
                                st.markdown(f"### {icon} Results for: '{question}'")
                                if response is not None:
                                    if isinstance(response, (pd.DataFrame, pd.Series)):
                                        st.dataframe(response, use_container_width=True)
                                    else:
                                        st.write(response)
                            except Exception as e:
                                st.error(f"Error: {str(e)}")
            
            except Exception as e:
                st.error(f"Error initializing AI model: {str(e)}")
                st.info("Please check your OpenAI API key and try again.")
    
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
            st.markdown("### 📈 Analysis Types")
            st.write("""
            - Summary statistics
            - Data filtering
            - Group comparisons
            - Trend analysis
            - Pattern detection
            """)
            
        with col2:
            st.markdown("### 🔍 Data Operations")
            st.write("""
            - Data type analysis
            - Missing values detection
            - Unique value counts
            - Correlation studies
            - Data validation
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
