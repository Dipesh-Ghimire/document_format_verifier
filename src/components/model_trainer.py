import os;import sys
from dataclasses import dataclass
from src.components.data_ingestion import DataIngestion
from src.components.data_transformation import DataTransformation
from src.exception import CustomException
from src.logger import logging
from transformers import AutoModelForTokenClassification
from transformers import TrainingArguments, AutoTokenizer
from transformers import DataCollatorForTokenClassification, Trainer

@dataclass
class ModelTrainerConfig:
    trained_model_file_path = os.path.join("artifacts","fine_tuned_bert_ner")
    tokenizer_file_path = os.path.join("artifacts","fine_tuned_bert_ner")

class ModelTrainer:
    def __init__(self):
        self.model_trainer_config = ModelTrainerConfig()
        self.label_list = ["O","B-AUTHOR", "I-AUTHOR", "B-ROLL_NUM",
              "B-ORG", "I-ORG","B-SUPERVISOR", "I-SUPERVISOR", "B-DATE", "I-DATE"]
    def initiate_model_trainer(self,tokenized_train_file_path,tokenized_test_file_path):
        try:
            logging.info("Model Trainer initiated")
            model_name = "bert-base-uncased"
            # Load pre-trained BERT model
            model = AutoModelForTokenClassification.from_pretrained(model_name, num_labels=len(self.label_list))
            training_args = TrainingArguments(
                output_dir="./bert_ner_model",
                eval_strategy="epoch",
                save_strategy="epoch",
                per_device_train_batch_size=8,
                per_device_eval_batch_size=8,
                num_train_epochs=5,
                weight_decay=0.01,
                logging_dir="./logs"
            )
            # Define Data Collator
            tokenizer = AutoTokenizer.from_pretrained(model_name)
            data_collator = DataCollatorForTokenClassification(tokenizer)

            # Define Trainer
            trainer = Trainer(
                model=model,
                args=training_args,
                train_dataset=tokenized_train_file_path,
                eval_dataset=tokenized_test_file_path,
                processing_class=tokenizer,
                data_collator=data_collator
            )
            logging.info("Training model")
            trainer.train()
            logging.info("Model trained successfully")
            model.save_pretrained(self.model_trainer_config.trained_model_file_path)
            tokenizer.save_pretrained(self.model_trainer_config.tokenizer_file_path)
            logging.info("Model and tokenizer saved successfully")
            return (self.model_trainer_config.trained_model_file_path,self.model_trainer_config.tokenizer_file_path)
        except Exception as e:
            raise CustomException(e,sys)

if __name__ == "__main__":
    data_ingestion = DataIngestion()
    merged_data_path =data_ingestion.initiate_data_ingestion()

    data_transform = DataTransformation("bert-base-uncased")
    tokenized_train_file_path,tokenized_test_file_path = data_transform.data_transformation(merged_data_path)
    
    model_trainer = ModelTrainer()
    model_trainer.initiate_model_trainer(tokenized_train_file_path,tokenized_test_file_path)