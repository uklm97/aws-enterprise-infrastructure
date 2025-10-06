#!/usr/bin/env python3
"""
AWS AI Services Manager
Comprehensive management of AWS AI services including Rekognition, Comprehend, Translate, etc.
"""

import boto3
import json
import time
import base64
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any, Union, BinaryIO
from botocore.exceptions import ClientError
import pandas as pd


class AIServicesManager:
    """Comprehensive AWS AI services management"""
    
    def __init__(self, region: str = 'us-east-1'):
        self.region = region
        self.rekognition_client = boto3.client('rekognition', region_name=region)
        self.comprehend_client = boto3.client('comprehend', region_name=region)
        self.translate_client = boto3.client('translate', region_name=region)
        self.polly_client = boto3.client('polly', region_name=region)
        self.transcribe_client = boto3.client('transcribe', region_name=region)
        self.textract_client = boto3.client('textract', region_name=region)
        self.forecast_client = boto3.client('forecast', region_name=region)
        self.personalize_client = boto3.client('personalize', region_name=region)
        self.s3_client = boto3.client('s3', region_name=region)
        self.cloudwatch_client = boto3.client('cloudwatch', region_name=region)
        
    # Amazon Rekognition
    def detect_faces(self, image: Union[str, BinaryIO], 
                    attributes: List[str] = None) -> Dict[str, Any]:
        """Detect faces in image using Rekognition"""
        try:
            if not attributes:
                attributes = ['ALL']
            
            if isinstance(image, str):
                # S3 object or local file path
                if image.startswith('s3://'):
                    bucket, key = image.replace('s3://', '').split('/', 1)
                    response = self.rekognition_client.detect_faces(
                        Image={'S3Object': {'Bucket': bucket, 'Name': key}},
                        Attributes=attributes
                    )
                else:
                    # Local file
                    with open(image, 'rb') as image_file:
                        image_bytes = image_file.read()
                    response = self.rekognition_client.detect_faces(
                        Image={'Bytes': image_bytes},
                        Attributes=attributes
                    )
            else:
                # BinaryIO object
                image_bytes = image.read()
                response = self.rekognition_client.detect_faces(
                    Image={'Bytes': image_bytes},
                    Attributes=attributes
                )
            
            return response
        except ClientError as e:
            print(f"Error detecting faces: {e}")
            return {}
    
    def detect_labels(self, image: Union[str, BinaryIO], 
                     max_labels: int = 10, min_confidence: float = 80.0) -> Dict[str, Any]:
        """Detect labels in image using Rekognition"""
        try:
            if isinstance(image, str):
                if image.startswith('s3://'):
                    bucket, key = image.replace('s3://', '').split('/', 1)
                    response = self.rekognition_client.detect_labels(
                        Image={'S3Object': {'Bucket': bucket, 'Name': key}},
                        MaxLabels=max_labels,
                        MinConfidence=min_confidence
                    )
                else:
                    with open(image, 'rb') as image_file:
                        image_bytes = image_file.read()
                    response = self.rekognition_client.detect_labels(
                        Image={'Bytes': image_bytes},
                        MaxLabels=max_labels,
                        MinConfidence=min_confidence
                    )
            else:
                image_bytes = image.read()
                response = self.rekognition_client.detect_labels(
                    Image={'Bytes': image_bytes},
                    MaxLabels=max_labels,
                    MinConfidence=min_confidence
                )
            
            return response
        except ClientError as e:
            print(f"Error detecting labels: {e}")
            return {}
    
    def detect_text(self, image: Union[str, BinaryIO]) -> Dict[str, Any]:
        """Detect text in image using Rekognition"""
        try:
            if isinstance(image, str):
                if image.startswith('s3://'):
                    bucket, key = image.replace('s3://', '').split('/', 1)
                    response = self.rekognition_client.detect_text(
                        Image={'S3Object': {'Bucket': bucket, 'Name': key}}
                    )
                else:
                    with open(image, 'rb') as image_file:
                        image_bytes = image_file.read()
                    response = self.rekognition_client.detect_text(
                        Image={'Bytes': image_bytes}
                    )
            else:
                image_bytes = image.read()
                response = self.rekognition_client.detect_text(
                    Image={'Bytes': image_bytes}
                )
            
            return response
        except ClientError as e:
            print(f"Error detecting text: {e}")
            return {}
    
    def detect_moderation_labels(self, image: Union[str, BinaryIO], 
                               min_confidence: float = 50.0) -> Dict[str, Any]:
        """Detect moderation labels in image using Rekognition"""
        try:
            if isinstance(image, str):
                if image.startswith('s3://'):
                    bucket, key = image.replace('s3://', '').split('/', 1)
                    response = self.rekognition_client.detect_moderation_labels(
                        Image={'S3Object': {'Bucket': bucket, 'Name': key}},
                        MinConfidence=min_confidence
                    )
                else:
                    with open(image, 'rb') as image_file:
                        image_bytes = image_file.read()
                    response = self.rekognition_client.detect_moderation_labels(
                        Image={'Bytes': image_bytes},
                        MinConfidence=min_confidence
                    )
            else:
                image_bytes = image.read()
                response = self.rekognition_client.detect_moderation_labels(
                    Image={'Bytes': image_bytes},
                    MinConfidence=min_confidence
                )
            
            return response
        except ClientError as e:
            print(f"Error detecting moderation labels: {e}")
            return {}
    
    def create_collection(self, collection_id: str) -> bool:
        """Create Rekognition collection"""
        try:
            self.rekognition_client.create_collection(CollectionId=collection_id)
            return True
        except ClientError as e:
            print(f"Error creating collection: {e}")
            return False
    
    def index_faces(self, collection_id: str, image: Union[str, BinaryIO],
                   external_image_id: str = None) -> Dict[str, Any]:
        """Index faces in collection"""
        try:
            if isinstance(image, str):
                if image.startswith('s3://'):
                    bucket, key = image.replace('s3://', '').split('/', 1)
                    response = self.rekognition_client.index_faces(
                        CollectionId=collection_id,
                        Image={'S3Object': {'Bucket': bucket, 'Name': key}},
                        ExternalImageId=external_image_id
                    )
                else:
                    with open(image, 'rb') as image_file:
                        image_bytes = image_file.read()
                    response = self.rekognition_client.index_faces(
                        CollectionId=collection_id,
                        Image={'Bytes': image_bytes},
                        ExternalImageId=external_image_id
                    )
            else:
                image_bytes = image.read()
                response = self.rekognition_client.index_faces(
                    CollectionId=collection_id,
                    Image={'Bytes': image_bytes},
                    ExternalImageId=external_image_id
                )
            
            return response
        except ClientError as e:
            print(f"Error indexing faces: {e}")
            return {}
    
    def search_faces_by_image(self, collection_id: str, image: Union[str, BinaryIO],
                            max_faces: int = 10, face_match_threshold: float = 80.0) -> Dict[str, Any]:
        """Search faces by image in collection"""
        try:
            if isinstance(image, str):
                if image.startswith('s3://'):
                    bucket, key = image.replace('s3://', '').split('/', 1)
                    response = self.rekognition_client.search_faces_by_image(
                        CollectionId=collection_id,
                        Image={'S3Object': {'Bucket': bucket, 'Name': key}},
                        MaxFaces=max_faces,
                        FaceMatchThreshold=face_match_threshold
                    )
                else:
                    with open(image, 'rb') as image_file:
                        image_bytes = image_file.read()
                    response = self.rekognition_client.search_faces_by_image(
                        CollectionId=collection_id,
                        Image={'Bytes': image_bytes},
                        MaxFaces=max_faces,
                        FaceMatchThreshold=face_match_threshold
                    )
            else:
                image_bytes = image.read()
                response = self.rekognition_client.search_faces_by_image(
                    CollectionId=collection_id,
                    Image={'Bytes': image_bytes},
                    MaxFaces=max_faces,
                    FaceMatchThreshold=face_match_threshold
                )
            
            return response
        except ClientError as e:
            print(f"Error searching faces: {e}")
            return {}
    
    # Amazon Comprehend
    def detect_sentiment(self, text: str, language_code: str = 'en') -> Dict[str, Any]:
        """Detect sentiment in text using Comprehend"""
        try:
            response = self.comprehend_client.detect_sentiment(
                Text=text,
                LanguageCode=language_code
            )
            return response
        except ClientError as e:
            print(f"Error detecting sentiment: {e}")
            return {}
    
    def detect_entities(self, text: str, language_code: str = 'en') -> Dict[str, Any]:
        """Detect entities in text using Comprehend"""
        try:
            response = self.comprehend_client.detect_entities(
                Text=text,
                LanguageCode=language_code
            )
            return response
        except ClientError as e:
            print(f"Error detecting entities: {e}")
            return {}
    
    def detect_key_phrases(self, text: str, language_code: str = 'en') -> Dict[str, Any]:
        """Detect key phrases in text using Comprehend"""
        try:
            response = self.comprehend_client.detect_key_phrases(
                Text=text,
                LanguageCode=language_code
            )
            return response
        except ClientError as e:
            print(f"Error detecting key phrases: {e}")
            return {}
    
    def detect_language(self, text: str) -> Dict[str, Any]:
        """Detect language of text using Comprehend"""
        try:
            response = self.comprehend_client.detect_dominant_language(Text=text)
            return response
        except ClientError as e:
            print(f"Error detecting language: {e}")
            return {}
    
    def detect_syntax(self, text: str, language_code: str = 'en') -> Dict[str, Any]:
        """Detect syntax in text using Comprehend"""
        try:
            response = self.comprehend_client.detect_syntax(
                Text=text,
                LanguageCode=language_code
            )
            return response
        except ClientError as e:
            print(f"Error detecting syntax: {e}")
            return {}
    
    def classify_document(self, text: str, endpoint_arn: str) -> Dict[str, Any]:
        """Classify document using custom Comprehend endpoint"""
        try:
            response = self.comprehend_client.classify_document(
                Text=text,
                EndpointArn=endpoint_arn
            )
            return response
        except ClientError as e:
            print(f"Error classifying document: {e}")
            return {}
    
    def create_document_classifier(self, classifier_config: Dict[str, Any]) -> Optional[str]:
        """Create document classifier"""
        try:
            response = self.comprehend_client.create_document_classifier(
                DocumentClassifierName=classifier_config['DocumentClassifierName'],
                DataAccessRoleArn=classifier_config['DataAccessRoleArn'],
                InputDataConfig=classifier_config['InputDataConfig'],
                OutputDataConfig=classifier_config['OutputDataConfig'],
                LanguageCode=classifier_config.get('LanguageCode', 'en'),
                Tags=classifier_config.get('Tags', [])
            )
            return response['DocumentClassifierArn']
        except ClientError as e:
            print(f"Error creating document classifier: {e}")
            return None
    
    def create_entity_recognizer(self, recognizer_config: Dict[str, Any]) -> Optional[str]:
        """Create entity recognizer"""
        try:
            response = self.comprehend_client.create_entity_recognizer(
                RecognizerName=recognizer_config['RecognizerName'],
                DataAccessRoleArn=recognizer_config['DataAccessRoleArn'],
                InputDataConfig=recognizer_config['InputDataConfig'],
                LanguageCode=recognizer_config.get('LanguageCode', 'en'),
                Tags=recognizer_config.get('Tags', [])
            )
            return response['EntityRecognizerArn']
        except ClientError as e:
            print(f"Error creating entity recognizer: {e}")
            return None
    
    # Amazon Translate
    def translate_text(self, text: str, source_language: str, 
                      target_language: str) -> Dict[str, Any]:
        """Translate text using Translate"""
        try:
            response = self.translate_client.translate_text(
                Text=text,
                SourceLanguageCode=source_language,
                TargetLanguageCode=target_language
            )
            return response
        except ClientError as e:
            print(f"Error translating text: {e}")
            return {}
    
    def batch_translate_text(self, job_config: Dict[str, Any]) -> Optional[str]:
        """Start batch translation job"""
        try:
            response = self.translate_client.start_text_translation_job(
                JobName=job_config['JobName'],
                InputDataConfig=job_config['InputDataConfig'],
                OutputDataConfig=job_config['OutputDataConfig'],
                DataAccessRoleArn=job_config['DataAccessRoleArn'],
                SourceLanguageCode=job_config['SourceLanguageCode'],
                TargetLanguageCodes=job_config['TargetLanguageCodes']
            )
            return response['JobId']
        except ClientError as e:
            print(f"Error starting batch translation: {e}")
            return None
    
    # Amazon Polly
    def synthesize_speech(self, text: str, voice_id: str = 'Joanna',
                         output_format: str = 'mp3') -> Optional[bytes]:
        """Synthesize speech using Polly"""
        try:
            response = self.polly_client.synthesize_speech(
                Text=text,
                VoiceId=voice_id,
                OutputFormat=output_format
            )
            return response['AudioStream'].read()
        except ClientError as e:
            print(f"Error synthesizing speech: {e}")
            return None
    
    def create_lexicon(self, lexicon_name: str, content: str) -> bool:
        """Create pronunciation lexicon"""
        try:
            self.polly_client.put_lexicon(
                Name=lexicon_name,
                Content=content
            )
            return True
        except ClientError as e:
            print(f"Error creating lexicon: {e}")
            return False
    
    def get_voices(self, language_code: str = None) -> List[Dict[str, Any]]:
        """Get available voices"""
        try:
            kwargs = {}
            if language_code:
                kwargs['LanguageCode'] = language_code
            
            response = self.polly_client.describe_voices(**kwargs)
            return response['Voices']
        except ClientError as e:
            print(f"Error getting voices: {e}")
            return []
    
    # Amazon Transcribe
    def start_transcription_job(self, job_config: Dict[str, Any]) -> Optional[str]:
        """Start transcription job"""
        try:
            response = self.transcribe_client.start_transcription_job(
                TranscriptionJobName=job_config['TranscriptionJobName'],
                LanguageCode=job_config.get('LanguageCode', 'en-US'),
                Media=job_config['Media'],
                MediaFormat=job_config.get('MediaFormat', 'mp3'),
                OutputBucketName=job_config.get('OutputBucketName'),
                OutputKey=job_config.get('OutputKey'),
                Settings=job_config.get('Settings', {})
            )
            return response['TranscriptionJob']['TranscriptionJobName']
        except ClientError as e:
            print(f"Error starting transcription job: {e}")
            return None
    
    def get_transcription_job(self, job_name: str) -> Optional[Dict[str, Any]]:
        """Get transcription job details"""
        try:
            response = self.transcribe_client.get_transcription_job(
                TranscriptionJobName=job_name
            )
            return response['TranscriptionJob']
        except ClientError as e:
            print(f"Error getting transcription job: {e}")
            return None
    
    def create_vocabulary(self, vocabulary_name: str, language_code: str,
                         phrases: List[str] = None, vocabulary_file_uri: str = None) -> bool:
        """Create custom vocabulary"""
        try:
            kwargs = {
                'VocabularyName': vocabulary_name,
                'LanguageCode': language_code
            }
            
            if phrases:
                kwargs['Phrases'] = phrases
            elif vocabulary_file_uri:
                kwargs['VocabularyFileUri'] = vocabulary_file_uri
            
            self.transcribe_client.create_vocabulary(**kwargs)
            return True
        except ClientError as e:
            print(f"Error creating vocabulary: {e}")
            return False
    
    # Amazon Textract
    def detect_document_text(self, document: Union[str, BinaryIO]) -> Dict[str, Any]:
        """Detect text in document using Textract"""
        try:
            if isinstance(document, str):
                if document.startswith('s3://'):
                    bucket, key = document.replace('s3://', '').split('/', 1)
                    response = self.textract_client.detect_document_text(
                        Document={'S3Object': {'Bucket': bucket, 'Name': key}}
                    )
                else:
                    with open(document, 'rb') as doc_file:
                        doc_bytes = doc_file.read()
                    response = self.textract_client.detect_document_text(
                        Document={'Bytes': doc_bytes}
                    )
            else:
                doc_bytes = document.read()
                response = self.textract_client.detect_document_text(
                    Document={'Bytes': doc_bytes}
                )
            
            return response
        except ClientError as e:
            print(f"Error detecting document text: {e}")
            return {}
    
    def analyze_document(self, document: Union[str, BinaryIO],
                        feature_types: List[str] = None) -> Dict[str, Any]:
        """Analyze document using Textract"""
        try:
            if not feature_types:
                feature_types = ['TABLES', 'FORMS']
            
            if isinstance(document, str):
                if document.startswith('s3://'):
                    bucket, key = document.replace('s3://', '').split('/', 1)
                    response = self.textract_client.analyze_document(
                        Document={'S3Object': {'Bucket': bucket, 'Name': key}},
                        FeatureTypes=feature_types
                    )
                else:
                    with open(document, 'rb') as doc_file:
                        doc_bytes = doc_file.read()
                    response = self.textract_client.analyze_document(
                        Document={'Bytes': doc_bytes},
                        FeatureTypes=feature_types
                    )
            else:
                doc_bytes = document.read()
                response = self.textract_client.analyze_document(
                    Document={'Bytes': doc_bytes},
                    FeatureTypes=feature_types
                )
            
            return response
        except ClientError as e:
            print(f"Error analyzing document: {e}")
            return {}
    
    def start_document_analysis(self, job_config: Dict[str, Any]) -> Optional[str]:
        """Start asynchronous document analysis"""
        try:
            response = self.textract_client.start_document_analysis(
                DocumentLocation=job_config['DocumentLocation'],
                FeatureTypes=job_config['FeatureTypes'],
                ClientRequestToken=job_config.get('ClientRequestToken'),
                JobTag=job_config.get('JobTag'),
                NotificationChannel=job_config.get('NotificationChannel', {})
            )
            return response['JobId']
        except ClientError as e:
            print(f"Error starting document analysis: {e}")
            return None
    
    # Amazon Forecast
    def create_dataset_group(self, dataset_group_config: Dict[str, Any]) -> Optional[str]:
        """Create Forecast dataset group"""
        try:
            response = self.forecast_client.create_dataset_group(
                DatasetGroupName=dataset_group_config['DatasetGroupName'],
                Domain=dataset_group_config['Domain'],
                DatasetArns=dataset_group_config.get('DatasetArns', [])
            )
            return response['DatasetGroupArn']
        except ClientError as e:
            print(f"Error creating dataset group: {e}")
            return None
    
    def create_dataset(self, dataset_config: Dict[str, Any]) -> Optional[str]:
        """Create Forecast dataset"""
        try:
            response = self.forecast_client.create_dataset(
                DatasetName=dataset_config['DatasetName'],
                Domain=dataset_config['Domain'],
                DatasetType=dataset_config['DatasetType'],
                DataFrequency=dataset_config.get('DataFrequency'),
                Schema=dataset_config['Schema']
            )
            return response['DatasetArn']
        except ClientError as e:
            print(f"Error creating dataset: {e}")
            return None
    
    def create_predictor(self, predictor_config: Dict[str, Any]) -> Optional[str]:
        """Create Forecast predictor"""
        try:
            response = self.forecast_client.create_predictor(
                PredictorName=predictor_config['PredictorName'],
                AlgorithmArn=predictor_config.get('AlgorithmArn'),
                ForecastHorizon=predictor_config['ForecastHorizon'],
                PerformAutoML=predictor_config.get('PerformAutoML', False),
                PerformHyperParameterOptimization=predictor_config.get('PerformHyperParameterOptimization', False),
                InputDataConfig=predictor_config['InputDataConfig'],
                FeaturizationConfig=predictor_config.get('FeaturizationConfig', {}),
                TrainingParameters=predictor_config.get('TrainingParameters', {})
            )
            return response['PredictorArn']
        except ClientError as e:
            print(f"Error creating predictor: {e}")
            return None
    
    def create_forecast(self, forecast_config: Dict[str, Any]) -> Optional[str]:
        """Create Forecast"""
        try:
            response = self.forecast_client.create_forecast(
                ForecastName=forecast_config['ForecastName'],
                PredictorArn=forecast_config['PredictorArn']
            )
            return response['ForecastArn']
        except ClientError as e:
            print(f"Error creating forecast: {e}")
            return None
    
    # Amazon Personalize
    def create_dataset_group(self, dataset_group_config: Dict[str, Any]) -> Optional[str]:
        """Create Personalize dataset group"""
        try:
            response = self.personalize_client.create_dataset_group(
                name=dataset_group_config['name'],
                roleArn=dataset_group_config['roleArn']
            )
            return response['datasetGroupArn']
        except ClientError as e:
            print(f"Error creating dataset group: {e}")
            return None
    
    def create_solution(self, solution_config: Dict[str, Any]) -> Optional[str]:
        """Create Personalize solution"""
        try:
            response = self.personalize_client.create_solution(
                name=solution_config['name'],
                datasetGroupArn=solution_config['datasetGroupArn'],
                recipeArn=solution_config.get('recipeArn'),
                performAutoML=solution_config.get('performAutoML', False)
            )
            return response['solutionArn']
        except ClientError as e:
            print(f"Error creating solution: {e}")
            return None
    
    def create_solution_version(self, solution_arn: str) -> Optional[str]:
        """Create solution version"""
        try:
            response = self.personalize_client.create_solution_version(
                solutionArn=solution_arn
            )
            return response['solutionVersionArn']
        except ClientError as e:
            print(f"Error creating solution version: {e}")
            return None
    
    def create_campaign(self, campaign_config: Dict[str, Any]) -> Optional[str]:
        """Create Personalize campaign"""
        try:
            response = self.personalize_client.create_campaign(
                name=campaign_config['name'],
                solutionVersionArn=campaign_config['solutionVersionArn'],
                minProvisionedTPS=campaign_config.get('minProvisionedTPS', 1)
            )
            return response['campaignArn']
        except ClientError as e:
            print(f"Error creating campaign: {e}")
            return None
    
    def get_recommendations(self, campaign_arn: str, user_id: str = None,
                           item_id: str = None, num_results: int = 10) -> Dict[str, Any]:
        """Get recommendations from Personalize campaign"""
        try:
            kwargs = {
                'campaignArn': campaign_arn,
                'numResults': num_results
            }
            
            if user_id:
                kwargs['userId'] = user_id
            if item_id:
                kwargs['itemId'] = item_id
            
            response = self.personalize_runtime_client.get_recommendations(**kwargs)
            return response
        except ClientError as e:
            print(f"Error getting recommendations: {e}")
            return {}
    
    def get_ai_services_metrics(self, service_name: str, 
                               start_time: datetime = None,
                               end_time: datetime = None) -> Dict[str, Any]:
        """Get CloudWatch metrics for AI services"""
        try:
            if not start_time:
                start_time = datetime.now() - timedelta(hours=24)
            if not end_time:
                end_time = datetime.now()
            
            response = self.cloudwatch_client.get_metric_statistics(
                Namespace=f'AWS/{service_name}',
                MetricName='Invocations',
                StartTime=start_time,
                EndTime=end_time,
                Period=3600,
                Statistics=['Sum', 'Average']
            )
            
            return {
                'service': service_name,
                'metrics': response['Datapoints'],
                'period': {'start': start_time.isoformat(), 'end': end_time.isoformat()}
            }
        except Exception as e:
            print(f"Error getting AI services metrics: {e}")
            return {}
    
    def create_ai_services_dashboard(self, services: List[str]) -> Dict[str, Any]:
        """Create AI services monitoring dashboard"""
        try:
            dashboard_data = {
                'services': services,
                'metrics': {},
                'created_at': datetime.now().isoformat()
            }
            
            for service in services:
                metrics = self.get_ai_services_metrics(service)
                dashboard_data['metrics'][service] = metrics
            
            return dashboard_data
        except Exception as e:
            print(f"Error creating AI services dashboard: {e}")
            return {}


