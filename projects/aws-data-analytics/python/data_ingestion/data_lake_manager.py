#!/usr/bin/env python3
"""
AWS Data Lake Manager for data ingestion and organization.

This module provides comprehensive data lake management capabilities including
S3 bucket management, Glue catalog setup, and data organization.
"""

import boto3
import json
import logging
import time
from typing import List, Dict, Any, Optional
from datetime import datetime
import yaml

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class DataLakeManager:
    """
    AWS Data Lake Manager for data ingestion and organization.
    """
    
    def __init__(self, region: str = 'us-east-1'):
        """Initialize DataLakeManager with AWS clients."""
        self.region = region
        self.s3_client = boto3.client('s3', region_name=region)
        self.glue_client = boto3.client('glue', region_name=region)
        self.lakeformation_client = boto3.client('lakeformation', region_name=region)
        self.iam_client = boto3.client('iam', region_name=region)
        
    def create_data_lake_structure(self, bucket_name: str, lake_config: Dict[str, Any]) -> bool:
        """Create organized data lake structure."""
        try:
            # Validate lake configuration
            self._validate_lake_config(lake_config)
            
            # Create S3 bucket if not exists
            if not self._bucket_exists(bucket_name):
                self._create_s3_bucket(bucket_name)
            
            # Create data lake zones
            zones = lake_config.get('zones', ['raw', 'processed', 'curated', 'analytics'])
            for zone in zones:
                self._create_data_zone(bucket_name, zone, lake_config.get('zone_configs', {}).get(zone, {}))
            
            # Setup Glue Data Catalog
            if lake_config.get('setup_glue_catalog', True):
                self._setup_glue_catalog(bucket_name, lake_config)
            
            # Setup Lake Formation
            if lake_config.get('setup_lake_formation', True):
                self._setup_lake_formation(bucket_name, lake_config)
            
            logger.info(f"Data lake structure created successfully in bucket: {bucket_name}")
            return True
            
        except Exception as e:
            logger.error(f"Error creating data lake structure: {str(e)}")
            return False
    
    def _validate_lake_config(self, config: Dict[str, Any]) -> None:
        """Validate data lake configuration."""
        required_fields = ['bucket_name']
        for field in required_fields:
            if field not in config:
                raise ValueError(f"Missing required field: {field}")
    
    def _bucket_exists(self, bucket_name: str) -> bool:
        """Check if S3 bucket exists."""
        try:
            self.s3_client.head_bucket(Bucket=bucket_name)
            return True
        except:
            return False
    
    def _create_s3_bucket(self, bucket_name: str) -> None:
        """Create S3 bucket for data lake."""
        try:
            # Create bucket
            if self.region == 'us-east-1':
                self.s3_client.create_bucket(Bucket=bucket_name)
            else:
                self.s3_client.create_bucket(
                    Bucket=bucket_name,
                    CreateBucketConfiguration={'LocationConstraint': self.region}
                )
            
            # Enable versioning
            self.s3_client.put_bucket_versioning(
                Bucket=bucket_name,
                VersioningConfiguration={'Status': 'Enabled'}
            )
            
            # Enable server-side encryption
            self.s3_client.put_bucket_encryption(
                Bucket=bucket_name,
                ServerSideEncryptionConfiguration={
                    'Rules': [{
                        'ApplyServerSideEncryptionByDefault': {
                            'SSEAlgorithm': 'AES256'
                        }
                    }]
                }
            )
            
            # Set lifecycle policy
            lifecycle_policy = {
                'Rules': [
                    {
                        'ID': 'DataLakeLifecycle',
                        'Status': 'Enabled',
                        'Transitions': [
                            {
                                'Days': 30,
                                'StorageClass': 'STANDARD_IA'
                            },
                            {
                                'Days': 90,
                                'StorageClass': 'GLACIER'
                            },
                            {
                                'Days': 365,
                                'StorageClass': 'DEEP_ARCHIVE'
                            }
                        ]
                    }
                ]
            }
            
            self.s3_client.put_bucket_lifecycle_configuration(
                Bucket=bucket_name,
                LifecycleConfiguration=lifecycle_policy
            )
            
            # Block public access
            self.s3_client.put_public_access_block(
                Bucket=bucket_name,
                PublicAccessBlockConfiguration={
                    'BlockPublicAcls': True,
                    'IgnorePublicAcls': True,
                    'BlockPublicPolicy': True,
                    'RestrictPublicBuckets': True
                }
            )
            
            logger.info(f"S3 bucket {bucket_name} created successfully")
            
        except Exception as e:
            logger.error(f"Error creating S3 bucket: {str(e)}")
            raise
    
    def _create_data_zone(self, bucket_name: str, zone: str, zone_config: Dict[str, Any]) -> None:
        """Create data zone in S3 bucket."""
        try:
            # Create zone folder
            self.s3_client.put_object(
                Bucket=bucket_name,
                Key=f'{zone}/',
                Body=''
            )
            
            # Create subfolders based on zone type
            if zone == 'raw':
                subfolders = ['landing', 'staging', 'archive']
            elif zone == 'processed':
                subfolders = ['cleaned', 'transformed', 'validated']
            elif zone == 'curated':
                subfolders = ['datasets', 'models', 'reports']
            elif zone == 'analytics':
                subfolders = ['dashboards', 'insights', 'ml-models']
            else:
                subfolders = zone_config.get('subfolders', [])
            
            for subfolder in subfolders:
                self.s3_client.put_object(
                    Bucket=bucket_name,
                    Key=f'{zone}/{subfolder}/',
                    Body=''
                )
            
            logger.info(f"Data zone {zone} created successfully")
            
        except Exception as e:
            logger.error(f"Error creating data zone {zone}: {str(e)}")
            raise
    
    def _setup_glue_catalog(self, bucket_name: str, config: Dict[str, Any]) -> None:
        """Setup Glue Data Catalog."""
        try:
            database_name = config.get('glue_database_name', f"{bucket_name}-catalog")
            
            # Create Glue database
            try:
                self.glue_client.create_database(
                    DatabaseInput={
                        'Name': database_name,
                        'Description': f'Data lake catalog for {bucket_name}',
                        'LocationUri': f's3://{bucket_name}/'
                    }
                )
                logger.info(f"Glue database {database_name} created successfully")
            except self.glue_client.exceptions.AlreadyExistsException:
                logger.info(f"Glue database {database_name} already exists")
            
            # Create crawlers for each zone
            zones = config.get('zones', ['raw', 'processed', 'curated', 'analytics'])
            for zone in zones:
                crawler_name = f"{database_name}-{zone}-crawler"
                
                try:
                    self.glue_client.create_crawler(
                        Name=crawler_name,
                        Role=config.get('glue_role_arn', self._get_glue_role_arn()),
                        DatabaseName=database_name,
                        Targets={
                            'S3Targets': [{
                                'Path': f's3://{bucket_name}/{zone}/',
                                'Exclusions': ['**/archive/**']
                            }]
                        },
                        Schedule=config.get('crawler_schedule', 'cron(0 2 * * ? *)'),
                        Description=f"Crawler for {zone} zone in {bucket_name}"
                    )
                    logger.info(f"Glue crawler {crawler_name} created successfully")
                except self.glue_client.exceptions.AlreadyExistsException:
                    logger.info(f"Glue crawler {crawler_name} already exists")
            
        except Exception as e:
            logger.error(f"Error setting up Glue catalog: {str(e)}")
            raise
    
    def _setup_lake_formation(self, bucket_name: str, config: Dict[str, Any]) -> None:
        """Setup Lake Formation."""
        try:
            # Register S3 location
            try:
                self.lakeformation_client.register_resource(
                    ResourceArn=f'arn:aws:s3:::{bucket_name}',
                    UseServiceLinkedRole=True
                )
                logger.info(f"S3 location {bucket_name} registered with Lake Formation")
            except self.lakeformation_client.exceptions.AlreadyExistsException:
                logger.info(f"S3 location {bucket_name} already registered with Lake Formation")
            
            # Create data lake administrators
            administrators = config.get('data_lake_administrators', [])
            if administrators:
                try:
                    self.lakeformation_client.put_data_lake_settings(
                        DataLakeSettings={
                            'DataLakeAdmins': [
                                {'DataLakePrincipalIdentifier': admin} for admin in administrators
                            ]
                        }
                    )
                    logger.info("Data lake administrators configured")
                except Exception as e:
                    logger.warning(f"Could not configure data lake administrators: {str(e)}")
            
        except Exception as e:
            logger.error(f"Error setting up Lake Formation: {str(e)}")
            raise
    
    def _get_glue_role_arn(self) -> str:
        """Get Glue service role ARN."""
        try:
            response = self.iam_client.get_role(RoleName='AWSGlueServiceRole')
            return response['Role']['Arn']
        except Exception as e:
            logger.error(f"Error getting Glue role: {str(e)}")
            return None
    
    def ingest_data(self, bucket_name: str, source_data: Dict[str, Any]) -> bool:
        """Ingest data into data lake."""
        try:
            # Validate source data
            self._validate_source_data(source_data)
            
            # Determine target zone
            target_zone = source_data.get('target_zone', 'raw')
            file_path = source_data.get('file_path', '')
            data = source_data.get('data', '')
            
            # Create S3 key
            timestamp = datetime.now().strftime('%Y/%m/%d/%H')
            s3_key = f"{target_zone}/landing/{timestamp}/{file_path}"
            
            # Upload data to S3
            self.s3_client.put_object(
                Bucket=bucket_name,
                Key=s3_key,
                Body=data,
                ContentType=source_data.get('content_type', 'application/json')
            )
            
            logger.info(f"Data ingested successfully to s3://{bucket_name}/{s3_key}")
            return True
            
        except Exception as e:
            logger.error(f"Error ingesting data: {str(e)}")
            return False
    
    def _validate_source_data(self, data: Dict[str, Any]) -> None:
        """Validate source data."""
        required_fields = ['file_path', 'data']
        for field in required_fields:
            if field not in data:
                raise ValueError(f"Missing required field: {field}")
    
    def get_data_lake_status(self, bucket_name: str) -> Dict[str, Any]:
        """Get data lake status and information."""
        try:
            # Get bucket information
            bucket_info = self.s3_client.head_bucket(Bucket=bucket_name)
            
            # List objects in each zone
            zones = ['raw', 'processed', 'curated', 'analytics']
            zone_stats = {}
            
            for zone in zones:
                try:
                    response = self.s3_client.list_objects_v2(
                        Bucket=bucket_name,
                        Prefix=f'{zone}/',
                        MaxKeys=1000
                    )
                    
                    zone_stats[zone] = {
                        'object_count': response.get('KeyCount', 0),
                        'total_size': sum(obj.get('Size', 0) for obj in response.get('Contents', [])),
                        'last_modified': max(
                            (obj.get('LastModified', datetime.min) for obj in response.get('Contents', [])),
                            default=None
                        )
                    }
                except Exception as e:
                    zone_stats[zone] = {'error': str(e)}
            
            return {
                'bucket_name': bucket_name,
                'region': self.region,
                'creation_date': bucket_info.get('ResponseMetadata', {}).get('HTTPHeaders', {}).get('date'),
                'zones': zone_stats
            }
            
        except Exception as e:
            logger.error(f"Error getting data lake status: {str(e)}")
            return {}


