#geodiscovery.streamlit.app 

import streamlit as st
import pandas as pd
import requests
from geopy.geocoders import Nominatim
from math import radians, sin, cos, sqrt, atan2
from sklearn.preprocessing import StandardScaler
from streamlit_folium import folium_static
import folium

# ------------------------------
# Utility: Haversine Distance
# ------------------------------
def haversine(lat1, lon1, lat2, lon2):
    R = 6371  # Earth's radius in km
    d_lat = radians(lat2 - lat1)
    d_lon = radians(lon2 - lon1)
    a = sin(d_lat/2)**2 + cos(radians(lat1)) * cos(radians(lat2)) * sin(d_lon/2)**2
    return R * 2 * atan2(sqrt(a), sqrt(1 - a))

# ------------------------------
# Static Cost Data (Mocked)
# ------------------------------
mock_city_costs = {
    "":0, "Delhi": 40000, "Mumbai": 45000, "Bangalore": 42000, "Hyderabad": 37000,
    "Ahmedabad": 35000, "Chennai": 39000, "Kolkata": 36000, "Pune": 38000,
    "Jaipur": 32000, "Lucknow": 31000, "Kanpur": 30000, "Nagpur": 32000,
    "Indore": 31000, "Thane": 35000, "Bhopal": 30000, "Visakhapatnam": 33000,
    "Patna": 29000, "Vadodara": 31000, "Ghaziabad": 34000, "Ludhiana": 30000
}

# ------------------------------
# Streamlit UI Setup
# ------------------------------
st.set_page_config(page_title="Relocation Recommendation System", layout="centered")
st.title("🏙️ Relocation Recommendation System")

# Load Amenity Category Data
df = pd.read_csv("personalization-apis-movement-sdk-categories.csv")
df[['Super Category', 'Sub Category']] = df['Category Label'].str.split(' > ', n=1, expand=True)
df.dropna(subset=['Super Category', 'Sub Category'], inplace=True)

# City Input
major_cities = list(mock_city_costs.keys())
st.markdown("### 📍 Preferred City")
city = st.selectbox("Enter the city or region you'd like to move to:", major_cities)

# Income Details
st.markdown("### 💸 Income Details")
income_ranges = {
    "Low": {"< ₹15,000": 10000, "₹15,000 - ₹25,000": 20000, "₹25,000 - ₹35,000": 30000},
    "Medium": {"₹35,000 - ₹50,000": 45000, "₹50,000 - ₹75,000": 65000, "₹75,000 - ₹1,00,000": 90000},
    "High": {"₹1,00,000 - ₹1,50,000": 125000, "₹1,50,000 - ₹2,00,000": 175000, "> ₹2,00,000": 225000}
}
income_super = st.selectbox("Income Category", list(income_ranges.keys()))
income_range = st.selectbox("Specific Income Range", list(income_ranges[income_super].keys()))
numeric_income = income_ranges[income_super][income_range]

# Food Preferences
st.markdown("### 🍲 Food Preferences (Rate from 1 to 5)")
food_prefs = {
    "ethnic_food": st.slider("Ethnic food", 1, 5, 3),
    "fast_food": st.slider("Fast food", 1, 5, 3),
    "veg_preference": st.slider("Vegetables/day", 1, 5, 3),
    "fruit_preference": st.slider("Fruits/day", 1, 5, 3),
    "organic_food": st.slider("Organic food", 1, 5, 3),
    "home_cooked": st.slider("Home-cooked meals", 1, 5, 3),
    "eating_out": st.slider("Eating out", 1, 5, 3),
    "sweet_tooth": st.slider("Sweet preference", 1, 5, 3),
    "spicy_food": st.slider("Spicy preference", 1, 5, 3)
}

# Amenity Preferences
st.markdown("### 🏋️ Amenity Preferences")
super_categories = sorted(df['Super Category'].unique())
selected_supers = st.multiselect("Select Super Categories", super_categories)

selected_subs, selected_category_ids = [], []
if selected_supers:
    filtered_subs = df[df['Super Category'].isin(selected_supers)]['Sub Category'].unique()
    selected_subs = st.multiselect("Now select specific amenities:", sorted(filtered_subs))
    selected_category_ids = df[df['Sub Category'].isin(selected_subs)]['Category ID'].unique().tolist()
    if not selected_category_ids:
        st.warning("⚠️ Please select at least one amenity.")
else:
    st.info("ℹ️ Start by selecting one or more super categories.")

