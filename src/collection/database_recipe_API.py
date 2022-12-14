#!/usr/bin/env python
# coding: utf-8

# # Welcome to our Edamame API scraper :)

# Let's get ready for scraping!


# Import packages
import requests
import json
import pandas as pd
import time
import os


# Choose diet (for example paleo)
diet = 'paleo'


# Get acces API
url = "https://api.edamam.com/api/recipes/v2"

api_id = os.environ['APP_ID']
api_key = os.environ['APP_KEY'] 

headers = {api_id, api_key}

querystring = {"type": "public", "q": diet, "app_id": api_id, "app_key": api_key}

response = requests.get(url, headers={"Authorization": api_key}, params=querystring)


# Create Json for data
json_response = json.loads(response.text.replace('null', '"None"').replace('True','"True"').replace('False','"False"'))
recipe_request = json_response


# # Extract all raw data for this diet

# This code snippet loops through all pages of the API for this recipe and extracts all data.
# In order to create a dataset with recipes of multiple diets, you should change the diet in the 'choose diet' snippet and run this part multiple times.


# Go to next url
still_some_data = True
next_url=url


# Extract all data for this specific diet to look at formatting
count = 0 
full_df_list = []
while still_some_data:
    response = requests.get(next_url, headers={"Authorization": api_key}, params=querystring)
    try: 
      response.json()
    except:
      still_some_data = False
    try:
      recipe_request = response.json()
    except:
      print('headersize: ', print(len(next_url)))
      print(response.text) 
    time.sleep(6)
    
    try:
        print(f'Getting data for the '+ str(diet) + ' diet, currently at recipe number ' + str(recipe_request['to']))
    except json.decoder.JSONDecodeError:
        print("There was a problem accessing the equipment data.")
        
    if recipe_request['to']==recipe_request['count']:
        still_some_data=False
    if recipe_request['to']> recipe_request['count']:
        still_some_data = False 
        
    next_url = recipe_request['_links']['next']['href']

    for idx, recipe in enumerate(recipe_request['hits']):
        count+=1 
        full_df_list.append([recipe["recipe"]])
        
    f = open("../../data/"+diet+'_raw_data.json','a',encoding='utf-8')
    f.write(json.dumps(full_df_list))
    f.write('\n')
    f.close()


# # Extract macronutrients of recipes


# Go to next url
still_some_data = True
next_url=url


# Loop through pages and extract recipe name, cuisine type and macronutrients
count = 0 
df_list = []
while still_some_data:
    response = requests.get(next_url, headers={"Authorization": api_key}, params=querystring)
    try: 
      response.json()
    except:
      still_some_data = False
    try:
      recipe_request = response.json()
    except:
      print('headersize: ', print(len(next_url)))
      print(response.text) 
    time.sleep(6)
    
    try:
        print(f'Getting the dataset for the '+ str(diet) + ' diet ready, currently at recipe number ' + str(recipe_request['to']))
    except:
        print("There was a problem accessing the equipment data.")
        
    if recipe_request['to']==recipe_request['count']:
        still_some_data=False
    if recipe_request['to']> recipe_request['count']:
        still_some_data = False 
        
    next_url = recipe_request['_links']['next']['href']

    for idx, recipe in enumerate(recipe_request['hits']):
        count+=1
        
        time_converted = time.gmtime()
        datestamp = time.strftime("%Y-%m-%d", time_converted)
        timestamp = time.strftime("%H:%M:%S", time_converted)
        
        if (recipe["recipe"]["mealType"][0]== 'lunch/dinner'):
            df_list.append([str(diet),                 
            recipe["recipe"]["label"],                 
            recipe["recipe"]["cuisineType"][0],                 
            float(round(recipe['recipe']["totalNutrients"]['PROCNT']['quantity'], 2)),                 
            float(round(recipe['recipe']["totalNutrients"]['CHOCDF']['quantity'], 2)),                
            float(round(recipe['recipe']["totalNutrients"]['FAT']['quantity'], 2)),                 
            datestamp,                 
            timestamp])



# Create dataframe for single diet
df = pd.DataFrame(df_list, columns = ['Diet_type', 'Recipe_name', 'Cuisine_type', 'Protein(g)', 'Carbs(g)', 'Fat(g)', 'Extraction_day', 'Extraction_time'])


# Save data from single diet into CSV
df.to_csv("../../data/"+diet+".csv", index = False) 



# Or read pandas
pd.read_csv("../../data/"+diet+".csv") 


# # Merge the data of different diets

# If you wish to compare data of different diets, you can merge the CSV's. Just extend the list and the code snippet will form a data frame for all diets. For now, we made a dataframe for Paleo, Keto, Dash, Vegan and Mediterranean. 



# Merging the files. You can add more files in the list. 
# Type CSV names of the diets you extracted data from
df_all_diets = pd.concat(
    map(pd.read_csv, ['../../data/paleo.csv',
                      '../../data/vegan.csv',
                      '../../data/keto.csv',
                      '../../data/mediterranean.csv',
                      '../../data/dash.csv']), ignore_index=True)
print(df_all_diets)



# Save merged dataframe into CSV
df_all_diets.to_csv('../../data/All_Diets.csv', index = False)



# Or read pandas
pd.read_csv('../../data/All_Diets.csv')

