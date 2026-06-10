# evaluate.py
# Classifier accuracy evaluation harness.
# Run this after you've set up your API keys to test the classifier's tier predictions.
#
# Usage: python3 evaluate.py
# Target: >85% accuracy on your real production query sample

from router import classify_query
import sys

TEST_CASES = [
    # (query, expected_tier)
    ("Extract all phone numbers from: 'Call 555-0123 or 555-0199'", "simple"),
    ("Translate 'Good morning' to French", "simple"),
    ("Is this email spam? Subject: 'You won $1,000,000'", "simple"),
    ("Summarise this 800-word product description in three sentences", "moderate"),
    ("Write a Python function that reads a CSV and validates email format in column B", "moderate"),
    (
        "Given these five conflicting regulatory documents, synthesise the EU and US "
        "compliance requirements for a fintech data pipeline",
        "complex",
    ),
    (
        "Our data pipeline fails intermittently under high load. "
        "Here are the logs: [500 lines]. What is causing it?",
        "complex",
    ),
]


def evaluate_classifier(test_cases: list) -> dict:
    """
    Evaluates the classifier against labelled test cases.
    Returns accuracy and per-test results with reasons and errors.
    """
    if not test_cases:
        return {"accuracy": 0.0, "results": []}

    correct = 0
    results = []

    for query, expected in test_cases:
        try:
            classification = classify_query(query)
            predicted = classification.get("tier", "unknown")
            reason = classification.get("reason", "")
            error = None
        except Exception as exc:
            # A single API failure does not kill the eval run — log and continue
            predicted = "error"
            reason = ""
            error = str(exc)

        is_correct = (predicted == expected)
        correct += int(is_correct)

        results.append({
            "query_snippet": query[:80] + "..." if len(query) > 80 else query,
            "expected": expected,
            "predicted": predicted,
            "reason": reason,
            "error": error,
            "correct": is_correct,
        })

    return {
        "accuracy": correct / len(test_cases),
        "results": results,
    }


if __name__ == "__main__":
    print("=" * 70)
    print("CLASSIFIER EVALUATION HARNESS")
    print("=" * 70)
    print()

    report = evaluate_classifier(TEST_CASES)

    print(f"Classifier accuracy: {report['accuracy']:.0%}")
    print()

    passed = 0
    failed = 0

    for r in report["results"]:
        status = "✓" if r["correct"] else "✗"
        label = f"[{r['expected']} → {r['predicted']}]"
        
        if r["correct"]:
            passed += 1
        else:
            failed += 1

        print(f"  {status} {label}")
        print(f"     Query: {r['query_snippet']}")
        if r["reason"]:
            print(f"     Reason: {r['reason']}")
        if r["error"]:
            print(f"     Error: {r['error']}")
        print()

    print("=" * 70)
    print(f"Results: {passed} passed, {failed} failed")

    if report["accuracy"] >= 0.85:
        print("✓ Accuracy is above 85%. Safe to enable live routing.")
        print("=" * 70)
        sys.exit(0)
    else:
        print("✗ Accuracy is below 85%. Review misclassified queries and refine the prompt.")
        print("=" * 70)
        sys.exit(1)
