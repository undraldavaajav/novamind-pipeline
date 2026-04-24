import os, json, datetime, random, pathlib
from groq import Groq
from dotenv import load_dotenv

load_dotenv()
client = Groq(api_key=os.environ.get("GROQ_API_KEY"))

def simulate_metrics(campaign_log):
    print("  Simulating engagement metrics...")
    metrics = {}
    base_rates = {
        "agency_owner":      {"open": 0.42, "click": 0.18, "unsub": 0.01},
        "freelance_designer": {"open": 0.38, "click": 0.14, "unsub": 0.02},
        "marketing_manager": {"open": 0.51, "click": 0.22, "unsub": 0.005},
    }
    for persona, base in base_rates.items():
        sends = [s for s in campaign_log["sends"] if s["persona"] == persona]
        count = len(sends)
        metrics[persona] = {
            "persona": persona,
            "sends": count,
            "opens": round(count * (base["open"] + random.uniform(-0.05, 0.05))),
            "clicks": round(count * (base["click"] + random.uniform(-0.03, 0.03))),
            "unsubscribes": round(count * (base["unsub"] + random.uniform(-0.005, 0.005))),
            "open_rate": round(base["open"] + random.uniform(-0.05, 0.05), 3),
            "click_rate": round(base["click"] + random.uniform(-0.03, 0.03), 3),
            "unsub_rate": round(base["unsub"] + random.uniform(-0.005, 0.005), 4),
        }
    return metrics

def save_metrics(campaign_id, metrics):
    pathlib.Path("data").mkdir(exist_ok=True)
    fname = f"data/{campaign_id}-metrics.json"
    payload = {
        "campaign_id": campaign_id,
        "recorded_at": datetime.datetime.utcnow().isoformat(),
        "metrics": metrics
    }
    with open(fname, "w") as f:
        json.dump(payload, f, indent=2)
    print(f"  Metrics saved: {fname}")
    return payload

def generate_summary(blog_title, metrics):
    print("  Generating AI performance summary...")
    metrics_text = ""
    for persona, m in metrics.items():
        metrics_text += f"{persona}: open={m['open_rate']*100:.1f}%, click={m['click_rate']*100:.1f}%, unsub={m['unsub_rate']*100:.2f}%\n"
    prompt = (
        "You are a marketing analyst for NovaMind. "
        f"Campaign: {blog_title}\n"
        f"Performance data:\n{metrics_text}"
        "Write a brief 3-4 sentence performance summary. Highlight the best performing persona, "
        "note any concerns, and give one concrete recommendation for the next campaign. "
        "Be specific with the numbers."
    )
    response = client.chat.completions.create(
        model="llama-3.3-70b-versatile",
        messages=[{"role": "user", "content": prompt}],
        temperature=0.7
    )
    return response.choices[0].message.content.strip()

def run(blog, campaign_log, campaign_id):
    print("\n[Stage 3] Performance Analytics")
    metrics = simulate_metrics(campaign_log)
    for persona, m in metrics.items():
        print(f"  {persona}: open={m['open_rate']*100:.1f}% click={m['click_rate']*100:.1f}%")
    save_metrics(campaign_id, metrics)
    summary = generate_summary(blog["title"], metrics)
    print("\n  AI Summary:")
    print(f"  {summary}")
    summary_path = f"data/{campaign_id}-summary.txt"
    with open(summary_path, "w") as f:
        f.write(summary)
    print(f"\n  Summary saved: {summary_path}")
    return metrics, summary
