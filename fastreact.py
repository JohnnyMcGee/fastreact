#!/usr/bin/python3

# 
# fastreact.py (url.com).
#
# Copyright (c) 2022 Easton Elliott
# 
# 
# This program is free software: you can redistribute it and/or modify  
# it under the terms of the GNU General Public License as published by  
# the Free Software Foundation, version 3.
#
# This program is distributed in the hope that it will be useful, but 
# WITHOUT ANY WARRANTY; without even the implied warranty of 
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the GNU 
# General Public License for more details.
#
# You should have received a copy of the GNU General Public License 
# along with this program. If not, see <http://www.gnu.org/licenses/>.
#
import sys
import json
import requests
import argparse

# Needed for colourful output
from pygments import highlight, lexers, formatters


from requests.adapters import HTTPAdapter
from requests.packages.urllib3.util.retry import Retry

# I don't fuck with regex, I let other people do it for me
# The Regex used:
# Thanks to https://www.geeksforgeeks.org/check-if-email-address-valid-or-not-in-python/
import re

_version = "0.1"


# Read the config file and lets set 
try:
    with open("config.json", "r") as f:
        config = json.load(f)
        api_url = config["api_url"]
        api_version = config["api_version"]
        api_token = config["api_token"]
except IOError:
    sys.exit("Could not open/read config file :(")


# Initiate the parser
parser = argparse.ArgumentParser()

# Add long and short argument
parser.add_argument(
    "--customer", "-c", help="lookup by customer email or ID (ReCharge & Shopify)"
)

parser.add_argument("--order", "-o", help="lookup by order ID (ReCharge & Shopify)")

#parser.add_argument(
#    "--email",
#    "-e",
#    default=False,
#    action="store_true",
#    help="Filter order by email address",
#)

parser.add_argument("--subscription", "-s", help="lookup by subscription number")
parser.add_argument(
    "--colour", "-z", help="Colour all JSON output", action="store_true"
)

# Read arguments from the command line
args = parser.parse_args()


# If we got empty params
if len(sys.argv) == 1:
    parser.print_help()
    sys.exit("Version %s" % _version)

# Headers needed for ReCharge REST requests
headers = {
    "Content-Type": "application/json",
    "X-Recharge-Version": api_version,
    "X-Recharge-Access-Token": api_token,
}


def http_req_with_retry(destination_url, headers, params=False):
    retry_strategy = Retry(
        total=3,
        status_forcelist=[429, 500, 502, 503, 504],
        allowed_methods=["HEAD", "GET", "OPTIONS"],
    )
    adapter = HTTPAdapter(max_retries=retry_strategy)
    http = requests.Session()
    http.mount("https://", adapter)
    http.mount("http://", adapter)

    response = http.get(destination_url, headers=headers)

    return response.json()


# Toggle colour output for JSON data (cool! neat!)
colour_flag = args.colour


# Check for customer by ID or email
if args.customer:
    print("Set input customer to [ %s ]" % args.customer)
    customer = args.customer

    if customer.isnumeric():
        print("Searching ReCharge customers....")

        # Search for ReCharge customer ID first since it will be inhernetly faster
        destination_url = api_url + "/customers/" + customer
        try:
            data = http_req_with_retry(destination_url, headers)

        except requests.exceptions.Timeout:
            # Maybe set up for a retry, or continue in a retry loop
            sys.exit("Timeout, try again")
        except requests.exceptions.TooManyRedirects:
            sys.exit("Too many redirects, API down?")

        # Tell the user their URL was bad and try a different one that isn't so bad
        except requests.exceptions.RequestException as e:
            raise SystemExit(e)

        # No ReCharge data 
        if "errors" in data:
            # No hit so we requery in the hope....
            print("Searching Shopify customers....")
            # Search Shopify customer ID
            destination_url = api_url + "/customers"
            try:

                data = http_req_with_retry(
                    destination_url, headers, {"external_customer_id": customer}
                )

            except requests.exceptions.Timeout:
                # Maybe set up for a retry, or continue in a retry loop
                sys.exit("Timeout, try again")
            except requests.exceptions.TooManyRedirects:
                sys.exit("Too many redirects, API down?")

            # the request itself was bad :\
            except requests.exceptions.RequestException as e:
                raise SystemExit(e)

            # No results at all
            if not data["customers"]:
                sys.exit("No customer found by ID, sorry fuck!")

            # Customer Hit on Shopify
            else:
                formatted_json = json.dumps(
                    data, indent=config["indent_level"], sort_keys=config["data_sort"]
                )
                if colour_flag:
                    colourful_json = highlight(
                        formatted_json,
                        lexers.JsonLexer(),
                        formatters.TerminalFormatter(),
                    )
                    print(colourful_json)
                    sys.exit()
                else:
                    print(formatted_json)
                    sys.exit()

        # Hit for ReCharge
        if data["customer"]:
            formatted_json = json.dumps(
                data, indent=config["indent_level"], sort_keys=config["data_sort"]
            )
            if colour_flag:
                colourful_json = highlight(
                    formatted_json, lexers.JsonLexer(), formatters.TerminalFormatter()
                )
                print(colourful_json)
                sys.exit()
            else:
                print(formatted_json)
                sys.exit()

    else:

        # If we are searching by email address
        if re.fullmatch(
            r"\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b", customer
        ):
            destination_url = api_url + "/customers"

            response = requests.get(
                destination_url, params={"email": customer}, headers=headers
            )
            response.json()
            data = response.json()

            # No customer ID means nothing found
            if not data["customers"]:
                sys.exit("No customer found by email, sorry fuck!")
            else:
                formatted_json = json.dumps(
                    data, indent=config["indent_level"], sort_keys=config["data_sort"]
                )
                if colour_flag:
                    colourful_json = highlight(
                        formatted_json,
                        lexers.JsonLexer(),
                        formatters.TerminalFormatter(),
                    )
                    print(colourful_json)
                    sys.exit()
                else:
                    print(formatted_json)
                    sys.exit()
        else:
            sys.exit("Error: No customer found :(")

