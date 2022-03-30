#!/usr/bin/env python
# coding: utf-8

# In[1]:


import pandas as pd
import numpy as np
import matplotlib as plt
import re


# In[2]:


# price_df = pd.read_csv("netflix-price.csv") # This is a repeat data set
# subscription_df = pd.read_csv("netflix-subscription-fee.csv") # focus on the latter set. more useful data
title_df = pd.read_csv("netflix-titles.csv")


# ## Title Data
# 
# - Nearly all qualitative data
# - type, country, release year, rating, duration could be of use
# - year data ranges from 1925 to 2021, good spread
# - year data median is 2017. unsure of spread
# 
# This data looks like I can use it to figure out: (what type of content format people are watching in which countries, ratings, whether tastes have changed over the years)
# 
# 
# **Issues**
# 
# Will need to find a way to iterate through and design a table that holds shows by show_id and country to show distribution.
# 
# 1. Iterate through each row of title_df
# 2. Grab contents of "country" column
#     - Parse each string into an array
#     - Iterate through array to isolate specific items
#     - Add each item to a separate array?

# ### Defined Functions

# In[3]:


# Functions to create frequency table from given dataframe


# Function: dv_splitter()
# Objective: Take delimiter and DataFrame column and return array of all given values
# Useful for: Data points composed of lists
# Requirement: N/A
def dv_splitter(delimiter, column):
    send_array = []
    
    for row in column:
        dv_array = re.split(delimiter, str(row))
        
        for element in dv_array:
            send_array.append(element)
            
    return send_array


# Function: unique()
# Objective: Take input array and output unique values of array only
# Useful for: Returning unique values in a list
# Requirement: N/A
def unique(array):
    unique_array = []
    
    for i in array:
        if i not in unique_array:
            unique_array.append(i)
    
    return unique_array


# Function: freq_table()
# Objective: Take category label and data source to return a frequency table composed of category and frequency
# Useful for: Creating quick frequency table
# Requirement: unique() is defined
def freq_dict(category_label, data):
    send_dict = {}
    category_label_col = []
    frequency_col = []
    
    for i in unique(data):
        category_label_col.append(i)
        frequency_col.append(data.count(i))
        
    send_dict[category_label] = category_label_col
    send_dict["frequency"] = frequency_col
        
    return send_dict


# Function: make_freq_table()
# Objective: Take df column and generate a frequency table
# Useful for: Nominal data
# Requirement: dv_splitter(), freq_table() defined
def make_freq_table(dataframe, column, delimiter):
    # Iterate and split string lists to array
    temp_array = dv_splitter(delimiter, dataframe.loc[:, column])
    # Convert array to frequncy dictionary
    temp_freq_table = freq_dict(column, temp_array)
    # Convert dict to Pandas dataframe
    send_freq_table = pd.DataFrame(data = temp_freq_table, columns = [column, "frequency"])
    
    return send_freq_table

# Function: export_df()
# Objective: Take list of tuples (dataframe, filename) and export csv
# Useful for: Export batch of DFs without rewriting pd.to_csv code
# Requirement: N/A
def export_to_csv(send_list):
    df = 0
    filename = 1

    for i in send_list:
        i[df].to_csv(i[filename])
            


# # Cleaned Code
# *Run this to generate all of the data frames without going through Scratchpad*

# #### Prepping dataframe

# In[4]:


# Create copy dataframe
new_df = title_df.copy()


# In[5]:


# Fixing import issues with Louis C.K. films
issue_tags = ["74 min", "84 min", "66 min"]

for i in issue_tags:
    new_df.loc[new_df["rating"] == i, "duration"] = i
    new_df.loc[new_df["rating"] == i, "rating"] = np.nan


# In[6]:


# Combining NR and UR (both mean unrated)
new_df.loc[new_df["rating"] == "UR", "rating"] = "NR"


# In[7]:


# Combining TV-Y7-FV and TV-Y7 (fv is subset of y7)
new_df.loc[new_df["rating"] == "TV-Y7-FV", "rating"] = "TV-Y7"


# In[8]:


# Split season count from duration col

# Create mask
season_mask = new_df["duration"].str.contains("[Ss]eason", regex=True)

# Only return rows with Seasons in 
season_labels = new_df.loc[season_mask, "duration"]

# Move "season" to new col, remove "season" from duration col
new_df.loc[season_mask, "season"] = season_labels
new_df.loc[season_mask, "duration"] = np.nan

# Remove "min" tag from duration col
new_df.loc[:, "duration"] = new_df.loc[:, "duration"].replace(to_replace="\smin", value="", regex=True)

# Cast to numeric
new_df.loc[:, "duration"] = pd.to_numeric(arg=new_df.loc[:, "duration"], errors="ignore")


# In[9]:


# Cast date_added to date dtype
new_df.loc[:, "date_added"] = pd.to_datetime(arg=new_df.loc[:, "date_added"], errors="ignore")


