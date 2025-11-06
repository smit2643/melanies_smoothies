import streamlit as st
import requests
import pandas as pd
from snowflake.snowpark.functions import col

st.title(":cup_with_straw: Customize Your Smoothie :cup_with_straw:")
st.write("Choose the fruit you want in your custom smoothie.")

# Name input
name_on_order = st.text_input("Name on Smoothie : ")

# Snowflake connection
cnx = st.connection("snowflake")
session = cnx.session()

# Get fruit list from Snowflake
fruit_df = session.table("SMOOTHIES.PUBLIC.FRUIT_OPTIONS").select(col("FRUIT_NAME")).to_pandas()

ingredients_list = st.multiselect(
    "Choose up to 5 ingredients:",
    fruit_df["FRUIT_NAME"].tolist(),
    max_selections=5
)

# Fetch the full fruit list once (not per fruit)
@st.cache_data
def load_api_data():
    url = "https://my.smoothiefroot.com/api/fruit/all"
    return requests.get(url).json()

api_data = load_api_data()

# When fruits selected → filter API data
if ingredients_list:

    # Normalize names (API uses many variations)
    selected_info = []
    for fruit in ingredients_list:
        match = next((item for item in api_data if item["name"].lower().startswith(fruit.lower())), None)
        if match:
            selected_info.append(match)

    # Convert to DataFrame
    df = pd.json_normalize(selected_info)   # this FLATTENS the nutrition field

    st.subheader("🍉 Nutrition Details for Your Selected Fruits")
    st.dataframe(df, use_container_width=True)

    # Submit to Snowflake
    if st.button("Submit Order"):
        ingredients_string = ", ".join(ingredients_list)

        session.sql("""
            INSERT INTO SMOOTHIES.PUBLIC.ORDERS (INGREDIENTS, NAME_ON_ORDER)
            VALUES (%s, %s)
        """, (ingredients_string, name_on_order)).collect()

        st.success("✅ Your Smoothie is ordered!")
