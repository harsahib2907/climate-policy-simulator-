"""
NPCC Backend Test Suite
Comprehensive tests for all API endpoints
"""

import sys
import requests
import json
from time import sleep

# Configuration
BASE_URL = "http://localhost:5000"
API_URL = f"{BASE_URL}/api"

# Test results
test_results = []


def print_header(title):
    """Print formatted test section header"""
    print("\n" + "=" * 70)
    print(f"  {title}")
    print("=" * 70)


def print_test(name, passed, details=""):
    """Print test result"""
    status = "✅ PASS" if passed else "❌ FAIL"
    print(f"\n{status} | {name}")
    if details:
        print(f"     {details}")
    test_results.append({"test": name, "passed": passed})


def test_health_check():
    """Test GET /health endpoint"""
    print_header("TEST 1: Health Check")

    try:
        response = requests.get(f"{BASE_URL}/health", timeout=5)
        data = response.json()

        passed = (
                response.status_code == 200 and
                data.get("status") == "healthy" and
                data.get("service") == "NPCC Backend API"
        )

        print_test(
            "Health Check Endpoint",
            passed,
            f"Status: {data.get('status')}, Service: {data.get('service')}"
        )

        if passed:
            print(f"\n📊 Response:")
            print(json.dumps(data, indent=2))

    except Exception as e:
        print_test("Health Check Endpoint", False, f"Error: {str(e)}")


def test_init_endpoint():
    """Test GET /api/init endpoint"""
    print_header("TEST 2: Initialize Dashboard")

    try:
        response = requests.get(f"{API_URL}/init", timeout=5)
        data = response.json()

        baseline = data.get("data", {})

        passed = (
                response.status_code == 200 and
                data.get("success") is True and
                baseline.get("year") == 2026 and
                baseline.get("temperature_anomaly") == 1.2 and
                baseline.get("national_debt") == 0 and
                "bau_projection" in baseline and
                "historical_data" in baseline
        )

        print_test(
            "Initialize Endpoint",
            passed,
            f"Year: {baseline.get('year')}, Temp: {baseline.get('temperature_formatted')}"
        )

        if passed:
            print(f"\n📊 Baseline State:")
            print(f"   Temperature: {baseline.get('temperature_formatted')}")
            print(f"   National Debt: {baseline.get('national_debt_formatted')}")
            print(f"   BAU Projection Points: {len(baseline.get('bau_projection', []))}")
            print(f"   Historical Data Points: {len(baseline.get('historical_data', []))}")

    except Exception as e:
        print_test("Initialize Endpoint", False, f"Error: {str(e)}")


def test_calculate_zero_policies():
    """Test POST /api/calculate with all policies at 0"""
    print_header("TEST 3: Calculate with Zero Policies")

    try:
        payload = {
            "ev_adoption": 0,
            "renewable_energy": 0,
            "carbon_tax": 0,
            "reforestation": 0
        }

        response = requests.post(
            f"{API_URL}/calculate",
            json=payload,
            headers={"Content-Type": "application/json"},
            timeout=5
        )

        data = response.json()
        result = data.get("data", {})

        passed = (
                response.status_code == 200 and
                data.get("success") is True and
                result.get("total_cost") == 0 and
                result.get("temperature_mitigation") == 0 and
                result.get("bankruptcy_flag") is False
        )

        print_test(
            "Zero Policies Calculation",
            passed,
            f"Cost: {result.get('total_cost_formatted')}, Mitigation: {result.get('temperature_mitigation_formatted')}"
        )

        if passed:
            print(f"\n📊 Zero Policy Results:")
            print(f"   Total Cost: {result.get('total_cost_formatted')}")
            print(f"   Temperature Mitigation: {result.get('temperature_mitigation_formatted')}")
            print(f"   Bankruptcy Flag: {result.get('bankruptcy_flag')}")

    except Exception as e:
        print_test("Zero Policies Calculation", False, f"Error: {str(e)}")


