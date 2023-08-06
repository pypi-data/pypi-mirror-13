"""
functions that could be useful in many places
"""

import math


#
#   convert City Trader API price to user expected price
#   learn more here: https://devservices.optionshop.com/docs/priceformatting
#
def price_to_decimal(price, display_factor, base_factor):
    # prevent NaN
    if not price or not display_factor or not base_factor or not price or not display_factor \
            or not base_factor or price == "" or display_factor == "" or base_factor == "":
        return None

    # if too many significant digits round
    if len(str(display_factor).replace(".", "")) > 15:
        display_factor = round(display_factor, 15)
    if len(str(base_factor).replace(".", "")) > 15:
        base_factor = round(base_factor, 15)
    if len(str(price).replace(".", "")) > 15:
        price = round(price, 15)

    price = price * display_factor

    if price > 0:
        whole_decimal = math.floor(price)
    else:
        whole_decimal = math.ceil(price)

    fraction = price - whole_decimal
    converted_fraction = fraction * base_factor

    return str(converted_fraction + whole_decimal)
