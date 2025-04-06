
#Get rank of a ticker from tiprank.com uisng pure lxml
def get_tiprank_value(ticker):
    import requests
    from lxml import html
    import random
    from browsers import user_agents

    # Randomly select a user agent from the list
    random_browser = random.choice(list(user_agents.items()))
    selected_browser_name = random_browser[0]
    selected_browser_ua = random_browser[1]

    headers = {
        "User-Agent": selected_browser_ua
    }


    # headers = {
    #     'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36',
    #     'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8',
    #     'Accept-Encoding': 'gzip, deflate, br',
    #     'Accept-Language': 'en-US,en;q=0.9',
    #     'Cache-Control': 'no-cache',
    # }
    xpath_expression = '//*[@id="tr-stock-page-content"]/div[1]/div[4]/div[2]/div[1]/div[2]/div[2]/div[2]/div[1]/div[2]/div[1]/div/div/div/div[1]/svg/text/tspan'
    
    # # Send an HTTP GET request to the URL
    url = f"https://www.tipranks.com/stocks/{ticker.lower()}"
    response = requests.get(url, headers=headers)

    elements = dict()    
    key = 'SmartScore'

    if response.status_code == 200:
        tree = html.fromstring(response.content)

        tspan_element = tree.find('.//tspan')
        if tspan_element is not None:
            tspan_element = tree.find('.//tspan', tspan_element)
            elements[key] = tspan_element.text
        else:
            print("tspan element not found.")
            elements[key]="-1"

    return elements



#Get rank and price target of a ticker from tiprank.com using beautifulsoup
def get_tiprank_values(ticker):

    from bs4 import BeautifulSoup
    import requests
    import random
    from browsers import user_agents

    # Randomly select a user agent from the list
    random_browser = random.choice(list(user_agents.items()))
    selected_browser_name = random_browser[0]
    selected_browser_ua = random_browser[1]

    headers = {
        "User-Agent": selected_browser_ua
    }

    # headers = {
    #     'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36',
    #     'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8',
    #     'Accept-Encoding': 'gzip, deflate, br',
    #     'Accept-Language': 'en-US,en;q=0.9',
    #     'Cache-Control': 'no-cache',
    # }

    # # Send an HTTP GET request to the URL
    url = f"https://www.tipranks.com/stocks/{ticker.lower()}"
    response = requests.get(url, headers=headers)

    elements = dict()    
    key = 'SmartScore'

    # key = list(xpathdict.keys())[0]

    if response.status_code == 200:
        # Parse the HTML content with BeautifulSoup
        soup = BeautifulSoup(response.content, 'html.parser')

        # Use CSS selector to extract the value
        elements['AveragePriceTarget'] = float(soup.select_one('.colorblack.fonth10_semibold').text[1:])
        elements['SmartScore'] = int(soup.select_one('.w_pxsmall60.mxauto.fontWeightbold.fontSizelarge').text)

    return elements


###############################################################################
#Main Loop
###############################################################################

import pandas as pd
import requests
import time
import os
from datetime import datetime
import argparse
from dotenv import load_dotenv

from utils import upload_to_hf_dataset, download_from_hf_dataset, load_hf_dataset

# Load environment variables from .env file
load_dotenv()

# Get the name of the HuggingFace dataset for TradingView to read from
dataset_name_TradingView_input = os.getenv('dataset_name_TradingView_input')

# Get the name of the HuggingFace dataset for FinViz to export
DATASET_NAME_TIPRANKS_OUTPUT = os.getenv('DATASET_NAME_TIPRANKS_OUTPUT')

# Get the Hugging Face API token from the environment; either set in .env file or in the environment directly in GitHub
HF_TOKEN_TIPRANKS = os.getenv('HF_TOKEN_TIPRANKS')

# Get current date and time
# current_datetime = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
current_datetime = datetime.now().strftime("%Y-%m-%d")

#Load lastest TradingView DataSet from HuggingFace Dataset which is always america.csv
# download_from_hf_dataset("america.csv", "AmirTrader/TradingViewData", HF_TOKEN_FINVIZ)
DFUSA = load_hf_dataset("america.csv", HF_TOKEN_TIPRANKS, dataset_name_TradingView_input)

#get ticker list by filtering only above 1 billion dollar company
# DFUSA = pd.read_csv('america_2023-09-16.csv')
tickerlst = list(DFUSA.query('`Market Capitalization`>1000e9').Ticker)
print(f"Number of Tickers: {len(tickerlst)}")

# Initialize the argument parser
parser = argparse.ArgumentParser(description="ETL Pipeline Runner")

# Add a positional argument for the pipeline part
parser.add_argument(
    'part',
    choices=['part1', 'part2'],
    help="Specify which part of the ETL pipeline to run: 'part1' or 'part2'"
)

# Parse the command-line arguments
args = parser.parse_args()

# Conditional logic based on the provided argument
if args.part == 'part1':
    tickerlst = tickerlst[0:len(tickerlst)//2]
elif args.part == 'part2':
    tickerlst = tickerlst[len(tickerlst)//2:len(tickerlst)]

# Main loop to retrieve profitability ranks for each ticker
dfs=[]
counter=0
for ticker in tickerlst:
    counter+=1
    print(f'{counter} out of {len(tickerlst)} {ticker}')
    if '/' in ticker:
        pass
    # try:
    # Get profitability rank for the current ticker
    # value = "-1"
    # while value == "-1":
    #     valuedic = get_tiprank_value(ticker)
    #     value = valuedic['rank']

    try:
        time.sleep(15)  # Pause for 15 seconds
        # dftemp = pd.DataFrame(get_tiprank_value(ticker).values(), columns=['SmartScore'])    
        tiprankvalue = get_tiprank_values(ticker)
        print(f"TipRanks Value = {tiprankvalue} of {ticker}")
        # Convert the dictionary to a DataFrame
        dftemp = pd.DataFrame([tiprankvalue])

        # Add the Ticker column for reference
        dftemp['Ticker'] = ticker
        dfs.append(dftemp)
    except:
        print(f"*** could not retrieve data for {ticker}")
        pass

# Concatenate the DataFrames in the list to create a single DataFrame    
DFmerge = pd.concat(dfs, ignore_index=True)    
DFtotal = DFmerge.merge(DFUSA)

DFtotal['AveragePriceTarget_percent'] = 100 * (DFtotal['AveragePriceTarget'] - DFtotal['Price']) /DFtotal['Price']


if not os.path.exists('./tipranks'):
    os.mkdir('tipranks')
    
current_datetime = datetime.now().strftime("%Y-%m-%d")    
DFtotal.to_csv(rf'.\tipranks\tipranks_{current_datetime}_{args.part}.csv' , index=False)