if args.subscription:
    print("Set input subscription to [ %s ]" % args.subscription)
    subscription = args.subscription

    if subscription.isnumeric():
        print("Searching subscriptions....")

        # Search for ReCharge subscription ID
        destination_url = api_url + "/subscriptions/" + subscription
        try:

            data = http_req_with_retry(destination_url, headers)

        except requests.exceptions.Timeout:
            # Maybe set up for a retry, or continue in a retry loop
            sys.exit("Timeout, try again")
        except requests.exceptions.TooManyRedirects:
            sys.exit("Too many redirects, API down?")

        # Tell the user their URL was bad and try a different one
        except requests.exceptions.RequestException as e:
            # catastrophic error. bail.
            raise SystemExit(e)

        # No ReCharge data (either nada or Shopify data)
        if "errors" in data:
            # No hit so we requery in the hope....

            #            print(data)
            # No results at all
            sys.exit("No subscription found, sorry fuck!")

        # Hit for ReCharge
        if data["subscription"]:
            formatted_json = json.dumps(
                data, indent=config["indent_level"], sort_keys=config["data_sort"]
            )
            if colour_flag:
                colourful_json = highlight(
                    formatted_json, lexers.JsonLexer(), formatters.TerminalFormatter()
                )
                print(colourful_json)
                sys.exit()
            else:
                print(formatted_json)
                sys.exit()

# Search by order ID NOT number
if args.order:
    print("Set input order to [ %s ]" % args.order)
    order = args.order

    if order.isnumeric():
        # Search ReCharge orders first
        print("Searching ReCharge orders.....")
        destination_url = api_url + "/orders/" + order
        response = requests.get(destination_url, headers=headers)
        response.json()
        data = response.json()


        # No hit on ReCharge, search by Shopify order ID (not number!)
        if "errors" in data:
            print("Searching Shopify orders....")

            # Search Shopify order ID
            destination_url = api_url + "/orders/"

            response = requests.get(
                destination_url, params={"external_order_id": order}, headers=headers
            )
            response.json()
            data = response.json()


            #Hit on Shopify
            if data["orders"]:
                formatted_json = json.dumps(
                    data, indent=config["indent_level"], sort_keys=config["data_sort"]
                )
                if colour_flag:
                    colourful_json = highlight(
                        formatted_json, lexers.JsonLexer(), formatters.TerminalFormatter()
                    )
                    print(colourful_json)
                    sys.exit()
                else:
                    print(formatted_json)
                    sys.exit()

            # No results on Shopify
            if not data["orders"]:
                sys.exit("No order found by ID, sorry fuck!")


        # Hit on Recharge
        if "order" in data:
            # sys.exit("hit on rc")
            formatted_json = json.dumps(
                data, indent=config["indent_level"], sort_keys=config["data_sort"]
            )
            if colour_flag:
                colourful_json = highlight(
                    formatted_json, lexers.JsonLexer(), formatters.TerminalFormatter()
                )
                print(colourful_json)
                sys.exit()
            else:
                print(formatted_json)
                sys.exit()
        else:
            sys.exit("Error: data error, try again?")
    else:
        sys.exit("Error: not numeric")

