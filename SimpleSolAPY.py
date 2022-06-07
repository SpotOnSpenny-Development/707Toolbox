#Imports
from datetime import datetime
import requests

def apy_calc(token_address):
    #Set datetime at time of running script
    unix_current = int(datetime.now().timestamp())
    #Set datetime a week prior to running script
    unix_weekago = int(unix_current - 604800)
    #Make http request to BirdEye for data
    url = 'https://public-api.birdeye.so/public/history_price?address={}&time_from={}&time_to={}'.format(token_address, unix_weekago, unix_current)
    response = requests.get(url)
    #Parse through response json object
    json_data = response.json()
    historic_price = json_data["data"]["items"][0]["value"]
    number_of_pricepoints = len(json_data["data"]["items"])
    current_price =json_data["data"]["items"][number_of_pricepoints - 1]["value"]
    print("The price of {} is currently {}, and was {} a week ago.".format(token_address, current_price, historic_price))
    #Calculate APY for commodity based on https://learn.bybit.com/investing/what-is-apy-in-crypto/ (7 day APY for this example)
    apy7 = (((current_price - historic_price)/historic_price) * 365)/7
    print("The 7 day APY for commoddity {} is {}%".format(token_address, apy7))

if __name__ == "__main__":
    #Ask user to input requested address and apply calculation
    input_token_addy = input("Please input the token address you'd like to calculate APY7 for:")
    apy_calc(input_token_addy)

"""
So, this is a super basic script to pull and calculate the APY of a token based on it's address on the SOL network.
THAT SAID, if you wanted to get crazy extra, you can use the solana token list json (https://raw.githubusercontent.com/solana-labs/token-list/main/src/tokens/solana.tokenlist.json)
to scrub the ENTIRE solana token library and look for tokens that are currently tradeable and calculate the APY for ALL of them.
You could then create a list of this data to parse through it and look for the top x of them, or even just export it all in
a JSON or spreadsheet to sort through the data however you want. I THINK all this would take is a simple for loop on the "Tokens"
item on the link above but there's no way this is a quick run.
"""