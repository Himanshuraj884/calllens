import json, statistics as st
import store

def compute():
    calls, events, fb = store.all_rows("calls"), store.all_rows("events"), store.all_rows("feedback")
    per_user = {}
    for c in calls:
        per_user.setdefault(c["user_id"], []).append(c)
    users = len(per_user)
    repeat = sum(1 for v in per_user.values() if len(v) >= 2)
    ratings = [f["rating"] for f in fb if f["rating"]]
    flags = [x for f in fb for x in json.loads(f["confirmed"] or "[]") if x is not None]
    asked = {e["call_id"] for e in events if e["name"] == "ask"}
    totals = [c["total_seconds"] for c in calls]
    return {
        "calls": len(calls), "pilot_users": users,
        "repeat_use_rate": round(repeat / users, 2) if users else None,
        "median_latency_s": round(st.median(totals), 1) if totals else None,
        "avg_summary_rating": round(sum(ratings) / len(ratings), 2) if ratings else None,
        "action_item_precision": round(sum(flags) / len(flags), 2) if flags else None,
        "qa_adoption_rate": round(len(asked) / len(calls), 2) if calls else None,
        "feedback_responses": len(fb),
    }
