import streamlit as st
import pprint
import google.generativeai as palm
import os
from ics import Calendar, Event
from datetime import datetime, timedelta
import json

palm.configure(api_key=('AIzaSyDt0b1VBJqtVI_O18AtFDhyboTS8gOg_4g'))
models = [m for m in palm.list_models() if 'generateText' in m.supported_generation_methods]
model = models[0].name
print(model)

# Streamlit app title and user input
st.title("Travel Itinerary Generator")

city = st.text_input("Enter the location you're visiting :")
start_date = st.date_input("Select the start date for your trip:", value=datetime.today())

# Set the maximum end date to 30 days after the start date
max_end_date = start_date + timedelta(days=30)

# User selects the end date of the trip
end_date = st.date_input("Select the end date for your trip:",
                         value=start_date + timedelta(days=1),  # Default to the next day
                         min_value=start_date,
                         max_value=max_end_date)

# Calculate the number of days between start_date and end_date
days = (end_date - start_date+timedelta(days=1)).days
# days = st.number_input("Enter the number of days for your trip:", min_value=1, max_value=30)

# User preferences checkboxes
st.write('\nChoose the type of attractions you prefer: ')
restaurant = st.checkbox("Restaurants")
museums = st.checkbox("Museums")
outdoor = st.checkbox("Outdoor Activities")
temple = st.checkbox("Temples")
kids_friendly = st.checkbox("Good for Kids")
nature = st.checkbox("Nature")

# Transport mode options
transport_modes = st.multiselect(
    "Please Select your preferred modes of transport:",
    ["Bicycle", "Car", "Bus"]
)

