import sys
from generate import run as generate_run
from crm import run as crm_run
from analytics import run as analytics_run

def run_pipeline(topic):
    print("=" * 55)
    print("   NovaMind AI Marketing Pipeline")
    print("=" * 55)
    blog, newsletters, path, campaign_id = generate_run(topic)
    campaign_log = crm_run(blog, newsletters, campaign_id)
    metrics, summary = analytics_run(blog, campaign_log, campaign_id)
    print("\n" + "=" * 55)
    print("Pipeline complete!")
    print(f"  Topic:      {topic}")
    print(f"  Blog:       {blog['title']}")
    print(f"  Campaign:   {campaign_id}")
    print(f"  Output:     {path}")
    print("=" * 55)

if __name__ == "__main__":
    topic = " ".join(sys.argv[1:]) if len(sys.argv) > 1 else "AI in creative workflow automation"
    run_pipeline(topic)
