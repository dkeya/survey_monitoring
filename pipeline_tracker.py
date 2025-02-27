import streamlit as st
import pandas as pd
import plotly.express as px
import os
import tempfile
import shutil
import base64

# Streamlit UI Config
st.set_page_config(page_title="Business Prospects Tracker", page_icon="📊", layout="wide")

# Hide Default Streamlit Elements
hide_streamlit_style = """
    <style>
        #MainMenu {visibility: hidden;}
        footer {visibility: hidden;}
        header {visibility: hidden;}
    </style>
"""
st.markdown(hide_streamlit_style, unsafe_allow_html=True)

# File Handling
file_path = "business_pipeline_tracker.csv"
if os.path.exists(file_path):
    try:
        df = pd.read_csv(file_path, dtype={"Phone": str})
    except PermissionError:
        st.error("🚨 The file 'business_pipeline_tracker.csv' is locked. Close it and restart.")
        st.stop()
else:
    df = pd.DataFrame(columns=[
        "Prospect Name", "Contact Person", "Email", "Phone", "Opportunity Size (KES)",
        "Status", "Stage", "Industry", "Follow-up Date", "Notes", "Priority"
    ])

# Ensure columns exist
df["Priority"] = df.get("Priority", "No")

# Load the logo image as Base64 (Prevents broken image issues)
def get_base64_logo(image_path):
    try:
        with open(image_path, "rb") as image_file:
            return base64.b64encode(image_file.read()).decode()
    except FileNotFoundError:
        return None

logo_path = "logo.png"
logo_base64 = get_base64_logo(logo_path)

# Sidebar: Fixed Logo at the Top, Menu Scrolls Normally
st.sidebar.markdown(f"""
    <style>
        [data-testid="stSidebar"] {{
            background-color: #f8f9fa;
            box-shadow: 2px 0px 8px rgba(0, 0, 0, 0.2);
            overflow-y: auto;
            height: 100vh;
        }}
        .sidebar-logo {{
            position: fixed;
            top: 0;
            left: 0;
            width: 300px;
            background-color: #f8f9fa;
            padding: 15px 0;
            text-align: center;
            z-index: 1000;
            border-bottom: 2px solid #ddd;
        }}
        .sidebar-logo img {{
            width: 80%;
            max-width: 200px;
            margin-bottom: 5px;
        }}
        .sidebar-content {{
            margin-top: 120px; /* Push content below the fixed logo */
            padding: 10px;
        }}
    </style>
    <div class="sidebar-logo">
        {f'<img src="data:image/png;base64,{logo_base64}" class="sidebar-logo">' if logo_base64 else '<p>⚠️ Logo Not Found</p>'}
    </div>
""", unsafe_allow_html=True)

# Sidebar content (scrolls normally)
st.sidebar.markdown('<div class="sidebar-content">', unsafe_allow_html=True)

# Sidebar: Menu Toggle Logic
if "menu_expanded" not in st.session_state:
    st.session_state["menu_expanded"] = True  # Default to expanded

# Menu button toggles state
if st.sidebar.button("☰ Menu", key="menu_toggle", help="Expand/Collapse Sidebar Sections"):
    st.session_state["menu_expanded"] = not st.session_state["menu_expanded"]

# Sidebar Content Wrapper
st.sidebar.markdown('<div class="sidebar-content">', unsafe_allow_html=True)

# ✅ Move this closing tag to after all sidebar elements
st.sidebar.markdown('</div>', unsafe_allow_html=True)

# Title & Marquee (Fixed with Proper Spacing)
st.markdown("""
    <style>
        .title-container {
            position: fixed;
            top: 0;
            left: 0;
            width: 100%;
            background: linear-gradient(to right, #1F3C63, #004aad);
            color: white;
            padding: 15px;
            font-size: 24px;
            font-weight: bold;
            text-align: center;
            z-index: 1000;
            box-shadow: 0px 4px 10px rgba(0, 0, 0, 0.2);
        }
        .marquee-container {
            position: fixed;
            top: 85px; /* Increased spacing to move it below the title */
            left: 0;
            width: 100%;
            background: rgba(0, 74, 173, 0.1);
            border-radius: 5px;
            padding: 10px; /* Increased padding for better visibility */
            z-index: 999;
            text-align: center;
            font-weight: bold;
            font-size: 16px;
            color: #004aad;
            white-space: nowrap;
            overflow: hidden;
            animation: scroll 15s linear infinite;
        }
        @keyframes scroll {
            0% { transform: translateX(100%); }
            100% { transform: translateX(-100%); }
        }
        /* Push main content down to avoid overlap */
        .main-content {
            margin-top: 100px;
        }
    </style>
    <div class="title-container">🎯 Business Prospects Pipeline Tracker</div>
    <div class="marquee-container">Track your business prospects in real-time | Data-driven insights | Sales pipeline optimization! 🔥✨</div>
""", unsafe_allow_html=True)

st.markdown('<div class="main-content"></div>', unsafe_allow_html=True)  # Push content down

