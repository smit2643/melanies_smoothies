import streamlit as st
import requests
from snowflake.snowpark.functions import col

# Title
st.title(":cup_with_straw: Customize Your Smoothie :cup_with_straw:")
st.write("Choose the fruit you want in your custom Smoothie")

# Name input
name_on_order = st.text_input("Name on Smoothie : ")
st.write("The name on your smoothie will be:", name_on_order)

# Connect to Snowflake
cnx = st.connection("snowflake")
session = cnx.session()

# Load fruit options (FRUIT_NAME + SEARCH_ON)
my_dataframe = session.table("smoothies.public.fruit_options").select(col("FRUIT_NAME"), col("SEARCH_ON"))
pd_df = my_dataframe.to_pandas()   # convert to pandas for UI

# Multi-select fruit list (correct input source)
ingredients_list = st.multiselect(
    "Choose up to 5 ingredients:",
    pd_df["FRUIT_NAME"].tolist(),
    max_selections=5
)

# When user selects fruits
if ingredients_list:
    
    # Convert list → space-separated string for DB insert
    ingredients_string = " ".join(ingredients_list)

    # Display nutrition for each selected fruit
    for fruit_chosen in ingredients_list:
        search_on = pd_df.loc[pd_df["FRUIT_NAME"] == fruit_chosen, "SEARCH_ON"].iloc[0]

        st.subheader(f"{fruit_chosen} Nutrition Information")
        smoothiefroot_response = requests.get(f"https://my.smoothiefroot.com/api/fruit/{search_on}")
        st.dataframe(smoothiefroot_response.json(), use_container_width=True)

    # Insert order into database
    submit_button = st.button("Submit Order")

    if submit_button:
        session.sql(
            f"""
            INSERT INTO smoothies.public.orders(ingredients, name_on_order)
            VALUES ('{ingredients_string}', '{name_on_order}')
            """
        ).collect()

        st.success("Your Smoothie is ordered! ✅")
