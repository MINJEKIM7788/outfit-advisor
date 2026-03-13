from flask import Flask, render_template, request, jsonify
import requests, json, os, sys
from datetime import datetime

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


@app.route("/api/daily")
def api_daily():
    """Used by iPhone Shortcuts — returns daily briefing content"""
    sys.path.insert(0, os.path.dirname(__file__))

    # English content
    WORDS = [
        {"word":"fascinating","meaning":"Extremely interesting","joe_says":"The most fascinating thing about it is how nobody talks about it.","use_it":"That's a fascinating perspective — I hadn't thought of it that way."},
        {"word":"legitimate","meaning":"Real, valid, genuinely serious","joe_says":"That's a legitimate concern and I think most people just ignore it.","use_it":"Do you think that's a legitimate reason or just an excuse?"},
        {"word":"nuanced","meaning":"Having subtle differences; not black and white","joe_says":"It's a very nuanced situation and people want a simple answer.","use_it":"The reality is way more nuanced than the media makes it seem."},
        {"word":"compelling","meaning":"Powerfully convincing or impossible to ignore","joe_says":"He made a really compelling argument that I couldn't disagree with.","use_it":"That's a compelling case — I need to look into that more."},
        {"word":"simultaneously","meaning":"At the same time","joe_says":"You can simultaneously believe two things that seem contradictory.","use_it":"I was simultaneously impressed and terrified by what he said."},
        {"word":"articulate","meaning":"Able to express ideas clearly and fluently","joe_says":"She's one of the most articulate people I've ever talked to.","use_it":"He's incredibly articulate — every word is exactly right."},
        {"word":"genuinely","meaning":"Truly and sincerely, not fake","joe_says":"I genuinely believe most people are doing the best they can.","use_it":"I genuinely don't know how they pulled that off."},
        {"word":"fundamentally","meaning":"At the most basic and important level","joe_says":"Fundamentally, the problem is that nobody wants to do the hard work.","use_it":"We fundamentally disagree on how to approach this."},
        {"word":"resilient","meaning":"Able to recover quickly from difficulty","joe_says":"Humans are incredibly resilient — we adapt to almost anything.","use_it":"She's one of the most resilient people I know."},
        {"word":"momentum","meaning":"The force that keeps something moving or growing","joe_says":"Once you build momentum it becomes almost impossible to stop.","use_it":"Don't break the momentum — keep going while it's working."},
        {"word":"inevitable","meaning":"Certain to happen, impossible to avoid","joe_says":"At some point the shift was inevitable — it was just a matter of when.","use_it":"Conflict was inevitable given how different they are."},
        {"word":"profound","meaning":"Very deep and meaningful","joe_says":"That's a profound statement and most people just brush past it.","use_it":"The impact of that decision was more profound than anyone expected."},
        {"word":"deliberate","meaning":"Done on purpose; intentional and careful","joe_says":"Everything about that decision was deliberate — nothing was accidental.","use_it":"You have to be deliberate about how you spend your time."},
        {"word":"narrative","meaning":"The story or version of events people believe","joe_says":"The mainstream narrative doesn't match what the data actually shows.","use_it":"They're trying to control the narrative before the truth comes out."},
    ]
    PATTERNS = [
        {"pattern":"Here's the thing about [topic]...","example":"Here's the thing about success — most people want it but don't want what it takes.","tip":"Use this to signal you're about to say something real and direct."},
        {"pattern":"What's interesting is [observation]","example":"What's interesting is nobody actually talks about the cost of not trying.","tip":"Sounds thoughtful and analytical — very natural in conversation."},
        {"pattern":"The reality is [truth]","example":"The reality is most people give up right before it starts working.","tip":"Sounds confident and grounded — great for professional settings."},
        {"pattern":"I genuinely believe [opinion]","example":"I genuinely believe that consistency beats talent almost every time.","tip":"'Genuinely' makes it sound sincere, not just filler."},
        {"pattern":"It's kind of wild when you think about [fact]","example":"It's kind of wild when you think about how fast everything is changing.","tip":"Very natural, casual, native — sounds like a real person talking."},
        {"pattern":"At some point you have to [action]","example":"At some point you have to stop planning and just start doing.","tip":"Sounds wise and direct without being aggressive."},
        {"pattern":"I'd argue [point]","example":"I'd argue this is the better approach and here's why.","tip":"Sounds educated and confident — great in debates and meetings."},
        {"pattern":"That's one of those things where [situation]","example":"That's one of those things where you don't realize how important it is until it's gone.","tip":"Makes people nod — very relatable and conversational."},
    ]
    GRAMMAR = [
        {"tip":"Drop 'very' — use a stronger word","wrong":"That was very good.","right":"That was exceptional / outstanding / remarkable."},
        {"tip":"Use contractions naturally","wrong":"I am not sure that is the right answer.","right":"I'm not sure that's the right answer."},
        {"tip":"Say 'That makes sense' not 'I understand'","wrong":"I understand what you mean.","right":"That makes sense. / That tracks."},
        {"tip":"Use 'I'd say' to give opinions smoothly","wrong":"In my opinion the deadline is too short.","right":"I'd say the deadline is a bit unrealistic honestly."},
        {"tip":"Use 'Honestly' to add emphasis","wrong":"I really think we need to change the plan.","right":"Honestly, we need to rethink the whole plan."},
        {"tip":"Use 'end up' for unplanned results","wrong":"Finally I became the team leader.","right":"I ended up becoming the team leader."},
    ]

    day = datetime.now().timetuple().tm_yday
    word    = WORDS[day % len(WORDS)]
    pattern = PATTERNS[day % len(PATTERNS)]
    grammar = GRAMMAR[day % len(GRAMMAR)]
    weather = get_weather("Toronto")

    # Siri-friendly spoken text
    morning_spoken = (
        f"Good morning Minje. Today is {datetime.now().strftime('%A, %B %d')}. "
        f"Toronto weather: {weather['temp']} degrees, {weather['desc']}. "
        f"Word of the day: {word['word']}. Meaning: {word['meaning']}. "
        f"Joe Rogan uses it like this: {word['joe_says']}"
    )
    carplay_spoken = (
        f"Hey Minje! English tip for your drive. "
        f"Today's pattern: {pattern['pattern']}. "
        f"Example: {pattern['example']}. "
        f"Grammar tip: {grammar['tip']}. "
        f"Correct version: {grammar['right']}. "
        f"Have a great drive!"
    )

    return jsonify({
        "date": datetime.now().strftime("%A, %B %d"),
        "weather": weather,
        "word": word,
        "pattern": pattern,
        "grammar": grammar,
        "morning_spoken": morning_spoken,
        "carplay_spoken": carplay_spoken
    })


if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5050))
    app.run(host="0.0.0.0", port=port, debug=False)
