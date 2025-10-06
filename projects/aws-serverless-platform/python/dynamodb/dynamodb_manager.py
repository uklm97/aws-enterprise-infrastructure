#!/usr/bin/env python3
"""
AWS DynamoDB Manager
Comprehensive DynamoDB management with tables, indexes, and data operations
"""

import boto3
import json
from typing import Dict, List, Optional, Any, Union
from botocore.exceptions import ClientError
from decimal import Decimal
import time


class DynamoDBManager:
    """Manage AWS DynamoDB with comprehensive features"""
    
    def __init__(self, region: str = 'us-east-1'):
        self.region = region
        self.dynamodb_client = boto3.client('dynamodb', region_name=region)
        self.dynamodb_resource = boto3.resource('dynamodb', region_name=region)
        self.cloudwatch_client = boto3.client('cloudwatch', region_name=region)
        
    def create_table(self, table_config: Dict[str, Any]) -> Optional[str]:
        """Create DynamoDB table"""
        try:
            # Prepare table definition
            table_definition = {
                'TableName': table_config['TableName'],
                'KeySchema': table_config['KeySchema'],
                'AttributeDefinitions': table_config['AttributeDefinitions'],
                'BillingMode': table_config.get('BillingMode', 'PAY_PER_REQUEST')
            }
            
            # Add provisioned throughput if not on-demand
            if table_definition['BillingMode'] == 'PROVISIONED':
                table_definition['ProvisionedThroughput'] = {
                    'ReadCapacityUnits': table_config.get('ReadCapacityUnits', 5),
                    'WriteCapacityUnits': table_config.get('WriteCapacityUnits', 5)
                }
            
            # Add global secondary indexes
            if 'GlobalSecondaryIndexes' in table_config:
                table_definition['GlobalSecondaryIndexes'] = table_config['GlobalSecondaryIndexes']
            
            # Add local secondary indexes
            if 'LocalSecondaryIndexes' in table_config:
                table_definition['LocalSecondaryIndexes'] = table_config['LocalSecondaryIndexes']
            
            # Add stream specification
            if 'StreamSpecification' in table_config:
                table_definition['StreamSpecification'] = table_config['StreamSpecification']
            
            # Add tags
            if 'Tags' in table_config:
                table_definition['Tags'] = table_config['Tags']
            
            # Add point in time recovery
            if 'PointInTimeRecoverySpecification' in table_config:
                table_definition['PointInTimeRecoverySpecification'] = table_config['PointInTimeRecoverySpecification']
            
            # Add server-side encryption
            if 'SSESpecification' in table_config:
                table_definition['SSESpecification'] = table_config['SSESpecification']
            
            response = self.dynamodb_client.create_table(**table_definition)
            
            # Wait for table to be active
            self._wait_for_table_active(table_config['TableName'])
            
            return response['TableDescription']['TableArn']
        except ClientError as e:
            print(f"Error creating table: {e}")
            return None
    
    def create_global_secondary_index(self, table_name: str, index_config: Dict[str, Any]) -> bool:
        """Create global secondary index"""
        try:
            self.dynamodb_client.update_table(
                TableName=table_name,
                GlobalSecondaryIndexUpdates=[{
                    'Create': {
                        'IndexName': index_config['IndexName'],
                        'KeySchema': index_config['KeySchema'],
                        'Projection': index_config['Projection'],
                        'ProvisionedThroughput': index_config.get('ProvisionedThroughput', {
                            'ReadCapacityUnits': 5,
                            'WriteCapacityUnits': 5
                        })
                    }
                }]
            )
            
            # Wait for index to be active
            self._wait_for_index_active(table_name, index_config['IndexName'])
            return True
        except ClientError as e:
            print(f"Error creating global secondary index: {e}")
            return False
    
    def create_local_secondary_index(self, table_name: str, index_config: Dict[str, Any]) -> bool:
        """Create local secondary index"""
        try:
            self.dynamodb_client.update_table(
                TableName=table_name,
                LocalSecondaryIndexUpdates=[{
                    'Create': {
                        'IndexName': index_config['IndexName'],
                        'KeySchema': index_config['KeySchema'],
                        'Projection': index_config['Projection']
                    }
                }]
            )
            
            # Wait for index to be active
            self._wait_for_index_active(table_name, index_config['IndexName'])
            return True
        except ClientError as e:
            print(f"Error creating local secondary index: {e}")
            return False
    
    def put_item(self, table_name: str, item: Dict[str, Any]) -> bool:
        """Put item in table"""
        try:
            # Convert Python types to DynamoDB types
            dynamodb_item = self._convert_to_dynamodb_types(item)
            
            self.dynamodb_client.put_item(
                TableName=table_name,
                Item=dynamodb_item
            )
            return True
        except ClientError as e:
            print(f"Error putting item: {e}")
            return False
    
    def get_item(self, table_name: str, key: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """Get item from table"""
        try:
            # Convert key to DynamoDB types
            dynamodb_key = self._convert_to_dynamodb_types(key)
            
            response = self.dynamodb_client.get_item(
                TableName=table_name,
                Key=dynamodb_key
            )
            
            if 'Item' in response:
                return self._convert_from_dynamodb_types(response['Item'])
            return None
        except ClientError as e:
            print(f"Error getting item: {e}")
            return None
    
    def update_item(self, table_name: str, key: Dict[str, Any], 
                   update_expression: str, expression_attribute_values: Dict[str, Any] = None,
                   expression_attribute_names: Dict[str, str] = None) -> bool:
        """Update item in table"""
        try:
            # Convert key to DynamoDB types
            dynamodb_key = self._convert_to_dynamodb_types(key)
            
            update_params = {
                'TableName': table_name,
                'Key': dynamodb_key,
                'UpdateExpression': update_expression
            }
            
            if expression_attribute_values:
                update_params['ExpressionAttributeValues'] = self._convert_to_dynamodb_types(expression_attribute_values)
            
            if expression_attribute_names:
                update_params['ExpressionAttributeNames'] = expression_attribute_names
            
            self.dynamodb_client.update_item(**update_params)
            return True
        except ClientError as e:
            print(f"Error updating item: {e}")
            return False
    
    def delete_item(self, table_name: str, key: Dict[str, Any]) -> bool:
        """Delete item from table"""
        try:
            # Convert key to DynamoDB types
            dynamodb_key = self._convert_to_dynamodb_types(key)
            
            self.dynamodb_client.delete_item(
                TableName=table_name,
                Key=dynamodb_key
            )
            return True
        except ClientError as e:
            print(f"Error deleting item: {e}")
            return False
    
    def query(self, table_name: str, key_condition_expression: str,
              expression_attribute_values: Dict[str, Any] = None,
              expression_attribute_names: Dict[str, str] = None,
              index_name: str = None, scan_index_forward: bool = True,
              limit: int = None) -> List[Dict[str, Any]]:
        """Query table"""
        try:
            query_params = {
                'TableName': table_name,
                'KeyConditionExpression': key_condition_expression
            }
            
            if expression_attribute_values:
                query_params['ExpressionAttributeValues'] = self._convert_to_dynamodb_types(expression_attribute_values)
            
            if expression_attribute_names:
                query_params['ExpressionAttributeNames'] = expression_attribute_names
            
            if index_name:
                query_params['IndexName'] = index_name
            
            query_params['ScanIndexForward'] = scan_index_forward
            
            if limit:
                query_params['Limit'] = limit
            
            response = self.dynamodb_client.query(**query_params)
            
            items = []
            for item in response['Items']:
                items.append(self._convert_from_dynamodb_types(item))
            
            return items
        except ClientError as e:
            print(f"Error querying table: {e}")
            return []
    
    def scan(self, table_name: str, filter_expression: str = None,
             expression_attribute_values: Dict[str, Any] = None,
             expression_attribute_names: Dict[str, str] = None,
             index_name: str = None, limit: int = None) -> List[Dict[str, Any]]:
        """Scan table"""
        try:
            scan_params = {
                'TableName': table_name
            }
            
            if filter_expression:
                scan_params['FilterExpression'] = filter_expression
            
            if expression_attribute_values:
                scan_params['ExpressionAttributeValues'] = self._convert_to_dynamodb_types(expression_attribute_values)
            
            if expression_attribute_names:
                scan_params['ExpressionAttributeNames'] = expression_attribute_names
            
            if index_name:
                scan_params['IndexName'] = index_name
            
            if limit:
                scan_params['Limit'] = limit
            
            response = self.dynamodb_client.scan(**scan_params)
            
            items = []
            for item in response['Items']:
                items.append(self._convert_from_dynamodb_types(item))
            
            return items
        except ClientError as e:
            print(f"Error scanning table: {e}")
            return []
    
    def batch_write_items(self, table_name: str, items: List[Dict[str, Any]]) -> bool:
        """Batch write items to table"""
        try:
            # Convert items to DynamoDB types
            dynamodb_items = []
            for item in items:
                dynamodb_items.append({
                    'PutRequest': {
                        'Item': self._convert_to_dynamodb_types(item)
                    }
                })
            
            # Split into batches of 25 (DynamoDB limit)
            batch_size = 25
            for i in range(0, len(dynamodb_items), batch_size):
                batch = dynamodb_items[i:i + batch_size]
                
                response = self.dynamodb_client.batch_write_item(
                    RequestItems={
                        table_name: batch
                    }
                )
                
                # Handle unprocessed items
                while 'UnprocessedItems' in response and response['UnprocessedItems']:
                    time.sleep(1)  # Wait before retry
                    response = self.dynamodb_client.batch_write_item(
                        RequestItems=response['UnprocessedItems']
                    )
            
            return True
        except ClientError as e:
            print(f"Error batch writing items: {e}")
            return False
    
    def create_backup(self, table_name: str, backup_name: str) -> Optional[str]:
        """Create table backup"""
        try:
            response = self.dynamodb_client.create_backup(
                TableName=table_name,
                BackupName=backup_name
            )
            return response['BackupDetails']['BackupArn']
        except ClientError as e:
            print(f"Error creating backup: {e}")
            return None
    
    def restore_table_from_backup(self, target_table_name: str, backup_arn: str) -> Optional[str]:
        """Restore table from backup"""
        try:
            response = self.dynamodb_client.restore_table_from_backup(
                TargetTableName=target_table_name,
                BackupArn=backup_arn
            )
            return response['TableDescription']['TableArn']
        except ClientError as e:
            print(f"Error restoring table from backup: {e}")
            return None
    
    def enable_point_in_time_recovery(self, table_name: str) -> bool:
        """Enable point-in-time recovery"""
        try:
            self.dynamodb_client.update_continuous_backups(
                TableName=table_name,
                PointInTimeRecoverySpecification={
                    'PointInTimeRecoveryEnabled': True
                }
            )
            return True
        except ClientError as e:
            print(f"Error enabling point-in-time recovery: {e}")
            return False
    
    def create_global_table(self, table_name: str, regions: List[str]) -> bool:
        """Create global table"""
        try:
            self.dynamodb_client.create_global_table(
                GlobalTableName=table_name,
                ReplicationGroup=regions
            )
            return True
        except ClientError as e:
            print(f"Error creating global table: {e}")
            return False
    
    def get_table_metrics(self, table_name: str, days: int = 7) -> Dict[str, Any]:
        """Get table CloudWatch metrics"""
        try:
            import time
            from datetime import datetime, timedelta
            
            end_time = datetime.utcnow()
            start_time = end_time - timedelta(days=days)
            
            metrics = {}
            
            # Get consumed read capacity
            read_capacity = self.cloudwatch_client.get_metric_statistics(
                Namespace='AWS/DynamoDB',
                MetricName='ConsumedReadCapacityUnits',
                Dimensions=[
                    {'Name': 'TableName', 'Value': table_name}
                ],
                StartTime=start_time,
                EndTime=end_time,
                Period=3600,
                Statistics=['Sum', 'Average']
            )
            metrics['ConsumedReadCapacity'] = read_capacity['Datapoints']
            
            # Get consumed write capacity
            write_capacity = self.cloudwatch_client.get_metric_statistics(
                Namespace='AWS/DynamoDB',
                MetricName='ConsumedWriteCapacityUnits',
                Dimensions=[
                    {'Name': 'TableName', 'Value': table_name}
                ],
                StartTime=start_time,
                EndTime=end_time,
                Period=3600,
                Statistics=['Sum', 'Average']
            )
            metrics['ConsumedWriteCapacity'] = write_capacity['Datapoints']
            
            # Get throttled requests
            throttled_requests = self.cloudwatch_client.get_metric_statistics(
                Namespace='AWS/DynamoDB',
                MetricName='ThrottledRequests',
                Dimensions=[
                    {'Name': 'TableName', 'Value': table_name}
                ],
                StartTime=start_time,
                EndTime=end_time,
                Period=3600,
                Statistics=['Sum']
            )
            metrics['ThrottledRequests'] = throttled_requests['Datapoints']
            
            # Get item count
            item_count = self.cloudwatch_client.get_metric_statistics(
                Namespace='AWS/DynamoDB',
                MetricName='ItemCount',
                Dimensions=[
                    {'Name': 'TableName', 'Value': table_name}
                ],
                StartTime=start_time,
                EndTime=end_time,
                Period=3600,
                Statistics=['Maximum']
            )
            metrics['ItemCount'] = item_count['Datapoints']
            
            return metrics
        except ClientError as e:
            print(f"Error getting table metrics: {e}")
            return {}
    
    def optimize_table(self, table_name: str) -> Dict[str, Any]:
        """Analyze and provide optimization recommendations"""
        try:
            # Get table description
            table_info = self.dynamodb_client.describe_table(TableName=table_name)
            table = table_info['Table']
            
            # Get metrics
            metrics = self.get_table_metrics(table_name)
            
            recommendations = []
            
            # Check billing mode
            billing_mode = table['BillingModeSummary']['BillingMode']
            if billing_mode == 'PROVISIONED':
                # Check if on-demand would be better
                read_capacity = table['ProvisionedThroughput']['ReadCapacityUnits']
                write_capacity = table['ProvisionedThroughput']['WriteCapacityUnits']
                
                if read_capacity < 5 and write_capacity < 5:
                    recommendations.append({
                        'type': 'billing_mode',
                        'current': 'PROVISIONED',
                        'recommended': 'PAY_PER_REQUEST',
                        'reason': 'Low capacity usage suggests on-demand billing would be more cost-effective'
                    })
            
            # Check for unused indexes
            if 'GlobalSecondaryIndexes' in table:
                for gsi in table['GlobalSecondaryIndexes']:
                    gsi_name = gsi['IndexName']
                    gsi_metrics = self.get_table_metrics(f"{table_name}-{gsi_name}")
                    
                    if not gsi_metrics.get('ConsumedReadCapacity'):
                        recommendations.append({
                            'type': 'unused_index',
                            'index_name': gsi_name,
                            'recommended': 'DELETE',
                            'reason': 'Index appears to be unused based on metrics'
                        })
            
            # Check throttling
            throttled_requests = metrics.get('ThrottledRequests', [])
            if throttled_requests:
                total_throttled = sum(point['Sum'] for point in throttled_requests)
                if total_throttled > 0:
                    recommendations.append({
                        'type': 'throttling',
                        'current': f"{total_throttled} throttled requests",
                        'recommended': 'Increase capacity or optimize queries',
                        'reason': 'Table is experiencing throttling'
                    })
            
            return {
                'table_name': table_name,
                'current_config': {
                    'billing_mode': billing_mode,
                    'read_capacity': table.get('ProvisionedThroughput', {}).get('ReadCapacityUnits'),
                    'write_capacity': table.get('ProvisionedThroughput', {}).get('WriteCapacityUnits'),
                    'item_count': table.get('ItemCount', 0)
                },
                'recommendations': recommendations
            }
        except ClientError as e:
            print(f"Error optimizing table: {e}")
            return {}
    
    def delete_table(self, table_name: str) -> bool:
        """Delete table"""
        try:
            self.dynamodb_client.delete_table(TableName=table_name)
            return True
        except ClientError as e:
            print(f"Error deleting table: {e}")
            return False
    
    def list_tables(self) -> List[str]:
        """List all tables"""
        try:
            response = self.dynamodb_client.list_tables()
            return response['TableNames']
        except ClientError as e:
            print(f"Error listing tables: {e}")
            return []
    
    def _convert_to_dynamodb_types(self, item: Any) -> Any:
        """Convert Python types to DynamoDB types"""
        if isinstance(item, dict):
            return {k: self._convert_to_dynamodb_types(v) for k, v in item.items()}
        elif isinstance(item, list):
            return [self._convert_to_dynamodb_types(v) for v in item]
        elif isinstance(item, str):
            return {'S': item}
        elif isinstance(item, (int, float)):
            return {'N': str(item)}
        elif isinstance(item, bool):
            return {'BOOL': item}
        elif item is None:
            return {'NULL': True}
        elif isinstance(item, bytes):
            return {'B': item}
        else:
            return {'S': str(item)}
    
    def _convert_from_dynamodb_types(self, item: Any) -> Any:
        """Convert DynamoDB types to Python types"""
        if isinstance(item, dict):
            if 'S' in item:
                return item['S']
            elif 'N' in item:
                try:
                    return int(item['N'])
                except ValueError:
                    return float(item['N'])
            elif 'BOOL' in item:
                return item['BOOL']
            elif 'NULL' in item:
                return None
            elif 'B' in item:
                return item['B']
            elif 'L' in item:
                return [self._convert_from_dynamodb_types(v) for v in item['L']]
            elif 'M' in item:
                return {k: self._convert_from_dynamodb_types(v) for k, v in item['M'].items()}
            else:
                return {k: self._convert_from_dynamodb_types(v) for k, v in item.items()}
        elif isinstance(item, list):
            return [self._convert_from_dynamodb_types(v) for v in item]
        else:
            return item
    
    def _wait_for_table_active(self, table_name: str, timeout: int = 300) -> bool:
        """Wait for table to be active"""
        start_time = time.time()
        while time.time() - start_time < timeout:
            try:
                response = self.dynamodb_client.describe_table(TableName=table_name)
                if response['Table']['TableStatus'] == 'ACTIVE':
                    return True
                time.sleep(5)
            except ClientError:
                time.sleep(5)
        return False
    
    def _wait_for_index_active(self, table_name: str, index_name: str, timeout: int = 300) -> bool:
        """Wait for index to be active"""
        start_time = time.time()
        while time.time() - start_time < timeout:
            try:
                response = self.dynamodb_client.describe_table(TableName=table_name)
                table = response['Table']
                
                # Check global secondary indexes
                if 'GlobalSecondaryIndexes' in table:
                    for gsi in table['GlobalSecondaryIndexes']:
                        if gsi['IndexName'] == index_name and gsi['IndexStatus'] == 'ACTIVE':
                            return True
                
                # Check local secondary indexes
                if 'LocalSecondaryIndexes' in table:
                    for lsi in table['LocalSecondaryIndexes']:
                        if lsi['IndexName'] == index_name and lsi['IndexStatus'] == 'ACTIVE':
                            return True
                
                time.sleep(5)
            except ClientError:
                time.sleep(5)
        return False


# Example usage and testing
if __name__ == "__main__":
    # Initialize DynamoDB manager
    dynamodb_manager = DynamoDBManager()
    
    # Example table configuration
    table_config = {
        'TableName': 'test-table',
        'KeySchema': [
            {'AttributeName': 'id', 'KeyType': 'HASH'},
            {'AttributeName': 'timestamp', 'KeyType': 'RANGE'}
        ],
        'AttributeDefinitions': [
            {'AttributeName': 'id', 'AttributeType': 'S'},
            {'AttributeName': 'timestamp', 'AttributeType': 'N'}
        ],
        'BillingMode': 'PAY_PER_REQUEST',
        'StreamSpecification': {
            'StreamEnabled': True,
            'StreamViewType': 'NEW_AND_OLD_IMAGES'
        }
    }
    
    # Create table
    table_arn = dynamodb_manager.create_table(table_config)
    if table_arn:
        print(f"Table created: {table_arn}")
        
        # Put item
        item = {
            'id': 'test-1',
            'timestamp': 1234567890,
            'data': 'test data',
            'active': True
        }
        
        if dynamodb_manager.put_item('test-table', item):
            print("Item put successfully")
            
            # Get item
            retrieved_item = dynamodb_manager.get_item('test-table', {'id': 'test-1', 'timestamp': 1234567890})
            print(f"Retrieved item: {retrieved_item}")
            
            # Query table
            items = dynamodb_manager.query('test-table', 'id = :id', {'id': 'test-1'})
            print(f"Query results: {items}")
            
            # Get metrics
            metrics = dynamodb_manager.get_table_metrics('test-table')
            print(f"Table metrics: {metrics}")
            
            # Optimize table
            optimization = dynamodb_manager.optimize_table('test-table')
            print(f"Optimization recommendations: {optimization}")