import argparse
import json

import requests
from bs4 import BeautifulSoup

def main():
    parser = argparse.ArgumentParser(description="Select a commentor")
    parser.add_argument("journal_url", metavar="URL", type=str)
    parser.add_argument("api_key", metavar="APIKey", type=str)
    args = parser.parse_args()
    print("Fetching journal {0}".format(args.journal_url))

    req = requests.get(args.journal_url)
    soup = BeautifulSoup(req.text, 'html.parser')
    users = set([r.text for r in soup.find_all('b', class_="replyto-name")])
    total_users = len(users)
    print("{0} users posted on your journal!".format(total_users))
    print("Fetching random number from random.org")
    payload = {
        "jsonrpc": "2.0",
        "method": "generateIntegers",
        "params": {
            "apiKey": args.api_key,
            "n": 1,
            "min": 0,
            "max": len(users) - 1
        },
        "id": 42
    }
    rand = requests.post("https://api.random.org/json-rpc/1/invoke", data=json.dumps(payload)).json()
    if 'error' in rand:
        print("Error getting number from random.org (did you set your API key?)")
    else:
        winning_number = rand['result']['random']['data'][0]
        print("Got {0} from random.org".format(winning_number))
        winner = list(users)[winning_number]
        print("The winner is {0}!".format(winner))
        print("http://www.furaffinity.net/user/{0}/".format(winner))
