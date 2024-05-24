# Import python packages
import streamlit as st
import requests
import pandas as pd
from snowflake.snowpark.functions import col


# Write directly to the app
st.title(":cup_with_straw: Customise Your Smoothie! :cup_with_straw:")
st.write(
    """Choose fruits that you would like in you custom Smoothie!!
    """)
#create a title for the smoothies

name_on_order = st.text_input("Name on Smoothie:")
st.write("The name on your smoothie will be:", name_on_order)

#st.write("You selected:", option)

#choose just the fruits column of the table
cnx = st.connection("snowflake")
session = cnx.session()
my_dataframe = session.table("smoothies.public.fruit_options").select(col('FRUIT_NAME'), col('SEARCH_ON')) #select which columns are shown
#st.dataframe(data=my_dataframe, use_container_width=True)
#st.stop()

#convert snowpark dataframe to pandas Dataframe to use LOC function
pd_df = my_dataframe.to_pandas()
#st.dataframe(pd_df)
#st.stop()


#print the instructions
ingredients_list = st.multiselect(
    'Choose up to 5 ingredients:',
    my_dataframe, 
    max_selections = 5
)

#for loop, if the fruit is clicked, then print it underneath
if ingredients_list:
    ingredients_string = ''

    for fruit_chosen in ingredients_list:
        ingredients_string += fruit_chosen + ' '     #adds the chosen fruit to the ingredients_string list
        
        search_on=pd_df.loc[pd_df['FRUIT_NAME'] == fruit_chosen, 'SEARCH_ON'].iloc[0]
        #st.write('The search value for ', fruit_chosen,' is ', search_on, '.')
        
        st.subheader(fruit_chosen + ' Nutrition Information')
        fruityvice_response = requests.get("https://fruityvice.com/api/fruit/" + search_on)
        fv_df = st.dataframe(data = fruityvice_response.json(),use_container_width= True)

    my_insert_stmt = """ Insert into smoothies.public.orders(ingredients, name_on_order)
                            values('"""+ ingredients_string + """', '""" + name_on_order + """')"""
    st.write(my_insert_stmt)
    #st.stop()       #the streamlit STOP command is great for troubleshooting. Want to get SQL right before altering database
    
    time_to_insert = st.button('Submit Order')

    if time_to_insert:
        session.sql(my_insert_stmt).collect()

        st.success('Your Smoothie is ordered, ' + name_on_order + '!', icon="✅")
        
