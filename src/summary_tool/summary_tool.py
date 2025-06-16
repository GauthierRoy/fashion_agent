from flask import Flask, render_template_string, request
import threading
import time
import requests
from werkzeug.serving import make_server

app = Flask(__name__)
selected_result = None
server = None

html = '''
<!doctype html>
<html>
<head>
    <title>Image Gallery</title>
    <style>
        .card {
            display: inline-block;
            margin: 10px;
            text-align: center;
        }
        .card img {
            width: 150px;
            height: auto;
        }
    </style>
</head>
<body>
    <h2>Select your images:</h2>
    <form method="POST" action="/submit">
        {% for url, price in items %}
        <div class="card">
            <img src="{{ url }}" alt="Image">
            <div class="price">{{ price }}</div>
            <input type="checkbox" name="selected" value="{{ url }}"> Select
        </div>
        {% endfor %}
        <br><br>
        <button type="submit" name="action" value="ok">OK</button>
        <button type="submit" name="action" value="none">None of these above</button>
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
    global selected_result, server
    action = request.form.get("action")

    if action == "ok":
        selected = request.form.getlist("selected")
        selected_result = selected
    elif action == "none":
        selected_result = []

    # Shutdown server in a separate thread to avoid blocking the response
    threading.Thread(target=shutdown_server_delayed).start()
    return "Thank you! Selection received. You can close this tab."


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
    global selected_result
    selected_result = None

    thread = threading.Thread(target=run_app, args=(images_with_prices, port))
    thread.daemon = True
    thread.start()

    # Wait a moment for server to start
    time.sleep(1)

    # Open browser automatically (optional)
    import webbrowser
    webbrowser.open(f'http://127.0.0.1:{port}')

    # Wait for user selection
    while selected_result is None:
        time.sleep(0.1)

    return selected_result


# Usage
if __name__ == "__main__":
    images = [
        (
        "https://static.nike.com/a/images/t_default/c433a467-8480-4938-bbf7-1d229fe606a4/WMNS+NIKE+P-6000.png", "$120"),
        ("https://www.example.com/image2.png", "$90")
    ]

    result = get_user_selection(images)
    print("User selected:", result)