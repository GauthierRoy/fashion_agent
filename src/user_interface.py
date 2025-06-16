from flask import Flask, render_template_string, request
import threading
import time
import requests
from werkzeug.serving import make_server
from fetch_and_extract_image import extrate_images
from smolagents import tool

app = Flask(__name__)
selected_result = None
server = None

html = '''
<!doctype html>
<html>
<head>
    <title>Image Gallery</title>
    <style>
        body {
            font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
            background-color: #f0f4f8;
            color: #333;
            padding: 20px;
            text-align: center;
        }

        h2 {
            color: #2c3e50;
        }

        .card {
            display: inline-block;
            background-color: white;
            border-radius: 12px;
            box-shadow: 0 4px 8px rgba(0, 0, 0, 0.1);
            margin: 15px;
            padding: 15px;
            width: 200px;
            transition: transform 0.2s;
        }

        .card:hover {
            transform: scale(1.05);
        }

        .card img {
            width: 100%;
            height: auto;
            border-radius: 8px;
        }

        .name {
            font-size: 1.1em;
            font-weight: 600;
            margin-top: 10px;
        }

        .price {
            color: #27ae60;
            margin: 8px 0;
        }

        input[type="checkbox"] {
            margin-top: 8px;
            transform: scale(1.2);
        }

        .button-container {
            margin-top: 30px;
        }

        button {
            background-color: #3498db;
            border: none;
            color: white;
            padding: 10px 20px;
            margin: 0 10px;
            font-size: 16px;
            border-radius: 8px;
            cursor: pointer;
            transition: background-color 0.3s ease;
        }

        button:hover {
            background-color: #2980b9;
        }

        button[name="action"][value="none"] {
            background-color: #e74c3c;
        }

        button[name="action"][value="none"]:hover {
            background-color: #c0392b;
        }
        .env-score {
            margin-top: 8px;
            color: #888;
            font-size: 0.85em;
            font-weight: 500;
            display: flex;
            align-items: center;
            justify-content: center;
            gap: 6px;
            font-size: 0.95em;
        }

        .co2-icon {
            font-size: 14px;  /* smaller emoji */
            line-height: 1;
        }

        .co2-text {
            font-size: 0.85em;
            color: #888;
        }
    </style>
</head>
<body>
    <h2>Select your products:</h2>
    <form method="POST" action="/submit">
        {% for url, price, name, env_score in items %}
        <div class="card">
            <img src="{{ url }}" alt="Image">
            <div class="name">{{ name }}</div>
            <div class="price">{{ price }} €</div>
            <div class="env-score">
                <span class="co2-icon">💨</span>
                <span class="co2-text">{{ env_score }} CO₂</span>
            </div>
            <input type="checkbox" name="selected" value="{{ loop.index0 }}"> Select
        </div>
        {% endfor %}
        <div class="feedback-section">
            <h3 style="margin-top: 40px;">Optional feedback:</h3>
            <textarea name="feedback" rows="4" cols="60" placeholder="Leave your comments here..." style="padding: 10px; border-radius: 8px; border: 1px solid #ccc;"></textarea>
        </div>

        <div class="button-container">
            <button type="submit" name="action" value="ok">OK</button>
            <button type="submit" name="action" value="none">None of these above</button>
        </div>
    </form>
</body>
</html>
'''


@app.route("/", methods=["GET"])
def display_gallery():
    global items
    return render_template_string(html, items=items)


@app.route("/submit", methods=["POST"])
def submit_selection():
    global selected_result, feedback_result, server
    print("Form data:", request.form)
    action = request.form.get("action")

    feedback_result = request.form.get("feedback", "")  # store feedback even if empty

    if action == "ok":
        selected = request.form.getlist("selected")
        selected_result = selected
    elif action == "none":
        selected_result = []

    threading.Thread(target=shutdown_server_delayed).start()
    return selected_result



def shutdown_server_delayed():
    global server
    time.sleep(1)  # Give time for the response to be sent
    if server:
        server.shutdown()


def run_app(images_with_prices, port=5000):
    global items, server
    items = images_with_prices
    server = make_server('127.0.0.1', port, app)
    print(f"Server running on http://127.0.0.1:{port}")
    server.serve_forever()


def get_user_selection(images_with_prices, port=5000):
    global selected_result, feedback_result
    selected_result = None
    feedback_result = None

    thread = threading.Thread(target=run_app, args=(images_with_prices, port))
    thread.daemon = True
    thread.start()

    time.sleep(1)
    import webbrowser
    webbrowser.open(f'http://127.0.0.1:{port}')

    while selected_result is None:
        time.sleep(0.1)

    return [int(idx) for idx in selected_result], feedback_result


@tool
def confirm_with_user(urls: list[str], prices: list[float], names:list[str], environment_score:list[float]) -> list[str]:
    """Given a list of URLs and prices, this function first gets the image URLs from the provided URLs,
    then displays them in a gallery format for user selection. User selects the product given the image and the price.
    We return the selected product URLs.

    Args:
        urls (list[str]): List of product URLs to extract images from.
        prices (list[float]): List of prices corresponding to each product URL.
        names (list[str]): List of product names corresponding to each product URL.
        environment_score (list[str]): List of environment scores corresponding to each product URL.
    Returns:
        list[str]: List of URLs selected by the user.
    
    """

    images = [(url, price, name, env_score) for url, price, name, env_score in zip(extrate_images(urls), prices, names, environment_score)]

    result, feedback_result= get_user_selection(images)
    url_results = []
    for idx in result:
        url_results.append(urls[idx])

    if url_results == []:
        print("User selected no products.")
        return ["No products selected"]

    print("User selected:", url_results)
    if feedback_result:
        print("User feedback:", feedback_result)
    return url_results, feedback_result


# Usage
if __name__ == "__main__":

    urls = [
        "https://www.nike.com/fr/t/chaussure-p-6000-T6ofxOFZ/FD9876-101?cp=10777067101_search_&Macro=--o-361508208-1176478328680660-e-c-FR-csscore--pla-4577129470675250-189521-00196604969376&ds_rl=1252249&msclkid=89f44dd2070e15832025259cb4001ec6&gclid=89f44dd2070e15832025259cb4001ec6&gclsrc=3p.ds&gad_source=7",
        "https://www.nike.com/fr/t/chaussure-p-6000-T6ofxOFZ/FD9876-101?cp=10777067101_search_&Macro=--o-361508208-1176478328680660-e-c-FR-csscore--pla-4577129470675250-189521-00196604969376&ds_rl=1252249&msclkid=89f44dd2070e15832025259cb4001ec6&gclid=89f44dd2070e15832025259cb4001ec6&gclsrc=3p.ds&gad_source=7"
    ]

    prices = [29.99, 45.50]
    names = ["Nike P-6000", "Nike P-6000"]
    env_scores = [10.5, 12.0]  # Example environment scores
    

    confirm_with_user(urls, prices, names, env_scores)