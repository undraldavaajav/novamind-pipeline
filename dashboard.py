import os, json, glob
from http.server import HTTPServer, BaseHTTPRequestHandler
from urllib.parse import urlparse, parse_qs
import threading

def get_campaigns():
    files = sorted(glob.glob("data/*-campaign-log.json"), reverse=True)
    campaigns = []
    for f in files:
        with open(f) as fp:
            data = json.load(fp)
        cid = data.get("campaign_id", "")
        metrics_file = f.replace("-campaign-log.json", "-metrics.json")
        summary_file = f.replace("-campaign-log.json", "-summary.txt")
        metrics = {}
        summary = ""
        if os.path.exists(metrics_file):
            with open(metrics_file) as fp:
                metrics = json.load(fp).get("metrics", {})
        if os.path.exists(summary_file):
            with open(summary_file) as fp:
                summary = fp.read()
        output_files = sorted(glob.glob(f"output/*.json"), reverse=True)
        blog_title = data.get("blog_title", "Unknown")
        campaigns.append({
            "campaign_id": cid,
            "blog_title": blog_title,
            "send_date": data.get("send_date", ""),
            "sends": len(data.get("sends", [])),
            "metrics": metrics,
            "summary": summary
        })
    return campaigns

HTML = """<!DOCTYPE html>
<html>
<head>
<title>NovaMind Pipeline Dashboard</title>
<style>
* {{ box-sizing: border-box; margin: 0; padding: 0; font-family: -apple-system, sans-serif; }}
body {{ background: #0f0f0f; color: #e0e0e0; padding: 32px; }}
h1 {{ font-size: 24px; font-weight: 600; margin-bottom: 4px; color: #fff; }}
.subtitle {{ color: #888; font-size: 14px; margin-bottom: 32px; }}
.run-box {{ background: #1a1a1a; border: 1px solid #333; border-radius: 12px; padding: 24px; margin-bottom: 32px; }}
.run-box h2 {{ font-size: 16px; margin-bottom: 16px; color: #fff; }}
input {{ background: #111; border: 1px solid #444; color: #fff; padding: 10px 14px; border-radius: 8px; width: 400px; font-size: 14px; }}
button {{ background: #6c5ce7; color: #fff; border: none; padding: 10px 20px; border-radius: 8px; font-size: 14px; cursor: pointer; margin-left: 8px; }}
button:hover {{ background: #5b4dd6; }}
.status {{ margin-top: 12px; font-size: 13px; color: #aaa; }}
.campaigns h2 {{ font-size: 16px; margin-bottom: 16px; color: #fff; }}
.card {{ background: #1a1a1a; border: 1px solid #333; border-radius: 12px; padding: 20px; margin-bottom: 16px; }}
.card-title {{ font-size: 16px; font-weight: 600; color: #fff; margin-bottom: 4px; }}
.card-meta {{ font-size: 12px; color: #666; margin-bottom: 16px; }}
.metrics {{ display: flex; gap: 12px; flex-wrap: wrap; margin-bottom: 16px; }}
.metric {{ background: #111; border-radius: 8px; padding: 10px 14px; min-width: 120px; }}
.metric-label {{ font-size: 11px; color: #666; margin-bottom: 2px; }}
.metric-value {{ font-size: 18px; font-weight: 600; color: #6c5ce7; }}
.metric-name {{ font-size: 11px; color: #888; margin-top: 2px; }}
.summary {{ background: #111; border-radius: 8px; padding: 14px; font-size: 13px; color: #aaa; line-height: 1.6; }}
.empty {{ color: #555; font-size: 14px; text-align: center; padding: 40px; }}
</style>
</head>
<body>
<h1>NovaMind Pipeline Dashboard</h1>
<p class="subtitle">AI-powered marketing content pipeline</p>

<div class="run-box">
  <h2>Run New Campaign</h2>
  <input type="text" id="topic" placeholder="Enter blog topic e.g. AI in creative automation" />
  <button onclick="runPipeline()">Run Pipeline</button>
  <div class="status" id="status"></div>
</div>

<div class="campaigns">
  <h2>Campaign History</h2>
  {campaigns_html}
</div>

<script>
async function runPipeline() {{
  const topic = document.getElementById("topic").value.trim();
  if (!topic) return alert("Please enter a topic!");
  document.getElementById("status").textContent = "Running pipeline... this takes about 30 seconds";
  document.querySelector("button").disabled = true;
  try {{
    const r = await fetch("/run?topic=" + encodeURIComponent(topic));
    const d = await r.json();
    if (d.success) {{
      document.getElementById("status").textContent = "Done! Blog: " + d.blog_title;
      setTimeout(() => location.reload(), 1500);
    }} else {{
      document.getElementById("status").textContent = "Error: " + d.error;
    }}
  }} catch(e) {{
    document.getElementById("status").textContent = "Error: " + e.message;
  }}
  document.querySelector("button").disabled = false;
}}
</script>
</body>
</html>"""

def build_campaigns_html(campaigns):
    if not campaigns:
        return "<div class='empty'>No campaigns yet. Run your first one above!</div>"
    html = ""
    for c in campaigns:
        metrics_html = ""
        for persona, m in c["metrics"].items():
            name = persona.replace("_", " ").title()
            metrics_html += f"""
            <div class="metric">
                <div class="metric-label">Open rate</div>
                <div class="metric-value">{m.get("open_rate",0)*100:.1f}%</div>
                <div class="metric-name">{name}</div>
            </div>
            <div class="metric">
                <div class="metric-label">Click rate</div>
                <div class="metric-value">{m.get("click_rate",0)*100:.1f}%</div>
                <div class="metric-name">{name}</div>
            </div>"""
        summary_html = f"<div class='summary'>{c['summary']}</div>" if c["summary"] else ""
        html += f"""
        <div class="card">
            <div class="card-title">{c["blog_title"]}</div>
            <div class="card-meta">{c["campaign_id"]} &bull; {c["send_date"][:10]} &bull; {c["sends"]} sends</div>
            <div class="metrics">{metrics_html}</div>
            {summary_html}
        </div>"""
    return html

class Handler(BaseHTTPRequestHandler):
    def log_message(self, format, *args): pass
    def do_GET(self):
        parsed = urlparse(self.path)
        if parsed.path == "/run":
            params = parse_qs(parsed.query)
            topic = params.get("topic", ["AI automation"])[0]
            try:
                from generate import run as gen_run
                from crm import run as crm_run
                from analytics import run as analytics_run
                from optimizer import suggest_topics
                blog, newsletters, path, cid = gen_run(topic)
                log = crm_run(blog, newsletters, cid)
                metrics, summary = analytics_run(blog, log, cid)
                suggest_topics(metrics, blog["title"])
                self.send_response(200)
                self.send_header("Content-type", "application/json")
                self.end_headers()
                self.wfile.write(json.dumps({"success": True, "blog_title": blog["title"]}).encode())
            except Exception as e:
                self.send_response(500)
                self.send_header("Content-type", "application/json")
                self.end_headers()
                self.wfile.write(json.dumps({"success": False, "error": str(e)}).encode())
        else:
            campaigns = get_campaigns()
            campaigns_html = build_campaigns_html(campaigns)
            html = HTML.format(campaigns_html=campaigns_html)
            self.send_response(200)
            self.send_header("Content-type", "text/html")
            self.end_headers()
            self.wfile.write(html.encode())

def run():
    server = HTTPServer(("localhost", 8080), Handler)
    print("\nDashboard running at: http://localhost:8080")
    print("Press Ctrl+C to stop")
    server.serve_forever()

run()

