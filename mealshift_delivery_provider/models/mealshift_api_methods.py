from odoo.http import request

import requests
import time

BASE_URL = "https://dev.mealshift.co.uk"
PARTNER = "odoo"
MS_PARTNER_ID = "b7a561f5cf94d8513079365a0757fbcc"
SECRET = "1292d661f8a65493c3ccc7f152211a89b56214f823d1266f17e70cf254da2e49"

# HEADERS = {
#     'ms-partner-id': MS_PARTNER_ID
# }

def generate_auth_token(configuration_parameters):
    endpoint_url = "/api/v2/auth/token"
    token_value = None
    token_expiration = None

    full_url = configuration_parameters['base_url'] + endpoint_url

    headers = {
        'ms-partner-id': configuration_parameters['ms_partner_id']
    }

    body = {
        "secret": configuration_parameters['secret']
    }

    response = requests.post(full_url, headers=headers, json=body)


    if response.status_code == 200:
        token_value = response.json()['token']
        token_expiration = response.json()['expiresIn']

    return token_value, token_expiration


def check_token_validity_existance(configuration_parameters):
    # should save token for every delivery method
    env = request.env
    ir_config = env['ir.config_parameter'].sudo()
    mealshift_token_value = ir_config.get_param('mealshift_delivery_provider.token_value' + configuration_parameters['id'])
    mealshift_token_expiration = ir_config.get_param('mealshift_delivery_provider.token_expiration' + configuration_parameters['id'])

    current_time_in_seconds = int(time.time())

    if mealshift_token_expiration:
        if current_time_in_seconds - int(mealshift_token_expiration) >= 0:
            token_value, token_expiration = generate_auth_token(configuration_parameters)
            ir_config.set_param('mealshift_delivery_provider.token_value' + configuration_parameters['id'], token_value)
            ir_config.set_param('mealshift_delivery_provider.token_expiration' + configuration_parameters['id'], current_time_in_seconds + token_expiration)
            mealshift_token_value = token_value
    else:
        token_value, token_expiration = generate_auth_token(configuration_parameters)
        ir_config.set_param('mealshift_delivery_provider.token_value' + configuration_parameters['id'], token_value)
        ir_config.set_param('mealshift_delivery_provider.token_expiration' + configuration_parameters['id'], current_time_in_seconds + token_expiration)
        mealshift_token_value = token_value

    return mealshift_token_value

def request_quote(configuration_parameters, data):
    endpoint_url = "/api/v2/integration/{}/request-quote"
    full_url = configuration_parameters['base_url'] + endpoint_url.format(configuration_parameters['partner'])

    mealshift_token_value = check_token_validity_existance(configuration_parameters)

    quote_amount = None
    quote_currency = None

    if mealshift_token_value:
        headers = {
            'ms-partner-id': configuration_parameters['ms_partner_id'],
            'ms-partner-token': mealshift_token_value
        }

        response = requests.post(full_url, headers=headers, json=data)
        print("This is response: ", response, "this is reponse json: ", response.json())
        if response.status_code == 200:
            response_json = response.json()
            quote_amount = response_json['price']['decimal']
            quote_currency = response_json['price']['currency']

    return quote_amount, quote_currency


def publish_order(configuration_parameters, data):
    endpoint_url = "/api/v2/integration/{}/publish"
    full_url = configuration_parameters['base_url'] + endpoint_url.format(configuration_parameters['partner'])

    mealshift_token_value = check_token_validity_existance(configuration_parameters)

    mealshift_order_id = None
    mealshift_partner_reference = None

    if mealshift_token_value:
        headers = {
            'ms-partner-id': configuration_parameters['ms_partner_id'],
            'ms-partner-token': mealshift_token_value
        }

        response = requests.post(full_url, headers=headers, json=data)
        print("publish order called: ", response)
        if response.status_code == 200:
            response_json = response.json()
            mealshift_order_id = response_json['id']
            mealshift_partner_reference = response_json['reference']

    return mealshift_order_id, mealshift_partner_reference


def cancel_order(configuration_parameters, data):
    endpoint_url = "/api/v2/integration/{}/cancel"
    full_url = configuration_parameters['base_url'] + endpoint_url.format(configuration_parameters['partner'])
    mealshift_token_value = check_token_validity_existance(configuration_parameters)
    canceled = False

    if mealshift_token_value:
        headers = {
            'ms-partner-id': configuration_parameters['ms_partner_id'],
            'ms-partner-token': mealshift_token_value
        }

        response = requests.post(full_url, headers=headers, json=data)

        if response.status_code == 200:
            canceled = True



    return canceled

