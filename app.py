from flask import Flask, render_template, request, jsonify
from geopy.geocoders import Nominatim
from geopy.exc import GeocoderServiceError, GeocoderTimedOut
import folium

app = Flask(__name__)

user_agent = "MyGeocodingApp/1.0 (myemailaddress@example.com)"

@app.route('/', methods=['GET', 'POST'])
def index():
    map_html = None
    error = None
    latitude = None
    longitude = None
    address = None
    map_type = 'OpenStreetMap'  # Default map type

    # If a location or address is enter in the form
    if request.method == 'POST':
        if 'address' in request.form:
            address = request.form['address']
            map_type = request.form.get('map_type', 'OpenStreetMap')
            geolocator = Nominatim(user_agent=user_agent)

            try:
                location = geolocator.geocode(address, timeout=10)

                if location:
                    latitude = location.latitude
                    longitude = location.longitude

                    # Create a map centered around the geocoded location
                    folium_map = folium.Map(location=[latitude, longitude], zoom_start=15, tiles=map_type)
                    folium.Marker([latitude, longitude], popup=location.address).add_to(folium_map)

                    # Save the map as an HTML file
                    map_html = folium_map._repr_html_()
                else:
                    error = "Location not found"
            except (GeocoderServiceError, GeocoderTimedOut):
                error = "Geocoding service error. Please try again later."
        # Else get use the decice location to displayed a map
        elif 'latitude' in request.form and 'longitude' in request.form:
            latitude = request.form['latitude']
            longitude = request.form['longitude']
            map_type = request.form.get('map_type', 'OpenStreetMap')

            # Validate latitude and longitude
            if latitude and longitude:
                #print(latitude, longitude) # Let see if our app get location coord from device.
                try:
                    latitude = float(latitude)
                    longitude = float(longitude)

                    print(latitude, longitude)
                    # Create a map centered around the provided latitude and longitude
                    folium_map = folium.Map(location=[latitude, longitude], zoom_start=15, tiles=map_type)
                   # print('folium_map:',folium_map)
                    folium.Marker([latitude, longitude], popup="Device Location").add_to(folium_map)

                    # Save the map as an HTML file
                    map_html = folium_map._repr_html_()
                    #print('map_html:',map_html)
                except ValueError:
                    error = "Invalid coordinates"
            else:
                error = "Coordinates not provided"

    return render_template('index.html', map_html=map_html, error=error, latitude=latitude, longitude=longitude, address=address, map_type=map_type)

@app.route('/update_map', methods=['POST'])
def update_map():
    latitude = request.form.get('latitude')
    longitude = request.form.get('longitude')
    map_type = request.form.get('map_type', 'OpenStreetMap')

    # Validate latitude and longitude
    if latitude and longitude:
        try:
            latitude = float(latitude)
            longitude = float(longitude)

            # Create a map centered around the given latitude and longitude
            folium_map = folium.Map(location=[latitude, longitude], zoom_start=15, tiles=map_type)
            folium.Marker([latitude, longitude], popup="Selected Location").add_to(folium_map)

            # Render the map HTML
            map_html = folium_map._repr_html_()

            return jsonify({'map_html': map_html})
        except ValueError:
            return jsonify({'error': 'Invalid coordinates'}), 400
    else:
        return jsonify({'error': 'Coordinates not provided'}), 400

if __name__ == '__main__':
    app.run(debug=True)
