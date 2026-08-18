import requests

def test_reports():
    # Login
    login_url = "http://localhost:8000/api/auth/login"
    login_data = {"username": "admin", "password": "123456"}
    try:
        resp = requests.post(login_url, json=login_data)
        if resp.status_code != 200:
            print("Login failed:", resp.text)
            return
        
        token = resp.json()['data']['token']
        print(f"Got token: {token[:10]}...")
        headers = {"Authorization": f"Bearer {token}"}
        
        # Test reports_dashboard
        url = "http://localhost:8000/api/reports/dashboard"
        resp = requests.get(url, headers=headers)
        print(f"Reports Dashboard Status: {resp.status_code}")
        if resp.status_code == 200:
            print("Reports Dashboard Data:", resp.json())
        else:
            print("Reports Dashboard Error:", resp.text)

        # Test reports_daily
        url = "http://localhost:8000/api/reports/daily"
        resp = requests.get(url, headers=headers)
        print(f"Reports Daily Status: {resp.status_code}")
        if resp.status_code == 200:
            # Print first item
            data = resp.json()['data']
            print("Reports Daily Data (first 1):", data['list'][0] if data['list'] else "Empty")
        else:
            print("Reports Daily Error:", resp.text)
            
    except Exception as e:
        print("Error:", e)

if __name__ == "__main__":
    test_reports()
