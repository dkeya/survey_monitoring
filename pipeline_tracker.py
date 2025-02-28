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
st.markdown("""
    <style>
        /* Sidebar default styles */
        [data-testid="stSidebar"] {
            background-color: #f8f9fa;
            box-shadow: 2px 0px 8px rgba(0, 0, 0, 0.2);
            overflow-y: auto;
            height: 100vh;
            width: 300px;
            transition: all 0.3s ease-in-out;
            position: fixed;
            left: 0;
            z-index: 1000;
        }

        /* Collapsed Sidebar for Mobile */
        .collapsed-sidebar {
            width: 0;
            overflow: hidden;
            padding: 0;
        }

        /* Sidebar Logo */
        .sidebar-logo {
            position: fixed;
            top: 0;
            left: 0;
            width: 300px;
            background-color: #f8f9fa;
            padding: 15px 0;
            text-align: center;
            z-index: 1001;
            border-bottom: 2px solid #ddd;
            transition: all 0.3s ease-in-out;
        }

        /* Menu button always visible on mobile */
        .menu-button {
            position: fixed;
            top: 10px;
            left: 10px;
            background-color: #ff4b4b;
            color: white;
            padding: 10px 15px;
            border-radius: 5px;
            border: none;
            font-size: 18px;
            cursor: pointer;
            z-index: 1100;
            display: block;
        }

        /* Hide menu button when sidebar is open */
        .expanded .menu-button {
            display: none;
        }

        /* Push content when sidebar is open */
        .main-content {
            margin-left: 300px;
            transition: margin-left 0.3s ease-in-out;
        }

        /* Shrink content when sidebar is collapsed */
        .collapsed .main-content {
            margin-left: 0;
        }
    </style>
""", unsafe_allow_html=True)

# Sidebar content (scrolls normally)
st.sidebar.markdown('<div class="sidebar-content">', unsafe_allow_html=True)

# Sidebar: Menu Toggle Logic (Ensures correct positioning & visibility)
if "sidebar_collapsed" not in st.session_state:
    st.session_state["sidebar_collapsed"] = False  # Default: Sidebar expanded on desktop

menu_button_html = """
    <style>
        /* Ensure button is inside the sidebar on desktop */
        .menu-button {
            position: fixed;
            top: 10px;
            left: 15px;
            background-color: #004aad;
            color: white;
            padding: 10px 15px;
            border-radius: 5px;
            font-size: 18px;
            cursor: pointer;
            z-index: 1200;
            transition: all 0.3s ease-in-out;
        }

        /* Move button to the main screen on mobile */
        @media (max-width: 768px) {
            .menu-button {
                top: 10px;
                left: 50%;
                transform: translateX(-50%);
                z-index: 2000;
            }
        }

        /* Sidebar Default */
        [data-testid="stSidebar"] {
            background-color: #f8f9fa;
            box-shadow: 2px 0px 8px rgba(0, 0, 0, 0.2);
            height: 100vh;
            position: fixed;
            left: 0;
            z-index: 1100;
            width: 300px;
            transition: all 0.3s ease-in-out;
        }

        /* Collapsed Sidebar */
        .collapsed-sidebar {
            width: 0px !important;
            overflow: hidden;
            padding: 0;
        }

        /* Ensure Main Content Adjusts */
        .main-content {
            margin-left: 300px;
            transition: margin-left 0.3s ease-in-out;
        }
        .collapsed .main-content {
            margin-left: 0px;
        }
    </style>

    <button class="menu-button" onclick="toggleSidebar()">☰ Menu</button>

    <script>
        function toggleSidebar() {
            var sidebar = document.querySelector('[data-testid="stSidebar"]');
            var mainContent = document.querySelector('.main-content');

            if (sidebar.classList.contains('collapsed-sidebar')) {
                sidebar.classList.remove('collapsed-sidebar');
                mainContent.classList.remove('collapsed');
                sidebar.style.width = "300px";
            } else {
                sidebar.classList.add('collapsed-sidebar');
                mainContent.classList.add('collapsed');
                sidebar.style.width = "0px";
            }
        }
    </script>
"""

st.markdown(menu_button_html, unsafe_allow_html=True)

# ✅ Sidebar Content Wrapper (Ensures Scroll)
st.sidebar.markdown('<div class="sidebar-content">', unsafe_allow_html=True)

# ✅ Sidebar Logo (Always Visible)
st.sidebar.markdown(f"""
    <div class="sidebar-logo">
        {f'<img src="data:image/png;base64,{logo_base64}" style="max-width: 80%; margin-bottom: 10px;">' if logo_base64 else '<p>⚠️ Logo Not Found</p>'}
    </div>
""", unsafe_allow_html=True)

# Sidebar: Menu Toggle Logic (Ensures visibility on mobile)
if "menu_expanded" not in st.session_state:
    st.session_state["menu_expanded"] = True  # Default to expanded

