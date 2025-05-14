import streamlit as st

st.set_page_config(page_title="Relocation Recommendation System", layout="centered")

st.title("🏙️ Relocation Recommendation System")

# City input
city = st.text_input("Enter the city or region you'd like to move to:")

# Income bracket
income = st.selectbox("Select your income level:", ["Low", "Medium", "High"])

# Food preferences
st.markdown("### 🍲 Food Preferences (Rate from 1 to 5)")
ethnic_food = st.slider("Ethnic food preference", 1, 5, 3)
fast_food = st.slider("Fast food preference", 1, 5, 3)
veg_preference = st.slider("Vegetables/day", 1, 5, 3)
fruit_preference = st.slider("Fruits/day", 1, 5, 3)

# Amenity preferences
st.markdown("### 🏋️ Amenity Preferences (Rate from 1 to 5)")
gym = st.slider("Gym", 1, 5, 3)
bar = st.slider("Bar/Pub", 1, 5, 3)
park = st.slider("Parks/Open spaces", 1, 5, 3)
public_transport = st.slider("Public Transport Access", 1, 5, 3)

# Submit button
if st.button("Submit Preferences"):
    st.success(f"Thank you! Searching best clusters in **{city}** for a {income} income profile...")
    # Here you can call your clustering and recommendation function
    # Use user preferences as weights or filters in the model
