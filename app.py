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

# Try to import Plotly with fallback
try:
    import plotly.express as px
    import plotly.graph_objects as go
    PLOTLY_AVAILABLE = True
except ImportError:
    PLOTLY_AVAILABLE = False

# Custom CSS for modern dark theme styling
st.markdown("""
<style>
    /* Main background styling */
    .main {
        background: linear-gradient(135deg, #0f0f23 0%, #1a1a2e 50%, #16213e 100%);
        color: #ffffff;
    }
    
    /* Sidebar background */
    .css-1d391kg, .css-1lcbmhc {
        background: linear-gradient(180deg, #1e1e2e 0%, #2d2d44 100%);
    }
    
    /* Main styling */
    .main-header {
        font-size: 4rem;
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        text-align: center;
        margin-bottom: 1rem;
        font-weight: 800;
    }
    
    .sub-header {
        font-size: 1.8rem;
        color: #a8d8ea;
        margin-bottom: 2rem;
        text-align: center;
        font-weight: 600;
    }
    
    /* Card styling */
    .feature-card {
        background: rgba(255, 255, 255, 0.1);
        backdrop-filter: blur(10px);
        padding: 25px;
        border-radius: 15px;
        border: 1px solid rgba(255, 255, 255, 0.2);
        margin: 15px 0;
        transition: transform 0.3s ease;
        color: #ffffff;
    }
    
    .feature-card:hover {
        transform: translateY(-5px);
        background: rgba(255, 255, 255, 0.15);
    }
    
    .info-card {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        color: white;
        padding: 25px;
        border-radius: 15px;
        margin: 15px 0;
        border: 1px solid rgba(255, 255, 255, 0.3);
    }
    
    .success-card {
        background: linear-gradient(135deg, #4facfe 0%, #00f2fe 100%);
        color: white;
        padding: 20px;
        border-radius: 15px;
        margin: 10px 0;
        border: 1px solid rgba(255, 255, 255, 0.3);
    }
    
    .metric-card {
        background: rgba(255, 255, 255, 0.1);
        backdrop-filter: blur(10px);
        padding: 20px;
        border-radius: 12px;
        border: 1px solid rgba(255, 255, 255, 0.2);
        text-align: center;
        color: #ffffff;
    }
    
    /* Button styling */
    .stButton button {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        color: white;
        border: none;
        padding: 12px 30px;
        border-radius: 8px;
        font-weight: 600;
        transition: all 0.3s ease;
    }
    
    .stButton button:hover {
        transform: translateY(-2px);
        box-shadow: 0 6px 20px rgba(102, 126, 234, 0.4);
        background: linear-gradient(135deg, #764ba2 0%, #667eea 100%);
    }
    
    /* Text input styling */
    .stTextInput input, .stTextArea textarea {
        background: rgba(255, 255, 255, 0.1);
        border: 1px solid rgba(255, 255, 255, 0.3);
        color: #ffffff;
        border-radius: 10px;
    }
    
    .stTextInput input:focus, .stTextArea textarea:focus {
        border-color: #667eea;
        box-shadow: 0 0 0 2px rgba(102, 126, 234, 0.2);
    }
    
    /* File uploader styling */
    .stFileUploader {
        background: rgba(255, 255, 255, 0.1) !important;
        border: 2px dashed rgba(102, 126, 234, 0.5) !important;
        border-radius: 10px;
        padding: 20px;
        color: #ffffff;
    }
    
    /* Selectbox styling */
    .stSelectbox div div {
        background: rgba(255, 255, 255, 0.1);
        color: #ffffff;
    }
    
    /* Dataframe styling */
    .dataframe {
        background: rgba(255, 255, 255, 0.1) !important;
        color: #ffffff !important;
    }
    
    /* Tab styling */
    .stTabs [data-baseweb="tab-list"] {
        background: rgba(255, 255, 255, 0.1);
        border-radius: 10px;
        padding: 10px;
    }
    
    .stTabs [data-baseweb="tab"] {
        background: transparent;
        color: #ffffff;
    }
    
    .stTabs [aria-selected="true"] {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%) !important;
        color: white !important;
    }
    
    /* Warning and info boxes */
    .stAlert {
        background: rgba(255, 255, 255, 0.1);
        border: 1px solid rgba(255, 255, 255, 0.2);
        color: #ffffff;
    }
    
    /* Sidebar text color */
    .css-1d391kg, .css-1lcbmhc {
        color: #ffffff !important;
    }
    
    /* Make all text in sidebar readable */
    .css-1d391kg p, .css-1lcbmhc p, .css-1d391kg label, .css-1lcbmhc label {
        color: #ffffff !important;
    }
    
    /* Make file uploader text readable */
    .stFileUploader label {
        color: #ffffff !important;
    }
    
    /* Make metric values stand out */
    .metric-card h2 {
        color: #667eea !important;
        text-shadow: 0 2px 4px rgba(0,0,0,0.3);
    }
    
    /* Make headers stand out */
    h1, h2, h3, h4, h5, h6 {
        color: #a8d8ea !important;
    }
    
    /* Make regular text readable */
    p, div, span {
        color: #e6e6e6 !important;
    }
</style>
""", unsafe_allow_html=True)

