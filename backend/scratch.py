from report.aggregator import generate_report

pipeline_output = {
    "code": "print('hello')",
    "test_suite": "def test_hello(): pass",
    "test_results": {
        "passed": True,
        "output": "test passed",
        "coverage": "100%"
    },
    "vulnerabilities": [{"title": "vuln1"}]
}

try:
    generate_report(pipeline_output)
    print("Report generated successfully.")
except Exception as exc:
    print(f"Exception string: {exc}")
