# shadow.py
# Shadow mode classifier — run alongside your existing system to measure real query distribution.
# This does NOT change any routing. It only logs predictions for analysis.
#
# Usage: Import shadow_classify() into your existing request handler and call it.
# After two weeks of logging, analyze tier distribution to validate routing assumptions.

from router import classify_query
import json
from datetime import datetime


def shadow_classify(user_input: str, request_id: str) -> dict:
    """
    Classifies the query and logs the predicted tier WITHOUT acting on it.
    Used to measure real query distribution before enabling live routing.

    Args:
        user_input: The user's query
        request_id: Unique identifier for this request (for logging correlation)

    Returns:
        {
            "tier": str — predicted tier ("simple", "moderate", "complex", or "error")
            "reason": str — classifier's reasoning
            "timestamp": str — ISO timestamp when classified
            "request_id": str — the request_id passed in
        }
    """
    result = {
        "tier": "error",
        "reason": "",
        "timestamp": datetime.utcnow().isoformat(),
        "request_id": request_id,
    }

    try:
        classification = classify_query(user_input)

        if not isinstance(classification, dict):
            raise ValueError("Classifier returned non-dict JSON")

        tier = classification.get("tier", "unknown")
        reason = classification.get("reason", "")

        result["tier"] = tier
        result["reason"] = reason

        # Log the prediction — replace print() with your observability stack
        # (Datadog, Grafana, CloudWatch, Sumologic, etc.)
        log_entry = {
            "timestamp": result["timestamp"],
            "request_id": request_id,
            "tier": tier,
            "query_length": len(user_input),
            "query_snippet": user_input[:100],
        }
        print(f"[SHADOW] {json.dumps(log_entry)}")

    except Exception as exc:
        result["tier"] = "error"
        result["reason"] = str(exc)
        print(f"[SHADOW ERROR] request_id={request_id} | error={str(exc)}")

    return result


if __name__ == "__main__":
    # Demo: classify some sample queries and show the output format
    sample_queries = [
        ("Extract invoice number from email", "req-001"),
        ("Write Python function for CSV validation", "req-002"),
        ("Synthesise conflicting regulations", "req-003"),
    ]

    print("=" * 70)
    print("SHADOW MODE — SAMPLE OUTPUT")
    print("=" * 70)
    print()

    for query, req_id in sample_queries:
        result = shadow_classify(query, req_id)
        print(f"Request {req_id}: tier={result['tier']}")
        print()

    print("=" * 70)
    print("After 2 weeks of shadow mode in production, analyze tier distribution.")
    print("Aggregate counts of 'simple', 'moderate', 'complex' from your logs.")
    print("This real distribution validates your cost model before live routing.")
    print("=" * 70)
