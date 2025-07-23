from flask import Flask, render_template_string
import plotly.io as pio
import asyncio
from main import generate_map  # We'll move your code into a function

app = Flask(__name__)

@app.route("/")
def index():
    fig = generate_map()  # This runs your async fetch + map build
    html = pio.to_html(fig, full_html=False)
    return render_template_string(f"""
    <html>
      <head><title>Trending Map</title></head>
      <body>{html}</body>
    </html>
    """)

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)
