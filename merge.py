import pandas as pd 
import os
from datetime import datetime

from utils import upload_to_hf_dataset, download_from_hf_dataset, load_hf_dataset
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()


# Get the name of the HuggingFace dataset for FinViz to export
DATASET_NAME_TIPRANKS_OUTPUT = os.getenv('DATASET_NAME_TIPRANKS_OUTPUT')

# Get the Hugging Face API token from the environment; either set in .env file or in the environment directly in GitHub
HF_TOKEN_TIPRANKS = os.getenv('HF_TOKEN_TIPRANKS')


current_datetime = datetime.now().strftime("%Y-%m-%d")    
DFtotal1= pd.read_csv(rf'.\tipranks\tipranks_{current_datetime}_part1.csv' , index=False)
DFtotal2= pd.read_csv(rf'.\tipranks\tipranks_{current_datetime}_part2.csv' , index=False)

DFtotal = pd.concat([DFtotal1, DFtotal2], ignore_index=True)

DFtotal.to_csv(rf'.\tipranks\tipranks_{current_datetime}.csv' , index=False)


file_path = fr'tipranks/tipranks_merged_{current_datetime}.csv'
latest_file_path = fr'tipranks/tipranks_merged.csv'


# Upload each file to the dataset
upload_to_hf_dataset(file_path, DATASET_NAME_tipranks_OUTPUT, HF_TOKEN_tipranks, repo_type="dataset")
upload_to_hf_dataset(latest_file_path, DATASET_NAME_tipranks_OUTPUT, HF_TOKEN_tipranks, repo_type="dataset")