def get_openai_api_key():
    """Retrieves API key from Streamlit secrets or sidebar input."""
    if "OPENAI_API_KEY" in st.secrets:
        return st.secrets["OPENAI_API_KEY"]
    
    with st.sidebar:
        st.markdown("### 🔑 API Configuration")
        api_key = st.text_input(
            "OpenAI API Key", 
            type="password",
            placeholder="sk-...",
            help="Get your API key from https://platform.openai.com/api-keys"
        )
        if api_key:
            st.success("✅ API Key configured!")
        return api_key

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
    """Display enhanced information about the dataset"""
    st.markdown("### 📋 Data Overview")
    
    # Metrics in columns
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.markdown(f'''
        <div class="metric-card">
            <h3>📊</h3>
            <h2 style="margin: 10px 0;">{df.shape[0]:,}</h2>
            <p>Total Rows</p>
        </div>
        ''', unsafe_allow_html=True)
    
    with col2:
        st.markdown(f'''
        <div class="metric-card">
            <h3>🔢</h3>
            <h2 style="margin: 10px 0;">{df.shape[1]}</h2>
            <p>Total Columns</p>
        </div>
        ''', unsafe_allow_html=True)
    
    with col3:
        memory_usage = df.memory_usage(deep=True).sum() / 1024**2
        st.markdown(f'''
        <div class="metric-card">
            <h3>💾</h3>
            <h2 style="margin: 10px 0;">{memory_usage:.2f}</h2>
            <p>Memory (MB)</p>
        </div>
        ''', unsafe_allow_html=True)
    
    with col4:
        null_count = df.isnull().sum().sum()
        st.markdown(f'''
        <div class="metric-card">
            <h3>⚠️</h3>
            <h2 style="margin: 10px 0;">{null_count}</h2>
            <p>Missing Values</p>
        </div>
        ''', unsafe_allow_html=True)
    
    # Data preview with tabs
    tab1, tab2, tab3 = st.tabs(["📊 Data Preview", "🔍 Column Info", "📈 Quick Stats"])
    
    with tab1:
        st.write("**First 10 rows of your data:**")
        st.dataframe(df.head(10), use_container_width=True, height=400)
    
    with tab2:
        st.write("**Column Information:**")
        col_info = pd.DataFrame({
            'Column': df.columns,
            'Data Type': df.dtypes,
            'Non-Null': df.count(),
            'Null': df.isnull().sum(),
            'Unique': [df[col].nunique() for col in df.columns]
        })
        st.dataframe(col_info, use_container_width=True)
    
    with tab3:
        st.write("**Basic Statistics:**")
        if df.select_dtypes(include=['number']).shape[1] > 0:
            st.dataframe(df.describe(), use_container_width=True)
        else:
            st.info("No numerical columns found for statistical summary.")

def create_quick_visualizations(df):
    """Create automatic visualizations for the data"""
    st.markdown("### 🎯 Quick Visualizations")
    
    if not PLOTLY_AVAILABLE:
        st.warning("""
        **Plotly not available** - Install plotly for enhanced visualizations:
        ```bash
        pip install plotly
        ```
        For now, using basic Streamlit charts...
        """)
        create_basic_visualizations(df)
        return
    
    numeric_cols = df.select_dtypes(include=['number']).columns
    categorical_cols = df.select_dtypes(include=['object', 'category']).columns
    
    if len(numeric_cols) > 0:
        col1, col2 = st.columns(2)
        
        with col1:
            if len(numeric_cols) >= 1:
                try:
                    fig = px.histogram(df, x=numeric_cols[0], 
                                     title=f"Distribution of {numeric_cols[0]}",
                                     color_discrete_sequence=['#667eea'])
                    fig.update_layout(
                        plot_bgcolor='rgba(0,0,0,0)',
                        paper_bgcolor='rgba(0,0,0,0)',
                        font_color='white'
                    )
                    st.plotly_chart(fig, use_container_width=True)
                except Exception as e:
                    st.error(f"Could not create histogram: {str(e)}")
        
        with col2:
            if len(numeric_cols) >= 2:
                try:
                    fig = px.scatter(df, x=numeric_cols[0], y=numeric_cols[1],
                                   title=f"{numeric_cols[0]} vs {numeric_cols[1]}",
                                   color_discrete_sequence=['#764ba2'])
                    fig.update_layout(
                        plot_bgcolor='rgba(0,0,0,0)',
                        paper_bgcolor='rgba(0,0,0,0)',
                        font_color='white'
                    )
                    st.plotly_chart(fig, use_container_width=True)
                except Exception as e:
                    st.error(f"Could not create scatter plot: {str(e)}")
    
    if len(categorical_cols) > 0 and len(numeric_cols) > 0:
        try:
            fig = px.box(df, x=categorical_cols[0], y=numeric_cols[0],
                       title=f"{numeric_cols[0]} by {categorical_cols[0]}",
                       color_discrete_sequence=['#f093fb'])
            fig.update_layout(
                plot_bgcolor='rgba(0,0,0,0)',
                paper_bgcolor='rgba(0,0,0,0)',
                font_color='white'
            )
            st.plotly_chart(fig, use_container_width=True)
        except Exception as e:
            st.error(f"Could not create box plot: {str(e)}")

def create_basic_visualizations(df):
    """Fallback visualizations using Streamlit's built-in charts"""
    numeric_cols = df.select_dtypes(include=['number']).columns
    categorical_cols = df.select_dtypes(include=['object', 'category']).columns
    
    if len(numeric_cols) > 0:
        col1, col2 = st.columns(2)
        
        with col1:
            if len(numeric_cols) >= 1:
                st.write(f"**Histogram of {numeric_cols[0]}**")
                st.bar_chart(df[numeric_cols[0]].value_counts())
        
        with col2:
            if len(numeric_cols) >= 2:
                st.write(f"**Line chart: {numeric_cols[0]} vs {numeric_cols[1]}**")
                st.line_chart(df[[numeric_cols[0], numeric_cols[1]]].head(50))
    
    if len(categorical_cols) > 0 and len(numeric_cols) > 0:
        st.write(f"**{numeric_cols[0]} by {categorical_cols[0]}**")
        summary = df.groupby(categorical_cols[0])[numeric_cols[0]].mean()
        st.bar_chart(summary)

def analyze_with_pandasai(df, question, api_key):
    """Analyze data using PandasAI"""
    try:
        from pandasai import SmartDataframe
        from pandasai.llm import OpenAI
        
        llm = OpenAI(api_token=api_key)
        smart_df = SmartDataframe(df, config={"llm": llm, "enable_cache": False})
        response = smart_df.chat(question)
        return response
    except ImportError:
        return "Error: pandasai is not installed. Please install it using: pip install pandasai"
    except Exception as e:
        return f"Error: {str(e)}"

