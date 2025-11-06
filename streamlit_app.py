import streamlit as st
from snowflake.snowpark.functions import col
import requests
import pandas as pd

st.title(":cup_with_straw: Customize Your Smoothie! :cup_with_straw:")
st.write("Choose the fruits you want in your custom Smoothie!")

name_on_order = st.text_input("Name on Smoothie:")
st.write("The name on smoothie will be:", name_on_order)

# Connect to Snowflake
cnx = st.connection("snowflake")
session = cnx.session()

# ✅ SELECT ONLY THE COLUMNS THAT EXIST
my_dataframe = session.table("smoothies.public.fruit_options").select(col('FRUIT_NAME'))

# Convert to pandas
pd_df = my_dataframe.to_pandas()

# Multi-select list
ingredients_list = st.multiselect(
    "Choose up to 5 ingredients:",
    pd_df['FRUIT_NAME'].tolist(),
    max_selections=5
)

if ingredients_list:
    ingredients_string = ' '.join(ingredients_list)

    for fruit_chosen in ingredients_list:
        search_name = fruit_chosen.lower()

        st.subheader(f"{fruit_chosen} Nutrition Information")

        fruityvice_response = requests.get(f"https://fruityvice.com/api/fruit/{search_name}")

        if fruityvice_response.status_code == 200:
            fv_data = fruityvice_response.json()
            st.dataframe(fv_data, use_container_width=True)
        else:
            st.warning(f"⚠ No nutrition data found for {fruit_chosen}")

    # Insert order into Snowflake
    submit = st.button("Submit Order")

    if submit:
        insert_sql = f"""
        INSERT INTO smoothies.public.orders(ingredients, name_on_order)
        VALUES ('{ingredients_string}', '{name_on_order}')
        """
        session.sql(insert_sql).collect()
        st.success(f"✅ Your Smoothie is ordered, {name_on_order}!")
