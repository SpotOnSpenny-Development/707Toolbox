#Imports
from datetime import datetime
from numpy import number
import requests
import time
import pandas #will need to install xlwt or xlsx when doing AWS

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
    ######print("The price of {} is currently {}, and was {} a week ago.".format(token_address, current_price, historic_price))######
    #Calculate APY for commodity based on https://learn.bybit.com/investing/what-is-apy-in-crypto/ (7 day APY for this example)
    apy7 = (((current_price - historic_price)/historic_price) * 365)/7
    print("The 7 day APY for commoddity {} is {}%".format(token_address, apy7))
    return apy7

"""
So, this is a super basic script to pull and calculate the APY of a token based on it's address on the SOL network.
THAT SAID, if you wanted to get crazy extra, you can use the solana token list json (https://raw.githubusercontent.com/solana-labs/token-list/main/src/tokens/solana.tokenlist.json)
to scrub the ENTIRE solana token library and look for tokens that are currently tradeable and calculate the APY for ALL of them.
You could then create a list of this data to parse through it and look for the top x of them, or even just export it all in
a JSON or spreadsheet to sort through the data however you want. I THINK all this would take is a simple for loop on the "Tokens"
item on the link above but there's no way this is a quick run.

Fuck it. We Ball. Let's try it.
"""

def get_tradeable_tokens():
    #Create empty list to put tradeable tokens inside
    tradeable_tokens = []
    #Request and define token list
    url = 'https://raw.githubusercontent.com/solana-labs/token-list/main/src/tokens/solana.tokenlist.json'
    response = requests.get(url)
    token_list = response.json()
    #Iterate through token list and search for tradeable tokens
    for token in token_list["tokens"]:
        #Get token address from token list
        token_address = token["address"]
        #Make Birdeye API query for token address
        query_url = 'https://public-api.birdeye.so/public/price?address={}'.format(token_address)
        query_response = requests.get(query_url)
        json_response = query_response.json()
        #Add to tradeable list if token data found
        if json_response['data'] == None:
            print("No data found for {}".format(token_address))
        else:
            tradeable_tokens.append(token_address)
            print("Data found, {} is tradable".format(token_address))
        time.sleep(2)
    return tradeable_tokens

def apy_dict(tradeable_tokens):
    #Create empty list to store APY values
    all_apy = []
    #Iterate through tradeable tokens and add their APY to list
    for token in tradeable_tokens:
        token_apy = apy_calc(token)
        all_apy.append(token_apy)
        time.sleep(2)
    #Create dict from lists with token address as key and APY as value
    token_apy_dict = dict(zip(tradeable_tokens, all_apy))
    #Create spreadsheet from dictionary TODO: Create better spreadsheet format
    excel_dataframe = pandas.DataFrame.from_dict(token_apy_dict, orient = 'index', columns=["APY over 7 Days"])
    excel_dataframe.to_excel('test1.xls')
    number_of_tokens_parsed = len(tradeable_tokens)
    print("APY data exported for {} tokens".format(number_of_tokens_parsed))

if __name__ == "__main__":
    tokens = get_tradeable_tokens()
    apy_dict(tokens)