# ✅ Sidebar State Control for Responsiveness
st.markdown("""
    <style>
        /* Sidebar Toggle Button */
        .menu-toggle {
            width: 100%;
            background-color: #004aad;
            color: white;
            padding: 10px;
            border-radius: 5px;
            text-align: center;
            font-size: 16px;
            font-weight: bold;
            cursor: pointer;
            transition: background-color 0.3s;
        }
        .menu-toggle:hover {
            background-color: #003580;
        }

        /* Sidebar Appearance */
        [data-testid="stSidebar"] {
            transition: all 0.3s ease-in-out;
            background-color: #f8f9fa;
            box-shadow: 2px 0px 8px rgba(0, 0, 0, 0.2);
            height: 100vh;
            width: 300px;
            position: fixed;
            left: 0;
            z-index: 1100;
        }

        /* Collapsed Sidebar */
        .collapsed-sidebar {
            transform: translateX(-310px);
        }

        /* Expanded Sidebar */
        .expanded-sidebar {
            transform: translateX(0);
        }
    </style>
""", unsafe_allow_html=True)

# ✅ JavaScript to Toggle Sidebar
st.markdown("""
    <script>
        document.addEventListener("DOMContentLoaded", function() {
            var sidebar = document.querySelector('[data-testid="stSidebar"]');
            var menuButton = document.querySelector('.menu-toggle');

            function toggleSidebar() {
                if (sidebar.classList.contains('collapsed-sidebar')) {
                    sidebar.classList.remove('collapsed-sidebar');
                    sidebar.classList.add('expanded-sidebar');
                } else {
                    sidebar.classList.remove('expanded-sidebar');
                    sidebar.classList.add('collapsed-sidebar');
                }
            }

            menuButton.addEventListener("click", toggleSidebar);
        });
    </script>
""", unsafe_allow_html=True)

# ✅ Sidebar State Control for Responsive Width Adjustment
st.markdown("""
    <style>
        /* Sidebar Appearance */
        [data-testid="stSidebar"] {
            transition: all 0.3s ease-in-out;
            background-color: #f8f9fa;
            box-shadow: 2px 0px 8px rgba(0, 0, 0, 0.2);
            height: 100vh;
            position: fixed;
            left: 0;
            z-index: 1100;
            width: 300px; /* Default width */
        }
        
        /* Collapsed Sidebar (Width Shrinks Instead of Hiding Length) */
        .collapsed-sidebar {
            width: 60px !important; /* Adjust width for better visibility on mobile */
        }
        
        /* Ensuring content adjusts when sidebar shrinks */
        .main-content {
            margin-left: 300px;
            transition: margin-left 0.3s ease-in-out;
        }
        .collapsed .main-content {
            margin-left: 60px; /* Matches collapsed sidebar width */
        }
        
        /* Always Visible Menu Button */
        .menu-button {
            width: 100%;
            background-color: #004aad;
            color: white;
            padding: 10px;
            border-radius: 5px;
            text-align: center;
            font-size: 16px;
            font-weight: bold;
            cursor: pointer;
            transition: background-color 0.3s;
        }
        .menu-button:hover {
            background-color: #003580;
        }

        /* Hide text inside collapsed sidebar */
        .collapsed-sidebar .sidebar-content {
            display: none;
        }
    </style>
""", unsafe_allow_html=True)

# ✅ JavaScript to Toggle Sidebar Width Dynamically
st.markdown("""
    <script>
        document.addEventListener("DOMContentLoaded", function() {
            var sidebar = document.querySelector('[data-testid="stSidebar"]');
            var bodyContent = document.querySelector('.main-content');

            function toggleSidebarWidth() {
                if (sidebar.classList.contains('collapsed-sidebar')) {
                    sidebar.classList.remove('collapsed-sidebar');
                    bodyContent.classList.remove('collapsed');
                } else {
                    sidebar.classList.add('collapsed-sidebar');
                    bodyContent.classList.add('collapsed');
                }
            }

            document.querySelector('.menu-button').addEventListener("click", toggleSidebarWidth);
        });
    </script>
""", unsafe_allow_html=True)

# Apply collapsed state if needed
sidebar_class = "collapsed-sidebar" if st.session_state["sidebar_collapsed"] else ""
st.markdown(f'<div class="{sidebar_class}"></div>', unsafe_allow_html=True)

# ✅ Sidebar State Control for Responsiveness
st.markdown("""
    <style>
        /* Sidebar Toggle Button */
        .menu-toggle {
            width: 100%;
            background-color: #004aad;
            color: white;
            padding: 10px;
            border-radius: 5px;
            text-align: center;
            font-size: 16px;
            font-weight: bold;
            cursor: pointer;
            transition: background-color 0.3s;
        }
        .menu-toggle:hover {
            background-color: #003580;
        }
        
        /* Sidebar Appearance */
        [data-testid="stSidebar"] {
            transition: all 0.3s ease-in-out;
            background-color: #f8f9fa;
            box-shadow: 2px 0px 8px rgba(0, 0, 0, 0.2);
            height: 100vh;
            width: 300px;
            position: fixed;
            left: 0;
            z-index: 1100;
        }
        
        /* Collapsed Sidebar */
        .collapsed-sidebar {
            transform: translateX(-310px);
        }
        
        /* Expanded Sidebar */
        .expanded-sidebar {
            transform: translateX(0);
        }
    </style>
""", unsafe_allow_html=True)