# Generate itinerary button
if st.button("Generate Itinerary"):
    # Create a prompt based on user input

    prompt = f"You are an travel expert. Give me an itenary , (give importance to),within a circular area of 20 kilometers in {city}, for {days} days, assume each day starting at 10am and ending at 8pm having a buffer. I like to"
    if restaurant:
        prompt += " know names of famous restaurants(only name),"
    if museums:
        prompt += " visit famous museums, libraries and art related places(only name),"
    if outdoor:
        prompt += " visit famous places where I can do outdoor activities(only name),"
    if temple:
        prompt += " visit famous temples(only name),"
    if kids_friendly:
        prompt += " find famous places suitable for kids(only name),"
    if nature:
        prompt += " discover famous beaches, mountains, waterfalls, caves or sand deserts(only name),"



    # prompt += ". Return the response in a properly formatted json string which can be imported in code using json.loads function in python."
    prompt += r"""Limit the length of output json string to 2000 characters. Generate a structured JSON representation for the travel itinerary.

       {
  "days": [
    {
      "day": 1,
      "activities": [
        {
          "title": "Name of place 1",
          "description": "Description of Place 1",
          "link": "https://example.com/activity1",
          "start_time": "10:00 AM",
          "end_time": "12:00 PM",
          "location": "https://maps.google.com/?q=location1in{city}"
        },
        {
          "title": "Name of place 2",
          "description": "Description of Place 2",
          "link": "https://example.com/activity2",
          "start_time": "02:00 PM",
          "end_time": "04:00 PM",
          "location": "https://maps.google.com/?q=location2in{city}"
        },
        ....
      ]
    },
    {
      "day": 2,
      "activities": [
        {
          "title": "Another Name of Place 1",
          "description": "Description of Another Name of Place 1",
          "start_time": "09:30 AM",
          "end_time": "11:30 AM",
          "location": "https://maps.google.com/?q=location1in{city}"
        },
        {
          "title": "Another Name of Place 2",
          "description": "Description of Another Name of Place 2 ",
          "start_time": "01:00 PM",
          "end_time": "03:00 PM",
          "location": "https://maps.google.com/?q=location2in{city}"
        },
        ....
      ]
    }
  ]
}

        Ensure that each day has a 'day' field and a list of 'activities' with 'title', 'description', 'start_time', 'end_time', and 'location' fields. Keep descriptions concise.
"""

    import folium
    from streamlit_folium import folium_static
    from geopy.geocoders import Nominatim




    # Call the OpenAI API
    completion = palm.generate_text(
        model=model,
        prompt=prompt,
        temperature=0,
        # The maximum length of the response
        max_output_tokens=3000,
    )

    # Extract and display the generated itinerary
    itinerary = completion.result.strip()
    itinerary = itinerary[7:-3]
    # Display the itinerary from the JSON response
    print(type(itinerary))
    print(len(itinerary))
    print(itinerary)

   # f = open(itinerary)
    itinerary_json = json.loads(itinerary)
    print(itinerary_json)
    # Initialize the map centered at a location
    import requests

    api_key = 'e409fa3d804c41ae8e530f8e307ed513'
    address = city
    url = f'https://api.geoapify.com/v1/geocode/search?text={address}&apiKey={api_key}'
    geocode_response = requests.get(url).json()
    location = geocode_response['features'][0]['geometry']['coordinates']
    lng, lat = location[0], location[1]

    #geolocator = Nominatim(user_agent="geoapiExercises")
    #location = geolocator.geocode(hyderabad)






    for day in itinerary_json["days"]:
        st.header(f"Day {day['day']}")
        for activity in day["activities"]:
            st.subheader(activity["title"])
            st.write(f"Description: {activity['description']}")
            st.write(f"Location: {activity['location']}")
            st.write(f"Time: {activity['start_time']} - {activity['end_time']}")
            st.write(f"Link: {activity['link']}")
            st.write("\n")

        m=folium.Map()
        m = folium.Map(location=[lat, lng])

        # Create an empty list named 'places'
        places = []

        # Iterate over the days and activities to get the 'title'
        for days in day:
            for activity in day['activities']:
                places.append(activity['title']+" "+city)

        # Add markers for the places
        for place in places:
            address = place + " " + city
            url = f'https://api.geoapify.com/v1/geocode/search?text={address}&apiKey={api_key}'
            geocode_response = requests.get(url).json()
            if geocode_response['features']:
              location = geocode_response['features'][0]['geometry']['coordinates']
              lng1, lat1 = location[0], location[1]
            # location = geolocator.geocode(place)
              folium.Marker([lat1, lng1], popup=address, icon=folium.Icon(color='red')).add_to(m)

        # Connect the places with lines (assuming travel by road)
        # folium.PolyLine(locations=[(geolocator.geocode(place).latitude, geolocator.geocode(place).longitude) for place in
        #                          activity["title"]], color='blue').add_to(m)

        # Initialize an empty list to store the coordinates
        coordinates = []

        # Get the coordinates for each place
        for place in places:
            address = place + " " + city
            url = f'https://api.geoapify.com/v1/geocode/search?text={address}&apiKey={api_key}'
            geocode_response = requests.get(url).json()
            if geocode_response['features']:
              location = geocode_response['features'][0]['geometry']['coordinates']
              lng2, lat2 = location[0], location[1]
              coordinates.append((lat2, lng2))  # Append the coordinates to the list

        # Add the PolyLine to the map
        folium.PolyLine(locations=coordinates[:-1], color='black').add_to(m)

        # sw=coordinates.min().values.tolist()
        # ne=coordinates.max().values.tolist()
        m.fit_bounds(coordinates)

        st.write('\n')
        st.write('Here is a map summarising your route:')
        # Display the map in Streamlit
        folium_static(m)

    # Set the start date to tomorrow
    start_date = datetime.now() + timedelta(days=1)


    def get_download_link(content, filename):
        """Generates a download link for the given content."""
        b64_content = content.encode().decode("utf-8")
        href = f'<a href="data:text/calendar;charset=utf-8,{b64_content}" download="{filename}">Download {filename}</a>'
        return href
        print("export")


    cal = Calendar()
    start_date = datetime.now() + timedelta(days=10)

    for day, activities in enumerate(itinerary_json.get("days", []), start=1):
        for activity in activities.get("activities", []):
            event = Event()
            event.name = activity.get("title", "")
            event.description = activity.get("description", "")
            event.location = activity.get("location", "")
            print(event.location)
            print("start_date:", start_date)
            print("end_time:",
                  start_date + timedelta(days=day - 1, hours=int(activity.get("end_time", "00:00").split(":")[0]),
                                         minutes=int(activity.get("end_time", "00:00").split(":")[1][:2])))
            event.begin = start_date + timedelta(days=day - 1,
                                                 hours=int(activity.get("start_time", "00:00").split(":")[0]),
                                                 minutes=int(activity.get("start_time", "00:00").split(":")[1][:2]))
            event.end = start_date + timedelta(days=day, hours=int(activity.get("end_time", "00:00").split(":")[0]),
                                               minutes=int(activity.get("end_time", "00:00").split(":")[1][:2]))
            cal.events.add(event)


    cal_content = str(cal)  # Use str to obtain the serialized iCalendar content

    # Create a download link
    st.success("Itinerary ready to export!")
    st.markdown(get_download_link(cal_content, "Itinerary.ics"), unsafe_allow_html=True)
