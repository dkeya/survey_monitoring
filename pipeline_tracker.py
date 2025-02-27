import streamlit as st
import pandas as pd
import plotly.express as px
import os
import tempfile
import shutil

# Streamlit UI
st.set_page_config(page_title="Business Prospects Tracker", page_icon="📊", layout="wide")

hide_streamlit_style = """
    <style>
        #MainMenu {visibility: hidden;}
        footer {visibility: hidden;}
        header {visibility: hidden;}
    </style>
"""

responsive_style = """
    <style>
        @media screen and (max-width: 768px) {
            .fancy-title { font-size: 22px; padding: 10px 5px; }
            .marquee-container { font-size: 14px; }
            .stButton>button { width: 100%; }
        }
    </style>
"""

st.markdown(responsive_style, unsafe_allow_html=True)

# Add Sidebar Responsiveness Styles
sidebar_style = """
    <style>
        @media screen and (max-width: 768px) {
            [data-testid="stSidebarContent"] {
                display: block !important;
                position: fixed !important;
                top: 0;
                left: 0;
                width: 75vw !important;
                height: 100vh !important;
                background: white !important;
                box-shadow: 4px 0px 10px rgba(0, 0, 0, 0.1);
                z-index: 1100;
                overflow-y: auto;
                transform: translateX(-100%);
                transition: transform 0.3s ease-in-out;
            }

            /* Ensure sidebar slides in when toggled */
            [data-testid="stSidebarContent"].active {
                transform: translateX(0);
            }

            /* Sidebar Toggle Button */
            .sidebar-toggle {
                display: block !important;
                position: fixed;
                top: 15px;
                left: 15px;
                background: #004aad;
                color: white;
                padding: 10px 15px;
                border-radius: 5px;
                font-size: 18px;
                font-weight: bold;
                cursor: pointer;
                z-index: 3000;  /* Ensure it's above all elements */
                box-shadow: 2px 2px 5px rgba(0, 0, 0, 0.3);
            }
        }

        /* Hide toggle button on larger screens */
        @media screen and (min-width: 769px) {
            .sidebar-toggle {
                display: none !important;
            }
        }
    </style>
"""

st.markdown(sidebar_style, unsafe_allow_html=True)

# Inject Sidebar Toggle Button at Main Level (NOT inside Sidebar)
st.markdown(
    """
    <div class="sidebar-toggle" onclick="document.querySelector('[data-testid=stSidebarContent]').classList.toggle('active');">
        ☰ Menu
    </div>
    """,
    unsafe_allow_html=True
)

st.markdown(responsive_style, unsafe_allow_html=True)
st.markdown(hide_streamlit_style, unsafe_allow_html=True)

# Step 1: Initialize tracker with CSV persistence
file_path = "business_pipeline_tracker.csv"

# Load or create the dataset
def load_data():
    if os.path.exists(file_path):
        try:
            return pd.read_csv(file_path, dtype={"Phone": str})
        except PermissionError:
            st.error("🚨 The file is locked. Close it and restart.")
            st.stop()
    return pd.DataFrame(columns=[
        "Prospect Name", "Contact Person", "Email", "Phone", "Opportunity Size (KES)", 
        "Status", "Stage", "Industry", "Follow-up Date", "Notes", "Priority"
    ])

df = load_data()  # Load once at the start

def save_data(df):
    """Save DataFrame to CSV and refresh."""
    df.to_csv(file_path, index=False)

# Ensure all expected columns exist
for col in ["Priority"]:
    if col not in df.columns:
        df[col] = "No"  # Default to "No"

# Define pipeline stages (including new 'Tender' category)
pipeline_stages = ["Lead Identified", "Contacted", "Proposal Sent", "Negotiation", "Won", "Lost", "Tender"]

# Define Industry categories
industry_categories = [
    "Technology", "Finance", "Healthcare", "Education", "Retail",
    "Manufacturing", "Agriculture", "Real Estate", "Government", "Other"
]

# --- SIDEBAR: LOGO AT THE TOP ---
st.sidebar.markdown(
    """
    <style>
        [data-testid="stSidebar"] img {
            position: fixed;
            top: 10px;
            left: 10px;
            width: 250px;  /* Adjust width as needed */
            z-index: 1000;
            margin-bottom: 50px;  /* Adds space below the logo */
            filter: drop-shadow(2px 2px 5px rgba(0, 0, 0, 0.2));  /* Soft shadow */
        }

        /* Push down other elements */
        [data-testid="stSidebarContent"] {
            margin-top: 120px;  /* Adjust based on logo size */
        }
    </style>
    """,
    unsafe_allow_html=True
)

