"""Quick end-to-end smoke test for all DesignMentor AI endpoints."""
import urllib.request
import json

BASE = "http://localhost:8000"


def post(path, payload):
    data = json.dumps(payload).encode()
    req = urllib.request.Request(
        BASE + path, data=data,
        headers={"Content-Type": "application/json"}, method="POST"
    )
    r = urllib.request.urlopen(req, timeout=120)
    return json.loads(r.read())


def get(path):
    r = urllib.request.urlopen(BASE + path, timeout=10)
    return json.loads(r.read())


# 1. Health
print("=" * 60)
print("1. GET /health")
resp = get("/health")
print(resp)

# 2. Design
print("\n" + "=" * 60)
print("2. POST /design  (topic: Instagram)")
resp = post("/design", {"topic": "Instagram"})
session_id = resp["session_id"]
print(f"session_id : {session_id}")
print(f"topic      : {resp['topic']}")
print(f"design snippet:\n{resp['design'][:800]}\n...")

# 3. Interview start
print("\n" + "=" * 60)
print("3. POST /interview/start  (topic: Netflix)")
resp = post("/interview/start", {"topic": "Netflix"})
interview_session = resp["session_id"]
print(f"session_id     : {interview_session}")
print(f"first_question : {resp['first_question']}")

# 4. Interview answer
print("\n" + "=" * 60)
print("4. POST /interview/answer")
resp = post("/interview/answer", {
    "session_id": interview_session,
    "answer": "I would use a CDN like CloudFront to cache video chunks close to users, "
              "reducing latency. The backend would use microservices: one for user management, "
              "one for recommendations, and one for streaming. Videos are stored in S3 and "
              "transcoded via AWS Elemental MediaConvert into adaptive bitrate formats."
})
print(f"is_complete    : {resp['is_complete']}")
print(f"evaluation snippet:\n{resp['evaluation'][:500]}\n...")
if resp["next_question"]:
    print(f"next_question  : {resp['next_question'][:200]}")

# 5. One-shot evaluate
print("\n" + "=" * 60)
print("5. POST /evaluate")
resp = post("/evaluate", {
    "question": "How would you design the database schema for a social media platform?",
    "user_answer": "I'd use a relational DB for user profiles and friendships, "
                   "and a NoSQL store like Cassandra for posts and feeds due to high write throughput."
})
print(f"evaluation snippet:\n{resp['evaluation'][:500]}\n...")

# 6. Chat
print("\n" + "=" * 60)
print("6. POST /chat")
resp = post("/chat", {"message": "What are the key trade-offs between SQL and NoSQL databases?"})
print(f"session_id : {resp['session_id']}")
print(f"reply snippet:\n{resp['reply'][:400]}\n...")

print("\n" + "=" * 60)
print("ALL TESTS PASSED")
