import os, time, random, json
from flask import Flask, request, render_template_string
import redis

app = Flask(__name__)
r = redis.Redis(host=os.getenv("REDIS_HOST", "redis"), port=6379, decode_responses=True)

THEMES = [
    {"name": "WordPress", "title": "WordPress Login", "css": "body{font-family:sans-serif;background:#f0f0f1;}"},
    {"name": "phpMyAdmin", "title": "phpMyAdmin", "css": "body{font-family:monospace;background:#fff;}"},
    {"name": "Joomla", "title": "Joomla Administrator", "css": "body{font-family:Arial;background:#eef;}",
]

@app.route("/", methods=["GET", "POST"])
def login():
    theme = random.choice(THEMES)
    if request.method == "POST":
        event = {
            "ts": time.time(),
            "source": "mimic-web",
            "theme": theme["name"],
            "ip": request.remote_addr,
            "method": request.method,
            "path": request.path,
            "username": request.form.get("username") or request.form.get("user"),
            "password": request.form.get("password") or request.form.get("pass"),
            "user_agent": request.headers.get("User-Agent"),
        }
        r.publish("deception.events", json.dumps(event))
        return "Invalid credentials", 401

    html = f"""
    <!doctype html>
    <html>
      <head><title>{theme['title']}</title><style>{theme['css']}</style></head>
      <body>
        <h1>{theme['title']}</h1>
        <form method="post">
          <input name="username" placeholder="Username"><br>
          <input name="password" type="password" placeholder="Password"><br>
          <button>Login</button>
        </form>
      </body>
    </html>
    """
    return render_template_string(html)

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)
