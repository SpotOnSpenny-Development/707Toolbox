#Imports
from datetime import datetime
from numpy import number
import requests
import time
import pandas #will need to install xlwt or xlsx when doing AWS
import json

#Function will calculate the apy over 7 days for a given token address
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
    #Catch error if token has not been listed long enough
    if current_price or historic_price == None:
        print("{} has not been listed long enough to calculate APY on specified timeframe.".format(token_address))
        message = "Not enough data"
        return message
    #Calculate APY for commodity based on https://learn.bybit.com/investing/what-is-apy-in-crypto/ 
    else:
        apy7 = (((current_price - historic_price)/historic_price) * 365)/7
        print("The 7 day APY for commoddity {} is {}%".format(token_address, apy7))
        return apy7

#Function to get all tradeable tokens on solana
def get_tradeable_tokens():
    #Create empty list to put tradeable tokens inside
    tradeable_tokens = []
    #Request and define token list #TODO save this json with the current date as a reference
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
    #Create JSON of tradable tokens for easy bug fixing
    json_token = json.dumps(tradeable_tokens)
    json_file = open("TradeableTokens.json", "w") #TODO add date to json filename
    json_file.write(json_token)
    json_file.close
    #Return list of tradeable tokens
    return tradeable_tokens

#Function will create a dict of all given tokens and export as a formatted spreadsheet
def apy_dict(tradeable_tokens): #TODO if len of tokens in current json do not match json at time of last pull, tell user how off it is and suggest pulling a new one
    #Create empty list to store APY values
    all_apy = []
    #Iterate through tradeable tokens and add their APY to list
    for token in tradeable_tokens: #TODO Fix this so that it will pull from the tradeable_tokens.json
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
    print(apy_calc("FYpdBuyAHSbdaAyD1sKkxyLWbAP8uUW9h6uvdhK74ij1"))