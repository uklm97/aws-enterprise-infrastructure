#!/usr/bin/env python3
"""
AWS Redshift Manager for data warehousing and analytics.

This module provides comprehensive Redshift management capabilities including
cluster management, query execution, and data warehouse operations.
"""

import boto3
import psycopg2
import logging
import time
from typing import List, Dict, Any, Optional, Tuple
from datetime import datetime
import json

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class RedshiftManager:
    """
    AWS Redshift Manager for data warehousing and analytics.
    """
    
    def __init__(self, region: str = 'us-east-1'):
        """Initialize RedshiftManager with AWS clients."""
        self.region = region
        self.redshift_client = boto3.client('redshift', region_name=region)
        self.ec2_client = boto3.client('ec2', region_name=region)
        self.iam_client = boto3.client('iam', region_name=region)
        
    def create_cluster(self, cluster_config: Dict[str, Any]) -> Optional[str]:
        """Create Redshift cluster."""
        try:
            # Validate cluster configuration
            self._validate_cluster_config(cluster_config)
            
            # Create IAM role if specified
            if 'iam_role_arn' not in cluster_config:
                cluster_config['iam_role_arn'] = self._create_redshift_role(cluster_config['cluster_identifier'])
            
            # Build cluster parameters
            cluster_params = {
                'ClusterIdentifier': cluster_config['cluster_identifier'],
                'NodeType': cluster_config['node_type'],
                'MasterUsername': cluster_config['master_username'],
                'MasterUserPassword': cluster_config['master_password'],
                'DBName': cluster_config.get('database_name', 'dev'),
                'ClusterType': cluster_config.get('cluster_type', 'multi-node'),
                'NumberOfNodes': cluster_config.get('number_of_nodes', 2),
                'VpcSecurityGroupIds': cluster_config.get('security_group_ids', []),
                'ClusterSubnetGroupName': cluster_config.get('subnet_group_name'),
                'PubliclyAccessible': cluster_config.get('publicly_accessible', False),
                'Encrypted': cluster_config.get('encrypted', True),
                'Tags': cluster_config.get('tags', [])
            }
            
            # Add optional parameters
            if 'preferred_maintenance_window' in cluster_config:
                cluster_params['PreferredMaintenanceWindow'] = cluster_config['preferred_maintenance_window']
            
            if 'automated_snapshot_retention_period' in cluster_config:
                cluster_params['AutomatedSnapshotRetentionPeriod'] = cluster_config['automated_snapshot_retention_period']
            
            if 'port' in cluster_config:
                cluster_params['Port'] = cluster_config['port']
            
            # Create cluster
            response = self.redshift_client.create_cluster(**cluster_params)
            
            cluster_id = response['Cluster']['ClusterIdentifier']
            logger.info(f"Redshift cluster {cluster_id} creation initiated")
            
            # Wait for cluster to become available
            if cluster_config.get('wait_for_available', True):
                self._wait_for_cluster_available(cluster_id)
            
            return cluster_id
            
        except Exception as e:
            logger.error(f"Error creating Redshift cluster: {str(e)}")
            return None
    
    def _validate_cluster_config(self, config: Dict[str, Any]) -> None:
        """Validate cluster configuration."""
        required_fields = ['cluster_identifier', 'node_type', 'master_username', 'master_password']
        for field in required_fields:
            if field not in config:
                raise ValueError(f"Missing required field: {field}")
    
    def _create_redshift_role(self, cluster_identifier: str) -> str:
        """Create IAM role for Redshift."""
        role_name = f"{cluster_identifier}-redshift-role"
        
        try:
            # Check if role exists
            self.iam_client.get_role(RoleName=role_name)
            logger.info(f"Redshift role {role_name} already exists")
            return f"arn:aws:iam::{self._get_account_id()}:role/{role_name}"
            
        except self.iam_client.exceptions.NoSuchEntityException:
            # Create role
            assume_role_policy = {
                "Version": "2012-10-17",
                "Statement": [{
                    "Effect": "Allow",
                    "Principal": {"Service": "redshift.amazonaws.com"},
                    "Action": "sts:AssumeRole"
                }]
            }
            
            self.iam_client.create_role(
                RoleName=role_name,
                AssumeRolePolicyDocument=json.dumps(assume_role_policy),
                Description=f"IAM role for {cluster_identifier} Redshift cluster"
            )
            
            # Attach policies
            policies = [
                "arn:aws:iam::aws:policy/AmazonS3ReadOnlyAccess"
            ]
            
            for policy_arn in policies:
                self.iam_client.attach_role_policy(
                    RoleName=role_name,
                    PolicyArn=policy_arn
                )
            
            logger.info(f"Created Redshift role: {role_name}")
            return f"arn:aws:iam::{self._get_account_id()}:role/{role_name}"
    
    def _wait_for_cluster_available(self, cluster_identifier: str, timeout: int = 1800) -> bool:
        """Wait for cluster to become available."""
        start_time = time.time()
        
        while time.time() - start_time < timeout:
            try:
                response = self.redshift_client.describe_clusters(ClusterIdentifier=cluster_identifier)
                cluster = response['Clusters'][0]
                status = cluster['ClusterStatus']
                
                if status == 'available':
                    logger.info(f"Redshift cluster {cluster_identifier} is now available")
                    return True
                elif status in ['deleting', 'deleted']:
                    logger.error(f"Redshift cluster {cluster_identifier} is being deleted")
                    return False
                
                logger.info(f"Waiting for cluster {cluster_identifier} to become available. Current status: {status}")
                time.sleep(30)
                
            except Exception as e:
                logger.error(f"Error checking cluster status: {str(e)}")
                return False
        
        logger.error(f"Timeout waiting for cluster {cluster_identifier} to become available")
        return False
    
    def get_cluster_info(self, cluster_identifier: str) -> Dict[str, Any]:
        """Get cluster information."""
        try:
            response = self.redshift_client.describe_clusters(ClusterIdentifier=cluster_identifier)
            cluster = response['Clusters'][0]
            
            return {
                'cluster_identifier': cluster['ClusterIdentifier'],
                'cluster_status': cluster['ClusterStatus'],
                'node_type': cluster['NodeType'],
                'cluster_type': cluster['ClusterType'],
                'number_of_nodes': cluster['NumberOfNodes'],
                'master_username': cluster['MasterUsername'],
                'database_name': cluster['DBName'],
                'endpoint': cluster['Endpoint'],
                'port': cluster['Port'],
                'vpc_security_groups': cluster['VpcSecurityGroups'],
                'cluster_subnet_group_name': cluster['ClusterSubnetGroupName'],
                'publicly_accessible': cluster['PubliclyAccessible'],
                'encrypted': cluster['Encrypted'],
                'cluster_create_time': cluster['ClusterCreateTime'],
                'cluster_version': cluster['ClusterVersion'],
                'preferred_maintenance_window': cluster.get('PreferredMaintenanceWindow'),
                'automated_snapshot_retention_period': cluster.get('AutomatedSnapshotRetentionPeriod'),
                'cluster_parameter_groups': cluster['ClusterParameterGroups'],
                'iam_roles': cluster.get('IamRoles', [])
            }
            
        except Exception as e:
            logger.error(f"Error getting cluster info: {str(e)}")
            return {}
    
    def execute_query(self, cluster_identifier: str, query: str, database: str = None, user: str = None, password: str = None) -> List[Dict[str, Any]]:
        """Execute SQL query on Redshift cluster."""
        try:
            # Get cluster endpoint
            cluster_info = self.get_cluster_info(cluster_identifier)
            if not cluster_info:
                raise ValueError("Could not get cluster information")
            
            endpoint = cluster_info['endpoint']['Address']
            port = cluster_info['port']
            db_name = database or cluster_info['database_name']
            username = user or cluster_info['master_username']
            
            if not password:
                raise ValueError("Password is required for query execution")
            
            # Connect to Redshift
            conn = psycopg2.connect(
                host=endpoint,
                port=port,
                database=db_name,
                user=username,
                password=password
            )
            
            cursor = conn.cursor()
            cursor.execute(query)
            
            # Get column names
            columns = [desc[0] for desc in cursor.description] if cursor.description else []
            
            # Fetch results
            results = []
            for row in cursor.fetchall():
                result_dict = {}
                for i, value in enumerate(row):
                    result_dict[columns[i]] = value
                results.append(result_dict)
            
            cursor.close()
            conn.close()
            
            logger.info(f"Query executed successfully, returned {len(results)} rows")
            return results
            
        except Exception as e:
            logger.error(f"Error executing query: {str(e)}")
            return []
    
    def create_table(self, cluster_identifier: str, table_name: str, columns: List[Dict[str, str]], 
                    database: str = None, user: str = None, password: str = None) -> bool:
        """Create table in Redshift."""
        try:
            # Build CREATE TABLE statement
            column_definitions = []
            for col in columns:
                col_def = f"{col['name']} {col['type']}"
                if 'not_null' in col and col['not_null']:
                    col_def += " NOT NULL"
                if 'default' in col:
                    col_def += f" DEFAULT {col['default']}"
                column_definitions.append(col_def)
            
            create_table_sql = f"""
            CREATE TABLE IF NOT EXISTS {table_name} (
                {', '.join(column_definitions)}
            )
            """
            
            # Execute query
            results = self.execute_query(cluster_identifier, create_table_sql, database, user, password)
            
            logger.info(f"Table {table_name} created successfully")
            return True
            
        except Exception as e:
            logger.error(f"Error creating table: {str(e)}")
            return False
    
    def load_data_from_s3(self, cluster_identifier: str, table_name: str, s3_path: str, 
                         iam_role_arn: str, database: str = None, user: str = None, password: str = None) -> bool:
        """Load data from S3 into Redshift table."""
        try:
            copy_sql = f"""
            COPY {table_name}
            FROM '{s3_path}'
            IAM_ROLE '{iam_role_arn}'
            FORMAT AS JSON 'auto'
            """
            
            # Execute COPY command
            results = self.execute_query(cluster_identifier, copy_sql, database, user, password)
            
            logger.info(f"Data loaded from S3 to table {table_name}")
            return True
            
        except Exception as e:
            logger.error(f"Error loading data from S3: {str(e)}")
            return False
    
    def create_snapshot(self, cluster_identifier: str, snapshot_identifier: str) -> bool:
        """Create manual snapshot of cluster."""
        try:
            response = self.redshift_client.create_cluster_snapshot(
                ClusterIdentifier=cluster_identifier,
                SnapshotIdentifier=snapshot_identifier
            )
            
            snapshot_id = response['Snapshot']['SnapshotIdentifier']
            logger.info(f"Snapshot {snapshot_id} creation initiated")
            return True
            
        except Exception as e:
            logger.error(f"Error creating snapshot: {str(e)}")
            return False
    
    def restore_from_snapshot(self, cluster_identifier: str, snapshot_identifier: str) -> bool:
        """Restore cluster from snapshot."""
        try:
            response = self.redshift_client.restore_from_cluster_snapshot(
                ClusterIdentifier=cluster_identifier,
                SnapshotIdentifier=snapshot_identifier
            )
            
            logger.info(f"Cluster {cluster_identifier} restore from snapshot {snapshot_identifier} initiated")
            return True
            
        except Exception as e:
            logger.error(f"Error restoring from snapshot: {str(e)}")
            return False
    
    def resize_cluster(self, cluster_identifier: str, node_type: str = None, number_of_nodes: int = None) -> bool:
        """Resize Redshift cluster."""
        try:
            resize_params = {
                'ClusterIdentifier': cluster_identifier
            }
            
            if node_type:
                resize_params['NodeType'] = node_type
            
            if number_of_nodes:
                resize_params['NumberOfNodes'] = number_of_nodes
            
            response = self.redshift_client.modify_cluster(**resize_params)
            
            logger.info(f"Cluster {cluster_identifier} resize initiated")
            return True
            
        except Exception as e:
            logger.error(f"Error resizing cluster: {str(e)}")
            return False
    
    def delete_cluster(self, cluster_identifier: str, skip_final_snapshot: bool = False, 
                      final_snapshot_identifier: str = None) -> bool:
        """Delete Redshift cluster."""
        try:
            delete_params = {
                'ClusterIdentifier': cluster_identifier,
                'SkipFinalClusterSnapshot': skip_final_snapshot
            }
            
            if not skip_final_snapshot and final_snapshot_identifier:
                delete_params['FinalClusterSnapshotIdentifier'] = final_snapshot_identifier
            
            response = self.redshift_client.delete_cluster(**delete_params)
            
            logger.info(f"Cluster {cluster_identifier} deletion initiated")
            return True
            
        except Exception as e:
            logger.error(f"Error deleting cluster: {str(e)}")
            return False
    
    def list_clusters(self) -> List[Dict[str, Any]]:
        """List all Redshift clusters."""
        try:
            response = self.redshift_client.describe_clusters()
            clusters = []
            
            for cluster in response['Clusters']:
                clusters.append({
                    'cluster_identifier': cluster['ClusterIdentifier'],
                    'cluster_status': cluster['ClusterStatus'],
                    'node_type': cluster['NodeType'],
                    'cluster_type': cluster['ClusterType'],
                    'number_of_nodes': cluster['NumberOfNodes'],
                    'database_name': cluster['DBName'],
                    'endpoint': cluster['Endpoint'],
                    'cluster_create_time': cluster['ClusterCreateTime']
                })
            
            return clusters
            
        except Exception as e:
            logger.error(f"Error listing clusters: {str(e)}")
            return []
    
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
    """Main function for testing RedshiftManager."""
    # Example usage
    redshift_manager = RedshiftManager()
    
    # Example cluster configuration
    cluster_config = {
        'cluster_identifier': 'test-cluster',
        'node_type': 'dc2.large',
        'master_username': 'admin',
        'master_password': 'SecurePassword123!',
        'database_name': 'analytics',
        'cluster_type': 'multi-node',
        'number_of_nodes': 2,
        'publicly_accessible': False,
        'encrypted': True,
        'tags': [
            {'Key': 'Environment', 'Value': 'test'},
            {'Key': 'Project', 'Value': 'data-analytics'}
        ]
    }
    
    # Create cluster
    cluster_id = redshift_manager.create_cluster(cluster_config)
    if cluster_id:
        print(f"Cluster created: {cluster_id}")
        
        # Get cluster info
        info = redshift_manager.get_cluster_info(cluster_id)
        print(f"Cluster info: {info}")
        
        # List clusters
        clusters = redshift_manager.list_clusters()
        print(f"All clusters: {clusters}")


if __name__ == "__main__":
    main()