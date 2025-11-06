import streamlit as st
import requests
import pandas as pd
from snowflake.snowpark.functions import col

# Streamlit UI
st.title(":cup_with_straw: Customize Your Smoothie :cup_with_straw:")
st.write("Choose the fruit you want in your custom smoothie.")

# Name input
name_on_order = st.text_input("Name on Smoothie : ")
st.write("The name on your smoothie will be:", name_on_order)

# Snowflake connection
cnx = st.connection("snowflake")
session = cnx.session()

# Fruit dropdown
fruit_df = session.table("SMOOTHIES.PUBLIC.FRUIT_OPTIONS").select(col("FRUIT_NAME"))
ingredients_list = st.multiselect(
    "Choose up to 5 ingredients:",
    fruit_df.to_pandas()["FRUIT_NAME"].tolist(),
    max_selections=5
)

# Fetch nutrition data when fruits selected
if ingredients_list:
    st.subheader("Nutrition Information for Selected Fruits:")

    api_data = []
    for fruit in ingredients_list:
        url = f"https://my.smoothiefroot.com/api/fruit/{fruit.lower()}"
        response = requests.get(url)

        if response.status_code == 200:
            fruit_data = response.json()
            api_data.append(fruit_data)

    nutrition_df = pd.DataFrame(api_data)
    st.dataframe(nutrition_df, use_container_width=True)

    # Submit order button
    if st.button("Submit Order"):
        ingredients_string = ", ".join(ingredients_list)

        session.sql(
            """
            INSERT INTO SMOOTHIES.PUBLIC.ORDERS (INGREDIENTS, NAME_ON_ORDER)
            VALUES (%s, %s)
            """,
            (ingredients_string, name_on_order)
        ).collect()

        st.success("✅ Your smoothie has been ordered!")
