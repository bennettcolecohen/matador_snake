import streamlit as st
import pandas as pd
import re
import numpy as np

# Define your function
def my_function(a, b, c):
    return a + b + c


# Set locations
# Set sheet and name
sheet_id = "1M8HvH49Wc94_c7lD67QWc46RbFZU9sygIg93tlXapjQ"
sheet_name = 'locations'
url = f"https://docs.google.com/spreadsheets/d/{sheet_id}/gviz/tq?tqx=out:csv&sheet={sheet_name}"
locations = pd.read_csv(url, index_col=0)
locations_options = list(locations.index)

# Set sheet and name
sheet_id = "1M8HvH49Wc94_c7lD67QWc46RbFZU9sygIg93tlXapjQ"
sheet_name = 'practice_areas'
url = f"https://docs.google.com/spreadsheets/d/{sheet_id}/gviz/tq?tqx=out:csv&sheet={sheet_name}"
topics = pd.read_csv(url, index_col=0)
topics_options = list(topics.index)

# Type otions 
type_options = [
    'Co-Op', 
]

def run_snake(topic: str, location: str, recipient_type: str): 
    
    """
    Runs the snake to generate a set of 5 recipients
    Params:
        - topic (str): the practice area / topic 
        - location (str): the city, state or state
        - recipient_type (str): Co-Op or Web-Property
    """
    
    # Set sheet and name
    sheet_id = "1M8HvH49Wc94_c7lD67QWc46RbFZU9sygIg93tlXapjQ"
    sheet_name = 'candidates'
    url = f"https://docs.google.com/spreadsheets/d/{sheet_id}/gviz/tq?tqx=out:csv&sheet={sheet_name}"
    df = pd.read_csv(url)
    candidates = df.drop([col for col in list(df) if 'Unnamed' in col.strip()], axis = 1)
    candidates.columns = ['url', 'location', 'recipient_type', 'start_date', 'topics', 'notes']
    
    # Clean
    candidates = candidates[~candidates['topics'].isna()]
    
    # Set conditions 
    c1 = candidates['recipient_type'] == recipient_type
    c2 = candidates['topics'].str.contains(topic)
    
    # Apply filters
    filtered_df = candidates[(c1) & (c2)]
        
    
    # Location is a bit more difficult to check 
    filtered_df['location_match'] = filtered_df['location'].apply(lambda x: check_location(location, x))
    
    # Finally filter
    output = filtered_df[filtered_df['location_match'] == False]
    
    # If len(ouput) == -> return 'NO MATCHES FOUND'
    if len(output) == 0: 
        return 'NO MATCHES FOUND'
    
    
    # load in the table of backlinks
    sheet_id = "1M8HvH49Wc94_c7lD67QWc46RbFZU9sygIg93tlXapjQ"
    sheet_name = 'backlinks'
    url = f"https://docs.google.com/spreadsheets/d/{sheet_id}/gviz/tq?tqx=out:csv&sheet={sheet_name}"
    df = pd.read_csv(url)
    
    # Join the candidates to backlinks
    merged_df = output.merge(df, left_on = 'url', right_on = 'source').reset_index(drop = True)
    
    
    # Format the date properly 
    merged_df['complete'].apply(lambda x: extract_date(x)).astype(str)
    merged_df['complete'] = merged_df['complete'].fillna(False)
    merged_df = merged_df[merged_df['complete'] != False]
    merged_df = merged_df[merged_df['complete'] != np.nan]
    merged_df = merged_df[merged_df['complete'] != 'x']
    
    

    
    
    # Group
    res = merged_df.groupby('source').agg({
    'url': 'count',
    'complete': 'max',
})
    
    a = res.sort_values('complete', ascending = False)
    
    a = a[~a['complete'].str.contains('a')]
    a = a[~a['complete'].str.contains('e')]
    a['most_recent'] = pd.to_datetime(a['complete'])
    a = a.sort_values('most_recent', ascending = True).drop('complete', axis = 1).head(5)
    
    return a

def extract_date(date_str):
    # Check if the input is a string; if not, return None
    if not isinstance(date_str, str):
        return False
    
    # Handle cases like "x" explicitly
    if date_str.strip().lower() == 'x':
        return False
    
    # Search for date-like patterns within the string
    match = re.search(r"(0?[1-9]|1[0-2])/(0?[1-9]|[12][0-9]|3[01])/(\d{2}|\d{4})", date_str)
    
    if match:
        month, day, year = match.groups()
        
        # Zero-pad month and day
        month = month.zfill(2)
        day = day.zfill(2)
        
        # If year is two digits, assume 20XX; otherwise, use as is
        if len(year) == 2:
            year = "20" + year
        
        formatted_date = f"{month}/{day}/{year}"
        
        # Check if formatted_date is a 10-character MM/DD/YYYY string
        if len(formatted_date) == 10:
            return formatted_date
        else:
            return False
    else:
        return False


def check_city_state_format(s):
    pattern = r"^[a-zA-Z\s]+,\s*[A-Z]{2}$"
    return bool(re.match(pattern, s))

def check_location(location, target): 
    
    """
    Checks if there is a lcoation match based on the input and targets
    """
    
    # Simple check to see if it is in there
    if location.lower().strip() in target.lower().strip():
        return True
    
    # If input is of form City, State -> get secondary forms
    state_abbreviations = {
        "AL": "Alabama",
        "AK": "Alaska",
        "AZ": "Arizona",
        "AR": "Arkansas",
        "CA": "California",
        "CO": "Colorado",
        "CT": "Connecticut",
        "DE": "Delaware",
        "FL": "Florida",
        "GA": "Georgia",
        "HI": "Hawaii",
        "ID": "Idaho",
        "IL": "Illinois",
        "IN": "Indiana",
        "IA": "Iowa",
        "KS": "Kansas",
        "KY": "Kentucky",
        "LA": "Louisiana",
        "ME": "Maine",
        "MD": "Maryland",
        "MA": "Massachusetts",
        "MI": "Michigan",
        "MN": "Minnesota",
        "MS": "Mississippi",
        "MO": "Missouri",
        "MT": "Montana",
        "NE": "Nebraska",
        "NV": "Nevada",
        "NH": "New Hampshire",
        "NJ": "New Jersey",
        "NM": "New Mexico",
        "NY": "New York",
        "NC": "North Carolina",
        "ND": "North Dakota",
        "OH": "Ohio",
        "OK": "Oklahoma",
        "OR": "Oregon",
        "PA": "Pennsylvania",
        "RI": "Rhode Island",
        "SC": "South Carolina",
        "SD": "South Dakota",
        "TN": "Tennessee",
        "TX": "Texas",
        "UT": "Utah",
        "VT": "Vermont",
        "VA": "Virginia",
        "WA": "Washington",
        "WV": "West Virginia",
        "WI": "Wisconsin",
        "WY": "Wyoming",
        "DC": "District of Columbia",
        # U.S. Territories
        "National": "National",
        "D.C.": "District of Columbia",
    }
    
    # Check citry state format
    is_city_state = check_city_state_format(location)
    
    # If it is in city, state format -> get the proper state name 
    if is_city_state:
        abbrv = location.strip()[-2:].upper()
        state_name = state_abbreviations.get(abbrv)
        
        if state_name: 
            if state_name.lower().strip() in target.lower().strip():
                return True
            
    return False



# Create UI elements for input
st.title("Matador Snake")
topic = st.selectbox("Topic", topics_options, 0)
location = st.selectbox("Location", locations_options, 0)



# Create a button to run the function
if st.button("Run Function"):
    result = run_snake(topic, location, 'Co-Op')
    st.write("The result is:")
    st.dataframe(result)
