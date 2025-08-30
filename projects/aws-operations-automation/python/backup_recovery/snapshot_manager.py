#!/usr/bin/env python3
"""
AWS Snapshot Manager - Backup & Recovery Automation

This script provides automated snapshot management for EBS volumes
including creation, cleanup, cross-region replication, and lifecycle management.

Features:
- Automated snapshot creation
- Intelligent snapshot cleanup
- Cross-region backup replication
- Snapshot lifecycle management
- Backup compliance monitoring
- Cost optimization

Author: AWS Operations Automation
Version: 1.0.0
"""

import boto3
import json
import logging
from datetime import datetime, timedelta
from typing import List, Dict, Any, Optional
import yaml
import os

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('snapshot_manager.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)


class SnapshotManager:
    """
    AWS Snapshot Manager for automated backup and recovery.
    """
    
    def __init__(self, config_file: str = 'config/automation_config.yaml'):
        """
        Initialize the snapshot manager.
        
        Args:
            config_file (str): Path to configuration file
        """
        self.config = self.load_config(config_file)
        self.ec2_client = boto3.client('ec2', region_name=self.config.get('aws_region', 'us-east-1'))
        self.cloudwatch_client = boto3.client('cloudwatch', region_name=self.config.get('aws_region', 'us-east-1'))
        self.sns_client = boto3.client('sns', region_name=self.config.get('aws_region', 'us-east-1'))
        
        # Backup tracking
        self.backup_stats = {
            'snapshots_created': 0,
            'snapshots_deleted': 0,
            'cross_region_copies': 0,
            'total_backup_size': 0
        }
    
    def load_config(self, config_file: str) -> Dict[str, Any]:
        """
        Load configuration from YAML file.
        
        Args:
            config_file (str): Path to configuration file
            
        Returns:
            Dict containing configuration
        """
        try:
            with open(config_file, 'r') as file:
                config = yaml.safe_load(file)
            logger.info(f"Configuration loaded from {config_file}")
            return config
        except FileNotFoundError:
            logger.warning(f"Configuration file {config_file} not found, using defaults")
            return self.get_default_config()
        except Exception as e:
            logger.error(f"Error loading configuration: {str(e)}")
            return self.get_default_config()
    
    def get_default_config(self) -> Dict[str, Any]:
        """
        Get default configuration.
        
        Returns:
            Dict containing default configuration
        """
        return {
            'aws_region': 'us-east-1',
            'backup_schedules': {
                'daily': {
                    'enabled': True,
                    'time': '02:00',
                    'retention_days': 7
                },
                'weekly': {
                    'enabled': True,
                    'day': 'sunday',
                    'time': '03:00',
                    'retention_days': 30
                },
                'monthly': {
                    'enabled': True,
                    'day': '1st',
                    'time': '04:00',
                    'retention_days': 90
                }
            },
            'cross_region_backup': {
                'enabled': True,
                'destination_regions': ['us-west-2', 'eu-west-1'],
                'retention_days': 365
            },
            'snapshot_tags': {
                'automated': 'true',
                'backup_type': 'automated',
                'environment': 'production'
            },
            'notifications': {
                'email': 'admin@company.com',
                'sns_topic': 'aws-operations-alerts'
            },
            'compliance': {
                'rto_hours': 4,
                'rpo_hours': 24,
                'encryption_required': True
            }
        }
    
    def get_volumes_for_backup(self, tag_key: str = 'Backup', tag_value: str = 'true') -> List[Dict[str, Any]]:
        """
        Get EBS volumes that need backup.
        
        Args:
            tag_key (str): Tag key to filter volumes
            tag_value (str): Tag value to filter volumes
            
        Returns:
            List of volume dictionaries
        """
        try:
            response = self.ec2_client.describe_volumes(
                Filters=[
                    {
                        'Name': f'tag:{tag_key}',
                        'Values': [tag_value]
                    },
                    {
                        'Name': 'attachment.status',
                        'Values': ['attached']
                    }
                ]
            )
            
            volumes = response['Volumes']
            logger.info(f"Found {len(volumes)} volumes for backup")
            return volumes
            
        except Exception as e:
            logger.error(f"Error getting volumes for backup: {str(e)}")
            return []
    
    def create_snapshots(self, backup_type: str = 'daily') -> List[str]:
        """
        Create snapshots for all volumes that need backup.
        
        Args:
            backup_type (str): Type of backup (daily, weekly, monthly)
            
        Returns:
            List of created snapshot IDs
        """
        try:
            volumes = self.get_volumes_for_backup()
            created_snapshots = []
            
            for volume in volumes:
                try:
                    # Create snapshot
                    snapshot = self.ec2_client.create_snapshot(
                        VolumeId=volume['VolumeId'],
                        Description=f"Automated {backup_type} backup - {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}",
                        TagSpecifications=[
                            {
                                'ResourceType': 'snapshot',
                                'Tags': [
                                    {'Key': 'Automated', 'Value': 'true'},
                                    {'Key': 'BackupType', 'Value': backup_type},
                                    {'Key': 'CreatedDate', 'Value': datetime.now().strftime('%Y-%m-%d')},
                                    {'Key': 'VolumeId', 'Value': volume['VolumeId']},
                                    {'Key': 'Environment', 'Value': self.get_volume_tag(volume, 'Environment', 'production')}
                                ]
                            }
                        ]
                    )
                    
                    created_snapshots.append(snapshot['SnapshotId'])
                    self.backup_stats['snapshots_created'] += 1
                    self.backup_stats['total_backup_size'] += volume.get('Size', 0)
                    
                    logger.info(f"Created snapshot {snapshot['SnapshotId']} for volume {volume['VolumeId']}")
                    
                except Exception as e:
                    logger.error(f"Error creating snapshot for volume {volume['VolumeId']}: {str(e)}")
            
            if created_snapshots:
                self.send_notification(
                    f"Created {len(created_snapshots)} {backup_type} snapshots",
                    f"Successfully created {len(created_snapshots)} snapshots at {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}"
                )
            
            return created_snapshots
            
        except Exception as e:
            logger.error(f"Error in create_snapshots: {str(e)}")
            return []
    
    def get_volume_tag(self, volume: Dict[str, Any], tag_key: str, default: str = '') -> str:
        """
        Get tag value from volume.
        
        Args:
            volume (Dict): Volume dictionary
            tag_key (str): Tag key to get
            default (str): Default value if tag not found
            
        Returns:
            Tag value or default
        """
        for tag in volume.get('Tags', []):
            if tag['Key'] == tag_key:
                return tag['Value']
        return default
    
    def cleanup_old_snapshots(self, retention_days: int = 30, backup_type: str = 'daily') -> List[str]:
        """
        Clean up old snapshots based on retention policy.
        
        Args:
            retention_days (int): Number of days to retain snapshots
            backup_type (str): Type of backup to clean up
            
        Returns:
            List of deleted snapshot IDs
        """
        try:
            cutoff_date = datetime.now() - timedelta(days=retention_days)
            deleted_snapshots = []
            
            # Get snapshots to delete
            snapshots = self.ec2_client.describe_snapshots(
                OwnerIds=['self'],
                Filters=[
                    {
                        'Name': 'tag:Automated',
                        'Values': ['true']
                    },
                    {
                        'Name': 'tag:BackupType',
                        'Values': [backup_type]
                    }
                ]
            )
            
            for snapshot in snapshots['Snapshots']:
                snapshot_date = snapshot['StartTime'].replace(tzinfo=None)
                
                if snapshot_date < cutoff_date:
                    try:
                        # Check if snapshot is in use
                        if not self.is_snapshot_in_use(snapshot['SnapshotId']):
                            self.ec2_client.delete_snapshot(
                                SnapshotId=snapshot['SnapshotId']
                            )
                            deleted_snapshots.append(snapshot['SnapshotId'])
                            self.backup_stats['snapshots_deleted'] += 1
                            
                            logger.info(f"Deleted old snapshot: {snapshot['SnapshotId']}")
                        else:
                            logger.warning(f"Snapshot {snapshot['SnapshotId']} is in use, skipping deletion")
                            
                    except Exception as e:
                        logger.error(f"Error deleting snapshot {snapshot['SnapshotId']}: {str(e)}")
            
            if deleted_snapshots:
                self.send_notification(
                    f"Deleted {len(deleted_snapshots)} old {backup_type} snapshots",
                    f"Successfully deleted {len(deleted_snapshots)} old snapshots at {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}"
                )
            
            return deleted_snapshots
            
        except Exception as e:
            logger.error(f"Error in cleanup_old_snapshots: {str(e)}")
            return []
    
    def is_snapshot_in_use(self, snapshot_id: str) -> bool:
        """
        Check if snapshot is in use (has AMIs or other dependencies).
        
        Args:
            snapshot_id (str): Snapshot ID to check
            
        Returns:
            True if snapshot is in use, False otherwise
        """
        try:
            # Check if snapshot is used by any AMI
            response = self.ec2_client.describe_images(
                Owners=['self'],
                Filters=[
                    {
                        'Name': 'block-device-mapping.snapshot-id',
                        'Values': [snapshot_id]
                    }
                ]
            )
            
            if response['Images']:
                return True
            
            # Check if snapshot is used by any volume
            response = self.ec2_client.describe_volumes(
                Filters=[
                    {
                        'Name': 'snapshot-id',
                        'Values': [snapshot_id]
                    }
                ]
            )
            
            if response['Volumes']:
                return True
            
            return False
            
        except Exception as e:
            logger.error(f"Error checking if snapshot {snapshot_id} is in use: {str(e)}")
            return True  # Assume in use if error
    
    def copy_snapshots_cross_region(self, snapshot_ids: List[str], destination_regions: List[str]) -> List[str]:
        """
        Copy snapshots to other regions for disaster recovery.
        
        Args:
            snapshot_ids (List[str]): List of snapshot IDs to copy
            destination_regions (List[str]): List of destination regions
            
        Returns:
            List of copied snapshot IDs
        """
        try:
            copied_snapshots = []
            
            for snapshot_id in snapshot_ids:
                for region in destination_regions:
                    try:
                        # Copy snapshot to destination region
                        response = self.ec2_client.copy_snapshot(
                            SourceRegion=self.config.get('aws_region', 'us-east-1'),
                            SourceSnapshotId=snapshot_id,
                            DestinationRegion=region,
                            Description=f"Cross-region backup copy of {snapshot_id}",
                            TagSpecifications=[
                                {
                                    'ResourceType': 'snapshot',
                                    'Tags': [
                                        {'Key': 'Automated', 'Value': 'true'},
                                        {'Key': 'CrossRegionCopy', 'Value': 'true'},
                                        {'Key': 'SourceSnapshot', 'Value': snapshot_id},
                                        {'Key': 'CreatedDate', 'Value': datetime.now().strftime('%Y-%m-%d')}
                                    ]
                                }
                            ]
                        )
                        
                        copied_snapshots.append(response['SnapshotId'])
                        self.backup_stats['cross_region_copies'] += 1
                        
                        logger.info(f"Copied snapshot {snapshot_id} to region {region}: {response['SnapshotId']}")
                        
                    except Exception as e:
                        logger.error(f"Error copying snapshot {snapshot_id} to region {region}: {str(e)}")
            
            if copied_snapshots:
                self.send_notification(
                    f"Copied {len(copied_snapshots)} snapshots cross-region",
                    f"Successfully copied snapshots to {len(destination_regions)} regions"
                )
            
            return copied_snapshots
            
        except Exception as e:
            logger.error(f"Error in copy_snapshots_cross_region: {str(e)}")
            return []
    
    def get_snapshot_lifecycle_status(self) -> Dict[str, Any]:
        """
        Get snapshot lifecycle status and compliance information.
        
        Returns:
            Dict containing snapshot lifecycle status
        """
        try:
            status = {
                'total_snapshots': 0,
                'daily_snapshots': 0,
                'weekly_snapshots': 0,
                'monthly_snapshots': 0,
                'cross_region_snapshots': 0,
                'total_size_gb': 0,
                'compliance_status': 'compliant'
            }
            
            # Get all automated snapshots
            snapshots = self.ec2_client.describe_snapshots(
                OwnerIds=['self'],
                Filters=[
                    {
                        'Name': 'tag:Automated',
                        'Values': ['true']
                    }
                ]
            )
            
            for snapshot in snapshots['Snapshots']:
                status['total_snapshots'] += 1
                status['total_size_gb'] += snapshot.get('VolumeSize', 0)
                
                # Count by backup type
                backup_type = self.get_snapshot_tag(snapshot, 'BackupType', 'unknown')
                if backup_type == 'daily':
                    status['daily_snapshots'] += 1
                elif backup_type == 'weekly':
                    status['weekly_snapshots'] += 1
                elif backup_type == 'monthly':
                    status['monthly_snapshots'] += 1
                
                # Count cross-region copies
                if self.get_snapshot_tag(snapshot, 'CrossRegionCopy') == 'true':
                    status['cross_region_snapshots'] += 1
            
            # Check compliance
            if status['daily_snapshots'] == 0:
                status['compliance_status'] = 'non-compliant'
            
            return status
            
        except Exception as e:
            logger.error(f"Error getting snapshot lifecycle status: {str(e)}")
            return {}
    
    def get_snapshot_tag(self, snapshot: Dict[str, Any], tag_key: str, default: str = '') -> str:
        """
        Get tag value from snapshot.
        
        Args:
            snapshot (Dict): Snapshot dictionary
            tag_key (str): Tag key to get
            default (str): Default value if tag not found
            
        Returns:
            Tag value or default
        """
        for tag in snapshot.get('Tags', []):
            if tag['Key'] == tag_key:
                return tag['Value']
        return default
    
    def send_notification(self, subject: str, message: str):
        """
        Send notification via SNS.
        
        Args:
            subject (str): Notification subject
            message (str): Notification message
        """
        try:
            sns_topic = self.config.get('notifications', {}).get('sns_topic')
            if sns_topic:
                self.sns_client.publish(
                    TopicArn=sns_topic,
                    Subject=subject,
                    Message=message
                )
                logger.info(f"Notification sent: {subject}")
        except Exception as e:
            logger.error(f"Error sending notification: {str(e)}")
    
    def publish_metrics(self):
        """Publish backup metrics to CloudWatch."""
        try:
            self.cloudwatch_client.put_metric_data(
                Namespace='AWS/OperationsAutomation',
                MetricData=[
                    {
                        'MetricName': 'SnapshotsCreated',
                        'Value': self.backup_stats['snapshots_created'],
                        'Unit': 'Count',
                        'Timestamp': datetime.utcnow()
                    },
                    {
                        'MetricName': 'SnapshotsDeleted',
                        'Value': self.backup_stats['snapshots_deleted'],
                        'Unit': 'Count',
                        'Timestamp': datetime.utcnow()
                    },
                    {
                        'MetricName': 'CrossRegionCopies',
                        'Value': self.backup_stats['cross_region_copies'],
                        'Unit': 'Count',
                        'Timestamp': datetime.utcnow()
                    },
                    {
                        'MetricName': 'TotalBackupSize',
                        'Value': self.backup_stats['total_backup_size'],
                        'Unit': 'Gigabytes',
                        'Timestamp': datetime.utcnow()
                    }
                ]
            )
            logger.info("Backup metrics published to CloudWatch")
        except Exception as e:
            logger.error(f"Error publishing metrics: {str(e)}")
    
    def run_daily_backup(self):
        """Run daily backup process."""
        try:
            logger.info("Starting daily backup process")
            
            # Create daily snapshots
            created_snapshots = self.create_snapshots('daily')
            
            # Clean up old daily snapshots
            self.cleanup_old_snapshots(7, 'daily')
            
            # Copy snapshots cross-region if enabled
            if self.config.get('cross_region_backup', {}).get('enabled', True):
                destination_regions = self.config.get('cross_region_backup', {}).get('destination_regions', [])
                if created_snapshots and destination_regions:
                    self.copy_snapshots_cross_region(created_snapshots, destination_regions)
            
            # Publish metrics
            self.publish_metrics()
            
            logger.info("Daily backup process completed")
            
        except Exception as e:
            logger.error(f"Error in daily backup process: {str(e)}")
    
    def run_weekly_backup(self):
        """Run weekly backup process."""
        try:
            logger.info("Starting weekly backup process")
            
            # Create weekly snapshots
            created_snapshots = self.create_snapshots('weekly')
            
            # Clean up old weekly snapshots
            self.cleanup_old_snapshots(30, 'weekly')
            
            # Copy snapshots cross-region
            if self.config.get('cross_region_backup', {}).get('enabled', True):
                destination_regions = self.config.get('cross_region_backup', {}).get('destination_regions', [])
                if created_snapshots and destination_regions:
                    self.copy_snapshots_cross_region(created_snapshots, destination_regions)
            
            logger.info("Weekly backup process completed")
            
        except Exception as e:
            logger.error(f"Error in weekly backup process: {str(e)}")
    
    def run_monthly_backup(self):
        """Run monthly backup process."""
        try:
            logger.info("Starting monthly backup process")
            
            # Create monthly snapshots
            created_snapshots = self.create_snapshots('monthly')
            
            # Clean up old monthly snapshots
            self.cleanup_old_snapshots(90, 'monthly')
            
            # Copy snapshots cross-region
            if self.config.get('cross_region_backup', {}).get('enabled', True):
                destination_regions = self.config.get('cross_region_backup', {}).get('destination_regions', [])
                if created_snapshots and destination_regions:
                    self.copy_snapshots_cross_region(created_snapshots, destination_regions)
            
            logger.info("Monthly backup process completed")
            
        except Exception as e:
            logger.error(f"Error in monthly backup process: {str(e)}")


def lambda_handler(event, context):
    """
    AWS Lambda handler for serverless execution.
    
    Args:
        event: Lambda event
        context: Lambda context
        
    Returns:
        Dict containing execution results
    """
    try:
        snapshot_manager = SnapshotManager()
        
        # Determine action based on event
        action = event.get('action', 'daily_backup')
        
        if action == 'daily_backup':
            snapshot_manager.run_daily_backup()
        elif action == 'weekly_backup':
            snapshot_manager.run_weekly_backup()
        elif action == 'monthly_backup':
            snapshot_manager.run_monthly_backup()
        elif action == 'create_snapshots':
            backup_type = event.get('backup_type', 'daily')
            created_snapshots = snapshot_manager.create_snapshots(backup_type)
            return {
                'statusCode': 200,
                'body': json.dumps({
                    'created_snapshots': created_snapshots,
                    'count': len(created_snapshots)
                })
            }
        elif action == 'cleanup_snapshots':
            retention_days = event.get('retention_days', 30)
            backup_type = event.get('backup_type', 'daily')
            deleted_snapshots = snapshot_manager.cleanup_old_snapshots(retention_days, backup_type)
            return {
                'statusCode': 200,
                'body': json.dumps({
                    'deleted_snapshots': deleted_snapshots,
                    'count': len(deleted_snapshots)
                })
            }
        elif action == 'get_status':
            status = snapshot_manager.get_snapshot_lifecycle_status()
            return {
                'statusCode': 200,
                'body': json.dumps(status)
            }
        
        return {
            'statusCode': 200,
            'body': json.dumps({
                'message': f'Action {action} completed successfully',
                'timestamp': datetime.now().isoformat()
            })
        }
        
    except Exception as e:
        logger.error(f"Lambda handler error: {str(e)}")
        return {
            'statusCode': 500,
            'body': json.dumps({
                'error': str(e),
                'timestamp': datetime.now().isoformat()
            })
        }


if __name__ == '__main__':
    # Run snapshot manager locally
    snapshot_manager = SnapshotManager()
    
    # Example usage
    snapshot_manager.run_daily_backup()
