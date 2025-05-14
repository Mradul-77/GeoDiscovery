import streamlit as st
import pandas as pd
import requests
from geopy.geocoders import Nominatim
from math import radians, sin, cos, sqrt, atan2
from sklearn.preprocessing import StandardScaler
from streamlit_folium import folium_static
import folium

# --------------------------
# Utility: Haversine formula
# --------------------------
def haversine(lat1, lon1, lat2, lon2):
    R = 6371  # km
    d_lat = radians(lat2 - lat1)
    d_lon = radians(lon2 - lon1)
    a = sin(d_lat/2)**2 + cos(radians(lat1)) * cos(radians(lat2)) * sin(d_lon/2)**2
    return R * 2 * atan2(sqrt(a), sqrt(1 - a))

# ----------------------------
# City-wise mocked cost lookup
# ----------------------------
mock_city_costs = {
    "Delhi": 40000,
    "Mumbai": 45000,
    "Bangalore": 42000,
    "Hyderabad": 37000,
    "Ahmedabad": 35000,
    "Chennai": 39000,
    "Kolkata": 36000,
    "Pune": 38000,
    "Jaipur": 32000,
    "Lucknow": 31000,
    "Kanpur": 30000,
    "Nagpur": 32000,
    "Indore": 31000,
    "Thane": 35000,
    "Bhopal": 30000,
    "Visakhapatnam": 33000,
    "Patna": 29000,
    "Vadodara": 31000,
    "Ghaziabad": 34000,
    "Ludhiana": 30000
}

# --------------------------
# UI Setup
# --------------------------
st.set_page_config(page_title="Relocation Recommendation System", layout="centered")
st.title("🏙️ Relocation Recommendation System")

# Load Foursquare categories
df = pd.read_csv("personalization-apis-movement-sdk-categories.csv")
df[['Super Category', 'Sub Category']] = df['Category Label'].str.split(' > ', n=1, expand=True)
df.dropna(subset=['Super Category', 'Sub Category'], inplace=True)

# Cities
major_cities = ["", "Mumbai", "Delhi", "Bangalore", "Hyderabad", "Ahmedabad", "Chennai", "Kolkata", "Pune", "Jaipur", "Lucknow", "Kanpur", "Nagpur", "Indore", "Thane", "Bhopal", "Visakhapatnam", "Patna", "Vadodara", "Ghaziabad", "Ludhiana"]
city = st.selectbox("📍 Preferred City", major_cities)

# Income
income_ranges = {
    "Low": {
        "< ₹15,000": 10000,
        "₹15,000 - ₹25,000": 20000,
        "₹25,000 - ₹35,000": 30000
    },
    "Medium": {
        "₹35,000 - ₹50,000": 45000,
        "₹50,000 - ₹75,000": 65000,
        "₹75,000 - ₹1,00,000": 90000
    },
    "High": {
        "₹1,00,000 - ₹1,50,000": 125000,
        "₹1,50,000 - ₹2,00,000": 175000,
        "> ₹2,00,000": 225000
    }
}
income_super = st.selectbox("💸 Income Category", list(income_ranges.keys()))
income_range = st.selectbox("Specific Income Range", list(income_ranges[income_super].keys()))
numeric_income = income_ranges[income_super][income_range]

# Food
st.markdown("### 🍲 Food Preferences")
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
selected_supers = st.multiselect("Super Categories", super_categories)

selected_subs = []
selected_category_ids = []
if selected_supers:
    filtered_subs = df[df['Super Category'].isin(selected_supers)]['Sub Category'].unique()
    selected_subs = st.multiselect("Select specific amenities:", sorted(filtered_subs))
    selected_category_ids = df[df['Sub Category'].isin(selected_subs)]['Category ID'].unique().tolist()