st.sidebar.image("logo.png", use_container_width=True)
st.sidebar.image("logo.png", use_container_width=True)

# --- HEADER & SUMMARY ---
st.markdown(
    """
    <style>
        .fancy-title {
            position: fixed;
            top: 0;
            left: 0;
            width: 100%;
            background: linear-gradient(to right, #1F3C63, #004aad);
            color: white;
            padding: 15px 10px;
            font-size: 28px;
            font-weight: bold;
            text-align: center;
            border-radius: 8px;
            box-shadow: 0px 4px 10px rgba(0, 0, 0, 0.2);
            z-index: 1000;
            min-height: 60px;
            display: flex;
            align-items: center;
            justify-content: center;
            line-height: 1.2;
        }

        .content-container {
            margin-top: 80px;
            transition: margin-top 0.3s ease-in-out;
        }

        /* Marquee styling */
        .marquee-container {
            position: fixed;
            top: 80px;
            left: 0;
            width: 100%;
            background: rgba(0, 74, 173, 0.1);
            border-radius: 5px;
            padding: 10px;
            z-index: 999;
            box-shadow: 0px 2px 8px rgba(0, 0, 0, 0.1);
            transition: top 0.3s ease-in-out;
        }

        @keyframes scroll {
            0% { transform: translateX(100%); }
            100% { transform: translateX(-100%); }
        }

        .marquee {
            display: inline-block;
            white-space: nowrap;
            font-size: 17px;
            font-style: italic;
            font-weight: bold;
            background: linear-gradient(90deg, #004aad, #00b4db);
            -webkit-background-clip: text;
            -webkit-text-fill-color: transparent;
            text-shadow: 1px 1px 10px rgba(0, 74, 173, 0.3);
            animation: scroll 15s linear infinite;
        }

        .marquee:hover {
            animation-play-state: paused;
        }

        /* Sidebar styles */
        @media screen and (max-width: 768px) {
            [data-testid="stSidebarContent"] {
                display: block !important;
                position: fixed !important;
                top: 0;
                left: 0;
                width: 75vw !important;
                height: 100vh !important;
                background: white !important;
                box-shadow: 4px 0px 10px rgba(0, 0, 0, 0.1);
                z-index: 1100;
                overflow-y: auto;
                transform: translateX(-100%);
                transition: transform 0.3s ease-in-out;
            }

            [data-testid="stSidebarContent"].active {
                transform: translateX(0);
            }

            /* Properly position ☰ Menu button below marquee */
            .sidebar-toggle {
                display: block !important;
                position: fixed;
                top: 140px;  /* Just below the marquee */
                left: 15px;
                background: #004aad;
                color: white;
                padding: 10px 15px;
                border-radius: 5px;
                font-size: 18px;
                font-weight: bold;
                cursor: pointer;
                z-index: 3000;
                box-shadow: 2px 2px 5px rgba(0, 0, 0, 0.3);
            }
        }

        /* Hide toggle button on larger screens */
        @media screen and (min-width: 769px) {
            .sidebar-toggle {
                display: none !important;
            }
        }
    </style>
    <div class="fancy-title">🎯 Business Prospects Pipeline Tracker</div>
    <div class="content-container"></div>
    <div class="marquee-container">
        <div class="marquee">Track your business prospects with real-time analytics | Stay ahead with data-driven insights | Optimize your sales pipeline efficiently! 🔥✨</div>
    </div>
    """,
    unsafe_allow_html=True
)

# --- Sidebar Toggle Button (Corrected Positioning) ---
st.markdown(
    """
    <div class="sidebar-toggle" onclick="document.querySelector('[data-testid=stSidebarContent]').classList.toggle('active');">
        ☰ Menu
    </div>
    """,
    unsafe_allow_html=True
)

# --- JavaScript to Close Sidebar When Clicking Outside ---
st.markdown(
    """
    <script>
        document.addEventListener("click", function(event) {
            let sidebar = document.querySelector('[data-testid=stSidebarContent]');
            let button = document.querySelector('.sidebar-toggle');
            
            if (sidebar && button) {
                if (!sidebar.contains(event.target) && !button.contains(event.target)) {
                    sidebar.classList.remove('active'); // Close sidebar when clicking outside
                }
            }
        });
    </script>
    """,
    unsafe_allow_html=True
)

# --- KPIs Overview ---
total_prospects = df.shape[0]
open_deals = df[df["Status"] == "Open"].shape[0]
closed_deals = df[df["Status"] == "Closed"].shape[0]
priority_deals = df[df["Priority"] == "Yes"].shape[0]

