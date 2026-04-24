import os, json, datetime
from groq import Groq
from dotenv import load_dotenv

load_dotenv()
client = Groq(api_key=os.environ.get("GROQ_API_KEY"))

PERSONAS = {
    "agency_owner": {"name": "Agency Owner", "description": "Runs a small creative agency. Cares about ROI and efficiency.", "tone": "business-focused, concise"},
    "freelance_designer": {"name": "Freelance Designer", "description": "Solo creative. Cares about saving time and getting projects.", "tone": "casual, practical"},
    "marketing_manager": {"name": "Marketing Manager", "description": "In-house marketer. Cares about performance and reporting.", "tone": "data-informed, professional"}
}

def call_groq(prompt):
    response = client.chat.completions.create(
        model="llama-3.3-70b-versatile",
        messages=[{"role": "user", "content": prompt}],
        temperature=0.7
    )
    text = response.choices[0].message.content.strip()
    if "```" in text:
        text = text.split("```")[1]
        if text.startswith("json"): text = text[4:]
    text = text.strip()
    text = text.replace("\r", " ").replace("\t", " ")
    import re
    text = re.sub(r"[\x00-\x1f\x7f]", " ", text)
    return json.loads(text)

def generate_blog(topic):
    print(f"  Generating blog about: {topic}")
    prompt = (
        "You are a content strategist for NovaMind, an AI startup for creative agencies. "
        f"Write a blog post on: {topic}. "
        "Return ONLY valid JSON, no markdown, no explanation: "
        '{"title": "SEO title here", "outline": ["Section 1", "Section 2", "Section 3", "Conclusion"], '
        '"draft": "Write a full 400-600 word blog post here with intro hook, 3 body sections, and CTA to try NovaMind", '
        '"meta_description": "under 155 chars", "tags": ["tag1", "tag2", "tag3"]}'
    )
    result = call_groq(prompt)
    result["topic"] = topic
    result["generated_at"] = datetime.datetime.utcnow().isoformat()
    return result

def generate_newsletters(blog):
    newsletters = {}
    for key, persona in PERSONAS.items():
        print(f"  Newsletter for: {persona['name']}")
        prompt = (
            "You are a copywriter for NovaMind, an AI workflow automation startup. "
            f"Blog title: {blog['title']}. "
            f"Blog summary: {blog['draft'][:400]}. "
            f"Write a newsletter for this persona: {persona['name']} - {persona['description']} - Tone: {persona['tone']}. "
            "Return ONLY valid JSON, no markdown, no explanation: "
            '{"subject_line": "under 60 chars", "preview_text": "under 90 chars", '
            '"body": "150-220 word newsletter body with hook and CTA", '
            '"cta_text": "under 30 chars", "cta_url": "https://blog.novamind.ai/slug"}'
        )
        result = call_groq(prompt)
        result["persona"] = key
        result["persona_name"] = persona["name"]
        newsletters[key] = result
    return newsletters

def save_output(blog, newsletters):
    import pathlib
    pathlib.Path("output").mkdir(exist_ok=True)
    ts = datetime.datetime.utcnow().strftime("%Y%m%d-%H%M%S")
    slug = "".join(c for c in blog["title"].lower().replace(" ", "-")[:40] if c.isalnum() or c == "-")
    fname = f"output/{ts}-{slug}.json"
    campaign_id = f"campaign-{ts}"
    with open(fname, "w") as f:
        json.dump({"campaign_id": campaign_id, "blog": blog, "newsletters": newsletters}, f, indent=2)
    return fname, campaign_id

def run(topic):
    print("\n[Stage 1] Content Generation")
    blog = generate_blog(topic)
    print(f"  Blog: {blog['title']}")
    newsletters = generate_newsletters(blog)
    print(f"  Newsletters done for {len(newsletters)} personas")
    path, campaign_id = save_output(blog, newsletters)
    print(f"  Saved: {path}")
    return blog, newsletters, path, campaign_id
