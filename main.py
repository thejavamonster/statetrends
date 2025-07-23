import asyncio
import aiohttp
import feedparser
import plotly.graph_objects as go
import colorsys
import random

# State coordinates (for text placement)
state_coords = {
    "AL": [32.806671, -86.791130], "AK": [61.370716, -152.404419],
    "AZ": [33.729759, -111.431221], "AR": [34.969704, -92.373123],
    "CA": [36.116203, -119.681564], "CO": [39.059811, -105.311104],
    "CT": [41.597782, -72.755371], "DE": [39.318523, -75.507141],
    "FL": [27.766279, -81.686783], "GA": [33.040619, -83.643074],
    "HI": [21.094318, -157.498337], "ID": [44.240459, -114.478828],
    "IL": [40.349457, -88.986137], "IN": [39.849426, -86.258278],
    "IA": [42.011539, -93.210526], "KS": [38.526600, -96.726486],
    "KY": [37.668140, -84.670067], "LA": [31.169546, -91.867805],
    "ME": [44.693947, -69.381927], "MD": [39.063946, -76.802101],
    "MA": [42.230171, -71.530106], "MI": [43.326618, -84.536095],
    "MN": [45.694454, -93.900192], "MS": [32.741646, -89.678696],
    "MO": [38.456085, -92.288368], "MT": [46.921925, -110.454353],
    "NE": [41.125370, -98.268082], "NV": [38.313515, -117.055374],
    "NH": [43.452492, -71.563896], "NJ": [40.298904, -74.521011],
    "NM": [34.840515, -106.248482], "NY": [42.165726, -74.948051],
    "NC": [35.630066, -79.806419], "ND": [47.528912, -99.784012],
    "OH": [40.388783, -82.764915], "OK": [35.565342, -96.928917],
    "OR": [44.572021, -122.070938], "PA": [40.590752, -77.209755],
    "RI": [41.680893, -71.511780], "SC": [33.856892, -80.945007],
    "SD": [44.299782, -99.438828], "TN": [35.747845, -86.692345],
    "TX": [31.054487, -97.563461], "UT": [40.150032, -111.862434],
    "VT": [44.045876, -72.710686], "VA": [37.769337, -78.169968],
    "WA": [47.400902, -121.490494], "WV": [38.491226, -80.954456],
    "WI": [44.268543, -89.616508], "WY": [42.755966, -107.302490]
}

headers = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/112.0 Safari/537.36",
    "Accept-Language": "en-US,en;q=0.9"
}

# Generate unique, vibrant colors
def generate_colors(n):
    colors = []
    for i in range(n):
        hue = i / n
        lightness = 0.5
        saturation = 0.8
        r, g, b = colorsys.hls_to_rgb(hue, lightness, saturation)
        colors.append(f'rgb({int(r*255)}, {int(g*255)}, {int(b*255)})')
    return colors

async def fetch_trend(session, state_code):
    url = f"https://trends.google.com/trending/rss?geo=US-{state_code}"
    for attempt in range(3):  # Retry up to 3 times
        await asyncio.sleep(random.uniform(0.5, 1.2))  # Slow down a bit to avoid blocks
        try:
            async with session.get(url, headers=headers) as response:
                text = await response.text()
                feed = feedparser.parse(text)
                if feed.entries:
                    return state_code, feed.entries[0].title
        except:
            pass
    return state_code, "No data"

async def get_all_trends():
    async with aiohttp.ClientSession() as session:
        tasks = [fetch_trend(session, code) for code in state_coords.keys()]
        results = await asyncio.gather(*tasks)
    return dict(results)

def generate_map():
    state_trends = asyncio.run(get_all_trends())
    unique_trends = list(set(state_trends.values()))
    colors = generate_colors(len(unique_trends))

    fig = go.Figure()
    fig.add_trace(go.Choropleth(
        locations=list(state_trends.keys()),
        z=[unique_trends.index(state_trends[code]) for code in state_trends],
        locationmode='USA-states',
        colorscale=[[i/(len(unique_trends)-1), colors[i]] for i in range(len(unique_trends))],
        showscale=False,
        hovertext=[f"{code}: {state_trends[code]}" for code in state_trends],
        hoverinfo='text'
    ))

    for code, trend in state_trends.items():
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

    return fig
