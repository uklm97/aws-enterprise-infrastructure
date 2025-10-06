#!/usr/bin/env python3
"""
AWS API Gateway Manager
Comprehensive API Gateway management with REST APIs, HTTP APIs, and WebSocket APIs
"""

import boto3
import json
from typing import Dict, List, Optional, Any
from botocore.exceptions import ClientError


class APIGatewayManager:
    """Manage AWS API Gateway with comprehensive features"""
    
    def __init__(self, region: str = 'us-east-1'):
        self.region = region
        self.api_gateway_client = boto3.client('apigateway', region_name=region)
        self.api_gateway_v2_client = boto3.client('apigatewayv2', region_name=region)
        self.lambda_client = boto3.client('lambda', region_name=region)
        self.iam_client = boto3.client('iam', region_name=region)
        
    def create_rest_api(self, api_config: Dict[str, Any]) -> Optional[str]:
        """Create REST API"""
        try:
            response = self.api_gateway_client.create_rest_api(
                name=api_config['name'],
                description=api_config.get('description', ''),
                version=api_config.get('version', '1.0'),
                binaryMediaTypes=api_config.get('binaryMediaTypes', []),
                minimumCompressionSize=api_config.get('minimumCompressionSize', 0),
                apiKeySource=api_config.get('apiKeySource', 'HEADER'),
                endpointConfiguration=api_config.get('endpointConfiguration', {
                    'types': ['REGIONAL']
                }),
                policy=api_config.get('policy', ''),
                tags=api_config.get('tags', {})
            )
            return response['id']
        except ClientError as e:
            print(f"Error creating REST API: {e}")
            return None
    
    def create_http_api(self, api_config: Dict[str, Any]) -> Optional[str]:
        """Create HTTP API (API Gateway v2)"""
        try:
            response = self.api_gateway_v2_client.create_api(
                Name=api_config['name'],
                Description=api_config.get('description', ''),
                ProtocolType=api_config.get('protocolType', 'HTTP'),
                RouteSelectionExpression=api_config.get('routeSelectionExpression', '$request.method $request.path'),
                Tags=api_config.get('tags', {})
            )
            return response['ApiId']
        except ClientError as e:
            print(f"Error creating HTTP API: {e}")
            return None
    
    def create_websocket_api(self, api_config: Dict[str, Any]) -> Optional[str]:
        """Create WebSocket API"""
        try:
            response = self.api_gateway_v2_client.create_api(
                Name=api_config['name'],
                Description=api_config.get('description', ''),
                ProtocolType='WEBSOCKET',
                RouteSelectionExpression=api_config.get('routeSelectionExpression', '$request.body.action'),
                Tags=api_config.get('tags', {})
            )
            return response['ApiId']
        except ClientError as e:
            print(f"Error creating WebSocket API: {e}")
            return None
    
    def create_resource(self, rest_api_id: str, parent_id: str, path_part: str) -> Optional[str]:
        """Create API resource"""
        try:
            response = self.api_gateway_client.create_resource(
                restApiId=rest_api_id,
                parentId=parent_id,
                pathPart=path_part
            )
            return response['id']
        except ClientError as e:
            print(f"Error creating resource: {e}")
            return None
    
    def create_method(self, rest_api_id: str, resource_id: str, http_method: str, 
                     method_config: Dict[str, Any]) -> bool:
        """Create HTTP method"""
        try:
            self.api_gateway_client.put_method(
                restApiId=rest_api_id,
                resourceId=resource_id,
                httpMethod=http_method,
                authorizationType=method_config.get('authorizationType', 'NONE'),
                authorizerId=method_config.get('authorizerId'),
                apiKeyRequired=method_config.get('apiKeyRequired', False),
                requestParameters=method_config.get('requestParameters', {}),
                requestValidatorId=method_config.get('requestValidatorId')
            )
            return True
        except ClientError as e:
            print(f"Error creating method: {e}")
            return False
    
    def create_integration(self, rest_api_id: str, resource_id: str, http_method: str,
                          integration_config: Dict[str, Any]) -> bool:
        """Create integration"""
        try:
            self.api_gateway_client.put_integration(
                restApiId=rest_api_id,
                resourceId=resource_id,
                httpMethod=http_method,
                type=integration_config['type'],
                integrationHttpMethod=integration_config.get('integrationHttpMethod'),
                uri=integration_config.get('uri'),
                credentials=integration_config.get('credentials'),
                requestParameters=integration_config.get('requestParameters', {}),
                requestTemplates=integration_config.get('requestTemplates', {}),
                cacheNamespace=integration_config.get('cacheNamespace'),
                cacheKeyParameters=integration_config.get('cacheKeyParameters', []),
                contentHandling=integration_config.get('contentHandling'),
                timeoutInMillis=integration_config.get('timeoutInMillis', 29000)
            )
            return True
        except ClientError as e:
            print(f"Error creating integration: {e}")
            return False
    
    def create_lambda_integration(self, rest_api_id: str, resource_id: str, http_method: str,
                                 lambda_function_arn: str) -> bool:
        """Create Lambda integration"""
        integration_config = {
            'type': 'AWS_PROXY',
            'integrationHttpMethod': 'POST',
            'uri': f'arn:aws:apigateway:{self.region}:lambda:path/2015-03-31/functions/{lambda_function_arn}/invocations'
        }
        
        if self.create_integration(rest_api_id, resource_id, http_method, integration_config):
            # Add Lambda permission
            try:
                self.lambda_client.add_permission(
                    FunctionName=lambda_function_arn,
                    StatementId=f'api-gateway-{rest_api_id}',
                    Action='lambda:InvokeFunction',
                    Principal='apigateway.amazonaws.com',
                    SourceArn=f'arn:aws:execute-api:{self.region}:*:{rest_api_id}/*/*'
                )
                return True
            except ClientError as e:
                print(f"Error adding Lambda permission: {e}")
                return False
        return False
    
    def create_route(self, api_id: str, route_config: Dict[str, Any]) -> Optional[str]:
        """Create route for HTTP/WebSocket API"""
        try:
            response = self.api_gateway_v2_client.create_route(
                ApiId=api_id,
                RouteKey=route_config['routeKey'],
                Target=route_config.get('target', 'integrations/{integrationId}'),
                AuthorizationType=route_config.get('authorizationType', 'NONE'),
                AuthorizerId=route_config.get('authorizerId'),
                RequestParameters=route_config.get('requestParameters', {}),
                RouteResponseSelectionExpression=route_config.get('routeResponseSelectionExpression'),
                OperationName=route_config.get('operationName')
            )
            return response['RouteId']
        except ClientError as e:
            print(f"Error creating route: {e}")
            return None
    
    def create_integration_v2(self, api_id: str, integration_config: Dict[str, Any]) -> Optional[str]:
        """Create integration for HTTP/WebSocket API"""
        try:
            response = self.api_gateway_v2_client.create_integration(
                ApiId=api_id,
                IntegrationType=integration_config['integrationType'],
                IntegrationMethod=integration_config.get('integrationMethod'),
                IntegrationUri=integration_config.get('integrationUri'),
                PayloadFormatVersion=integration_config.get('payloadFormatVersion', '1.0'),
                CredentialsArn=integration_config.get('credentialsArn'),
                RequestParameters=integration_config.get('requestParameters', {}),
                RequestTemplates=integration_config.get('requestTemplates', {}),
                ResponseParameters=integration_config.get('responseParameters', {}),
                TemplateSelectionExpression=integration_config.get('templateSelectionExpression'),
                TimeoutInMillis=integration_config.get('timeoutInMillis', 29000)
            )
            return response['IntegrationId']
        except ClientError as e:
            print(f"Error creating integration: {e}")
            return None
    
    def create_stage(self, rest_api_id: str, stage_name: str, deployment_id: str,
                    stage_config: Dict[str, Any] = None) -> bool:
        """Create deployment stage"""
        try:
            config = stage_config or {}
            self.api_gateway_client.create_stage(
                restApiId=rest_api_id,
                stageName=stage_name,
                deploymentId=deployment_id,
                description=config.get('description', ''),
                cacheClusterEnabled=config.get('cacheClusterEnabled', False),
                cacheClusterSize=config.get('cacheClusterSize', '0.5'),
                variables=config.get('variables', {}),
                documentationVersion=config.get('documentationVersion'),
                tracingEnabled=config.get('tracingEnabled', False),
                tags=config.get('tags', {})
            )
            return True
        except ClientError as e:
            print(f"Error creating stage: {e}")
            return False
    
    def create_deployment(self, rest_api_id: str, stage_name: str = 'prod') -> Optional[str]:
        """Create API deployment"""
        try:
            response = self.api_gateway_client.create_deployment(
                restApiId=rest_api_id,
                stageName=stage_name,
                stageDescription=f'Deployment for {stage_name}',
                description=f'Deployment created for {stage_name}'
            )
            return response['id']
        except ClientError as e:
            print(f"Error creating deployment: {e}")
            return None
    
    def create_authorizer(self, rest_api_id: str, authorizer_config: Dict[str, Any]) -> Optional[str]:
        """Create API authorizer"""
        try:
            response = self.api_gateway_client.create_authorizer(
                restApiId=rest_api_id,
                name=authorizer_config['name'],
                type=authorizer_config['type'],
                providerARNs=authorizer_config.get('providerARNs', []),
                authType=authorizer_config.get('authType', 'token'),
                authorizerUri=authorizer_config.get('authorizerUri'),
                authorizerCredentials=authorizer_config.get('authorizerCredentials'),
                identitySource=authorizer_config.get('identitySource', 'method.request.header.Authorization'),
                identityValidationExpression=authorizer_config.get('identityValidationExpression'),
                authorizerResultTtlInSeconds=authorizer_config.get('authorizerResultTtlInSeconds', 300)
            )
            return response['id']
        except ClientError as e:
            print(f"Error creating authorizer: {e}")
            return None
    
    def create_api_key(self, api_key_config: Dict[str, Any]) -> Optional[str]:
        """Create API key"""
        try:
            response = self.api_gateway_client.create_api_key(
                name=api_key_config['name'],
                description=api_key_config.get('description', ''),
                enabled=api_key_config.get('enabled', True),
                generateDistinctId=api_key_config.get('generateDistinctId', True),
                value=api_key_config.get('value'),
                stageKeys=api_key_config.get('stageKeys', []),
                tags=api_key_config.get('tags', {})
            )
            return response['id']
        except ClientError as e:
            print(f"Error creating API key: {e}")
            return None
    
    def create_usage_plan(self, usage_plan_config: Dict[str, Any]) -> Optional[str]:
        """Create usage plan"""
        try:
            response = self.api_gateway_client.create_usage_plan(
                name=usage_plan_config['name'],
                description=usage_plan_config.get('description', ''),
                apiStages=usage_plan_config.get('apiStages', []),
                throttle=usage_plan_config.get('throttle', {}),
                quota=usage_plan_config.get('quota', {}),
                tags=usage_plan_config.get('tags', {})
            )
            return response['id']
        except ClientError as e:
            print(f"Error creating usage plan: {e}")
            return None
    
    def create_domain_name(self, domain_config: Dict[str, Any]) -> Optional[str]:
        """Create custom domain name"""
        try:
            response = self.api_gateway_client.create_domain_name(
                domainName=domain_config['domainName'],
                certificateName=domain_config.get('certificateName'),
                certificateBody=domain_config.get('certificateBody'),
                certificatePrivateKey=domain_config.get('certificatePrivateKey'),
                certificateChain=domain_config.get('certificateChain'),
                certificateArn=domain_config.get('certificateArn'),
                regionalCertificateName=domain_config.get('regionalCertificateName'),
                regionalCertificateArn=domain_config.get('regionalCertificateArn'),
                endpointConfiguration=domain_config.get('endpointConfiguration', {
                    'types': ['REGIONAL']
                }),
                tags=domain_config.get('tags', {})
            )
            return response['domainName']
        except ClientError as e:
            print(f"Error creating domain name: {e}")
            return None
    
    def create_base_path_mapping(self, domain_name: str, mapping_config: Dict[str, Any]) -> bool:
        """Create base path mapping"""
        try:
            self.api_gateway_client.create_base_path_mapping(
                domainName=domain_name,
                basePath=mapping_config.get('basePath', ''),
                restApiId=mapping_config['restApiId'],
                stage=mapping_config.get('stage', 'prod')
            )
            return True
        except ClientError as e:
            print(f"Error creating base path mapping: {e}")
            return False
    
    def get_api_metrics(self, api_id: str, stage_name: str = None, days: int = 7) -> Dict[str, Any]:
        """Get API Gateway metrics"""
        try:
            import time
            from datetime import datetime, timedelta
            
            end_time = datetime.utcnow()
            start_time = end_time - timedelta(days=days)
            
            cloudwatch = boto3.client('cloudwatch', region_name=self.region)
            
            metrics = {}
            
            # Get request count
            request_count = cloudwatch.get_metric_statistics(
                Namespace='AWS/ApiGateway',
                MetricName='Count',
                Dimensions=[
                    {'Name': 'ApiName', 'Value': api_id}
                ],
                StartTime=start_time,
                EndTime=end_time,
                Period=3600,
                Statistics=['Sum']
            )
            metrics['RequestCount'] = request_count['Datapoints']
            
            # Get latency
            latency = cloudwatch.get_metric_statistics(
                Namespace='AWS/ApiGateway',
                MetricName='Latency',
                Dimensions=[
                    {'Name': 'ApiName', 'Value': api_id}
                ],
                StartTime=start_time,
                EndTime=end_time,
                Period=3600,
                Statistics=['Average', 'Maximum']
            )
            metrics['Latency'] = latency['Datapoints']
            
            # Get error count
            error_count = cloudwatch.get_metric_statistics(
                Namespace='AWS/ApiGateway',
                MetricName='4XXError',
                Dimensions=[
                    {'Name': 'ApiName', 'Value': api_id}
                ],
                StartTime=start_time,
                EndTime=end_time,
                Period=3600,
                Statistics=['Sum']
            )
            metrics['ErrorCount'] = error_count['Datapoints']
            
            return metrics
        except ClientError as e:
            print(f"Error getting API metrics: {e}")
            return {}
    
    def enable_cors(self, rest_api_id: str, resource_id: str, methods: List[str] = None) -> bool:
        """Enable CORS for API resource"""
        try:
            if not methods:
                methods = ['GET', 'POST', 'PUT', 'DELETE', 'OPTIONS']
            
            for method in methods:
                self.api_gateway_client.put_method(
                    restApiId=rest_api_id,
                    resourceId=resource_id,
                    httpMethod=method
                )
                
                self.api_gateway_client.put_integration(
                    restApiId=rest_api_id,
                    resourceId=resource_id,
                    httpMethod=method,
                    type='MOCK',
                    requestTemplates={
                        'application/json': '{"statusCode": 200}'
                    }
                )
                
                if method == 'OPTIONS':
                    self.api_gateway_client.put_method_response(
                        restApiId=rest_api_id,
                        resourceId=resource_id,
                        httpMethod=method,
                        statusCode='200',
                        responseParameters={
                            'method.response.header.Access-Control-Allow-Headers': True,
                            'method.response.header.Access-Control-Allow-Methods': True,
                            'method.response.header.Access-Control-Allow-Origin': True
                        }
                    )
                    
                    self.api_gateway_client.put_integration_response(
                        restApiId=rest_api_id,
                        resourceId=resource_id,
                        httpMethod=method,
                        statusCode='200',
                        responseParameters={
                            'method.response.header.Access-Control-Allow-Headers': "'Content-Type,X-Amz-Date,Authorization,X-Api-Key,X-Amz-Security-Token'",
                            'method.response.header.Access-Control-Allow-Methods': f"'{','.join(methods)}'",
                            'method.response.header.Access-Control-Allow-Origin': "'*'"
                        }
                    )
            
            return True
        except ClientError as e:
            print(f"Error enabling CORS: {e}")
            return False
    
    def delete_api(self, api_id: str, api_type: str = 'REST') -> bool:
        """Delete API"""
        try:
            if api_type == 'REST':
                self.api_gateway_client.delete_rest_api(restApiId=api_id)
            else:
                self.api_gateway_v2_client.delete_api(ApiId=api_id)
            return True
        except ClientError as e:
            print(f"Error deleting API: {e}")
            return False
    
    def list_apis(self, api_type: str = 'REST') -> List[Dict[str, Any]]:
        """List APIs"""
        try:
            if api_type == 'REST':
                response = self.api_gateway_client.get_rest_apis()
                return response['items']
            else:
                response = self.api_gateway_v2_client.get_apis()
                return response['Items']
        except ClientError as e:
            print(f"Error listing APIs: {e}")
            return []


# Example usage and testing
if __name__ == "__main__":
    # Initialize API Gateway manager
    api_manager = APIGatewayManager()
    
    # Example REST API configuration
    rest_api_config = {
        'name': 'test-rest-api',
        'description': 'Test REST API',
        'version': '1.0',
        'endpointConfiguration': {'types': ['REGIONAL']}
    }
    
    # Create REST API
    api_id = api_manager.create_rest_api(rest_api_config)
    if api_id:
        print(f"REST API created: {api_id}")
        
        # Create resource
        resource_id = api_manager.create_resource(api_id, 'root', 'test')
        if resource_id:
            print(f"Resource created: {resource_id}")
            
            # Create method
            if api_manager.create_method(api_id, resource_id, 'GET', {}):
                print("Method created successfully")
                
                # Create deployment
                deployment_id = api_manager.create_deployment(api_id)
                if deployment_id:
                    print(f"Deployment created: {deployment_id}")
    
    # Example HTTP API configuration
    http_api_config = {
        'name': 'test-http-api',
        'description': 'Test HTTP API',
        'protocolType': 'HTTP'
    }
    
    # Create HTTP API
    http_api_id = api_manager.create_http_api(http_api_config)
    if http_api_id:
        print(f"HTTP API created: {http_api_id}")