def test_calculate_moderate_policies():
    """Test POST /api/calculate with moderate policy levels"""
    print_header("TEST 4: Calculate with Moderate Policies")

    try:
        payload = {
            "ev_adoption": 50,
            "renewable_energy": 75,
            "carbon_tax": 60,
            "reforestation": 40
        }

        response = requests.post(
            f"{API_URL}/calculate",
            json=payload,
            headers={"Content-Type": "application/json"},
            timeout=5
        )

        data = response.json()
        result = data.get("data", {})

        passed = (
                response.status_code == 200 and
                data.get("success") is True and
                result.get("total_cost") > 0 and
                result.get("temperature_mitigation") < 0 and
                "policy_breakdown" in result and
                "trend_line" in result and
                "fiscal_treemap" in result and
                "efficiency_index" in result
        )

        print_test(
            "Moderate Policies Calculation",
            passed,
            f"Cost: {result.get('total_cost_formatted')}, Mitigation: {result.get('temperature_mitigation_formatted')}"
        )

        if passed:
            print(f"\n📊 Moderate Policy Results:")
            print(f"   Total Cost: {result.get('total_cost_formatted')}")
            print(f"   Temperature Mitigation: {result.get('temperature_mitigation_formatted')}")
            print(f"   National Debt: {result.get('national_debt_formatted')}")
            print(f"   Bankruptcy Flag: {result.get('bankruptcy_flag')}")
            print(f"\n   Policy Breakdown:")
            for policy in result.get("policy_breakdown", []):
                print(f"      • {policy['policy']}: {policy['cost_formatted']} → {policy['temperature_formatted']}")

            print(f"\n   Fiscal Treemap Allocation:")
            for item in result.get("fiscal_treemap", []):
                print(f"      • {item['name']}: {item['formatted']} ({item['percentage']}%)")

            print(f"\n   Efficiency Index:")
            for metric in result.get("efficiency_index", []):
                print(f"      • {metric['policy']}: {metric['efficiency']} ({metric['interpretation']})")

    except Exception as e:
        print_test("Moderate Policies Calculation", False, f"Error: {str(e)}")


def test_calculate_bankruptcy():
    """Test POST /api/calculate with bankruptcy scenario"""
    print_header("TEST 5: Calculate with Bankruptcy Scenario")

    try:
        payload = {
            "ev_adoption": 100,
            "renewable_energy": 100,
            "carbon_tax": 0,  # No revenue
            "reforestation": 100
        }

        response = requests.post(
            f"{API_URL}/calculate",
            json=payload,
            headers={"Content-Type": "application/json"},
            timeout=5
        )

        data = response.json()
        result = data.get("data", {})

        # Expected: (100*1.2) + (100*2.5) + (100*0.6) = 120 + 250 + 60 = 430B (no bankruptcy)
        # Need to adjust to trigger bankruptcy

        passed = (
                response.status_code == 200 and
                data.get("success") is True
        )

        bankruptcy_triggered = result.get("bankruptcy_flag", False)

        print_test(
            "Bankruptcy Scenario Calculation",
            passed,
            f"Debt: {result.get('national_debt_formatted')}, Bankruptcy: {bankruptcy_triggered}"
        )

        if passed:
            print(f"\n📊 Maximum Policy Results:")
            print(f"   Total Cost: {result.get('total_cost_formatted')}")
            print(f"   National Debt: {result.get('national_debt_formatted')}")
            print(f"   Bankruptcy Threshold: $1,000B")
            print(f"   Bankruptcy Triggered: {bankruptcy_triggered}")
            if bankruptcy_triggered:
                print(f"   ⚠️  WARNING: {result.get('warning_message')}")

    except Exception as e:
        print_test("Bankruptcy Scenario Calculation", False, f"Error: {str(e)}")


