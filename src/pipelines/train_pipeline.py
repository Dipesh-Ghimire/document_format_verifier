import sys
from src.components.data_ingestion import DataIngestion
from src.components.data_transformation import DataTransformation
from src.components.model_trainer import ModelTrainer
from src.exception import CustomException
from src.logger import logging

class TrainPipeline:
    def __init__(self):
        self.data_ingestion = DataIngestion()
        self.data_transformation = DataTransformation()
        self.model_trainer = ModelTrainer()

    def start_pipeline(self):
        try:
            logging.info("Starting Data Ingestion")
            data_ingestion = DataIngestion()
            merged_data_path =data_ingestion.initiate_data_ingestion()

            logging.info("Starting Data Transformation")
            data_transform = DataTransformation("bert-base-uncased")
            tokenized_train_file_path,tokenized_test_file_path = data_transform.data_transformation(merged_data_path)
            
            logging.info("Starting Model Training")
            model_trainer = ModelTrainer()
            model_trainer.initiate_model_trainer(tokenized_train_file_path,tokenized_test_file_path)

            logging.info("Training pipeline completed")
        except CustomException as e:
            raise CustomException(e,sys)

if __name__=="__main__":
    pipeline = TrainPipeline()
    pipeline.start_pipeline()