def main():
    """Main function for testing DataLakeManager."""
    # Example usage
    data_lake_manager = DataLakeManager()
    
    # Example data lake configuration
    lake_config = {
        'bucket_name': 'my-data-lake-bucket',
        'zones': ['raw', 'processed', 'curated', 'analytics'],
        'setup_glue_catalog': True,
        'setup_lake_formation': True,
        'glue_database_name': 'my-data-lake-catalog',
        'crawler_schedule': 'cron(0 2 * * ? *)',
        'data_lake_administrators': ['arn:aws:iam::123456789012:user/admin']
    }
    
    # Create data lake structure
    success = data_lake_manager.create_data_lake_structure('my-data-lake-bucket', lake_config)
    if success:
        print("Data lake structure created successfully")
        
        # Ingest sample data
        sample_data = {
            'file_path': 'sample-data.json',
            'data': json.dumps({'message': 'Hello, Data Lake!'}),
            'target_zone': 'raw',
            'content_type': 'application/json'
        }
        
        ingest_success = data_lake_manager.ingest_data('my-data-lake-bucket', sample_data)
        if ingest_success:
            print("Sample data ingested successfully")
        
        # Get data lake status
        status = data_lake_manager.get_data_lake_status('my-data-lake-bucket')
        print(f"Data lake status: {json.dumps(status, indent=2, default=str)}")


if __name__ == "__main__":
    main()