# In[10]:


# Renaming columns for readability

# Change show_id to content_id{
new_df = new_df.rename(columns={"show_id": "content_id"})

# Change duration to runtime
new_df = new_df.rename(columns={"duration": "runtime (min)"})


# In[ ]:


# Check
new_df.head()


# #### Generate frequency tables

# In[11]:


# Generate frequency tables for nominal data

# country column
country_ft_df = make_freq_table(new_df, "country", ", ")
cmask = country_ft_df["country"].str.contains(",", regex=True)
country_ft_df.loc[cmask, "country"] = country_ft_df.loc[cmask, "country"].str.replace(pat=",", repl="", regex=True)

# rating column
rating_ft_df = make_freq_table(new_df, "rating", ", ")

# listed_in column
listedin_ft_df = make_freq_table(new_df, "listed_in", ", ")


# In[24]:


# Fixing found errors in country
country_ft_df.loc[cmask, "country"] = country_ft_df.loc[cmask, "country"].str.replace(pat=",", repl="", regex=True)


# In[27]:


# Listed-In needs separation of movies and tv-shows

# Movies
movie_genres = ["Action & Adventure", "Anime Features", "Children & Family Movies", "Classic Movies", "Comedies", "Cult Movies", "Documentaries", "Dramas", "Faith & Spirituality", "Horror Movies", "Independent Movies", "International Movies", "LGBTQ Movies", "Movies", "Music & Musicals", "Romantic Movies", "Sci-Fi & Fantasy", "Sports Movies", "Stand-Up Comedy", "Thrillers"]
movie_genres_ft = listedin_ft_df.loc[listedin_ft_df["listed_in"].isin(movie_genres)]

# TV Shows
tv_genres = ["Anime Series", "British TV Shows", "Classic & Cult TV", "Crime TV Shows", "Docuseries", "International TV Shows", "Kids' TV", "Korean TV Shows", "Reality TV", "Romantic TV Shows", "Science & Nature TV", "Spanish-Language TV Shows", "Stand-Up Comedy & Talk Shows", "Teen TV Shows", "TV Action & Adventure", "TV Comedies", "TV Dramas", "TV Horror", "TV Mysteries", "TV Sci-Fi & Fantasy", "TV Shows", "TV Thrillers"]
tv_genres_ft = listedin_ft_df.loc[listedin_ft_df["listed_in"].isin(tv_genres)]


# In[ ]:


# 5-num sum
# Used to calculate best central tendency for vizzes

percentiles = [0.25, 0.50, 0.75]

print(f"Min: {country_ft_df.loc[:,'frequency'].min()}")

for i in percentiles:
    print(f"{i}: {country_ft_df.loc[:,'frequency'].quantile(q=i)}")
    
print(f"Max: {country_ft_df.loc[:,'frequency'].max()}")


# #### Creating mirror dataframes without US influence

# In[38]:


# Creating non_us mask
nus_mask = new_df.loc[:, "country"].str.contains("United\sStates", na=False, regex=True)


# In[42]:


# New DF without US
nus_df = new_df.loc[~nus_mask, :].copy()


# In[48]:


# Creating frequency tables without US

# movie genres
nus_listedin = make_freq_table(nus_df, "listed_in", ",")

nus_mgenres = nus_listedin.loc[nus_listedin["listed_in"].isin(movie_genres)]
nus_tvgenres = nus_listedin.loc[nus_listedin["listed_in"].isin(tv_genres)]

# ratings
nus_ratings = make_freq_table(nus_df, "rating", ", ")


# #### Exporting DFs to CSV

# In[28]:


# Create export dataframe
export_df = new_df[["content_id", "type", "title", "country", "date_added", "rating", "runtime (min)", "season", "listed_in"]].copy()


# In[50]:


# Create export dict
send_list = [(export_df, "cl_netflix_dataframe.csv"),
            (country_ft_df, "cl_netflix_country.csv"),
            (movie_genres_ft, "cl_netflix_movie_genres.csv"),
            (tv_genres_ft, "cl_netflix_tv_genres.csv"),
            (listedin_ft_df, "cl_netflix_listedin.csv")]

nus_list = [(nus_mgenres, "cl_nus_mgenres.csv"),
           (nus_tvgenres, "cl_nus_tvgenres.csv"),
           (nus_ratings, "cl_nus_ratings.csv")]


# In[30]:


# Call export function
export_to_csv(send_list)


# In[51]:


# Export NUS files
export_to_csv(nus_list)


# # Scratchpad
# *Me throwing stuff together*

# In[ ]:


title_df.head()


# In[ ]:


title_df.columns


# In[ ]:


title_df.dtypes


# In[ ]:


print(f"Min Show ID {title_df['show_id'].min()}")
print(f"Max Show ID {title_df['show_id'].max()}")


# ### Country Col
# 
# **Issues**
# * Individuals countries are grouped together in a string
# 
# **Solutions**
# * Create columns for each country and count by 1 and 0
# * Create separate frequency table for values

