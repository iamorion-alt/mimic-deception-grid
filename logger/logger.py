import os, json, time, threading
from datetime import datetime, timezone
import redis

r = redis.Redis(host=os.getenv("REDIS_HOST", "redis"), port=6379, decode_responses=True)
LOG_FILE = "/logs/events.jsonl"
COWRIE_LOG = os.getenv("COWRIE_LOG", "/cowrie-logs/cowrie.json")

def write_event(event):
    event["ingested_at"] = datetime.now(timezone.utc).isoformat()
    with open(LOG_FILE, "a") as f:
        f.write(json.dumps(event) + "\n")

def redis_listener():
    pubsub = r.pubsub()
    pubsub.subscribe("deception.events")
    for message in pubsub.listen():
        if message["type"] == "message":
            try:
                write_event(json.loads(message["data"]))
            except Exception as e:
                print("Redis parse error:", e)

def cowrie_tailer():
    if not os.path.exists(COWRIE_LOG):
        return
    with open(COWRIE_LOG, "r") as f:
        f.seek(0, 2)
        while True:
            line = f.readline()
            if not line:
                time.sleep(1)
                continue
            try:
                event = json.loads(line)
                event["source"] = "cowrie"
                write_event(event)
            except Exception as e:
                print("Cowrie parse error:", e)

if __name__ == "__main__":
    threading.Thread(target=redis_listener, daemon=True).start()
    threading.Thread(target=cowrie_tailer, daemon=True).start()
    while True:
        time.sleep(10)
