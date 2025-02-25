import streamlit as st
import pandas as pd
import plotly.express as px
import os
import tempfile
import shutil

# Step 1: Initialize tracker with CSV persistence
file_path = "business_pipeline_tracker.csv"

# Load or create the dataset
if os.path.exists(file_path):
    try:
        df = pd.read_csv(file_path, dtype={"Phone": str})  # Ensure phone numbers remain as strings
    except PermissionError:
        st.error("🚨 The file 'business_pipeline_tracker.csv' is locked or open elsewhere. Close it and restart.")
        st.stop()
else:
    df = pd.DataFrame(columns=[
        "Prospect Name", "Contact Person", "Email", "Phone", "Opportunity Size (KES)", 
        "Status", "Stage", "Industry", "Follow-up Date", "Notes", "Priority"
    ])

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

# Streamlit UI
st.set_page_config(page_title="Business Prospects Tracker", page_icon="📊", layout="wide")

# --- SIDEBAR: LOGO AT THE TOP ---
st.sidebar.image("logo.png", use_container_width=True)

# --- HEADER & SUMMARY ---
st.title("📊 Business Prospects Pipeline Tracker")
st.markdown("###### *Track your business prospects with real-time analytics*")

# --- KPIs Overview ---
total_prospects = df.shape[0]
open_deals = df[df["Status"] == "Open"].shape[0]
closed_deals = df[df["Status"] == "Closed"].shape[0]
priority_deals = df[df["Priority"] == "Yes"].shape[0]

st.metric("Total Prospects", total_prospects)
col1, col2, col3 = st.columns(3)
col1.metric("Open Deals", open_deals)
col2.metric("Closed Deals", closed_deals)
col3.metric("Priority Prospects", priority_deals)

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
    new_data = pd.DataFrame([{
        "Prospect Name": prospect_name,
        "Contact Person": contact_person,
        "Email": email,
        "Phone": f"0{int(phone[-9:])}" if phone and phone.isdigit() and len(phone) >= 9 else phone,
        "Opportunity Size (KES)": round(opportunity_size, 2),
        "Status": status,
        "Stage": stage,
        "Industry": industry,
        "Priority": priority,
        "Follow-up Date": followup_date.strftime('%d/%m/%Y') if followup_date else "N/A",
        "Notes": notes
    }])

    df = pd.concat([df, new_data], ignore_index=True).drop_duplicates(subset=["Prospect Name", "Email", "Phone"], keep="first")

    # Save safely using a temporary file
    temp_file = tempfile.NamedTemporaryFile(delete=False, mode='w', encoding='utf-8', newline='')
    df.to_csv(temp_file.name, index=False)
    temp_file.close()

    if os.path.exists(file_path):
        os.remove(file_path)
    shutil.move(temp_file.name, file_path)

    st.sidebar.success("✅ Prospect added successfully!")
    st.rerun()

# --- COLLAPSIBLE "MODIFY EXISTING PROSPECT" FORM ---
with st.sidebar.expander("📝 Modify Existing Prospect", expanded=False):
    selected_prospect = st.selectbox("Select Prospect to Modify", ["None"] + list(df["Prospect Name"].unique()))

    if selected_prospect != "None":
        selected_row = df[df["Prospect Name"] == selected_prospect].iloc[0]

        # Convert Follow-up Date, setting a default value if NaT
        followup_date_value = pd.to_datetime(selected_row["Follow-up Date"], errors="coerce")
        if pd.isna(followup_date_value):
            followup_date_value = pd.to_datetime("today")  # Default to today's date

        with st.form("modify_prospect_form"):
            new_contact_person = st.text_input("Contact Person", selected_row["Contact Person"])
            new_email = st.text_input("Email", selected_row["Email"])
            new_phone = st.text_input("Phone", f"0{int(selected_row['Phone'][-9:])}" if str(selected_row["Phone"]).isdigit() and len(str(selected_row["Phone"])) >= 9 else selected_row["Phone"])
            new_opportunity_size = st.number_input("Opportunity Size (KES)", min_value=0.0, step=100.0, value=float(selected_row["Opportunity Size (KES)"]))
            new_status = st.selectbox("Status", ["Open", "Closed"], index=["Open", "Closed"].index(selected_row["Status"]))
            new_stage = st.selectbox("Pipeline Stage", pipeline_stages, index=pipeline_stages.index(selected_row["Stage"]))
            new_industry = st.selectbox("Industry", industry_categories, index=industry_categories.index(selected_row["Industry"]))
            new_priority = st.selectbox("Priority", ["Yes", "No"], index=["Yes", "No"].index(selected_row["Priority"]))
            new_followup_date = st.date_input("Follow-up Date", followup_date_value)  # Fixed NaT issue
            new_notes = st.text_area("Additional Notes", selected_row["Notes"])

            update_button = st.form_submit_button("Update Prospect")

        if update_button:
            df.loc[df["Prospect Name"] == selected_prospect, :] = [
                selected_prospect, new_contact_person, new_email, new_phone,
                round(new_opportunity_size, 2), new_status, new_stage, new_industry, 
                new_followup_date.strftime('%d/%m/%Y'),  # Convert to formatted date string
                new_notes, new_priority
            ]

            temp_file = tempfile.NamedTemporaryFile(delete=False, mode='w', encoding='utf-8', newline='')
            df.to_csv(temp_file.name, index=False)
            temp_file.close()

            if os.path.exists(file_path):
                os.remove(file_path)
            shutil.move(temp_file.name, file_path)

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

# Display the filtered prospects
st.subheader("📋 Filtered Business Prospects")
st.dataframe(filtered_df, height=400, use_container_width=True)

# --- UPLOAD & DOWNLOAD ---
st.sidebar.download_button("📥 Download CSV", df.to_csv(index=False), "filtered_prospects.csv", "text/csv")
uploaded_file = st.sidebar.file_uploader("📤 Upload a CSV file", type=["csv"])
if uploaded_file is not None:
    df = pd.read_csv(uploaded_file)
    st.sidebar.success("✅ File uploaded successfully!")

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