col1, col2, col3 = st.columns([1, 1, 1])  # Balanced width
col1.metric("📌 Total Prospects", total_prospects)
col2.metric("✅ Open Deals", open_deals)
col3.metric("🔒 Closed Deals", closed_deals)

st.markdown("<br>", unsafe_allow_html=True)  # Adds a little spacing
st.metric("🚀 Priority Prospects", priority_deals)

# --- COLLAPSIBLE "ADD NEW BUSINESS PROSPECT" FORM ---
with st.sidebar.expander("➕ Add New Business Prospect", expanded=False):  
    with st.form("add_prospect_form"):
        prospect_name = st.text_input("Prospect Name")
        contact_person = st.text_input("Contact Person")
        email = st.text_input("Email")
        phone = st.text_input("Phone Number")
        opportunity_size = st.number_input("Opportunity Size (KES)", min_value=0.0, step=100.0)
        status = st.selectbox("Status", ["Open", "Closed"])
        stage = st.selectbox("Pipeline Stage", pipeline_stages)
        industry = st.selectbox("Industry", industry_categories)
        priority = st.selectbox("Priority", ["Yes", "No"])
        followup_date = st.date_input("Follow-up Date")
        notes = st.text_area("Additional Notes")

        submit_button = st.form_submit_button("Add Prospect")

if submit_button:
    if not prospect_name or not contact_person or not email:
        st.sidebar.error("❌ Please fill in all required fields.")
    else:
        new_data = pd.DataFrame([{
            "Prospect Name": prospect_name.strip(),
            "Contact Person": contact_person.strip(),
            "Email": email.strip(),
            "Phone": f"0{int(phone[-9:])}" if phone and phone.isdigit() and len(phone) >= 9 else phone.strip(),
            "Opportunity Size (KES)": round(opportunity_size, 2),
            "Status": status,
            "Stage": stage,
            "Industry": industry,
            "Priority": priority,
            "Follow-up Date": followup_date.strftime('%d/%m/%Y') if followup_date else "N/A",
            "Notes": notes.strip()
        }])

        df = pd.concat([df, new_data]).drop_duplicates(subset=["Prospect Name", "Email", "Phone"], keep="first").reset_index(drop=True)

        save_data(df)  # Use the new save function
        st.sidebar.success("✅ Prospect added successfully!")
        st.rerun()

# --- COLLAPSIBLE "MODIFY EXISTING PROSPECT" FORM ---
with st.sidebar.expander("📝 Modify Existing Prospect", expanded=False):
    selected_prospect = st.selectbox("Select Prospect to Modify", ["None"] + list(df["Prospect Name"].unique()))

    if selected_prospect != "None":
        # Fetch the row index
        row_index = df[df["Prospect Name"] == selected_prospect].last_valid_index()
        selected_row = df.loc[row_index]

        # Convert Follow-up Date safely
        followup_date_value = pd.to_datetime(selected_row["Follow-up Date"], errors="coerce")
        if pd.isna(followup_date_value):
            followup_date_value = pd.to_datetime("today")  # Default to today's date

        with st.form("modify_prospect_form"):
            new_contact_person = st.text_input("Contact Person", selected_row["Contact Person"])
            new_email = st.text_input("Email", selected_row["Email"])
            new_phone = st.text_input("Phone", selected_row["Phone"])
            new_opportunity_size = st.number_input("Opportunity Size (KES)", min_value=0.0, step=100.0, value=float(selected_row["Opportunity Size (KES)"]))
            new_status = st.selectbox("Status", ["Open", "Closed"], index=["Open", "Closed"].index(selected_row["Status"]))
            new_stage = st.radio("Update Pipeline Stage", pipeline_stages, horizontal=True, index=pipeline_stages.index(selected_row["Stage"]))
            new_industry = st.selectbox("Industry", industry_categories, index=industry_categories.index(selected_row["Industry"]))
            new_priority = st.selectbox("Priority", ["Yes", "No"], index=["Yes", "No"].index(selected_row["Priority"]))
            new_followup_date = st.date_input("Follow-up Date", followup_date_value)
            new_notes = st.text_area("Additional Notes", selected_row["Notes"])

            update_button = st.form_submit_button("Update Prospect")

        if update_button:
            df.at[row_index, "Contact Person"] = new_contact_person.strip()
            df.at[row_index, "Email"] = new_email.strip()
            df.at[row_index, "Phone"] = new_phone.strip()
            df.at[row_index, "Opportunity Size (KES)"] = round(new_opportunity_size, 2)
            df.at[row_index, "Status"] = new_status
            df.at[row_index, "Stage"] = new_stage
            df.at[row_index, "Industry"] = new_industry
            df.at[row_index, "Priority"] = new_priority
            df.at[row_index, "Follow-up Date"] = new_followup_date.strftime('%d/%m/%Y')
            df.at[row_index, "Notes"] = new_notes.strip()

            save_data(df)  # Use direct saving
            st.sidebar.success("✅ Prospect updated successfully!")
            st.rerun()       

