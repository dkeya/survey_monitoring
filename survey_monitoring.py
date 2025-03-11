import streamlit as st
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
from scipy.stats import zscore
from datetime import datetime

# --- Streamlit App Layout ---
st.title("Maize Survey Monitoring Dashboard")

# --- Load Data ---
@st.cache_data(ttl=60)  # Cache data for 60 seconds
def load_data(file_name):
    """
    Loads the survey data from the specified file.
    Caches the data to avoid reloading on every interaction.
    """
    try:
        df = pd.read_excel(file_name, sheet_name="Maize P&L Survey")
        return df
    except Exception as e:
        st.error(f"❌ Error loading file: {e}")
        return None

# Load dataset
df = load_data("Maize_PL_Survey_Thursday 2025.xlsx")

if df is not None:
    st.success("✅ File loaded successfully!")
    
    # --- Debugging: Print all column names ---
    st.write("Columns in the dataset:")
    st.write(df.columns.tolist())  # Print all column names

    # --- Data Preprocessing ---
    df["_submission_time"] = pd.to_datetime(df["_submission_time"])
    df["Date"] = df["_submission_time"].dt.date

    # --- Calculate Necessary Fields ---
    # Example: Calculate total maize harvested (MAM + OND seasons)
    if "4G. What quantity of maize did you harvest in the MAM (March, April, May) harvesting season (90 kgs bag)?" in df.columns and \
       "4H. What quantity did you harvest in the OND (October, November and December ) harvesting season (90 kgs bag)?" in df.columns:
        df["Total Maize Harvested (90 kgs bag)"] = df["4G. What quantity of maize did you harvest in the MAM (March, April, May) harvesting season (90 kgs bag)?"].fillna(0) + \
                                                  df["4H. What quantity did you harvest in the OND (October, November and December ) harvesting season (90 kgs bag)?"].fillna(0)
    else:
        st.warning("⚠️ Columns for MAM and OND harvest quantities not found. Total harvest cannot be calculated.")

    # Example: Calculate total maize lost
    loss_columns = [col for col in df.columns if "What quantity of maize was lost due to" in col]
    if loss_columns:
        df["Total Maize Lost (90 kgs bag)"] = df[loss_columns].sum(axis=1)
    else:
        st.warning("⚠️ Columns for maize loss not found. Total loss cannot be calculated.")

    # Example: Calculate total production cost
    cost_columns = [col for col in df.columns if "How much did you spend on" in col]
    if cost_columns:
        df["Total Production Cost (KES)"] = df[cost_columns].sum(axis=1)
    else:
        st.warning("⚠️ Columns for production costs not found. Total cost cannot be calculated.")

    # --- Sidebar Reorganization ---
    st.sidebar.header("👤 Enumerator Filter")
    
    # Use the correct column name for enumerators (including the trailing space)
    enumerator_column = "2B. Name of Enumerator "  # Updated to include the trailing space
    if enumerator_column in df.columns:
        enumerators = df[enumerator_column].unique()
        selected_enumerator = st.sidebar.selectbox("Select Enumerator", ["All"] + list(enumerators))
    else:
        st.error(f"❌ Column '{enumerator_column}' not found in the dataset. Please check the column names above.")
        selected_enumerator = "All"

    # Low Submission Threshold
    low_submission_threshold = st.sidebar.number_input("Set low submission threshold", value=5)

    # Add space
    st.sidebar.markdown("---")

    # --- Enumerator Metrics Submodules ---
    st.sidebar.header("📊 Enumerator Metrics")
    enumerator_metric = st.sidebar.radio(
        "Select Metric",
        ["Start Time", "Stop Time", "Survey Duration", "No Pattern", "Missing Data Pattern", "Outlier Pattern", "GPS Location vs Polygon/Homestead"]
    )

    # --- Survey-Wide Analysis Submodules ---
    st.sidebar.header("📈 Survey-Wide Analysis")
    survey_analysis = st.sidebar.radio(
        "Select Analysis",
        ["Outliers", "Price Range", "Acreage", "Seeding Rate", "Scale No", "Production Cost Parameters", "Seed Type", "Monocrop vs. Intercrop Ratio"]
    )

    # --- Dynamic Content Rendering ---
    if selected_enumerator != "All":
        enumerator_df = df[df[enumerator_column] == selected_enumerator]

        # Enumerator Metrics
        if enumerator_metric == "Start Time":
            st.header("⏰ Start Time")
            start_time = enumerator_df["_submission_time"].min()
            st.write(f"**Start Time:** {start_time}")

        elif enumerator_metric == "Stop Time":
            st.header("⏰ Stop Time")
            stop_time = enumerator_df["_submission_time"].max()
            st.write(f"**Stop Time:** {stop_time}")

        elif enumerator_metric == "Survey Duration":
            st.header("⏳ Survey Duration")
            start_time = enumerator_df["_submission_time"].min()
            stop_time = enumerator_df["_submission_time"].max()
            survey_duration = stop_time - start_time
            st.write(f"**Survey Duration:** {survey_duration}")

        elif enumerator_metric == "No Pattern":
            st.header("🚫 No Pattern")
            no_pattern = enumerator_df.apply(lambda x: x.astype(str).str.contains("No").sum()).sum()
            st.write(f"**'No' Pattern Count:** {no_pattern}")

        elif enumerator_metric == "Missing Data Pattern":
            st.header("❓ Missing Data Pattern")
            missing_data = enumerator_df.isnull().sum().sum()
            st.write(f"**Missing Data Count:** {missing_data}")

        elif enumerator_metric == "Outlier Pattern":
            st.header("📉 Outlier Pattern")
            numeric_cols = enumerator_df.select_dtypes(include=['float64', 'int64']).columns
            outlier_count = 0
            for col in numeric_cols:
                z_scores = (enumerator_df[col] - enumerator_df[col].mean()) / enumerator_df[col].std()
                outlier_count += (z_scores.abs() > 3).sum()
            st.write(f"**Outlier Count:** {outlier_count}")

        elif enumerator_metric == "GPS Location vs Polygon/Homestead":
            st.header("📍 GPS Location vs Polygon/Homestead")
            st.write("**GPS Location vs Polygon/Homestead:** (Functionality to be implemented)")

    # Survey-Wide Analysis
    if survey_analysis == "Outliers":
        st.header("📉 Outliers")
        numeric_cols = df.select_dtypes(include=['float64', 'int64']).columns
        outlier_summary = {}
        for col in numeric_cols:
            z_scores = (df[col] - df[col].mean()) / df[col].std()
            outlier_summary[col] = (z_scores.abs() > 3).sum()
        st.write(pd.Series(outlier_summary).rename("Outlier Count"))

    elif survey_analysis == "Price Range":
        st.header("💰 Price Range")
        if "6C1. How much (KES) did you sell your maize at the farm gate per kg in January?" in df.columns:
            price_columns = [col for col in df.columns if "How much (KES) did you sell your maize at the farm gate per kg in" in col]
            min_price = df[price_columns].min().min()
            max_price = df[price_columns].max().max()
            st.write(f"Min Price: {min_price}")
            st.write(f"Max Price: {max_price}")
        else:
            st.warning("⚠️ Price columns not found in the dataset.")

    elif survey_analysis == "Acreage":
        st.header("🌾 Acreage")
        
        # Define the relevant columns for acreage
        acreage_columns = [
            "4A. What  is the total size of land you own in acres?",
            "4B. What  is the total size of land you borrowed in acres?",
            "4C. What  is the total size of land you leased in acres?"
        ]
        
        # Check if the columns exist in the dataset
        if all(col in df.columns for col in acreage_columns):
            # Calculate total acreage (owned + borrowed + leased)
            df["Total Acreage"] = df[acreage_columns].sum(axis=1)
            
            # Display min and max total acreage
            min_acreage = df["Total Acreage"].min()
            max_acreage = df["Total Acreage"].max()
            st.write(f"Min Total Acreage: {min_acreage}")
            st.write(f"Max Total Acreage: {max_acreage}")
            
            # Display summary statistics for each type of acreage
            st.subheader("Summary Statistics for Acreage")
            st.write(df[acreage_columns].describe())
        else:
            st.warning("⚠️ One or more acreage columns not found in the dataset.")

    # --- Existing Functionality (Retained) ---
    # --- Enumerators with Low Submissions ---
    st.header("⚠️ Enumerators with Low Submissions")
    if enumerator_column in df.columns:
        enumerator_counts = df[enumerator_column].value_counts()
        low_enumerators = enumerator_counts[enumerator_counts < low_submission_threshold]

        if not low_enumerators.empty:
            st.warning(f"These enumerators have fewer than {low_submission_threshold} submissions and may need follow-up:")
            st.write(low_enumerators)
        else:
            st.success("✅ No enumerators with low submissions detected.")
    else:
        st.error(f"❌ Column '{enumerator_column}' not found in the dataset.")

    # --- Submissions Over Time ---
    st.header("📅 Daily Submissions Trend")
    fig, ax = plt.subplots(figsize=(8, 3))
    df.set_index("_submission_time").resample("D").size().plot(kind="line", marker="o", ax=ax)
    plt.xlabel("Date")
    plt.ylabel("Number of Submissions")
    plt.title("Daily Survey Submissions")
    plt.grid()
    st.pyplot(fig)

    # --- Enumerator Performance ---
    st.header("👤 Enumerator Performance")
    if enumerator_column in df.columns:
        st.bar_chart(df[enumerator_column].value_counts())
    else:
        st.error(f"❌ Column '{enumerator_column}' not found in the dataset.")

    # --- Daily Submissions Per Enumerator ---
    st.header("📆 Daily Submissions Per Enumerator")
    if enumerator_column in df.columns:
        daily_enumerator_counts = df.groupby(["Date", enumerator_column]).size().unstack(fill_value=0)
        st.line_chart(daily_enumerator_counts)
    else:
        st.error(f"❌ Column '{enumerator_column}' not found in the dataset.")

    # --- Missing Data Analysis ---
    st.header("⚠️ Missing Data Overview")

    # Missing data by field
    st.subheader("🔍 Missing Data by Field")
    missing_values = df.isnull().sum() / len(df) * 100
    critical_missing = missing_values[missing_values > 50]  # Highlight fields missing >50%

    if not critical_missing.empty:
        st.warning("🚨 Critical fields with more than 50% missing data:")
        st.write(critical_missing)
    else:
        st.success("✅ No critical missing data detected.")

    # Missing data by enumerator
    st.subheader("🔍 Missing Data Per Enumerator")
    if enumerator_column in df.columns:
        missing_by_enumerator = df.groupby(enumerator_column).apply(lambda x: x.isnull().sum().sum()).sort_values(ascending=False)
        st.bar_chart(missing_by_enumerator)
        st.write(missing_by_enumerator)
    else:
        st.error(f"❌ Column '{enumerator_column}' not found in the dataset.")

    # --- Duplicate Responses ---
    st.header("🔁 Duplicate Responses")
    duplicate_rows = df[df.duplicated(subset=["_submission_time", enumerator_column], keep=False)]

    if not duplicate_rows.empty:
        st.warning(f"⚠️ {len(duplicate_rows)} duplicate responses detected!")
        
        if st.button("👀 Show Duplicate Responses"):
            st.write(duplicate_rows[["_submission_time", enumerator_column]])
    else:
        st.success("✅ No duplicate responses found.")

    # --- Outlier Detection ---
    st.header("📉 Outlier Detection")

    # Select only numeric columns
    numeric_cols = df.select_dtypes(include=['float64', 'int64']).columns.tolist()

    if numeric_cols:
        skipped_columns = []
        all_outliers = pd.DataFrame()

        for col in numeric_cols:
            # Check for NaN or infinite values
            if df[col].isnull().any() or np.isinf(df[col]).any():
                skipped_columns.append(col)
                continue

            # Ensure there is enough data to plot
            if len(df[col].dropna()) < 2:
                skipped_columns.append(col)
                continue

            st.subheader(f"Outliers in {col}")
            fig, ax = plt.subplots()
            
            try:
                sns.boxplot(data=df[col], ax=ax)
                plt.title(f"Boxplot for {col}")
                st.pyplot(fig)
            except Exception as e:
                st.error(f"❌ Error generating boxplot for {col}: {e}")
                continue

            # Z-score based outlier detection
            df["zscore"] = (df[col] - df[col].mean()) / df[col].std()  # Manual Z-score calculation
            outliers = df[df["zscore"].abs() > 3]
            if not outliers.empty:
                st.warning(f"🚨 Outliers detected in {col}:")
                st.write(outliers[[col, enumerator_column, "_submission_time"]])
                all_outliers = pd.concat([all_outliers, outliers[[col, enumerator_column, "_submission_time"]]])
            else:
                st.success(f"✅ No outliers detected in {col}.")

        if skipped_columns:
            st.warning(f"⚠️ The following columns were skipped due to NaN, infinite values, or insufficient data: {skipped_columns}")

        if not all_outliers.empty:
            st.warning("🚨 Summary of all detected outliers:")
            st.write(all_outliers)
    else:
        st.warning("⚠️ No numeric columns found for outlier detection.")

    # --- Data Export ---
    st.header("📥 Export Data")
    if st.button("Export Cleaned Data"):
        df.to_csv("cleaned_survey_data.csv", index=False)
        st.success("✅ Data exported successfully!")

    if st.button("Export Cleaned Data (Outliers Removed)"):
        cleaned_df = df[df["zscore"].abs() <= 3]  # Example: Remove outliers
        cleaned_df.to_csv("cleaned_survey_data_outliers_removed.csv", index=False)
        st.success("✅ Cleaned data (outliers removed) exported successfully!")

else:
    st.warning("⚠️ Please ensure the survey file is in the correct folder and refresh Streamlit.")