# In[ ]:


title_df["country"].unique()


# In[ ]:


# Calling dv_splitter to convert df to array
master_country_array = dv_splitter(", ", title_df["country"])


# In[ ]:


# Separating out each unique country
unique_country_array = unique(master_country_array)


# In[ ]:


#Create freq table
country_freq_table = freq_dict("country", master_country_array)   


# In[ ]:


country_ft_df = pd.DataFrame(data = country_freq_table, columns = ["country", "frequency"])   #Convert to dataframe


# In[31]:


# Checking for incorrect separations in country
cmask = country_ft_df["country"].str.contains(",", regex=True)
country_ft_df.loc[cmask, :]


# In[ ]:


country_ft_df.head()


# ### Rating Data

# In[ ]:


title_df["rating"].unique()


# In[ ]:


title_df.loc[title_df["rating"] == "74 min"]


# In[ ]:


# Fixing issues with Louis C.K. film imports
issue_tags = ["74 min", "84 min", "66 min"]

for i in issue_tags:
    title_df.loc[title_df["rating"] == i, "duration"] = i
    title_df.loc[title_df["rating"] == i, "rating"] = np.nan


# In[ ]:


# Check
title_df.loc[title_df["director"] == "Louis C.K."]


# In[ ]:


# Convert from original DF to 
rating_array_raw = dv_splitter(", ", title_df["rating"])
unique_rating_array = unique(rating_array_raw)
rating_frequency_table = freq_dict("rating", rating_array_raw)

rating_ft_df = pd.DataFrame(data = rating_frequency_table, columns = ["rating", "frequency"]) 


# In[19]:


# Checking for incorrect separations in ratings 
rmask = rating_ft_df["rating"].str.contains(",", regex=True)
rating_ft_df.loc[rmask, :]

# No errors found


# In[ ]:


rating_ft_df.head()


# ### Listed In

# In[ ]:


title_df["listed_in"].unique() # Needs frequency table


# In[ ]:


# Convert from original DF to 
listedin_array_raw = dv_splitter(", ", title_df["listed_in"])
listedin_array_unique = unique(listedin_array_raw)
listedin_frequency_table = freq_dict("listedin", listedin_array_raw)

listedin_ft_df = pd.DataFrame(data = listedin_frequency_table, columns = ["listedin", "frequency"]) 


# In[20]:


# Checking for incorrect separations in listedin
lmask = listedin_ft_df["listed_in"].str.contains(",", regex=True)
listedin_ft_df.loc[lmask, :]

# No errors found


# In[ ]:


listedin_ft_df.head()


# In[ ]:


# Tests


# print(len(movie_genres_ft)
# print(len(tv_genres_ft))


# ### Duration
# 
# Nominal tag is intertwined with numeric data.
# 
# Solutions:
# - Split into "duration" and "seasons" column
# - Split into 2 DFs (one for TV shows, one for Movies)

# In[ ]:


# Scratchpad
new_df = title_df.copy()


# In[ ]:


# new_df.loc[:, "season"] = new_df.loc[new_df["duration"].str.contains("[Ss]eason", regex=True), "duration"]
# Issue with the right side of the code, looks like it's returning a copy of a slice from DF..


# In[ ]:


# Using mask as row indexer
mask = new_df["duration"].str.contains("[Ss]eason", regex=True)

# Season labels to grab data values for new column
season_labels = new_df.loc[mask, "duration"]


# In[ ]:


# new_df.loc[mask, "duration"]

# using mask as row indexer, and specifying duration as col indexer
# returns a list of data values


# In[ ]:


# Moving all data over and removing from duration col
new_df.loc[mask, "season"] = season_labels
new_df.loc[mask, "duration"] = None


# In[ ]:


# Removing "min" label in duration col
new_df.loc[:, "duration"] = new_df.loc[:, "duration"].replace(to_replace="\smin", value="", regex=True)

# Casting duration col to numeric dtype
pd.to_numeric(arg=new_df.loc[:, "duration"], errors="ignore")


# In[ ]:


# Cleaning up for production code

# Create copy dataframe
new_df = title_df.copy()

# Split season count from duration col

# Create mask
season_mask = new_df["duration"].str.contains("[Ss]eason", regex=True)
# Only return rows with Seasons in 
season_labels = new_df.loc[season_mask, "duration"]
# Move "season" to new col, remove "season" from duration col
new_df.loc[season_mask, "season"] = season_labels
new_df.loc[season_mask, "duration"] = np.nan
# Remove "min" tag from duration col
new_df.loc[:, "duration"] = new_df.loc[:, "duration"].replace(to_replace="\smin", value="", regex=True)
# Cast to numeric
pd.to_numeric(arg=new_df.loc[:, "duration"], errors="ignore")
# Change duration col name for readability
new_df = new_df.rename(columns={"duration": "duration (min)"})


# In[ ]:




