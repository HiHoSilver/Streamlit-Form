import streamlit as st
from streamlit_gsheets import GSheetsConnection
import pandas as pd

# App configuration and headings
st.set_page_config(
    page_title="Form Testing",
    page_icon="📝",
    layout="wide"
)
st.title("📝 Form Testing")
st.markdown("_Prototype v0.0.1_")

# Establish connnection with google cloud and fetch data
conn = st.connection("gsheets", type=GSheetsConnection)
existing_data = conn.read(worksheet="Sheet1", usecols=list(range(6)), ttl=5)
existing_data = existing_data.dropna(how="all")

# Define lists
BUSINESS_TYPES = [
    "Manufacturer",
    "Distributor",
    "Whoesaler",
    "Retailer",
    "Service Provider",
]
PRODUCTS = [
    "Electronics",
    "Apparel",
    "Groceries",
    "Software",
    "Other",
]

# Define form entry and logic
with st.form(key="form"):
    company_name = st.text_input(label="Company Name*")
    business_type = st.selectbox(label="Business Type*", options=BUSINESS_TYPES, index=None)
    products = st.multiselect("Products Offered", options=PRODUCTS)
    years_in_business = st.slider("Years in Business", 0, 50, 5)
    onboarding_date = st.date_input(label="Onboarding Date")
    additional_info = st.text_area("Additional Information")
    st.markdown("**Required Fields*")
    submit_button = st.form_submit_button(label="Submit Vendor Details")

if submit_button:
    # Validate form data
    if not company_name or not business_type:
        st.warning("⚠️ Please fill in all required fields")
        st.stop()
    elif existing_data["CompanyName"].str.contains(company_name).any():
        st.warning("⚠️ Company name already exists in system")
        st.stop()
    else:
        # Create new entry
        new_entry = pd.DataFrame(
            [
                {
                    "CompanyName": company_name,
                    "BusinessType": business_type,
                    "Products": ", ".join(products),
                    "YearsInBusiness": years_in_business,
                    "OnboardingDate": onboarding_date.strftime("%Y-%m-%d"),
                    "AdditionalInfo": additional_info,
                }
            ]
        )

        # Append new entry to existing data and push to google cloud
        updated_data = pd.concat([existing_data, new_entry], ignore_index=True)
        conn.update(worksheet="Sheet1", data=updated_data)

        st.write("✅ Form submitted successfully")