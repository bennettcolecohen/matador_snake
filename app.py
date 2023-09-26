# Imports 
import pandas as pd
import re 
import numpy as np
import streamlit as st

def load_candidates(): 
    sheet_id = "1M8HvH49Wc94_c7lD67QWc46RbFZU9sygIg93tlXapjQ"
    sheet_name = 'candidates'
    url = f"https://docs.google.com/spreadsheets/d/{sheet_id}/gviz/tq?tqx=out:csv&sheet={sheet_name}"
    df = pd.read_csv(url)
    candidates = df.drop([col for col in list(df) if 'Unnamed' in col.strip()], axis = 1)
    candidates.columns = ['url', 'location', 'recipient_type', 'start_date', 'topics', 'notes']
    return candidates

def load_topics():
    sheet_id = "1M8HvH49Wc94_c7lD67QWc46RbFZU9sygIg93tlXapjQ"
    sheet_name = 'practice_areas'
    url = f"https://docs.google.com/spreadsheets/d/{sheet_id}/gviz/tq?tqx=out:csv&sheet={sheet_name}"
    topics = pd.read_csv(url, index_col=0)
    topics_options = list(topics.index)
    return topics_options

def load_locations(): 
    sheet_id = "1M8HvH49Wc94_c7lD67QWc46RbFZU9sygIg93tlXapjQ"
    sheet_name = 'locations'
    url = f"https://docs.google.com/spreadsheets/d/{sheet_id}/gviz/tq?tqx=out:csv&sheet={sheet_name}"
    locations = pd.read_csv(url, index_col=0)
    locations_options = list(locations.index)
    return locations_options

def load_backlinks():
    sheet_id = "1M8HvH49Wc94_c7lD67QWc46RbFZU9sygIg93tlXapjQ"
    sheet_name = 'backlinks'
    url = f"https://docs.google.com/spreadsheets/d/{sheet_id}/gviz/tq?tqx=out:csv&sheet={sheet_name}"
    df = pd.read_csv(url)
    return df

candidates = load_candidates()
candidates_options = candidates['url'].to_list()    
topic_options = load_topics()
locations = load_locations()
backlinks = load_backlinks()


def run_snake(url, state, topics): 
    
    # Convert web properties state to string
    candidates['location'] = candidates['location'].fillna('NAN')

    # Make sure not in the same state
    df = candidates[~candidates['location'].str.contains(state)].reset_index(drop = True)

    # Must match one of the topics
    df = df[df['topics'].apply(lambda x: any(topic in x for topic in topics))].reset_index(drop = True)

    # Get all backlinks (source and recipient) for the url
    exchanged_rows = backlinks[(backlinks['source'] == url) | (backlinks['recipient'] == url)]
    exchanges = exchanged_rows['source'].to_list() + exchanged_rows['recipient'].to_list()
    this_firm_links = [item for item in list(set(exchanges)) if item != url]


    # Remove all ones that have been here
    available_urls = df[df['url'].apply(lambda x: x not in this_firm_links)].reset_index(drop = True)


    # If none
    if len(available_urls) == 0: 
        last_5 = exchanged_rows.sort_values('complete', ascending = False).reset_index(drop = True).iloc[:5]
        return last_5

    return available_urls


# Create UI elements for input
st.title("Matador Snake")
url = st.selectbox("URL", candidates_options, 0)
topics = st.multiselect("Topic", topic_options)
state = st.selectbox("Location", locations, 0)



# Create a button to run the function
if st.button("Run Function"):
    result = run_snake(url, state, topics)
    st.write("The result is:")
    st.dataframe(result)