def main():
    api_key = get_openai_api_key()

    # Header with gradient
    st.markdown('<div class="main-header">📊 DataSense</div>', unsafe_allow_html=True)
    st.markdown('<div class="sub-header">Your No-Code Data Analysis Assistant</div>', unsafe_allow_html=True)
    
    # Check for API Key
    if not api_key:
        st.markdown('''
        <div class="info-card">
            <h3>🔑 API Key Required</h3>
            <p>Please enter your OpenAI API key in the sidebar to activate the AI analysis engine.</p>
            <p><small>Your API key is used solely for data analysis and is not stored.</small></p>
        </div>
        ''', unsafe_allow_html=True)

    # Enhanced Sidebar
    with st.sidebar:
        st.markdown("### 🚀 Get Started")
        
        st.markdown("### 📁 Data Upload")
        uploaded_file = st.file_uploader(
            "Drag and drop your data file here",
            type=['csv', 'xlsx', 'xls'],
            help="Supported formats: CSV, Excel (.xlsx, .xls)"
        )
        
        st.markdown("### 💡 Example Questions")
        st.markdown("""
        <div style="background: rgba(255,255,255,0.1); padding: 15px; border-radius: 10px; border-left: 4px solid #667eea;">
        <b style="color: #a8d8ea;">📈 For Sales Data:</b><br>
        <span style="color: #e6e6e6;">• "Show monthly sales trends"</span><br>
        <span style="color: #e6e6e6;">• "Top 5 products by revenue"</span><br>
        <span style="color: #e6e6e6;">• "Sales by region pie chart"</span><br><br>
        
        <b style="color: #a8d8ea;">👥 For HR Data:</b><br>
        <span style="color: #e6e6e6;">• "Average salary by department"</span><br>
        <span style="color: #e6e6e6;">• "Employee age distribution"</span><br>
        <span style="color: #e6e6e6;">• "Department headcount bar chart"</span><br><br>
        
        <b style="color: #a8d8ea;">🔧 General Analysis:</b><br>
        <span style="color: #e6e6e6;">• "Show basic statistics"</span><br>
        <span style="color: #e6e6e6;">• "Find missing values"</span><br>
        <span style="color: #e6e6e6;">• "Correlation heatmap"</span>
        </div>
        """, unsafe_allow_html=True)
        
        st.markdown("---")
        st.markdown("### 🛠️ Features")
        features = [
            ("📊", "Smart Data Profiling", "Automatic data quality assessment"),
            ("🤖", "AI-Powered Analysis", "Natural language queries"),
            ("📈", "Auto Visualizations", "Instant charts and graphs"),
            ("⚡", "Real-time Processing", "Fast analysis results")
        ]
        
        for emoji, title, desc in features:
            st.markdown(f"""
            <div style="margin: 10px 0; padding: 10px; background: rgba(255,255,255,0.1); border-radius: 8px;">
                <strong style="color: #a8d8ea;">{emoji} {title}</strong><br>
                <small style="color: #e6e6e6;">{desc}</small>
            </div>
            """, unsafe_allow_html=True)

    # Main content area
    if uploaded_file is not None:
        # Load and display data
        df = load_data(uploaded_file)
        if df is not None:
            display_data_overview(df)
            
            # Quick visualizations
            create_quick_visualizations(df)
            
            if api_key:
                st.markdown("---")
                st.markdown("### 💬 Ask Anything About Your Data")
                
                # Enhanced chat interface
                col1, col2 = st.columns([3, 1])
                with col1:
                    user_question = st.text_area(
                        "Enter your question:",
                        placeholder="e.g., 'What is the correlation between age and salary?', 'Show me a bar chart of sales by product', 'What are the top 5 performing regions?'",
                        height=120,
                        label_visibility="collapsed"
                    )
                
                with col2:
                    st.write("")  # Spacer
                    st.write("")  # Spacer
                    analyze_btn = st.button("🚀 Analyze", use_container_width=True)
                
                if analyze_btn and user_question:
                    with st.spinner("🔍 Analyzing your data with AI... This may take a few moments."):
                        try:
                            response = analyze_with_pandasai(df, user_question, api_key)
                            
                            st.markdown("### 📊 Analysis Results")
                            
                            if response is not None:
                                if isinstance(response, (pd.DataFrame, pd.Series)):
                                    st.markdown("**📋 Data Table:**")
                                    st.dataframe(response, use_container_width=True, height=400)
                                elif isinstance(response, (int, float)):
                                    st.markdown(f'''
                                    <div class="success-card">
                                        <h3>🎯 Result:</h3>
                                        <h1 style="text-align: center; margin: 20px 0; font-size: 3rem;">{response:,.2f}</h1>
                                    </div>
                                    ''', unsafe_allow_html=True)
                                elif isinstance(response, str) and response.startswith("Error:"):
                                    st.error(f"**Analysis Error:** {response}")
                                else:
                                    st.markdown("**📝 Analysis Output:**")
                                    st.info(response)
                            else:
                                st.info("The analysis was completed but no specific output was returned.")
                                
                        except Exception as e:
                            st.error(f"An unexpected error occurred: {str(e)}")
                elif analyze_btn and not user_question:
                    st.warning("Please enter a question to analyze.")
            else:
                st.warning("🔑 Please enter your OpenAI API key in the sidebar to enable AI-powered analysis.")
    
    else:
        # Enhanced welcome screen
        st.markdown("""
        <div class="info-card">
            <h2>🎯 Transform Your Data into Insights - No Code Required</h2>
            <p>DataSense makes advanced data analysis accessible to everyone. Upload your data and start asking questions in plain English!</p>
        </div>
        """, unsafe_allow_html=True)
        
        # Features grid
        st.markdown("### ✨ Why Choose DataSense?")
        col1, col2, col3 = st.columns(3)
        
        with col1:
            st.markdown("""
            <div class="feature-card">
                <h3>🚀 Instant Setup</h3>
                <p>Upload your CSV or Excel file and start analyzing immediately. No installation or setup required.</p>
            </div>
            """, unsafe_allow_html=True)
            
        with col2:
            st.markdown("""
            <div class="feature-card">
                <h3>🤖 AI-Powered</h3>
                <p>Ask questions in natural language and get intelligent insights, charts, and summaries.</p>
            </div>
            """, unsafe_allow_html=True)
            
        with col3:
            st.markdown("""
            <div class="feature-card">
                <h3>📊 Smart Visualizations</h3>
                <p>Automatic charts and graphs that help you understand your data at a glance.</p>
            </div>
            """, unsafe_allow_html=True)
        
        # Sample data preview
        st.markdown("### 📋 Sample Data Formats")
        col1, col2 = st.columns(2)
        
        with col1:
            st.markdown("#### 💼 Sales Data Example")
            sample_sales = pd.DataFrame({
                'Date': ['2024-01-01', '2024-01-01', '2024-01-02', '2024-01-02', '2024-01-03'],
                'Product': ['Laptop', 'Mouse', 'Laptop', 'Keyboard', 'Monitor'],
                'Sales': [15000, 8000, 16000, 4500, 22000],
                'Region': ['North', 'South', 'North', 'East', 'West'],
                'Units': [15, 80, 16, 45, 22]
            })
            st.dataframe(sample_sales, use_container_width=True)
            
        with col2:
            st.markdown("#### 👥 Employee Data Example")
            sample_employees = pd.DataFrame({
                'Name': ['John Smith', 'Sarah Johnson', 'Mike Brown', 'Emily Davis', 'David Wilson'],
                'Department': ['Engineering', 'Marketing', 'Engineering', 'Sales', 'HR'],
                'Salary': [85000, 65000, 95000, 75000, 60000],
                'Age': [32, 28, 35, 29, 41],
                'Experience': [5, 3, 8, 4, 12]
            })
            st.dataframe(sample_employees, use_container_width=True)

if __name__ == "__main__":
    main()
