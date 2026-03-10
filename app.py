from flask import Flask, render_template, request, jsonify
import requests, json, os

app = Flask(__name__)

DATA_FILE = os.path.join(os.path.dirname(__file__), "data/outfits.json")
with open(DATA_FILE) as f:
    DATA = json.load(f)


def get_weather(city):
    try:
        r = requests.get(f"https://wttr.in/{city}?format=j1", timeout=5)
        w = r.json()
        current = w["current_condition"][0]
        temp_c  = int(current["temp_C"])
        feels   = int(current["FeelsLikeC"])
        desc    = current["weatherDesc"][0]["value"]
        humidity = current["humidity"]
        return {"temp": temp_c, "feels": feels, "desc": desc,
                "humidity": humidity, "city": city, "error": None}
    except Exception as e:
        return {"temp": 18, "feels": 18, "desc": "Partly Cloudy",
                "humidity": "60", "city": city, "error": str(e)}


def get_weather_category(temp):
    if temp >= 28:  return "hot"
    if temp >= 22:  return "warm"
    if temp >= 15:  return "mild"
    if temp >= 8:   return "cool"
    return "cold"


@app.route("/")
def index():
    return render_template("index.html")


@app.route("/api/outfits")
def api_outfits():
    city     = request.args.get("city", "Toronto")
    weather  = get_weather(city)
    category = get_weather_category(weather["temp"])
    outfits  = DATA["weather_outfits"][category]
    trends   = DATA["trends_2026"]
    return jsonify({
        "weather":  weather,
        "category": category,
        "outfits":  outfits,
        "trends":   trends
    })


if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5050))
    app.run(host="0.0.0.0", port=port, debug=False)