# KPI Metrics
# KPI Metrics
col1, col2, col3, col4 = st.columns(4)
col1.metric("📌 Total Prospects", df.shape[0])
col2.metric("✅ Open Deals", df[df["Status"] == "Open"].shape[0])
col3.metric("🔒 Closed Deals", df[df["Status"] == "Closed"].shape[0])
col4.metric("🚀 Priority Prospects", df[df["Priority"] == "Yes"].shape[0])

# Sidebar: Add Business Prospect 
with st.sidebar.expander("➕ Add New Prospect", expanded=st.session_state["menu_expanded"]):
    with st.form("add_prospect_form"):
        prospect_name = st.text_input("Prospect Name")
        contact_person = st.text_input("Contact Person")
        email = st.text_input("Email")
        phone = st.text_input("Phone Number")
        opportunity_size = st.number_input("Opportunity Size (KES)", min_value=0.0, step=100.0)
        status = st.selectbox("Status", ["Open", "Closed"])
        stage = st.selectbox("Pipeline Stage", ["Lead Identified", "Contacted", "Proposal Sent", "Negotiation", "Won", "Lost", "Tender"])
        industry = st.selectbox("Industry", ["Technology", "Finance", "Healthcare", "Education", "Retail", "Manufacturing", "Agriculture", "Real Estate", "Government", "Other"])
        priority = st.selectbox("Priority", ["Yes", "No"])
        followup_date = st.date_input("Follow-up Date")
        notes = st.text_area("Additional Notes")
        submit_button = st.form_submit_button("Add Prospect")

if submit_button:
    new_data = pd.DataFrame([{ 
        "Prospect Name": prospect_name, 
        "Contact Person": contact_person, 
        "Email": email,
        "Phone": f"0{int(phone[-9:])}" if phone.isdigit() and len(phone) >= 9 else phone,
        "Opportunity Size (KES)": opportunity_size, 
        "Status": status, 
        "Stage": stage,
        "Industry": industry, 
        "Priority": priority, 
        "Follow-up Date": followup_date.strftime('%d/%m/%Y'),
        "Notes": notes 
    }])

    df = pd.concat([df, new_data], ignore_index=True)

    # Save the DataFrame safely using a temporary file first
    temp_file = tempfile.NamedTemporaryFile(delete=False, mode='w', encoding='utf-8', newline='')
    df.to_csv(temp_file.name, index=False)
    temp_file.close()

    # Ensure existing file is removed safely before replacing it
    if os.path.exists(file_path):
        os.remove(file_path)

    # Move the temporary file to the final destination
    shutil.move(temp_file.name, file_path)

    st.sidebar.success("✅ Prospect added successfully!")
    st.rerun()

# Sidebar: Modify Existing Prospect  
with st.sidebar.expander("📝 Modify Existing Prospect", expanded=st.session_state["menu_expanded"]):
    selected_prospect = st.selectbox("Select Prospect to Modify", ["None"] + list(df["Prospect Name"].unique()))

    if selected_prospect != "None":
        selected_row = df[df["Prospect Name"] == selected_prospect].iloc[0]

        with st.form("modify_prospect_form"):
            new_contact_person = st.text_input("Contact Person", selected_row["Contact Person"])
            new_email = st.text_input("Email", selected_row["Email"])
            new_phone = st.text_input("Phone", selected_row["Phone"])
            new_opportunity_size = st.number_input("Opportunity Size (KES)", min_value=0.0, step=100.0, value=float(selected_row["Opportunity Size (KES)"]))

            new_status = st.selectbox("Status", ["Open", "Closed"], index=["Open", "Closed"].index(selected_row["Status"]))
            new_stage = st.selectbox("Pipeline Stage", ["Lead Identified", "Contacted", "Proposal Sent", "Negotiation", "Won", "Lost", "Tender"], index=["Lead Identified", "Contacted", "Proposal Sent", "Negotiation", "Won", "Lost", "Tender"].index(selected_row["Stage"]))
            new_industry = st.selectbox("Industry", ["Technology", "Finance", "Healthcare", "Education", "Retail", "Manufacturing", "Agriculture", "Real Estate", "Government", "Other"], index=["Technology", "Finance", "Healthcare", "Education", "Retail", "Manufacturing", "Agriculture", "Real Estate", "Government", "Other"].index(selected_row["Industry"]))
            new_priority = st.selectbox("Priority", ["Yes", "No"], index=["Yes", "No"].index(selected_row["Priority"]))

            # Convert Follow-up Date, setting a default value if NaT
            followup_date_value = pd.to_datetime(selected_row["Follow-up Date"], errors="coerce")
            if pd.isna(followup_date_value):
                followup_date_value = pd.to_datetime("today")  # Default to today's date

            new_followup_date = st.date_input("Follow-up Date", followup_date_value)
            new_notes = st.text_area("Additional Notes", selected_row["Notes"])

            update_button = st.form_submit_button("Update Prospect")

        if update_button:
            df.loc[df["Prospect Name"] == selected_prospect, ["Contact Person", "Email", "Phone", "Opportunity Size (KES)", "Status", "Stage", "Industry", "Priority", "Follow-up Date", "Notes"]] = [
                new_contact_person, new_email, new_phone, round(new_opportunity_size, 2), new_status, new_stage, new_industry, new_priority, new_followup_date.strftime('%d/%m/%Y'), new_notes
            ]

            # Save the DataFrame safely using a temporary file first
            temp_file = tempfile.NamedTemporaryFile(delete=False, mode='w', encoding='utf-8', newline='')
            df.to_csv(temp_file.name, index=False)
            temp_file.close()

            # Ensure existing file is properly closed before replacement
            try:
                if os.path.exists(file_path):
                    os.replace(temp_file.name, file_path)  # Uses os.replace to safely overwrite the file
                else:
                    shutil.move(temp_file.name, file_path)  # Moves the temp file if the original doesn't exist
            except PermissionError:
                st.sidebar.error("🚨 Could not replace the file. Close any applications using it and try again.")

            st.sidebar.success("✅ Prospect updated successfully!")
            st.rerun()

