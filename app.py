from flask import Flask
from main import generate_map

app = Flask(__name__)

@app.route("/")
def index():
    html_map = generate_map()
    return f"""
    <html>
        <head><title>State Trends</title></head>
        <body>
            <h1 style="text-align:center;">Top Google Trends by State</h1>
            {html_map}
        </body>
    </html>
    """

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)
