import requests

def test_dashboard():
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
        
        # Get Stats
        stats_url = "http://localhost:8000/api/dashboard/stats"
        headers = {"Authorization": f"Bearer {token}"}
        resp = requests.get(stats_url, headers=headers)
        print(f"Stats Status: {resp.status_code}")
        print(f"Stats Content: {resp.text}")
        print("Stats Response:", resp.json())
        
    except Exception as e:
        print("Error:", e)

if __name__ == "__main__":
    test_dashboard()
