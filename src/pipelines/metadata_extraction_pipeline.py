import os
import sys
import pandas as pd
from src.exception import CustomException
from transformers import pipeline, AutoTokenizer, AutoModelForTokenClassification
from src.pipelines.utils import convert_ner_results, clean_pdf_text, extract_first_page_text, capitalize_metadata
from src.components.extraction.utils import extract_metadata_llama


class MetadataExtractionPipeline:
    def  __init__(self):
        pass
    def extract(self,pdf):
        try:
            bert_model_path = os.path.join(os.getcwd(),'artifacts',"fine_tuned_bert_ner")
            # Load fine-tuned model and tokenizer
            tokenizer = AutoTokenizer.from_pretrained(bert_model_path)
            model = AutoModelForTokenClassification.from_pretrained(bert_model_path)
        
            # Create NER pipeline
            ner_pipeline = pipeline("ner", model=model, tokenizer=tokenizer)

            # Predict entities
            #text = "Under the Supervision of Mr. Nabaraj Bahadur Negi Lecturer Submitted by: Dipesh Ghimire (199), Rabin Pant (200), Prabin Raj Amatya (201) Submitted To: Tribhuvan University February 2025"
            pdf_text = extract_first_page_text(pdf)
            cleaned_text = clean_pdf_text(pdf_text)
            bert_result = ner_pipeline(cleaned_text)

            # Convert NER results to structured metadata
            bert_structured_metadata = {'Author': {'rabin pant', 'prabin raj amatya', 'dipesh ghimire'}, 
                                        'Roll number': {'199', '201', '200'}, 
                                        'Organization': 'tribhuvan university', 
                                        'Supervisor': 'mr. nabaraj bahadur negi', 
                                        'Submission Date': 'february 2025'}
            bert_metadata = convert_ner_results(bert_result)
            bert_structured_metadata = capitalize_metadata(bert_metadata)
            # Extract metadata using Llama 2
            #llama_metadata = extract_metadata_llama(text)
            llama_metadata ={"Metadata": {
                                "Author": ["Dipesh Ghimire", "Rajesh Adhikari", "Sijan B.K."],
                                "Organization": ["Department of Information Technology", "Amrit Campus Lainchaur, Kathmandu"],
                                "Roll Number": ["199/077", "212/077", "223/077"],
                                "Supervisor": ["Mr. Nabaraj Bahadur Negi"],
                                "Submission Date": ["February 2025"]
                                        }
                            }
            
            return (bert_structured_metadata,llama_metadata)
        except Exception as e:
            raise CustomException(e,sys)

if __name__ == "__main__":
    me_pipeline = MetadataExtractionPipeline()
    me_pipeline.extract("")