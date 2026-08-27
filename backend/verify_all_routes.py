import urllib.request
import urllib.parse
import json
import sys

BASE_URL = "http://127.0.0.1:5000"

def check_endpoint(name, path, expected_strings=None):
    url = f"{BASE_URL}{path}"
    try:
        req = urllib.request.Request(url, headers={'User-Agent': 'FlavorBridge-Tester/1.0'})
        with urllib.request.urlopen(req) as resp:
            content = resp.read().decode('utf-8')
            status = resp.status
            if status != 200:
                print(f"[FAIL] {name} ({path}) returned status {status}")
                return False

            if expected_strings:
                for expected in expected_strings:
                    if expected not in content:
                        print(f"[FAIL] {name} ({path}) missing expected string: '{expected}'")
                        return False

            print(f"[PASS] {name} ({path}) -> Status 200 OK")
            return True
    except Exception as e:
        print(f"[FAIL] {name} ({path}) failed with error: {e}")
        return False

def check_post_api(name, path, payload, expected_keys=None):
    url = f"{BASE_URL}{path}"
    try:
        data = json.dumps(payload).encode('utf-8')
        req = urllib.request.Request(url, data=data, headers={
            'Content-Type': 'application/json',
            'User-Agent': 'FlavorBridge-Tester/1.0'
        })
        with urllib.request.urlopen(req) as resp:
            raw = resp.read().decode('utf-8')
            res_json = json.loads(raw)
            if expected_keys:
                for key in expected_keys:
                    if key not in res_json:
                        print(f"[FAIL] {name} ({path}) missing key '{key}' in JSON response")
                        return False
            print(f"[PASS] {name} ({path}) -> JSON API OK (reply: '{res_json.get('reply', '')[:50]}...')")
            return True
    except Exception as e:
        print(f"[FAIL] {name} ({path}) failed with error: {e}")
        return False

def main():
    print("--- LIVE WEB ENDPOINT VERIFICATION ---")
    all_ok = True

    # 1. Homepage
    all_ok &= check_endpoint("Homepage", "/", ["Discover the Taste of", "Explore by Food Category", "Popular Regional Delicacies", "Meet Our Verified Traditional Food Makers"])

    # 2. Products Listing
    all_ok &= check_endpoint("Products Catalog", "/products", ["All Regional Delicacies", "Spice Powders", "Filters"])

    # 3. Product Filter by Category
    all_ok &= check_endpoint("Category Filter", "/products?category=Traditional+Sweets", ["Tirunelveli Halwa", "Mysore Pak"])

    # 4. Product Detail Page
    all_ok &= check_endpoint("Product Detail (Halwa)", "/product/16", ["Tirunelveli Halwa", "Crafted By Traditional Maker", "Customer Ratings & Reviews"])

    # 5. Food Makers Directory
    all_ok &= check_endpoint("Food Makers Directory", "/food-makers", ["Priya Sundaram", "Kumaravel M", "Lakshmi Narayanan", "Arunachalam S", "Meenakshi R"])

    # 6. Food Maker Public Profile
    all_ok &= check_endpoint("Food Maker Profile (Priya)", "/food-maker/1", ["Priya Sundaram", "Verified Maker", "Authentic Delicacies by"])

    # 7. AI Recommendations Hub
    all_ok &= check_endpoint("AI Recommendations", "/recommendations", ["Curated Delicacies For You", "Personalized Top Picks", "Trending Regional Delicacies"])

    # 8. Local Recipe Partner Matcher
    all_ok &= check_endpoint("Recipe Partners", "/recipe-partners?dish=Madurai+Kari+Dosa&city=Madurai", ["Matched Culinary Partners", "Match Score"])

    # 9. Smart Search Page
    all_ok &= check_endpoint("Smart TF-IDF Search", "/smart-search?q=spicy+Tamil+food", ["Search Results for", "Relevance"])

    # 10. Regional Food Assistant UI
    all_ok &= check_endpoint("Food Assistant UI", "/food-assistant", ["Regional Food Assistant", "FlavorBridge Culinary Guide", "Suggested Queries"])

    # 11. Regional Food Assistant JSON API
    all_ok &= check_post_api("Food Assistant API", "/api/food-assistant", {"query": "I want spicy food from Tamil Nadu under 300"}, ["reply", "products", "filters", "safety_note"])

    # 12. Login, Register, & Forgot Password Pages & Role Portals
    all_ok &= check_endpoint("Customer Login Portal", "/login?role=customer", ["Customer Sign In", "Registered Email Address"])
    all_ok &= check_endpoint("Food Maker Partner Portal", "/maker-login", ["Food Maker Partner Portal", "Registered Email Address"])
    all_ok &= check_endpoint("Forgot Password Page", "/forgot-password", ["Reset Your Password", "Registered Email Address"])
    all_ok &= check_endpoint("Register Page", "/register", ["Join FlavorBridge", "Account Type", "Customer", "Food Maker"])

    print("--------------------------------------")
    if all_ok:
        print("[ALL TESTS PASSED] 100% of FlavorBridge endpoints and live AI services are working flawlessly!")
    else:
        print("[WARNING] Some endpoints failed.")
        sys.exit(1)

if __name__ == '__main__':
    main()
