from credit_card_extractor import extract_credit_card_info

raw_text = '''5355555555555555|12|26|123'''


# Print the JSON representation of the extracted credit card information
print(extract_credit_card_info(raw_text).get('json'))

# Result:
#     {
#         "card_number": "4491455555555555",
#         "card_type": "Visa",
#         "expiration_date": "12/2026",
#         "expiration_year": 2026,
#         "expiration_month": 12,
#         "cvv": "123",
#         "bin_data":
#             {
#                 "BIN": "44914555",
#                 "Scheme": "None",
#                 "Type": "None",
#                 "Brand": "None",
#                 "Country": "None",
#                 "Currency": "None",
#                 "Country Emoji": "None",
#                 "Bank": "None"
#             }
#     }







# Print the list representation of the extracted credit card information
print(extract_credit_card_info(raw_text).get('list'))

# Result:
# [{'card_number': '4491455555555555',
#   'card_type': 'Visa',
#   'expiration_date': '12/2026',
#   'expiration_year': 2026,
#   'expiration_month': 12,
#   'cvv': '123',
#   'bin_data': [{'BIN': '44914555',
#     'Scheme': 'None',
#     'Type': 'None',
#     'Brand': 'None',
#     'Country': 'None',
#     'Currency': 'None',
#     'Country Emoji': 'None',
#     'Bank': 'None'}]}]
