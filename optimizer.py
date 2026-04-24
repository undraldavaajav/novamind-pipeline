import os
from groq import Groq
from dotenv import load_dotenv

load_dotenv()
client = Groq(api_key=os.environ.get("GROQ_API_KEY"))

def suggest_topics(metrics, previous_blog_title):
    print("\n[Bonus] Generating next topic suggestions...")
    best_persona = max(metrics, key=lambda p: metrics[p]["click_rate"])
    best_click = metrics[best_persona]["click_rate"] * 100
    prompt = (
        "You are a content strategist for NovaMind, an AI startup for creative agencies. "
        f"Our last blog was: {previous_blog_title}. "
        f"Our best performing audience was {best_persona} with a {best_click:.1f}% click rate. "
        "Based on this, suggest 5 blog topics optimized for this audience. "
        "Return ONLY valid JSON, no markdown: "
        '{"suggestions": ['
        '{"title": "topic title", "why": "one sentence reason based on performance data"}, '
        '{"title": "topic title", "why": "one sentence reason"}, '
        '{"title": "topic title", "why": "one sentence reason"}, '
        '{"title": "topic title", "why": "one sentence reason"}, '
        '{"title": "topic title", "why": "one sentence reason"}'
        ']}'
    )
    import json, re
    response = client.chat.completions.create(
        model="llama-3.3-70b-versatile",
        messages=[{"role": "user", "content": prompt}],
        temperature=0.7
    )
    text = response.choices[0].message.content.strip()
    if "```" in text:
        text = text.split("```")[1]
        if text.startswith("json"): text = text[4:]
    text = re.sub(r"[\x00-\x1f\x7f]", " ", text.strip())
    result = json.loads(text)
    print("  Suggested next topics:")
    for i, s in enumerate(result["suggestions"], 1):
        print(f"  {i}. {s['title']}")
        print(f"     Why: {s['why']}")
    import pathlib, datetime
    pathlib.Path("data").mkdir(exist_ok=True)
    ts = datetime.datetime.utcnow().strftime("%Y%m%d-%H%M%S")
    with open(f"data/{ts}-topic-suggestions.json", "w") as f:
        json.dump(result, f, indent=2)
    return result
