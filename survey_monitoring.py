import streamlit as st
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
import os
from scipy.stats import zscore

# --- Streamlit App Layout ---
st.title("Maize Survey Monitoring Dashboard")

# --- File Upload ---
uploaded_file = st.sidebar.file_uploader("Upload Survey Data (Excel file)", type=["xlsx"])

if uploaded_file is not None:
    try:
        # Load dataset
        df = pd.read_excel(uploaded_file, sheet_name="Maize P&L Survey")
        st.success("✅ File uploaded and loaded successfully!")

        # --- Data Preprocessing ---
        df["_submission_time"] = pd.to_datetime(df["_submission_time"])
        df["Date"] = df["_submission_time"].dt.date

        # --- Survey Progress Overview ---
        st.header("📌 Survey Progress Overview")
        col1, col2 = st.columns(2)
        with col1:
            st.metric("Total Submissions", len(df))
        with col2:
            st.metric("Unique Enumerators", df["_submitted_by"].nunique())

        # --- Enumerator Filter ---
        st.sidebar.header("👤 Enumerator Filter")
        enumerators = df["_submitted_by"].unique()
        selected_enumerator = st.sidebar.selectbox("Select Enumerator", ["All"] + list(enumerators))

        if selected_enumerator != "All":
            df = df[df["_submitted_by"] == selected_enumerator]

        # --- Enumerators with Low Submissions ---
        st.header("⚠️ Enumerators with Low Submissions")
        low_submission_threshold = st.sidebar.number_input("Set low submission threshold", value=5)
        enumerator_counts = df["_submitted_by"].value_counts()
        low_enumerators = enumerator_counts[enumerator_counts < low_submission_threshold]

        if not low_enumerators.empty:
            st.warning(f"These enumerators have fewer than {low_submission_threshold} submissions and may need follow-up:")
            st.write(low_enumerators)
        else:
            st.success("✅ No enumerators with low submissions detected.")

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
        st.bar_chart(df["_submitted_by"].value_counts())

        # --- Daily Submissions Per Enumerator ---
        st.header("📆 Daily Submissions Per Enumerator")
        daily_enumerator_counts = df.groupby(["Date", "_submitted_by"]).size().unstack(fill_value=0)
        st.line_chart(daily_enumerator_counts)

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
        missing_by_enumerator = df.groupby("_submitted_by").apply(lambda x: x.isnull().sum().sum()).sort_values(ascending=False)
        st.bar_chart(missing_by_enumerator)
        st.write(missing_by_enumerator)

        # --- Duplicate Responses ---
        st.header("🔁 Duplicate Responses")
        duplicate_rows = df[df.duplicated(subset=["_submission_time", "_submitted_by"], keep=False)]

        if not duplicate_rows.empty:
            st.warning(f"⚠️ {len(duplicate_rows)} duplicate responses detected!")
            
            if st.button("👀 Show Duplicate Responses"):
                st.write(duplicate_rows[["_submission_time", "_submitted_by"]])
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
                    st.write(outliers[[col, "_submitted_by", "_submission_time"]])
                    all_outliers = pd.concat([all_outliers, outliers[[col, "_submitted_by", "_submission_time"]]])
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

    except Exception as e:
        st.error(f"❌ Error loading or processing the file: {e}")

else:
    st.warning("⚠️ Please upload a survey data file.")