# --- FILTERING PROSPECTS ---
st.sidebar.subheader("🔍 Filter Prospects")

selected_stage = st.sidebar.selectbox("Filter by Stage", ["All"] + pipeline_stages)
selected_status = st.sidebar.selectbox("Filter by Status", ["All", "Open", "Closed"])
selected_industry = st.sidebar.selectbox("Filter by Industry", ["All"] + industry_categories)

# Insert the missing slider for opportunity size filtering
min_opportunity = st.sidebar.slider("Min Opportunity Size (KES)", 0, 10000000, 0)

# Apply filtering based on user selections
filtered_df = df.copy()
if selected_stage != "All":
    filtered_df = filtered_df[filtered_df["Stage"] == selected_stage]
if selected_status != "All":
    filtered_df = filtered_df[filtered_df["Status"] == selected_status]
if selected_industry != "All":
    filtered_df = filtered_df[filtered_df["Industry"] == selected_industry]

# Apply Opportunity Size filter
filtered_df = filtered_df[filtered_df["Opportunity Size (KES)"] >= min_opportunity]

# Ensure priority prospects appear at the top
filtered_df = filtered_df.sort_values(by=["Priority"], ascending=False).reset_index(drop=True)

# Function to mask phone numbers for UI display
def mask_phone(phone):
    if isinstance(phone, str) and len(phone) >= 7:  # Ensure it's a valid phone number
        return phone[:4] + "****" + phone[-2:]  # Example: 0722****34
    return phone  # Return as is if invalid

# Create a display version with masked phone numbers
filtered_df_display = filtered_df.copy()
filtered_df_display["Phone"] = filtered_df_display["Phone"].apply(mask_phone)

# Display the masked phone numbers in Streamlit UI
st.subheader("📋 Filtered Business Prospects")
st.dataframe(filtered_df_display.head(50), height=400, use_container_width=True)
st.caption("Showing first 50 rows. Use filters for more details.")

# --- UPLOAD & DOWNLOAD ---
st.sidebar.download_button("📥 Download CSV", df.to_csv(index=False), "filtered_prospects.csv", "text/csv")
uploaded_file = st.sidebar.file_uploader("📤 Upload a CSV file", type=["csv"])
if uploaded_file is not None:
    try:
        df = pd.read_csv(uploaded_file, dtype={"Phone": str})
        save_data(df)
        st.sidebar.success("✅ File uploaded successfully!")
        st.rerun()
    except Exception as e:
        st.sidebar.error(f"❌ Error loading file: {str(e)}")

# --- INTERACTIVE VISUALIZATIONS ---
st.header("🔄 Conversion Funnel")  # Keep the main header but remove subheader

if not df.empty:
    funnel_data = df["Stage"].value_counts().reset_index()
    funnel_data.columns = ["Stage", "Count"]

    # Merge "Tender" inside "Lead Identified"
    if "Tender" in funnel_data["Stage"].values:
        lead_identified_count = funnel_data.loc[funnel_data["Stage"] == "Lead Identified", "Count"].values[0]
        tender_count = funnel_data.loc[funnel_data["Stage"] == "Tender", "Count"].values[0]

        # Update "Lead Identified" count to include Tender
        funnel_data.loc[funnel_data["Stage"] == "Lead Identified", "Count"] = lead_identified_count + tender_count
        
        # Remove "Tender" as a separate stage
        funnel_data = funnel_data[funnel_data["Stage"] != "Tender"]

    fig = px.funnel(funnel_data, x="Count", y="Stage", title="")  # Remove the title inside the chart
    st.plotly_chart(fig, use_container_width=True)

st.header("📈 Opportunity Size by Industry")  # Keep the main header but remove subheader
if not df.empty:
    industry_chart = df.groupby("Industry")["Opportunity Size (KES)"].sum().reset_index()
    industry_chart["Opportunity Size (KES)"] = industry_chart["Opportunity Size (KES)"].clip(lower=0)  # Ensure no negative values
    fig = px.bar(industry_chart, x="Industry", y="Opportunity Size (KES)", color="Industry", title="")  # Remove the title inside the chart
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