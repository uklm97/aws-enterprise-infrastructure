#!/usr/bin/env python3
"""
AWS SQS and SNS Manager
Comprehensive SQS and SNS management with queues, topics, and messaging
"""

import boto3
import json
import time
from typing import Dict, List, Optional, Any
from botocore.exceptions import ClientError


class SQSSNSManager:
    """Manage AWS SQS and SNS with comprehensive features"""
    
    def __init__(self, region: str = 'us-east-1'):
        self.region = region
        self.sqs_client = boto3.client('sqs', region_name=region)
        self.sns_client = boto3.client('sns', region_name=region)
        self.cloudwatch_client = boto3.client('cloudwatch', region_name=region)
        
    # SQS Methods
    def create_queue(self, queue_config: Dict[str, Any]) -> Optional[str]:
        """Create SQS queue"""
        try:
            create_params = {
                'QueueName': queue_config['QueueName']
            }
            
            # Add attributes
            if 'Attributes' in queue_config:
                create_params['Attributes'] = queue_config['Attributes']
            
            # Add tags
            if 'Tags' in queue_config:
                create_params['tags'] = queue_config['Tags']
            
            response = self.sqs_client.create_queue(**create_params)
            return response['QueueUrl']
        except ClientError as e:
            print(f"Error creating queue: {e}")
            return None
    
    def create_fifo_queue(self, queue_name: str, content_based_deduplication: bool = True) -> Optional[str]:
        """Create FIFO queue"""
        try:
            attributes = {
                'FifoQueue': 'true',
                'ContentBasedDeduplication': str(content_based_deduplication).lower()
            }
            
            response = self.sqs_client.create_queue(
                QueueName=f"{queue_name}.fifo",
                Attributes=attributes
            )
            return response['QueueUrl']
        except ClientError as e:
            print(f"Error creating FIFO queue: {e}")
            return None
    
    def create_dlq(self, dlq_name: str, max_receive_count: int = 3) -> Optional[str]:
        """Create Dead Letter Queue"""
        try:
            dlq_url = self.create_queue({
                'QueueName': dlq_name,
                'Attributes': {
                    'MessageRetentionPeriod': '1209600'  # 14 days
                }
            })
            
            if dlq_url:
                # Get DLQ ARN
                dlq_attributes = self.sqs_client.get_queue_attributes(
                    QueueUrl=dlq_url,
                    AttributeNames=['QueueArn']
                )
                dlq_arn = dlq_attributes['Attributes']['QueueArn']
                
                return dlq_arn
            return None
        except ClientError as e:
            print(f"Error creating DLQ: {e}")
            return None
    
    def set_queue_attributes(self, queue_url: str, attributes: Dict[str, str]) -> bool:
        """Set queue attributes"""
        try:
            self.sqs_client.set_queue_attributes(
                QueueUrl=queue_url,
                Attributes=attributes
            )
            return True
        except ClientError as e:
            print(f"Error setting queue attributes: {e}")
            return False
    
    def send_message(self, queue_url: str, message_body: str, 
                    message_attributes: Dict[str, Any] = None,
                    delay_seconds: int = 0) -> Optional[str]:
        """Send message to queue"""
        try:
            send_params = {
                'QueueUrl': queue_url,
                'MessageBody': message_body
            }
            
            if message_attributes:
                send_params['MessageAttributes'] = message_attributes
            
            if delay_seconds > 0:
                send_params['DelaySeconds'] = delay_seconds
            
            response = self.sqs_client.send_message(**send_params)
            return response['MessageId']
        except ClientError as e:
            print(f"Error sending message: {e}")
            return None
    
    def send_message_batch(self, queue_url: str, messages: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Send batch of messages"""
        try:
            # Prepare batch entries
            entries = []
            for i, message in enumerate(messages):
                entry = {
                    'Id': str(i),
                    'MessageBody': message['body']
                }
                
                if 'attributes' in message:
                    entry['MessageAttributes'] = message['attributes']
                
                if 'delay_seconds' in message:
                    entry['DelaySeconds'] = message['delay_seconds']
                
                entries.append(entry)
            
            response = self.sqs_client.send_message_batch(
                QueueUrl=queue_url,
                Entries=entries
            )
            
            return {
                'Successful': response.get('Successful', []),
                'Failed': response.get('Failed', [])
            }
        except ClientError as e:
            print(f"Error sending message batch: {e}")
            return {'Successful': [], 'Failed': []}
    
    def receive_messages(self, queue_url: str, max_messages: int = 1,
                        wait_time_seconds: int = 0,
                        visibility_timeout: int = None) -> List[Dict[str, Any]]:
        """Receive messages from queue"""
        try:
            receive_params = {
                'QueueUrl': queue_url,
                'MaxNumberOfMessages': max_messages,
                'WaitTimeSeconds': wait_time_seconds
            }
            
            if visibility_timeout:
                receive_params['VisibilityTimeoutSeconds'] = visibility_timeout
            
            response = self.sqs_client.receive_message(**receive_params)
            
            messages = []
            for message in response.get('Messages', []):
                messages.append({
                    'MessageId': message['MessageId'],
                    'ReceiptHandle': message['ReceiptHandle'],
                    'Body': message['Body'],
                    'Attributes': message.get('Attributes', {}),
                    'MessageAttributes': message.get('MessageAttributes', {})
                })
            
            return messages
        except ClientError as e:
            print(f"Error receiving messages: {e}")
            return []
    
    def delete_message(self, queue_url: str, receipt_handle: str) -> bool:
        """Delete message from queue"""
        try:
            self.sqs_client.delete_message(
                QueueUrl=queue_url,
                ReceiptHandle=receipt_handle
            )
            return True
        except ClientError as e:
            print(f"Error deleting message: {e}")
            return False
    
    def delete_message_batch(self, queue_url: str, messages: List[Dict[str, str]]) -> Dict[str, Any]:
        """Delete batch of messages"""
        try:
            entries = []
            for i, message in enumerate(messages):
                entries.append({
                    'Id': str(i),
                    'ReceiptHandle': message['receipt_handle']
                })
            
            response = self.sqs_client.delete_message_batch(
                QueueUrl=queue_url,
                Entries=entries
            )
            
            return {
                'Successful': response.get('Successful', []),
                'Failed': response.get('Failed', [])
            }
        except ClientError as e:
            print(f"Error deleting message batch: {e}")
            return {'Successful': [], 'Failed': []}
    
    def purge_queue(self, queue_url: str) -> bool:
        """Purge all messages from queue"""
        try:
            self.sqs_client.purge_queue(QueueUrl=queue_url)
            return True
        except ClientError as e:
            print(f"Error purging queue: {e}")
            return False
    
    def get_queue_attributes(self, queue_url: str, attribute_names: List[str] = None) -> Dict[str, str]:
        """Get queue attributes"""
        try:
            params = {'QueueUrl': queue_url}
            
            if attribute_names:
                params['AttributeNames'] = attribute_names
            else:
                params['AttributeNames'] = ['All']
            
            response = self.sqs_client.get_queue_attributes(**params)
            return response['Attributes']
        except ClientError as e:
            print(f"Error getting queue attributes: {e}")
            return {}
    
    # SNS Methods
    def create_topic(self, topic_name: str, display_name: str = None) -> Optional[str]:
        """Create SNS topic"""
        try:
            create_params = {'Name': topic_name}
            
            if display_name:
                create_params['Attributes'] = {'DisplayName': display_name}
            
            response = self.sns_client.create_topic(**create_params)
            return response['TopicArn']
        except ClientError as e:
            print(f"Error creating topic: {e}")
            return None
    
    def create_fifo_topic(self, topic_name: str, content_based_deduplication: bool = True) -> Optional[str]:
        """Create FIFO topic"""
        try:
            attributes = {
                'FifoTopic': 'true',
                'ContentBasedDeduplication': str(content_based_deduplication).lower()
            }
            
            response = self.sns_client.create_topic(
                Name=f"{topic_name}.fifo",
                Attributes=attributes
            )
            return response['TopicArn']
        except ClientError as e:
            print(f"Error creating FIFO topic: {e}")
            return None
    
    def subscribe(self, topic_arn: str, protocol: str, endpoint: str) -> Optional[str]:
        """Subscribe to topic"""
        try:
            response = self.sns_client.subscribe(
                TopicArn=topic_arn,
                Protocol=protocol,
                Endpoint=endpoint
            )
            return response['SubscriptionArn']
        except ClientError as e:
            print(f"Error subscribing to topic: {e}")
            return None
    
    def confirm_subscription(self, topic_arn: str, token: str) -> bool:
        """Confirm subscription"""
        try:
            self.sns_client.confirm_subscription(
                TopicArn=topic_arn,
                Token=token
            )
            return True
        except ClientError as e:
            print(f"Error confirming subscription: {e}")
            return False
    
    def publish_message(self, topic_arn: str, message: str, subject: str = None,
                       message_attributes: Dict[str, Any] = None,
                       message_group_id: str = None,
                       message_deduplication_id: str = None) -> Optional[str]:
        """Publish message to topic"""
        try:
            publish_params = {
                'TopicArn': topic_arn,
                'Message': message
            }
            
            if subject:
                publish_params['Subject'] = subject
            
            if message_attributes:
                publish_params['MessageAttributes'] = message_attributes
            
            if message_group_id:
                publish_params['MessageGroupId'] = message_group_id
            
            if message_deduplication_id:
                publish_params['MessageDeduplicationId'] = message_deduplication_id
            
            response = self.sns_client.publish(**publish_params)
            return response['MessageId']
        except ClientError as e:
            print(f"Error publishing message: {e}")
            return None
    
    def publish_batch_messages(self, topic_arn: str, messages: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Publish batch of messages"""
        try:
            entries = []
            for i, message in enumerate(messages):
                entry = {
                    'Id': str(i),
                    'Message': message['body']
                }
                
                if 'subject' in message:
                    entry['Subject'] = message['subject']
                
                if 'attributes' in message:
                    entry['MessageAttributes'] = message['attributes']
                
                if 'group_id' in message:
                    entry['MessageGroupId'] = message['group_id']
                
                if 'deduplication_id' in message:
                    entry['MessageDeduplicationId'] = message['deduplication_id']
                
                entries.append(entry)
            
            response = self.sns_client.publish_batch(
                TopicArn=topic_arn,
                PublishBatchRequestEntries=entries
            )
            
            return {
                'Successful': response.get('Successful', []),
                'Failed': response.get('Failed', [])
            }
        except ClientError as e:
            print(f"Error publishing batch messages: {e}")
            return {'Successful': [], 'Failed': []}
    
    def set_topic_attributes(self, topic_arn: str, attribute_name: str, attribute_value: str) -> bool:
        """Set topic attributes"""
        try:
            self.sns_client.set_topic_attributes(
                TopicArn=topic_arn,
                AttributeName=attribute_name,
                AttributeValue=attribute_value
            )
            return True
        except ClientError as e:
            print(f"Error setting topic attributes: {e}")
            return False
    
    def get_topic_attributes(self, topic_arn: str) -> Dict[str, str]:
        """Get topic attributes"""
        try:
            response = self.sns_client.get_topic_attributes(TopicArn=topic_arn)
            return response['Attributes']
        except ClientError as e:
            print(f"Error getting topic attributes: {e}")
            return {}
    
    def list_subscriptions(self, topic_arn: str = None) -> List[Dict[str, Any]]:
        """List subscriptions"""
        try:
            params = {}
            if topic_arn:
                params['TopicArn'] = topic_arn
            
            response = self.sns_client.list_subscriptions(**params)
            return response['Subscriptions']
        except ClientError as e:
            print(f"Error listing subscriptions: {e}")
            return []
    
    def unsubscribe(self, subscription_arn: str) -> bool:
        """Unsubscribe from topic"""
        try:
            self.sns_client.unsubscribe(SubscriptionArn=subscription_arn)
            return True
        except ClientError as e:
            print(f"Error unsubscribing: {e}")
            return False
    
    # Integration Methods
    def create_sqs_sns_integration(self, queue_url: str, topic_arn: str) -> bool:
        """Create SQS-SNS integration"""
        try:
            # Get queue ARN
            queue_attributes = self.get_queue_attributes(queue_url, ['QueueArn'])
            queue_arn = queue_attributes['QueueArn']
            
            # Subscribe queue to topic
            subscription_arn = self.subscribe(topic_arn, 'sqs', queue_arn)
            
            if subscription_arn:
                # Set queue policy to allow SNS to send messages
                policy = {
                    "Version": "2012-10-17",
                    "Statement": [
                        {
                            "Effect": "Allow",
                            "Principal": {"Service": "sns.amazonaws.com"},
                            "Action": "sqs:SendMessage",
                            "Resource": queue_arn,
                            "Condition": {
                                "ArnEquals": {
                                    "aws:SourceArn": topic_arn
                                }
                            }
                        }
                    ]
                }
                
                self.set_queue_attributes(queue_url, {
                    'Policy': json.dumps(policy)
                })
                
                return True
            return False
        except ClientError as e:
            print(f"Error creating SQS-SNS integration: {e}")
            return False
    
    def create_lambda_sns_integration(self, lambda_function_arn: str, topic_arn: str) -> bool:
        """Create Lambda-SNS integration"""
        try:
            # Subscribe Lambda to topic
            subscription_arn = self.subscribe(topic_arn, 'lambda', lambda_function_arn)
            
            if subscription_arn:
                # Add Lambda permission for SNS
                lambda_client = boto3.client('lambda', region_name=self.region)
                lambda_client.add_permission(
                    FunctionName=lambda_function_arn,
                    StatementId=f'sns-{topic_arn.split(":")[-1]}',
                    Action='lambda:InvokeFunction',
                    Principal='sns.amazonaws.com',
                    SourceArn=topic_arn
                )
                return True
            return False
        except ClientError as e:
            print(f"Error creating Lambda-SNS integration: {e}")
            return False
    
    def create_lambda_sqs_integration(self, lambda_function_arn: str, queue_url: str) -> bool:
        """Create Lambda-SQS integration"""
        try:
            # Get queue ARN
            queue_attributes = self.get_queue_attributes(queue_url, ['QueueArn'])
            queue_arn = queue_attributes['QueueArn']
            
            # Add Lambda permission for SQS
            lambda_client = boto3.client('lambda', region_name=self.region)
            lambda_client.add_permission(
                FunctionName=lambda_function_arn,
                StatementId=f'sqs-{queue_url.split("/")[-1]}',
                Action='lambda:InvokeFunction',
                Principal='sqs.amazonaws.com',
                SourceArn=queue_arn
            )
            
            # Create event source mapping
            lambda_client.create_event_source_mapping(
                EventSourceArn=queue_arn,
                FunctionName=lambda_function_arn,
                BatchSize=10
            )
            
            return True
        except ClientError as e:
            print(f"Error creating Lambda-SQS integration: {e}")
            return False
    
    # Monitoring Methods
    def get_sqs_metrics(self, queue_url: str, days: int = 7) -> Dict[str, Any]:
        """Get SQS CloudWatch metrics"""
        try:
            import time
            from datetime import datetime, timedelta
            
            end_time = datetime.utcnow()
            start_time = end_time - timedelta(days=days)
            
            queue_name = queue_url.split('/')[-1]
            
            metrics = {}
            
            # Get message count
            message_count = self.cloudwatch_client.get_metric_statistics(
                Namespace='AWS/SQS',
                MetricName='ApproximateNumberOfMessages',
                Dimensions=[
                    {'Name': 'QueueName', 'Value': queue_name}
                ],
                StartTime=start_time,
                EndTime=end_time,
                Period=3600,
                Statistics=['Average', 'Maximum']
            )
            metrics['MessageCount'] = message_count['Datapoints']
            
            # Get sent messages
            sent_messages = self.cloudwatch_client.get_metric_statistics(
                Namespace='AWS/SQS',
                MetricName='NumberOfMessagesSent',
                Dimensions=[
                    {'Name': 'QueueName', 'Value': queue_name}
                ],
                StartTime=start_time,
                EndTime=end_time,
                Period=3600,
                Statistics=['Sum']
            )
            metrics['SentMessages'] = sent_messages['Datapoints']
            
            # Get received messages
            received_messages = self.cloudwatch_client.get_metric_statistics(
                Namespace='AWS/SQS',
                MetricName='NumberOfMessagesReceived',
                Dimensions=[
                    {'Name': 'QueueName', 'Value': queue_name}
                ],
                StartTime=start_time,
                EndTime=end_time,
                Period=3600,
                Statistics=['Sum']
            )
            metrics['ReceivedMessages'] = received_messages['Datapoints']
            
            return metrics
        except ClientError as e:
            print(f"Error getting SQS metrics: {e}")
            return {}
    
    def get_sns_metrics(self, topic_arn: str, days: int = 7) -> Dict[str, Any]:
        """Get SNS CloudWatch metrics"""
        try:
            import time
            from datetime import datetime, timedelta
            
            end_time = datetime.utcnow()
            start_time = end_time - timedelta(days=days)
            
            topic_name = topic_arn.split(':')[-1]
            
            metrics = {}
            
            # Get published messages
            published_messages = self.cloudwatch_client.get_metric_statistics(
                Namespace='AWS/SNS',
                MetricName='NumberOfMessagesPublished',
                Dimensions=[
                    {'Name': 'TopicName', 'Value': topic_name}
                ],
                StartTime=start_time,
                EndTime=end_time,
                Period=3600,
                Statistics=['Sum']
            )
            metrics['PublishedMessages'] = published_messages['Datapoints']
            
            # Get delivered messages
            delivered_messages = self.cloudwatch_client.get_metric_statistics(
                Namespace='AWS/SNS',
                MetricName='NumberOfNotificationsDelivered',
                Dimensions=[
                    {'Name': 'TopicName', 'Value': topic_name}
                ],
                StartTime=start_time,
                EndTime=end_time,
                Period=3600,
                Statistics=['Sum']
            )
            metrics['DeliveredMessages'] = delivered_messages['Datapoints']
            
            # Get failed deliveries
            failed_deliveries = self.cloudwatch_client.get_metric_statistics(
                Namespace='AWS/SNS',
                MetricName='NumberOfNotificationsFailed',
                Dimensions=[
                    {'Name': 'TopicName', 'Value': topic_name}
                ],
                StartTime=start_time,
                EndTime=end_time,
                Period=3600,
                Statistics=['Sum']
            )
            metrics['FailedDeliveries'] = failed_deliveries['Datapoints']
            
            return metrics
        except ClientError as e:
            print(f"Error getting SNS metrics: {e}")
            return {}
    
    def delete_queue(self, queue_url: str) -> bool:
        """Delete queue"""
        try:
            self.sqs_client.delete_queue(QueueUrl=queue_url)
            return True
        except ClientError as e:
            print(f"Error deleting queue: {e}")
            return False
    
    def delete_topic(self, topic_arn: str) -> bool:
        """Delete topic"""
        try:
            self.sns_client.delete_topic(TopicArn=topic_arn)
            return True
        except ClientError as e:
            print(f"Error deleting topic: {e}")
            return False
    
    def list_queues(self, queue_name_prefix: str = None) -> List[str]:
        """List queues"""
        try:
            params = {}
            if queue_name_prefix:
                params['QueueNamePrefix'] = queue_name_prefix
            
            response = self.sqs_client.list_queues(**params)
            return response.get('QueueUrls', [])
        except ClientError as e:
            print(f"Error listing queues: {e}")
            return []
    
    def list_topics(self) -> List[Dict[str, Any]]:
        """List topics"""
        try:
            response = self.sns_client.list_topics()
            return response['Topics']
        except ClientError as e:
            print(f"Error listing topics: {e}")
            return []


# Example usage and testing
if __name__ == "__main__":
    # Initialize SQS/SNS manager
    sqs_sns_manager = SQSSNSManager()
    
    # Example queue configuration
    queue_config = {
        'QueueName': 'test-queue',
        'Attributes': {
            'VisibilityTimeoutSeconds': '30',
            'MessageRetentionPeriod': '1209600',
            'ReceiveMessageWaitTimeSeconds': '20'
        }
    }
    
    # Create queue
    queue_url = sqs_sns_manager.create_queue(queue_config)
    if queue_url:
        print(f"Queue created: {queue_url}")
        
        # Send message
        message_id = sqs_sns_manager.send_message(queue_url, 'Hello World!')
        if message_id:
            print(f"Message sent: {message_id}")
            
            # Receive messages
            messages = sqs_sns_manager.receive_messages(queue_url)
            print(f"Received messages: {messages}")
    
    # Example topic configuration
    topic_arn = sqs_sns_manager.create_topic('test-topic', 'Test Topic')
    if topic_arn:
        print(f"Topic created: {topic_arn}")
        
        # Publish message
        message_id = sqs_sns_manager.publish_message(topic_arn, 'Hello from SNS!')
        if message_id:
            print(f"Message published: {message_id}")
            
            # Get metrics
            metrics = sqs_sns_manager.get_sns_metrics(topic_arn)
            print(f"SNS metrics: {metrics}")