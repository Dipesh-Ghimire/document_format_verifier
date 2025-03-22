from dataclasses import dataclass
import json
import os
import sys
from src.exception import CustomException
from src.logger import logging

@dataclass
class DataIngestionConfig:
    raw_data_path : str = os.path.join('dataset','annoted_dataset')
    merged_data_path : str = os.path.join('artifacts','merged_dataset.json')

class DataIngestion:
    def __init__(self) -> None:
        self.ingestion_config = DataIngestionConfig()
    
    def initiate_data_ingestion(self):
        logging.info("Entered the Data Ingestion Component")
        try:
            #create artifact directory
            os.makedirs(os.path.dirname(self.ingestion_config.raw_data_path),exist_ok=True)
            # Initialize an empty list to hold all the data
            merged_data = []
            logging.info(f"Reading data from {self.ingestion_config.raw_data_path}")
            # Iterate over all JSON files in the annoted_dataset folder
            for filename in os.listdir(self.ingestion_config.raw_data_path):
                if filename.endswith('.json'):
                    file_path = os.path.join(self.ingestion_config.raw_data_path, filename)
                    with open(file_path, 'r') as f:
                        # Load the JSON data and append it to the merged_data list
                        data = json.load(f)
                        merged_data.append(data)

            # Write the merged data to the merged_dataset.json file
            with open(self.ingestion_config.merged_data_path, 'w') as f:
                json.dump(merged_data, f, indent=4)

            logging.info(f"Merged dataset saved to {self.ingestion_config.merged_data_path}")

            return (self.ingestion_config.merged_data_path)

        except Exception as e:
            raise CustomException(e,sys)


if __name__=="__main__":
    data_ingestion = DataIngestion()
    data_ingestion.initiate_data_ingestion()