# Example usage and testing
if __name__ == "__main__":
    # Initialize AI services manager
    ai_manager = AIServicesManager()
    
    # Test Rekognition
    print("Testing Amazon Rekognition...")
    # Note: You would need actual image files for testing
    # labels = ai_manager.detect_labels("path/to/image.jpg")
    # print(f"Detected labels: {labels}")
    
    # Test Comprehend
    print("Testing Amazon Comprehend...")
    sentiment = ai_manager.detect_sentiment("I love this product! It's amazing.")
    print(f"Sentiment: {sentiment}")
    
    entities = ai_manager.detect_entities("Apple Inc. is located in Cupertino, California.")
    print(f"Entities: {entities}")
    
    # Test Translate
    print("Testing Amazon Translate...")
    translation = ai_manager.translate_text("Hello, world!", "en", "es")
    print(f"Translation: {translation}")
    
    # Test Polly
    print("Testing Amazon Polly...")
    voices = ai_manager.get_voices()
    print(f"Available voices: {len(voices)}")
    
    # Test Textract
    print("Testing Amazon Textract...")
    # Note: You would need actual document files for testing
    # text = ai_manager.detect_document_text("path/to/document.pdf")
    # print(f"Extracted text: {text}")
    
    # Create AI services dashboard
    dashboard = ai_manager.create_ai_services_dashboard(['Rekognition', 'Comprehend', 'Translate'])
    print(f"Created dashboard for {len(dashboard['services'])} services")