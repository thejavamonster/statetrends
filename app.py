from flask import Flask
import threading, time
from main import fetch_trends, state_coords
import plotly.graph_objects as go
import plotly.express as px

app = Flask(__name__)
cache = {"data": {}, "last_update": 0}

# Background updater
def updater():
    while True:
        print("Fetching Google Trends...")
        try:
            cache["data"] = fetch_trends()
            cache["last_update"] = time.time()
            print("Update successful.")
        except Exception as e:
            print("Update failed:", e)
        time.sleep(900)  # 15 min interval

def generate_map(trends):
    if not trends:
        return "<h2>No data yet. Refresh in a minute.</h2>"

    unique_trends = list(set(trends.values()))
    colors = px.colors.qualitative.Safe * ((len(unique_trends) // len(px.colors.qualitative.Safe)) + 1)

    fig = go.Figure()

    # Base Choropleth
    fig.add_trace(go.Choropleth(
        locations=list(trends.keys()),
        z=[unique_trends.index(trends[code]) for code in trends],
        locationmode='USA-states',
        colorscale=[[i/(len(unique_trends)-1), colors[i]] for i in range(len(unique_trends))],
        showscale=False,
        hovertext=[f"{code}: {trends[code]}" for code in trends],
        hoverinfo='text'
    ))

    # Inline text labels for each state
    for code, trend in trends.items():
        lat, lon = state_coords[code]
        label = trend if len(trend) <= 14 else trend[:14] + "…"
        fig.add_trace(go.Scattergeo(
            lon=[lon], lat=[lat],
            text=label,
            mode='text',
            textfont=dict(size=10, color='black', family="Arial Black")
        ))

    fig.update_layout(
        geo=dict(scope='usa'),
        title_text='Top Google Trend by State',
        margin=dict(l=0, r=0, t=50, b=0),
        paper_bgcolor='white'
    )

    return fig.to_html(full_html=False)

@app.route("/")
def index():
    return f"""
    <html>
    <head><title>US State Trends</title></head>
    <body>
        <h1>US Top Google Trends by State</h1>
        <p>Last updated: {time.ctime(cache['last_update'])}</p>
        {generate_map(cache['data'])}
    </body>
    </html>
    """

if __name__ == "__main__":
    threading.Thread(target=updater, daemon=True).start()
    app.run(host="0.0.0.0", port=10000)
