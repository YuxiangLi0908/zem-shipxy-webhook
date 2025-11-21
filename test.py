import requests
import os 

SEARCH_SHIP_URL = "https://api.shipxy.com/apicall/v3/SearchShip"
ADD_SHIP_URL = "https://api.shipxy.com/apicall/v3/AddFleetShip"
REMOVE_SHIP_URL = "https://api.shipxy.com/apicall/v3/DeleteFleetShip"
FLEET_ID = "2b827b55-a57d-4fd4-9b38-abcfb8ddef54"

if __name__ == "__main__":
    api_key = os.environ.get("SHIPXY_API_KEY")
    # resp = requests.post(
    #     ADD_SHIP_URL,
    #     params = {
    #     "key": api_key,
    #     "fleet_id": FLEET_ID,
    #     "mmsis": "338383024,414951000,256988012",
    # }
    # )

    resp = requests.post(
        REMOVE_SHIP_URL,
        params = {
        "key": api_key,
        "fleet_id": FLEET_ID,
        "mmsis": "338383024",
    }
    )

    print(resp.json())
    print()
    print(resp.headers)
    print()
    print(resp)
