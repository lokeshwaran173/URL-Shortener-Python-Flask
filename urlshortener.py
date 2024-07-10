#libraries
#install packages

from flask import Flask, request, redirect, jsonify
import string
import random
import threading
import requests
import time

app = Flask(__name__)

# In-memory database to store URLs
url_map = {}

# Base URL for the shortened URLs
BASE_URL = "http://localhost:5000/"

def generate_short_id(length=6):
    """Generate a random string of fixed length."""
    characters = string.ascii_letters + string.digits
    return ''.join(random.choice(characters) for _ in range(length))

@app.route('/shorten', methods=['POST'])
def shorten_url():
    """Endpoint to shorten a URL."""
    original_url = request.json.get('url')
    if not original_url:
        return jsonify({"error": "URL is required"}), 400

    short_id = generate_short_id()
    while short_id in url_map:
        short_id = generate_short_id()
    
    url_map[short_id] = original_url
    short_url = BASE_URL + short_id

    return jsonify({"short_url": short_url})

@app.route('/<short_id>', methods=['GET'])
def redirect_url(short_id):
    """Redirect to the original URL."""
    original_url = url_map.get(short_id)
    if original_url:
        return redirect(original_url)
    else:
        return jsonify({"error": "URL not found"}), 404

def start_flask_app():
    """Start the Flask app in a separate thread."""
    app.run(debug=True, use_reloader=False)

def shorten_url_via_terminal(original_url):
    """Shorten URL by sending a POST request to the Flask app."""
    try:
        response = requests.post(BASE_URL + 'shorten', json={'url': original_url})
        response.raise_for_status()
        return response.json().get('short_url', 'Error: No short URL returned')
    except requests.exceptions.RequestException as e:
        return f"Error: {e}"

if __name__ == '__main__':
    # Start Flask app in a separate thread
    threading.Thread(target=start_flask_app).start()

    # Give the server some time to start
    time.sleep(2)

    # Get original URL from terminal input
    original_url = input("Enter the URL to shorten: ")
    short_url = shorten_url_via_terminal(original_url)
    print("Shortened URL:", short_url)
