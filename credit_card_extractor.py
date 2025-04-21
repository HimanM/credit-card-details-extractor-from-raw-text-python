import re
from datetime import datetime
import json
import requests


def check_bin_number(cc_number):
    bin_number = cc_number[:8]
    try:
        response = requests.get(f'https://lookup.binlist.net/{bin_number}')
        response.raise_for_status()  # Raise error for non-2xx responses
        bindata = response.json()

        scheme = bindata.get('scheme', 'None')
        type_ = bindata.get('type', 'None')
        brand = bindata.get('brand', 'None')

        country_data = bindata.get('country', {})
        country = country_data.get('name', 'None')
        currency = country_data.get('currency', 'None')
        country_emoji = country_data.get('emoji', 'None')

        bank_data = bindata.get('bank', {})
        bank = bank_data.get('name', 'None')

        bindata_JSON = {
            "BIN": bin_number,
            "Scheme": scheme,
            "Type": type_,
            "Brand": brand,
            "Country": country,
            "Currency": currency,
            "Country Emoji": country_emoji,
            "Bank": bank
        }

    except Exception as e:
        # Optionally log the error
        print(f"BIN lookup failed: {e}")
        bindata_JSON = {
            "BIN": bin_number,
            "Scheme": "None",
            "Type": "None",
            "Brand": "None",
            "Country": "None",
            "Currency": "None",
            "Country Emoji": "None",
            "Bank": "None"
        }

    return bindata_JSON

def filter_message(text):

# ------------------- GENERIC CREDIT CARD DETECTION -------------------
    possible_card_numbers = re.findall(r'(?:\d[ -]*?){13,19}', text)
    card_number = None
    card_type = None


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
        
    
    for raw_card in possible_card_numbers:
        digits = re.sub(r'\D', '', raw_card)  # Remove non-digit characters
        if 13 <= len(digits) <= 19:  # Check if it's a valid card number length
            card_type = get_card_type(digits)
            card_number = digits
            break

    if not card_number:
        return None  # Return None if no valid card number is found

    current_year = datetime.now().year

    digit_tokens = re.findall(r'\d{1,}', text)

    

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
                if card_type in ['Visa', 'MasterCard', 'Discover'] and len(val) == 3:
                    cvv = val
                    break
                elif card_type == 'American Express' and len(val) == 4:
                    cvv = val
                    break
                elif card_type == 'Other' and len(val) in [3, 4] and int(val) < 2100:
                    cvv = val
                    break

            results = {
                'cc_num': card_number,
                'cc_type': card_type,
                'cc_day': expiration_date,
                'cc_year': year,
                'cc_month': f"{month:02d}",
                'cvv': cvv,
                'bin_data': check_bin_number(card_number)
            }

            
            i = j + 6  # move past block
        else:
            i += 1
    return results