# Submit Button
if st.button("Submit Preferences", key="submit_button"):
    geolocator = Nominatim(user_agent="relocation-system")
    loc = geolocator.geocode(city)
    if not loc:
        st.error("City not found.")
        st.stop()

    lat, lon = loc.latitude, loc.longitude
    cost = mock_city_costs.get(city, 30000)
    st.write(f"📍 Coordinates of {city}: ({lat}, {lon})")
    st.write(f"💰 Estimated Living Cost: ₹{cost:,.0f}")

    # Fetch Residential Areas
    fsq_api = "fsq3boHgIjG5qvz5vBtpvE8ns4qAo4lrrPFLBf+tlbn+dr8="
    headers = {"Accept": "application/json", "Authorization": fsq_api}
    res_url = "https://api.foursquare.com/v3/places/search"
    res_params = {
        "ll": f"{lat},{lon}",
        "radius": 5000,
        "categories": "4f2a25ac4b909258e854f55f,4e67e38e036454776db1fb3a,4d954b06a243a5684965b473",
        "limit": 15
    }
    res_response = requests.get(res_url, params=res_params, headers=headers).json()
    results = res_response.get("results", [])

    if not results:
        st.warning("No residential areas found.")
        st.stop()

    locations = []
    for i, r in enumerate(results):
        locations.append({
            "serial": i + 1,
            "name": r.get("name", "N/A"),
            "address": r.get("location", {}).get("formatted_address", "N/A"),
            "lat": r["geocodes"]["main"]["latitude"],
            "lon": r["geocodes"]["main"]["longitude"]
        })

    df_locations = pd.DataFrame(locations)

    # Calculate avg distance to amenities
    def average_distance(lat, lon, categories):
        distances = []
        for cid in categories:
            amenity_resp = requests.get(res_url, params={
                "ll": f"{lat},{lon}",
                "radius": 5000,
                "categories": cid,
                "limit": 1
            }, headers=headers).json()
            results = amenity_resp.get("results", [])
            if results:
                a = results[0]["geocodes"]["main"]
                dist = haversine(lat, lon, a["latitude"], a["longitude"])
                distances.append(dist)
        return sum(distances) / len(distances) if distances else 9999

    df_locations["avg_amenity_distance"] = df_locations.apply(
        lambda x: average_distance(x["lat"], x["lon"], selected_category_ids), axis=1
    )

    # Add preferences
    for pref, val in food_prefs.items():
        df_locations[pref] = val
    df_locations["income"] = numeric_income
    df_locations["estimated_cost"] = cost

    # Scoring
    df_locations["proximity_score"] = 1 / df_locations["avg_amenity_distance"]
    df_locations["proximity_score"] /= df_locations["proximity_score"].max()

    df_locations["affordability_score"] = df_locations["income"] / df_locations["estimated_cost"]
    df_locations["affordability_score"] = df_locations["affordability_score"].apply(lambda x: min(x, 1.5))

    food_cols = list(food_prefs.keys())
    df_locations["food_score"] = df_locations[food_cols].sum(axis=1)
    df_locations["food_score"] /= df_locations["food_score"].max()

    df_locations["final_score"] = (
        0.5 * df_locations["proximity_score"] +
        0.3 * df_locations["affordability_score"] +
        0.2 * df_locations["food_score"]
    )
    df_locations.sort_values("final_score", ascending=False, inplace=True)

    # ✅ 8. Visualize
    st.markdown("### 🗺️ Recommended Residential Clusters")
    map_center = [df_locations['lat'].mean(), df_locations['lon'].mean()]
    recommendation_map = folium.Map(location=map_center, zoom_start=13)

    for _, row in df_locations.iterrows():
        popup_text = f"""
        🏠 <b>{row['name']}</b><br>
        📍 {row['address']}<br>
        💸 Income: ₹{numeric_income:,}<br>
        📉 City Cost: ₹{int(cost):,}<br>
        ✅ Match Score: {round(row['final_score'], 2)}
        """
        folium.Marker(
            location=[row['lat'], row['lon']],
            popup=folium.Popup(popup_text, max_width=300),
            icon=folium.Icon(color="blue", icon="home", prefix="fa")
        ).add_to(recommendation_map)

    folium_static(recommendation_map)


    # # ✅ 1. Geocode the City
    # geolocator = Nominatim(user_agent="mradulgupta8306@example.com")
    # location = geolocator.geocode(city)

    # if not location:
    #     st.error("Could not fetch location. Please check the city name.")
    #     st.stop()

    # lat, lon = location.latitude, location.longitude
    # st.write(f"📍 Coordinates of {city}: ({lat}, {lon})")

    # # ✅ 2. Get estimated living cost from Numbeo
    
    # # ⚡ Use mock cost data
    # estimated_cost = mock_city_costs.get(city, 30000)
    # st.info(f"📊 Estimated Monthly Living Cost in {city.title()}: ₹{estimated_cost:,}")


    # # ✅ 3. Fetch residential locations nearby
    # api_key = "fsq3boHgIjG5qvz5vBtpvE8ns4qAo4lrrPFLBf+tlbn+dr8="
    # headers = {"Accept": "application/json", "Authorization": api_key}
    # res_url = "https://api.foursquare.com/v3/places/search"
    # res_params = {
    #     "ll": f"{lat},{lon}",
    #     "radius": 5000,
    #     "categories": "4f2a25ac4b909258e854f55f,4e67e38e036454776db1fb3a,4d954b06a243a5684965b473",
    #     "limit": 10
    # }
    # res_response = requests.get(res_url, params=res_params, headers=headers).json()

    # residential_df = pd.DataFrame([{
    #     "serial_number": i + 1,
    #     "latitude": r['geocodes']['main']['latitude'],
    #     "longitude": r['geocodes']['main']['longitude'],
    #     "name": r.get("name", "Unnamed"),
    #     "address": r.get("location", {}).get("formatted_address", "Unknown")
    # } for i, r in enumerate(res_response.get("results", []))])

    # if residential_df.empty:
    #     st.warning("No residential locations found for the entered city.")
    #     st.stop()

    # # ✅ 4. Fetch amenity data near each location
    # for category_id in selected_category_ids:
    #     counts = []
    #     for _, row in residential_df.iterrows():
    #         params = {
    #             "ll": f"{row['latitude']},{row['longitude']}",
    #             "radius": 500,
    #             "categories": category_id,
    #             "limit": 50
    #         }
    #         response = requests.get(res_url, headers=headers, params=params)
    #         result = response.json().get("results", [])
    #         counts.append(len(result))
    #     residential_df[f"Amenities_{category_id}"] = counts

    # # ✅ 5. Add user profile and income
    # residential_df["ethnic_food"] = ethnic_food
    # residential_df["fast_food"] = fast_food
    # residential_df["veg_preference"] = veg_preference
    # residential_df["fruit_preference"] = fruit_preference
    # residential_df["organic_food"] = organic_food
    # residential_df["home_cooked"] = home_cooked
    # residential_df["eating_out"] = eating_out
    # residential_df["sweet_tooth"] = sweet_tooth
    # residential_df["spicy_food"] = spicy_food
    # residential_df["income"] = numeric_income

    # # ✅ 6. Score based on affordability
    # residential_df["affordability_score"] = numeric_income / estimated_cost
    # residential_df["affordability_score"] = residential_df["affordability_score"].apply(lambda x: min(x, 1.5))

    # # ✅ 7. Calculate final score
    # amenity_columns = [col for col in residential_df.columns if col.startswith("Amenities_")]
    # residential_df["amenity_score"] = residential_df[amenity_columns].sum(axis=1)
    # residential_df["final_score"] = (
    #     0.5 * residential_df["amenity_score"] +
    #     0.5 * residential_df["affordability_score"] * 100
    # )

    # # ✅ 8. Visualize
    # st.markdown("### 🗺️ Recommended Residential Clusters")
    # map_center = [residential_df['latitude'].mean(), residential_df['longitude'].mean()]
    # recommendation_map = folium.Map(location=map_center, zoom_start=13)

    # for _, row in residential_df.iterrows():
    #     popup_text = f"""
    #     🏠 <b>{row['name']}</b><br>
    #     📍 {row['address']}<br>
    #     💸 Income: ₹{numeric_income:,}<br>
    #     📉 City Cost: ₹{int(estimated_cost):,}<br>
    #     ✅ Match Score: {round(row['final_score'], 2)}
    #     """
    #     folium.Marker(
    #         location=[row['latitude'], row['longitude']],
    #         popup=folium.Popup(popup_text, max_width=300),
    #         icon=folium.Icon(color="blue", icon="home", prefix="fa")
    #     ).add_to(recommendation_map)

    # folium_static(recommendation_map)

    

