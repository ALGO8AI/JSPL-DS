import requests

def test_calculate_preparation_time():
    url = "http://127.0.0.1:5000/calculate-preparation-time"
    input_data = {
        "delays": [
            {"Machine breakdown": 15},
            {"Material shortage": 20},
            {"Quality inspection": 10}
        ],
        "Mainteinence": [
            {"Electrode change": 15},
            {"Gunning": 20},
            {"Other": 10}
        ]
    }

    try:
        response = requests.post(url, json=input_data)
        print("Response status code:", response.status_code)
        print("Response JSON:", response.json())
    except requests.exceptions.RequestException as e:
        print("An error occurred:", e)

if __name__ == "__main__":
    test_calculate_preparation_time()
