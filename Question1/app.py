from flask import Flask, jsonify
import requests
import time

app = Flask(__name__)

WINDOW_SIZE = 10

number_store = {
    "p": [],  
    "f": [], 
    "e": [],  
    "r": []   
}

# API URLs
API_URLS = {
    "p": "http://20.244.56.144/evaluation-service/primes",
    "f": "http://20.244.56.144/evaluation-service/fibo",
    "e": "http://20.244.56.144/evaluation-service/even",
    "r": "http://20.244.56.144/evaluation-service/rand"
}

def fetch_numbers(number_id):
    """Fetch numbers from the external API within a 500ms timeout."""
    url = API_URLS.get(number_id)
    if not url:
        return []
    
    try:
        response = requests.get(url, timeout=0.5) 
        response.raise_for_status()  
        data = response.json()
        return data.get("numbers", [])
    except (requests.exceptions.RequestException, ValueError):
        return []

def update_window(number_id, new_numbers):
    
    prev_state = list(number_store[number_id])  

    number_store[number_id].extend(num for num in new_numbers if num not in number_store[number_id])

    number_store[number_id] = number_store[number_id][-WINDOW_SIZE:]
    
    return prev_state, list(number_store[number_id])  

@app.route('/numbers/<string:number_id>', methods=['GET'])
def get_numbers(number_id):
    if number_id not in number_store:
        return jsonify({"error": "Invalid number ID"}), 400

    new_numbers = fetch_numbers(number_id)

    prev_state, curr_state = update_window(number_id, new_numbers)

    avg = round(sum(curr_state) / len(curr_state), 2) if curr_state else 0

    return jsonify({
        "windowPrevState": prev_state,
        "windowCurrState": curr_state,
        "numbers": new_numbers,
        "avg": avg
    })

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)
