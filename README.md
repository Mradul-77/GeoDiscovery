# GeoDiscovery: Exploratory Analysis of Geolocational Data<br>

## (On the basis of predefined dataset)<br>

### Overview:
GeoDiscovery is a project designed to help individuals to find the best accommodations in any city based on their preferences for amenities, budget, and proximity to specific locations. Utilizing K-Means Clustering, the system classifies available accommodations and provides personalized recommendations for the locations where the individual can accommodate, simplifying the decision-making process for users.
### Data Set:
The data set used in the project can be downloaded from: https://drive.google.com/drive/folders/1TbRjwBz3Pvy0Fn8t__DUmZgtj21ttDhn?usp=sharing
### Data Dictionary:
The data dictionary document explains the meaning of the CSV values in the data set and can be downloaded from: https://www.kaggle.com/borapajo/food-choices

## (User-centric and dynamic version)<br>

# 🏙️ Relocation Recommendation System<br>

This is an intelligent, user-centric web application that helps users discover optimal residential areas in major Indian cities based on their income, food preferences, and proximity to preferred amenities like gyms, airports, restaurants, hospitals, parks, etc. The system uses real-time geolocation data from the Foursquare Places API and builds personalized recommendations by combining proximity, affordability, and lifestyle-based scoring.

---

## 📌 Features

- 🌍 **Real-Time City Selection**: Users can choose from major Indian cities, with autocomplete functionality.
- 💸 **Income-Based Filtering**: Dynamically adjusts scoring based on the user's income and estimated cost of living in the city.
- 🍲 **Personalized Food Preferences**: Considers ethnic food, fast food, organic food, spicy food, and more.
- 🏋️ **Amenity Preferences**: Users can choose preferred super categories and subcategories from actual Foursquare category IDs.
- 📍 **Proximity Calculations**: Uses the Haversine formula to calculate real-world distance from residential areas to nearby selected amenities.
- 🧠 **Custom Scoring Engine**: Combines proximity score, affordability score, and food match score into a final recommendation score.
- 📊 **Visual Output**: Displays a map with top residential locations based on the calculated score.
- 📄 **Downloadable Output**: Allows users to download recommended residential areas as a CSV file.

---

## 🛠️ Tools & Technologies Used

| Tool | Purpose |
|------|---------|
| **Streamlit** | Web application interface |
| **Pandas** | Data manipulation and preprocessing |
| **NumPy** | Numerical operations |
| **scikit-learn** | Clustering (KMeans), data scaling |
| **Geopy (Nominatim)** | Geocoding cities to latitude & longitude |
| **Foursquare API (Places)** | Fetching residential locations and nearby amenities |
| **Folium** | Map generation with markers and clustering |
| **Haversine Formula** | Calculating real distances between geo-coordinates |
| **CSV Export** | Allows download of output recommendations |

---

## 🧠 Project Logic

1. **User Input**:
   - City to relocate
   - Income category and exact range
   - Food preferences (variety of sliders from 1 to 5)
   - Amenity preferences (select super and subcategories)

2. **Location and Cost Lookup**:
   - Latitude and longitude are retrieved using `geopy`
   - Estimated living cost is fetched from a mock city dictionary (or real-time APIs if enabled)

3. **Residential Area Extraction**:
   - 10–15 residential coordinates are fetched via Foursquare using neighborhood category IDs

4. **Amenity Distance Calculation**:
   - The Haversine formula is used to calculate the average distance from each location to selected amenities

5. **Scoring**:
   - **Proximity Score** (shorter distances = better)
   - **Affordability Score** (income-to-cost ratio)
   - **Food Score** (based on user slider values)
   - Final score = weighted average of all three

6. **Output**:
   - Sorted list of top locations
   - Displayed on an interactive map
   - Exportable as CSV

# 🙋‍♂️ Author
**Mradul Gupta**  
***Built as part of a major project presentation for a data science application.***