# ✅ JavaScript to Toggle Sidebar
st.markdown("""
    <script>
        document.addEventListener("DOMContentLoaded", function() {
            var sidebar = document.querySelector('[data-testid="stSidebar"]');
            var menuButton = document.querySelector('.menu-toggle');

            function toggleSidebar() {
                if (sidebar.classList.contains('collapsed-sidebar')) {
                    sidebar.classList.remove('collapsed-sidebar');
                    sidebar.classList.add('expanded-sidebar');
                } else {
                    sidebar.classList.remove('expanded-sidebar');
                    sidebar.classList.add('collapsed-sidebar');
                }
            }

            menuButton.addEventListener("click", toggleSidebar);
        });
    </script>
""", unsafe_allow_html=True)

# ✅ Sidebar State Control
if "menu_expanded" not in st.session_state:
    st.session_state["menu_expanded"] = True  # Default to expanded

# ✅ JavaScript for Full Responsiveness & Sidebar Control
st.markdown("""
    <script>
        document.addEventListener("DOMContentLoaded", function() {
            var sidebar = document.querySelector('[data-testid="stSidebar"]');
            var menuButton = document.getElementById("menuToggle");

            function toggleSidebar() {
                if (sidebar.classList.contains('collapsed-sidebar')) {
                    sidebar.classList.remove('collapsed-sidebar');
                    sidebar.classList.add('expanded-sidebar');
                } else {
                    sidebar.classList.remove('expanded-sidebar');
                    sidebar.classList.add('collapsed-sidebar');
                }
            }

            menuButton.addEventListener("click", toggleSidebar);
        });
    </script>
""", unsafe_allow_html=True)

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
        z-index: 999; /* Lower z-index so sidebar overlays it */
        box-shadow: 0px 4px 10px rgba(0, 0, 0, 0.2);
    }

    [data-testid="stSidebar"] {
        background-color: #f8f9fa;
        box-shadow: 2px 0px 8px rgba(0, 0, 0, 0.2);
        overflow-y: auto;
        height: 100vh;
        width: 300px;
        transition: all 0.3s ease-in-out;
        position: fixed;
        left: 0;
        z-index: 1001; /* Higher z-index to overlay title */
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
    <div class="marquee-container">Track your business prospects in real-time   |   Data-driven insights   |   Sales pipeline optimization!!   🔥✨</div>
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
with st.sidebar.expander("➕ Add New Business Prospect", expanded=False):
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
with st.sidebar.expander("📝 Modify Existing Prospect", expanded=False):
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

    # Mapping 'Tender' to 'Lead Identified'
    stage_mapping = {
        "Tender": "Lead Identified",
        "Lead Identified": "Lead Identified",
        "Contacted": "Contacted",
        "Proposal Sent": "Contacted",
        "Negotiation": "Contacted",
        "Won": "Won",
        "Lost": "Won"  # Lost is grouped under Won to maintain 3 categories
    }

    df["Mapped Stage"] = df["Stage"].map(stage_mapping)

    # Aggregating counts for the simplified categories
    funnel_data = df["Mapped Stage"].value_counts().reset_index()
    funnel_data.columns = ["Stage", "Count"]

    # Sorting for logical funnel sequence
    stage_order = ["Lead Identified", "Contacted", "Won"]
    funnel_data = funnel_data.set_index("Stage").reindex(stage_order).reset_index()

    fig = px.funnel(funnel_data, x="Count", y="Stage", title="🔄 Simplified Conversion Funnel")
    st.plotly_chart(fig, use_container_width=True)

    st.header("📈 Opportunity Size by Industry")
    industry_chart = df.groupby("Industry")["Opportunity Size (KES)"].sum().reset_index()
    fig = px.bar(industry_chart, x="Industry", y="Opportunity Size (KES)", color="Industry")
    st.plotly_chart(fig, use_container_width=True)

st.header("📊 Industry Contribution")

if not df.empty:
    fig = px.pie(df, names="Industry", values="Opportunity Size (KES)", 
                 title="📊 Industry Contribution", color_discrete_sequence=px.colors.sequential.Blues)
    st.plotly_chart(fig, use_container_width=True)

st.header("📊 Business Prospect Status Distribution")

if not df.empty:
    status_counts = df["Status"].value_counts().reset_index()
    status_counts.columns = ["Status", "Count"]

    fig_pie = px.pie(status_counts, names="Status", values="Count", 
                     title="Current Status of Business Prospects",
                     color_discrete_sequence=["#004aad", "#00b4db"])
    st.plotly_chart(fig_pie, use_container_width=True)