# ---------------------------------
# ✅ Submit Button Logic
# ---------------------------------
if st.button("Submit Preferences", key="submit_button_final"):
    geolocator = Nominatim(user_agent="relocation-system")
    loc = geolocator.geocode(city)
    if not loc:
        st.error("City not found.")
        st.stop()

    lat, lon = loc.latitude, loc.longitude
    cost = mock_city_costs.get(city, 30000)
    st.write(f"📍 Coordinates of {city}: ({lat}, {lon})")
    st.write(f"💰 Estimated Living Cost: ₹{cost:,.0f}")

    # Fetch Residential Areas Nearby
    fsq_api = "fsq3boHgIjG5qvz5vBtpvE8ns4qAo4lrrPFLBf+tlbn+dr8="
    headers = {"Accept": "application/json", "Authorization": fsq_api}
    res_url = "https://api.foursquare.com/v3/places/search"
    res_params = {
        "ll": f"{lat},{lon}",
        "radius": 5000,
        "categories": "4f2a25ac4b909258e854f55f,4e67e38e036454776db1fb3a,4d954b06a243a5684965b473",
        "limit": 20
    }
    res_response = requests.get(res_url, params=res_params, headers=headers).json()
    results = res_response.get("results", [])

    if not results:
        st.warning("No residential areas found.")
        st.stop()

    # Prepare Residential DataFrame
    df_locations = pd.DataFrame([{
        "Name": r.get("name", "N/A"),
        "Address": r.get("location", {}).get("formatted_address", "N/A"),
        "Latitude": r["geocodes"]["main"]["latitude"],
        "Longitude": r["geocodes"]["main"]["longitude"]
    } for r in results])

    # Calculate Average Distance to Amenities
    def avg_dist(lat, lon, categories):
        dists = []
        for cid in categories:
            resp = requests.get(res_url, params={"ll": f"{lat},{lon}", "radius": 5000, "categories": cid, "limit": 1}, headers=headers).json()
            r = resp.get("results", [])
            if r:
                g = r[0]["geocodes"]["main"]
                dists.append(haversine(lat, lon, g["latitude"], g["longitude"]))
        return sum(dists) / len(dists) if dists else 9999

    df_locations["Avg Amenity Distance"] = df_locations.apply(lambda x: avg_dist(x["Latitude"], x["Longitude"], selected_category_ids), axis=1)

    # Add Food & Income Preferences
    for pref, val in food_prefs.items():
        df_locations[pref] = val
    df_locations["Income"] = numeric_income``
    df_locations["Estimated City Cost"] = cost

    # Score Calculations
    df_locations["Proximity Score"] = 1 / df_locations["Avg Amenity Distance"]
    df_locations["Proximity Score"] /= df_locations["Proximity Score"].max()

    df_locations["Affordability Score"] = df_locations["Income"] / df_locations["Estimated City Cost"]
    df_locations["Affordability Score"] = df_locations["Affordability Score"].apply(lambda x: min(x, 1.5))

    food_cols = list(food_prefs.keys())
    df_locations["Food Score"] = df_locations[food_cols].sum(axis=1)
    df_locations["Food Score"] /= df_locations["Food Score"].max()

    # Final Score
    df_locations["Final Score"] = (
        0.5 * df_locations["Proximity Score"] +
        0.3 * df_locations["Affordability Score"] +
        0.2 * df_locations["Food Score"]
    )

    # Sort and limit top 10 recommendations
    df_locations = df_locations.sort_values("Final Score", ascending=False).head(10)

    # 🗺️ Map Visualization
    st.markdown("### 📌 Recommended Residential Clusters")
    map_center = [df_locations['Latitude'].mean(), df_locations['Longitude'].mean()]
    recommendation_map = folium.Map(location=map_center, zoom_start=13)

    for _, row in df_locations.iterrows():
        popup_text = f"""
        🏠 <b>{row['Name']}</b><br>
        📍 {row['Address']}<br>
        💸 Income: ₹{numeric_income:,}<br>
        📉 City Cost: ₹{int(cost):,}<br>
        ✅ Match Score: {round(row['Final Score'], 2)}
        """
        folium.Marker(
            location=[row['Latitude'], row['Longitude']],
            popup=folium.Popup(popup_text, max_width=300),
            icon=folium.Icon(color="blue", icon="home", prefix="fa")
        ).add_to(recommendation_map)

    folium_static(recommendation_map)

    # ⬇️ CSV Download Option
    st.markdown("### 📄 Download Recommendations")
    st.download_button(
        label="Download as CSV",
        data=df_locations.to_csv(index=False),
        file_name=f"{city}_recommendations.csv",
        mime="text/csv"
    )
