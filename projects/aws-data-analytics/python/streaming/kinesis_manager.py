#!/usr/bin/env python3
"""
AWS Kinesis Data Streams Manager for real-time data processing.

This module provides comprehensive Kinesis management capabilities including
stream creation, data ingestion, and real-time analytics.
"""

import boto3
import json
import logging
import time
import base64
from typing import List, Dict, Any, Optional, Iterator
from datetime import datetime
import uuid

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class KinesisManager:
    """
    AWS Kinesis Data Streams Manager for real-time data processing.
    """
    
    def __init__(self, region: str = 'us-east-1'):
        """Initialize KinesisManager with AWS clients."""
        self.region = region
        self.kinesis_client = boto3.client('kinesis', region_name=region)
        self.kinesis_analytics_client = boto3.client('kinesisanalytics', region_name=region)
        self.kinesis_firehose_client = boto3.client('firehose', region_name=region)
        self.s3_client = boto3.client('s3', region_name=region)
        self.iam_client = boto3.client('iam', region_name=region)
        
    def create_stream(self, stream_name: str, shard_count: int = 1, retention_period: int = 24) -> bool:
        """Create Kinesis data stream."""
        try:
            # Check if stream already exists
            try:
                response = self.kinesis_client.describe_stream(StreamName=stream_name)
                logger.info(f"Stream {stream_name} already exists")
                return True
            except self.kinesis_client.exceptions.ResourceNotFoundException:
                pass
            
            # Create stream
            response = self.kinesis_client.create_stream(
                StreamName=stream_name,
                ShardCount=shard_count,
                RetentionPeriodHours=retention_period
            )
            
            # Wait for stream to become active
            self._wait_for_stream_active(stream_name)
            
            logger.info(f"Kinesis stream {stream_name} created successfully")
            return True
            
        except Exception as e:
            logger.error(f"Error creating Kinesis stream: {str(e)}")
            return False
    
    def _wait_for_stream_active(self, stream_name: str, timeout: int = 300) -> bool:
        """Wait for stream to become active."""
        start_time = time.time()
        
        while time.time() - start_time < timeout:
            try:
                response = self.kinesis_client.describe_stream(StreamName=stream_name)
                status = response['StreamDescription']['StreamStatus']
                
                if status == 'ACTIVE':
                    return True
                elif status in ['DELETING', 'DELETED']:
                    return False
                
                time.sleep(10)
                
            except Exception as e:
                logger.error(f"Error checking stream status: {str(e)}")
                return False
        
        return False
    
    def put_record(self, stream_name: str, data: Dict[str, Any], partition_key: str = None) -> Optional[str]:
        """Put single record to Kinesis stream."""
        try:
            if partition_key is None:
                partition_key = str(uuid.uuid4())
            
            # Convert data to JSON string
            data_json = json.dumps(data)
            
            response = self.kinesis_client.put_record(
                StreamName=stream_name,
                Data=data_json,
                PartitionKey=partition_key
            )
            
            sequence_number = response['SequenceNumber']
            shard_id = response['ShardId']
            
            logger.info(f"Record put to stream {stream_name}, shard {shard_id}, sequence {sequence_number}")
            return sequence_number
            
        except Exception as e:
            logger.error(f"Error putting record to Kinesis: {str(e)}")
            return None
    
    def put_records(self, stream_name: str, records: List[Dict[str, Any]], partition_key: str = None) -> Dict[str, Any]:
        """Put multiple records to Kinesis stream."""
        try:
            if partition_key is None:
                partition_key = str(uuid.uuid4())
            
            # Prepare records for batch put
            kinesis_records = []
            for record in records:
                kinesis_records.append({
                    'Data': json.dumps(record),
                    'PartitionKey': partition_key
                })
            
            response = self.kinesis_client.put_records(
                StreamName=stream_name,
                Records=kinesis_records
            )
            
            # Process response
            failed_record_count = response['FailedRecordCount']
            records = response['Records']
            
            result = {
                'total_records': len(records),
                'failed_records': failed_record_count,
                'successful_records': len(records) - failed_record_count,
                'records': records
            }
            
            logger.info(f"Batch put completed: {result['successful_records']} successful, {result['failed_records']} failed")
            return result
            
        except Exception as e:
            logger.error(f"Error putting records to Kinesis: {str(e)}")
            return {'total_records': 0, 'failed_records': 0, 'successful_records': 0, 'records': []}
    
    def get_records(self, stream_name: str, shard_id: str, shard_iterator: str = None, limit: int = 100) -> Dict[str, Any]:
        """Get records from Kinesis stream."""
        try:
            # Get shard iterator if not provided
            if shard_iterator is None:
                response = self.kinesis_client.get_shard_iterator(
                    StreamName=stream_name,
                    ShardId=shard_id,
                    ShardIteratorType='LATEST'
                )
                shard_iterator = response['ShardIterator']
            
            # Get records
            response = self.kinesis_client.get_records(
                ShardIterator=shard_iterator,
                Limit=limit
            )
            
            # Process records
            records = []
            for record in response['Records']:
                try:
                    data = json.loads(record['Data'].decode('utf-8'))
                    records.append({
                        'sequence_number': record['SequenceNumber'],
                        'partition_key': record['PartitionKey'],
                        'data': data,
                        'approximate_arrival_timestamp': record['ApproximateArrivalTimestamp']
                    })
                except json.JSONDecodeError:
                    # Handle non-JSON data
                    records.append({
                        'sequence_number': record['SequenceNumber'],
                        'partition_key': record['PartitionKey'],
                        'data': record['Data'].decode('utf-8'),
                        'approximate_arrival_timestamp': record['ApproximateArrivalTimestamp']
                    })
            
            return {
                'records': records,
                'next_shard_iterator': response.get('NextShardIterator'),
                'millis_behind_latest': response.get('MillisBehindLatest', 0)
            }
            
        except Exception as e:
            logger.error(f"Error getting records from Kinesis: {str(e)}")
            return {'records': [], 'next_shard_iterator': None, 'millis_behind_latest': 0}
    
    def list_streams(self) -> List[str]:
        """List all Kinesis streams."""
        try:
            response = self.kinesis_client.list_streams()
            return response['StreamNames']
            
        except Exception as e:
            logger.error(f"Error listing Kinesis streams: {str(e)}")
            return []
    
    def describe_stream(self, stream_name: str) -> Dict[str, Any]:
        """Describe Kinesis stream."""
        try:
            response = self.kinesis_client.describe_stream(StreamName=stream_name)
            stream_description = response['StreamDescription']
            
            return {
                'stream_name': stream_description['StreamName'],
                'stream_arn': stream_description['StreamARN'],
                'stream_status': stream_description['StreamStatus'],
                'shard_count': stream_description['ShardCount'],
                'retention_period_hours': stream_description['RetentionPeriodHours'],
                'encryption_type': stream_description.get('EncryptionType', 'NONE'),
                'key_id': stream_description.get('KeyId'),
                'shards': stream_description['Shards'],
                'has_more_shards': stream_description['HasMoreShards']
            }
            
        except Exception as e:
            logger.error(f"Error describing Kinesis stream: {str(e)}")
            return {}
    
    def create_firehose_delivery_stream(self, stream_name: str, s3_bucket: str, prefix: str = "firehose/") -> bool:
        """Create Kinesis Data Firehose delivery stream."""
        try:
            # Create IAM role for Firehose
            role_arn = self._create_firehose_role(stream_name)
            
            # Create Firehose delivery stream
            response = self.kinesis_firehose_client.create_delivery_stream(
                DeliveryStreamName=stream_name,
                DeliveryStreamType='DirectPut',
                ExtendedS3DestinationConfiguration={
                    'RoleARN': role_arn,
                    'BucketARN': f'arn:aws:s3:::{s3_bucket}',
                    'Prefix': prefix,
                    'BufferingHints': {
                        'SizeInMBs': 64,
                        'IntervalInSeconds': 60
                    },
                    'CompressionFormat': 'GZIP',
                    'CloudWatchLoggingOptions': {
                        'Enabled': True,
                        'LogGroupName': f'/aws/kinesisfirehose/{stream_name}',
                        'LogStreamName': 'S3Delivery'
                    }
                }
            )
            
            logger.info(f"Firehose delivery stream {stream_name} created successfully")
            return True
            
        except Exception as e:
            logger.error(f"Error creating Firehose delivery stream: {str(e)}")
            return False
    
    def _create_firehose_role(self, stream_name: str) -> str:
        """Create IAM role for Firehose."""
        role_name = f"{stream_name}-firehose-role"
        
        try:
            # Check if role exists
            self.iam_client.get_role(RoleName=role_name)
            logger.info(f"Firehose role {role_name} already exists")
            return f"arn:aws:iam::{self._get_account_id()}:role/{role_name}"
            
        except self.iam_client.exceptions.NoSuchEntityException:
            # Create role
            assume_role_policy = {
                "Version": "2012-10-17",
                "Statement": [{
                    "Effect": "Allow",
                    "Principal": {"Service": "firehose.amazonaws.com"},
                    "Action": "sts:AssumeRole"
                }]
            }
            
            self.iam_client.create_role(
                RoleName=role_name,
                AssumeRolePolicyDocument=json.dumps(assume_role_policy),
                Description=f"IAM role for {stream_name} Firehose"
            )
            
            # Attach policies
            policies = [
                "arn:aws:iam::aws:policy/service-role/AWSKinesisFirehoseServiceRole"
            ]
            
            for policy_arn in policies:
                self.iam_client.attach_role_policy(
                    RoleName=role_name,
                    PolicyArn=policy_arn
                )
            
            logger.info(f"Created Firehose role: {role_name}")
            return f"arn:aws:iam::{self._get_account_id()}:role/{role_name}"
    
    def create_kinesis_analytics_application(self, app_name: str, input_stream: str, output_stream: str = None) -> bool:
        """Create Kinesis Analytics application."""
        try:
            # Create IAM role for Kinesis Analytics
            role_arn = self._create_kinesis_analytics_role(app_name)
            
            # Build application configuration
            app_config = {
                'ApplicationName': app_name,
                'RuntimeEnvironment': 'FLINK-1_15',
                'ServiceExecutionRole': role_arn,
                'ApplicationConfiguration': {
                    'FlinkApplicationConfiguration': {
                        'CheckpointConfiguration': {
                            'ConfigurationType': 'DEFAULT'
                        },
                        'MonitoringConfiguration': {
                            'ConfigurationType': 'DEFAULT',
                            'LogLevel': 'INFO'
                        }
                    }
                }
            }
            
            # Add input configuration
            app_config['ApplicationConfiguration']['FlinkApplicationConfiguration']['InputConfigurations'] = [{
                'InputId': 'input-1',
                'InputSchema': {
                    'RecordFormat': {
                        'RecordFormatType': 'JSON'
                    },
                    'RecordColumns': [
                        {'Name': 'timestamp', 'SqlType': 'TIMESTAMP'},
                        {'Name': 'value', 'SqlType': 'DOUBLE'}
                    ]
                }
            }]
            
            # Add output configuration if specified
            if output_stream:
                app_config['ApplicationConfiguration']['FlinkApplicationConfiguration']['OutputConfigurations'] = [{
                    'OutputId': 'output-1',
                    'DestinationSchema': {
                        'RecordFormatType': 'JSON'
                    }
                }]
            
            response = self.kinesis_analytics_client.create_application(**app_config)
            
            logger.info(f"Kinesis Analytics application {app_name} created successfully")
            return True
            
        except Exception as e:
            logger.error(f"Error creating Kinesis Analytics application: {str(e)}")
            return False
    
    def _create_kinesis_analytics_role(self, app_name: str) -> str:
        """Create IAM role for Kinesis Analytics."""
        role_name = f"{app_name}-kinesis-analytics-role"
        
        try:
            # Check if role exists
            self.iam_client.get_role(RoleName=role_name)
            logger.info(f"Kinesis Analytics role {role_name} already exists")
            return f"arn:aws:iam::{self._get_account_id()}:role/{role_name}"
            
        except self.iam_client.exceptions.NoSuchEntityException:
            # Create role
            assume_role_policy = {
                "Version": "2012-10-17",
                "Statement": [{
                    "Effect": "Allow",
                    "Principal": {"Service": "kinesisanalytics.amazonaws.com"},
                    "Action": "sts:AssumeRole"
                }]
            }
            
            self.iam_client.create_role(
                RoleName=role_name,
                AssumeRolePolicyDocument=json.dumps(assume_role_policy),
                Description=f"IAM role for {app_name} Kinesis Analytics"
            )
            
            # Attach policies
            policies = [
                "arn:aws:iam::aws:policy/service-role/AWSKinesisAnalyticsServiceRole"
            ]
            
            for policy_arn in policies:
                self.iam_client.attach_role_policy(
                    RoleName=role_name,
                    PolicyArn=policy_arn
                )
            
            logger.info(f"Created Kinesis Analytics role: {role_name}")
            return f"arn:aws:iam::{self._get_account_id()}:role/{role_name}"
    
    def delete_stream(self, stream_name: str) -> bool:
        """Delete Kinesis stream."""
        try:
            self.kinesis_client.delete_stream(StreamName=stream_name)
            logger.info(f"Kinesis stream {stream_name} deleted successfully")
            return True
            
        except Exception as e:
            logger.error(f"Error deleting Kinesis stream: {str(e)}")
            return False
    
    def _get_account_id(self) -> str:
        """Get AWS account ID."""
        try:
            sts_client = boto3.client('sts', region_name=self.region)
            response = sts_client.get_caller_identity()
            return response['Account']
        except Exception as e:
            logger.error(f"Error getting account ID: {str(e)}")
            return ""


def main():
    """Main function for testing KinesisManager."""
    # Example usage
    kinesis_manager = KinesisManager()
    
    # Create stream
    stream_name = "test-data-stream"
    if kinesis_manager.create_stream(stream_name, shard_count=2):
        print(f"Stream {stream_name} created successfully")
        
        # Put sample records
        sample_data = [
            {"timestamp": datetime.now().isoformat(), "value": 100, "metric": "cpu_usage"},
            {"timestamp": datetime.now().isoformat(), "value": 200, "metric": "memory_usage"},
            {"timestamp": datetime.now().isoformat(), "value": 150, "metric": "disk_usage"}
        ]
        
        result = kinesis_manager.put_records(stream_name, sample_data)
        print(f"Put records result: {result}")
        
        # Get stream info
        stream_info = kinesis_manager.describe_stream(stream_name)
        print(f"Stream info: {stream_info}")


if __name__ == "__main__":
    main()