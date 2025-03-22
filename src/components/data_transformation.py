import pickle
import sys
import os
import json
import re
from dataclasses import dataclass
from src.exception import CustomException
from src.logger import logging
from transformers import AutoTokenizer
from datasets import Dataset

@dataclass
class DataTransformationConfig:
    tokenized_train_pickle_file_path = os.path.join('artifacts', 'tokenized_train_data.pkl')
    tokenized_test_pickle_file_path = os.path.join('artifacts', 'tokenized_test_data.pkl')

class TextPreprocessor:
    """Handles text cleaning and dataset conversion."""
    
    def __init__(self):
        self.label_list = ["O","B-AUTHOR", "I-AUTHOR", "B-ROLL_NUM",
                           "B-ORG", "I-ORG","B-SUPERVISOR", "I-SUPERVISOR", "B-DATE", "I-DATE"]
        self.label_map = {label: idx for idx, label in enumerate(self.label_list)}

    def clean_text(self, text):
        """Remove all special characters except '/', normalize spaces, and remove new lines."""
        logging.info("clean_text() called")
        text = text.strip()  # Remove leading/trailing spaces
        text = re.sub(r'[^a-zA-Z0-9/\s]', '', text)  # Keep only letters, numbers, and '/'
        text = re.sub(r'\s+', ' ', text)  # Replace multiple spaces with a single space
        return text

    def convert_to_hf_format(self, data):
        """Convert raw data into Hugging Face dataset format with cleaned text and mapped labels."""
        logging.info("convert_to_hf_format() called")
        tokenized_data = []
        for doc in data:  # Iterate over top-level list
            for entry in doc:  # Iterate over each inner list
                if isinstance(entry, dict) and "tokens" in entry and "ner_tags" in entry:
                    tokenized_data.append({
                        "tokens": [self.clean_text(token) for token in entry["tokens"]],
                        "ner_tags": [self.label_map[self.label_list[idx]] for idx in entry["ner_tags"]]
                    })
        return Dataset.from_list(tokenized_data)

class DataTransformer:
    """Handles tokenization and label alignment for BERT model training and inference."""

    def __init__(self, tokenizer_path):
        self.preprocessor = TextPreprocessor()  # Use the new text preprocessor
        self.tokenizer = AutoTokenizer.from_pretrained(tokenizer_path)

    def tokenize_and_align_labels(self, examples):
        """Tokenize input and align NER labels for BERT model."""
        logging.info("tokenize_and_align_labels() called")
        tokenized_inputs = self.tokenizer(examples["tokens"], truncation=True, is_split_into_words=True, padding="max_length", max_length=128)

        all_labels = []

        for i in range(len(examples["tokens"])):  # Process each example in batch
            word_ids = tokenized_inputs.word_ids(batch_index=i)  # Get word IDs per sentence
            previous_word_idx = None
            labels = []

            for word_idx in word_ids:
                if word_idx is None:
                    labels.append(-100)  # Padding tokens get -100
                elif word_idx != previous_word_idx:
                    labels.append(examples["ner_tags"][i][word_idx])  # Assign correct label
                else:
                    labels.append(examples["ner_tags"][i][word_idx])  # Extend label to subwords

                previous_word_idx = word_idx

            all_labels.append(labels)

        tokenized_inputs["labels"] = all_labels  # Ensure consistent list format
        return tokenized_inputs

    def transform_data(self, data):
        """Transform input data into tokenized format for BERT model training or inference."""
        logging.info("transform_data() called")
        hf_dataset = self.preprocessor.convert_to_hf_format(data)
        transformed_dataset = hf_dataset.map(self.tokenize_and_align_labels, batched=True)
        return transformed_dataset

class DataTransformation:
    def __init__(self, tokenizer_path):
        self.data_transformation_config = DataTransformationConfig()
        self.transformer = DataTransformer(tokenizer_path)

    def data_transformation(self, merged_dataset_path: str):
        try:
            logging.info("data_transformation() called")
            # Load dataset
            with open(merged_dataset_path, 'r') as f:
                data = json.load(f)

            # Transform dataset
            tokenized_datasets = self.transformer.transform_data(data)

            # Split into train/test
            tokenized_datasets = tokenized_datasets.train_test_split(test_size=0.1)

            # Save train/test datasets as Pickle
            with open(self.data_transformation_config.tokenized_train_pickle_file_path, "wb") as f:
                pickle.dump(tokenized_datasets["train"], f)

            with open(self.data_transformation_config.tokenized_test_pickle_file_path, "wb") as f:
                pickle.dump(tokenized_datasets["test"], f)

            logging.info(f"Tokenized datasets saved as Pickle at:\n{self.data_transformation_config.tokenized_train_pickle_file_path}\n{self.data_transformation_config.tokenized_test_pickle_file_path}")

            return (self.data_transformation_config.tokenized_train_pickle_file_path, 
                    self.data_transformation_config.tokenized_test_pickle_file_path)

        except Exception as e:
            raise CustomException(e, sys)

# main function
if __name__ == "__main__":
    dt = DataTransformation("bert-base-uncased")
    dt.data_transformation("artifacts/merged_dataset.json")
