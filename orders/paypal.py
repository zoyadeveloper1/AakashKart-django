import requests
from django.conf import settings

def get_paypal_access_token():
    url = "https://api-m.sandbox.paypal.com/v1/oauth2/token"

    response = requests.post(
        url,
        headers={
            "Accept": "application/json",
            "Accept-Language": "en_US",
        },
        data={"grant_type": "client_credentials"},
        auth=(settings.PAYPAL_CLIENT_ID, settings.PAYPAL_SECRET),
    )

    if response.status_code == 200:
        return response.json().get("access_token")

    print("PayPal Token Error:", response.status_code, response.text)
    return None
