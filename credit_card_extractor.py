import re
from datetime import datetime
import json
import requests


def check_bin_number(cc_number):
    bin = cc_number[:8]
    try:        
        bindata = requests.get(f'https://lookup.binlist.net/{bin}').json()
        try: 
                if bindata['scheme'] != []:scheme = bindata['scheme'] 
        except: scheme = "None"
        try:
                if bindata['type'] != []:type = bindata['type']
        except: type = "None"
        try:
                if bindata['brand'] != []:brand = bindata['brand']
        except: brand = "None"
        try:
                if bindata['country']['name'] != []:country = bindata['country']['name']
        except: country = "None"
        try:
                if bindata['country']['name'] != []:currency = bindata['country']['currency']
        except: currency = "None"
        try:
                if bindata['country']['emoji'] != []:country_emoji = bindata['country']['emoji']
        except: country_emoji = "None"
        try:
                if bindata['bank']['name'] != []:bank = bindata['bank']['name']
        except: bank = "None"
        
        bindata_JSON = []
        bindata_JSON.append({
            "BIN": bin,
            "Scheme": scheme,
            "Type": type,
            "Brand": brand,
            "Country": country,
            "Currency": currency,
            "Country Emoji": country_emoji,
            "Bank": bank
        })

    except:
            bindata_JSON = bin

    return bindata_JSON

def extract_credit_card_info(text):
    current_year = datetime.now().year
    results_list = []

    digit_tokens = re.findall(r'\d{1,}', text)

    def get_card_type(number):
        if number.startswith('4'):
            return 'Visa'
        elif re.match(r"^5[1-5]", number):
            return 'MasterCard'
        elif re.match(r"^3[47]", number):
            return 'American Express'
        elif re.match(r"^6(?:011|5)", number):
            return 'Discover'
        else:
            return 'Other'

    i = 0
    while i < len(digit_tokens):
        token = digit_tokens[i]
        if 12 <= len(token) <= 16:
            card_number = token
            card_type = get_card_type(card_number)

            expiration_date = None
            cvv = None

            # Look ahead for expiration
            j = i + 1
            while j < len(digit_tokens) - 1:
                y, m = digit_tokens[j], digit_tokens[j + 1]

                year, month = None, None

                if re.fullmatch(r'\d{4}', y) and 2020 <= int(y) <= 2100:
                    year = int(y)
                elif re.fullmatch(r'\d{2}', y):
                    year = 2000 + int(y)

                if m.isdigit() and 1 <= int(m) <= 12:
                    month = int(m)

                if year and month and year >= current_year:
                    expiration_date = f"{month:02d}/{year}"
                    break

                # Try flipped month/year
                if re.fullmatch(r'\d{2}', y) and 1 <= int(y) <= 12:
                    month = int(y)
                    if re.fullmatch(r'\d{4}', m) and 2020 <= int(m) <= 2100:
                        year = int(m)
                        expiration_date = f"{month:02d}/{year}"
                        break
                    elif re.fullmatch(r'\d{2}', m):
                        year = 2000 + int(m)
                        if year >= current_year:
                            expiration_date = f"{month:02d}/{year}"
                            break
                j += 1

            # Look for CVV within 6 tokens after card
            for k in range(i + 1, min(i + 7, len(digit_tokens))):
                val = digit_tokens[k]
                if not val.isdigit():
                    continue
                if card_type in ['Visa', 'MasterCard'] and len(val) == 3:
                    cvv = val
                    break
                elif card_type == 'American Express' and len(val) == 4:
                    cvv = val
                    break
                elif card_type == 'Other' and len(val) in [3, 4] and int(val) < 2100:
                    cvv = val
                    break

            results_list.append({
                'card_number': card_number,
                'card_type': card_type,
                'expiration_date': expiration_date,
                'expiration_year': year,
                'expiration_month': month,
                'cvv': cvv,
                'bin_data': check_bin_number(card_number)
            })

            for result in results_list:
                if isinstance(result.get("bin_data"), list) and len(result["bin_data"]) == 1:
                    result["bin_data"] = result["bin_data"][0]

            # Dump just the first item without list brackets
            result_JSON = json.dumps(results_list[0], indent=4)

            results = {
                 "list": results_list,
                 "json": result_JSON
            }

            i = j + 6  # move past block
        else:
            i += 1
    try:
        return results
    except UnboundLocalError:
        print("No credit card found")
        return None
        