# Filter Section
if st.session_state["menu_expanded"]:
    st.sidebar.subheader("🔍 Filter Prospects")
selected_stage = st.sidebar.selectbox("Filter by Stage", ["All"] + list(df["Stage"].unique()))
selected_status = st.sidebar.selectbox("Filter by Status", ["All", "Open", "Closed"])
selected_industry = st.sidebar.selectbox("Filter by Industry", ["All"] + list(df["Industry"].unique()))
min_opportunity = st.sidebar.slider("Min Opportunity Size (KES)", 0, 10000000, 0)

# Sidebar: Download & Upload CSV
if st.session_state["menu_expanded"]:
    st.sidebar.subheader("📥 Data Management")

# Download CSV Button
st.sidebar.download_button(
    label="📥 Download CSV",
    data=df.to_csv(index=False),
    file_name="filtered_prospects.csv",
    mime="text/csv"
)

# Upload CSV File
uploaded_file = st.sidebar.file_uploader("📤 Upload a CSV file", type=["csv"])

if uploaded_file is not None:
    try:
        df_uploaded = pd.read_csv(uploaded_file)
        
        # Ensure uploaded file has expected columns
        expected_columns = ["Prospect Name", "Contact Person", "Email", "Phone", "Opportunity Size (KES)",
                            "Status", "Stage", "Industry", "Follow-up Date", "Notes", "Priority"]
        if all(col in df_uploaded.columns for col in expected_columns):
            df = df_uploaded

            # Save the DataFrame safely using a temporary file first
            temp_file = tempfile.NamedTemporaryFile(delete=False, mode='w', encoding='utf-8', newline='')
            df.to_csv(temp_file.name, index=False)
            temp_file.close()

            # Ensure existing file is properly closed before replacement
            try:
                if os.path.exists(file_path):
                    os.replace(temp_file.name, file_path)  # Uses os.replace to safely overwrite the file
                else:
                    shutil.move(temp_file.name, file_path)  # Moves the temp file if the original doesn't exist
            except PermissionError:
                st.sidebar.error("🚨 Could not replace the file. Close any applications using it and try again.")

            st.sidebar.success("✅ File uploaded successfully!")
            st.rerun()
        else:
            st.sidebar.error("🚨 Uploaded file is missing required columns.")
    except Exception as e:
        st.sidebar.error(f"🚨 Error processing file: {e}")

filtered_df = df.copy()
if selected_stage != "All":
    filtered_df = filtered_df[filtered_df["Stage"] == selected_stage]
if selected_status != "All":
    filtered_df = filtered_df[filtered_df["Status"] == selected_status]
if selected_industry != "All":
    filtered_df = filtered_df[filtered_df["Industry"] == selected_industry]
filtered_df = filtered_df[filtered_df["Opportunity Size (KES)"] >= min_opportunity]

# Mask Phone Numbers
def mask_phone(phone):
    return phone[:4] + "****" + phone[-2:] if isinstance(phone, str) and len(phone) >= 7 else phone
filtered_df["Phone"] = filtered_df["Phone"].apply(mask_phone)

# Display Prospects
df_display = filtered_df.copy()
st.subheader("📋 Filtered Business Prospects")
st.dataframe(df_display, height=400, use_container_width=True)

# Visualization
if not df.empty:
    st.header("🔄 Conversion Funnel")
    funnel_data = df["Stage"].value_counts().reset_index()
    funnel_data.columns = ["Stage", "Count"]
    fig = px.funnel(funnel_data, x="Count", y="Stage")
    st.plotly_chart(fig, use_container_width=True)

    st.header("📈 Opportunity Size by Industry")
    industry_chart = df.groupby("Industry")["Opportunity Size (KES)"].sum().reset_index()
    fig = px.bar(industry_chart, x="Industry", y="Opportunity Size (KES)", color="Industry")
    st.plotly_chart(fig, use_container_width=True)