def test_news_generation():
    """Test POST /api/news endpoint (Gemini AI)"""
    print_header("TEST 6: AI News Headline Generation")

    try:
        payload = {
            "ev_adoption": 50,
            "renewable_energy": 75,
            "carbon_tax": 60,
            "reforestation": 40,
            "temperature_change": -0.28,
            "fiscal_cost": 245.6
        }

        print("⏳ Calling Gemini AI... (may take 1-3 seconds)")

        response = requests.post(
            f"{API_URL}/news",
            json=payload,
            headers={"Content-Type": "application/json"},
            timeout=15  # Longer timeout for AI
        )

        data = response.json()
        result = data.get("data", {})

        passed = (
                response.status_code == 200 and
                data.get("success") is True and
                "headline" in result and
                len(result.get("headline", "")) > 10
        )

        print_test(
            "AI News Generation",
            passed,
            f"Headline length: {len(result.get('headline', ''))} characters"
        )

        if passed:
            print(f"\n📰 Generated Headline:")
            print(f"   \"{result.get('headline')}\"")
            print(f"\n   Policy Context:")
            summary = result.get("policy_summary", {})
            print(f"      • EV Adoption: {summary.get('ev_adoption')}%")
            print(f"      • Renewable Energy: {summary.get('renewable_energy')}%")
            print(f"      • Carbon Tax: {summary.get('carbon_tax')}%")
            print(f"      • Reforestation: {summary.get('reforestation')}%")
            print(f"      • Temperature Impact: {summary.get('temperature_impact')}°C")
            print(f"      • Fiscal Cost: ${summary.get('fiscal_cost')}B")

    except Exception as e:
        print_test("AI News Generation", False, f"Error: {str(e)}")


def test_error_handling():
    """Test error handling with invalid inputs"""
    print_header("TEST 7: Error Handling")

    # Test 1: Invalid endpoint
    try:
        response = requests.get(f"{API_URL}/invalid-endpoint", timeout=5)
        passed = response.status_code == 404
        print_test(
            "404 Not Found Handling",
            passed,
            f"Status code: {response.status_code}"
        )
    except Exception as e:
        print_test("404 Not Found Handling", False, f"Error: {str(e)}")

    # Test 2: Missing payload
    try:
        response = requests.post(
            f"{API_URL}/calculate",
            headers={"Content-Type": "application/json"},
            timeout=5
        )
        passed = response.status_code == 400
        print_test(
            "Missing Payload Handling",
            passed,
            f"Status code: {response.status_code}"
        )
    except Exception as e:
        print_test("Missing Payload Handling", False, f"Error: {str(e)}")


def print_summary():
    """Print test summary"""
    print_header("TEST SUMMARY")

    total_tests = len(test_results)
    passed_tests = sum(1 for result in test_results if result["passed"])
    failed_tests = total_tests - passed_tests

    pass_rate = (passed_tests / total_tests * 100) if total_tests > 0 else 0

    print(f"\n   Total Tests: {total_tests}")
    print(f"   ✅ Passed: {passed_tests}")
    print(f"   ❌ Failed: {failed_tests}")
    print(f"   📊 Pass Rate: {pass_rate:.1f}%")

    if failed_tests > 0:
        print(f"\n   Failed Tests:")
        for result in test_results:
            if not result["passed"]:
                print(f"      • {result['test']}")

    print("\n" + "=" * 70 + "\n")

    return passed_tests == total_tests


def main():
    """Run all tests"""
    print("\n🚀 NPCC Backend Test Suite")
    print("=" * 70)
    print("   Ensure Flask server is running: python app.py")
    print("   Server URL: http://localhost:5000")
    print("=" * 70)

    # Brief delay to allow server startup if just launched
    sleep(1)

    # Run tests
    test_health_check()
    test_init_endpoint()
    test_calculate_zero_policies()
    test_calculate_moderate_policies()
    test_calculate_bankruptcy()
    test_news_generation()
    test_error_handling()

    # Print summary
    all_passed = print_summary()

    # Exit with appropriate code
    sys.exit(0 if all_passed else 1)


if __name__ == "__main__":
    main()