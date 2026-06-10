#!/usr/bin/env python3
"""
AWS ECR Manager for container registry operations.

This module provides comprehensive ECR management capabilities including
repository management, image operations, and lifecycle policies.
"""

import boto3
import logging
import json
import time
from typing import List, Dict, Any, Optional
from datetime import datetime
import base64

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class ECRManager:
    """
    AWS ECR Manager for container registry operations.
    """
    
    def __init__(self, region: str = 'us-east-1'):
        """Initialize ECRManager with AWS clients."""
        self.region = region
        self.ecr_client = boto3.client('ecr', region_name=region)
        self.ecr_public_client = boto3.client('ecr-public', region_name=region)
        
    def create_repository(self, repository_name: str, repository_config: Dict[str, Any] = None) -> Optional[str]:
        """Create ECR repository."""
        try:
            logger.info(f"Creating ECR repository: {repository_name}")
            
            # Default configuration
            config = repository_config or {}
            
            # Build repository parameters
            repo_params = {
                'repositoryName': repository_name,
                'imageTagMutability': config.get('image_tag_mutability', 'MUTABLE'),
                'imageScanningConfiguration': {
                    'scanOnPush': config.get('scan_on_push', True)
                }
            }
            
            # Add encryption configuration if specified
            if 'encryption_configuration' in config:
                repo_params['encryptionConfiguration'] = config['encryption_configuration']
            
            # Add lifecycle policy if specified
            if 'lifecycle_policy' in config:
                repo_params['lifecyclePolicyText'] = json.dumps(config['lifecycle_policy'])
            
            # Add repository policy if specified
            if 'repository_policy' in config:
                repo_params['repositoryPolicyText'] = json.dumps(config['repository_policy'])
            
            # Create repository
            response = self.ecr_client.create_repository(**repo_params)
            
            repository_uri = response['repository']['repositoryUri']
            logger.info(f"ECR repository {repository_name} created successfully: {repository_uri}")
            return repository_uri
            
        except self.ecr_client.exceptions.RepositoryAlreadyExistsException:
            logger.info(f"ECR repository {repository_name} already exists")
            return f"{self._get_account_id()}.dkr.ecr.{self.region}.amazonaws.com/{repository_name}"
        except Exception as e:
            logger.error(f"Error creating ECR repository: {str(e)}")
            return None
    
    def list_repositories(self) -> List[Dict[str, Any]]:
        """List all ECR repositories."""
        try:
            response = self.ecr_client.describe_repositories()
            repositories = []
            
            for repo in response['repositories']:
                repositories.append({
                    'repository_name': repo['repositoryName'],
                    'repository_uri': repo['repositoryUri'],
                    'registry_id': repo['registryId'],
                    'repository_arn': repo['repositoryArn'],
                    'created_at': repo['createdAt'],
                    'image_tag_mutability': repo['imageTagMutability'],
                    'image_scanning_configuration': repo.get('imageScanningConfiguration', {}),
                    'encryption_configuration': repo.get('encryptionConfiguration', {}),
                    'lifecycle_policy': repo.get('lifecyclePolicy', {}),
                    'repository_policy': repo.get('repositoryPolicy', {})
                })
            
            return repositories
            
        except Exception as e:
            logger.error(f"Error listing repositories: {str(e)}")
            return []
    
    def get_repository_info(self, repository_name: str) -> Dict[str, Any]:
        """Get detailed repository information."""
        try:
            response = self.ecr_client.describe_repositories(
                repositoryNames=[repository_name]
            )
            
            if not response['repositories']:
                return {}
            
            repo = response['repositories'][0]
            
            # Get additional information
            lifecycle_policy = self.get_lifecycle_policy(repository_name)
            repository_policy = self.get_repository_policy(repository_name)
            images = self.list_images(repository_name)
            
            return {
                'repository_name': repo['repositoryName'],
                'repository_uri': repo['repositoryUri'],
                'registry_id': repo['registryId'],
                'repository_arn': repo['repositoryArn'],
                'created_at': repo['createdAt'],
                'image_tag_mutability': repo['imageTagMutability'],
                'image_scanning_configuration': repo.get('imageScanningConfiguration', {}),
                'encryption_configuration': repo.get('encryptionConfiguration', {}),
                'lifecycle_policy': lifecycle_policy,
                'repository_policy': repository_policy,
                'images': images
            }
            
        except Exception as e:
            logger.error(f"Error getting repository info: {str(e)}")
            return {}
    
    def list_images(self, repository_name: str, max_results: int = 100) -> List[Dict[str, Any]]:
        """List images in repository."""
        try:
            response = self.ecr_client.describe_images(
                repositoryName=repository_name,
                maxResults=max_results
            )
            
            images = []
            for image in response['imageDetails']:
                images.append({
                    'image_digest': image['imageDigest'],
                    'image_tags': image.get('imageTags', []),
                    'image_size_in_bytes': image.get('imageSizeInBytes'),
                    'image_pushed_at': image.get('imagePushedAt'),
                    'image_scan_status': image.get('imageScanStatus', {}),
                    'image_scan_findings_summary': image.get('imageScanFindingsSummary', {}),
                    'vulnerability_counts': image.get('imageScanFindingsSummary', {}).get('findingCounts', {}),
                    'registry_id': image['registryId'],
                    'repository_name': image['repositoryName']
                })
            
            return images
            
        except Exception as e:
            logger.error(f"Error listing images: {str(e)}")
            return []
    
    def get_image_scan_findings(self, repository_name: str, image_digest: str) -> Dict[str, Any]:
        """Get image scan findings."""
        try:
            response = self.ecr_client.describe_image_scan_findings(
                repositoryName=repository_name,
                imageId={'imageDigest': image_digest}
            )
            
            findings = response.get('imageScanFindings', {}).get('findings', [])
            
            # Process findings
            processed_findings = []
            for finding in findings:
                processed_findings.append({
                    'name': finding.get('name'),
                    'description': finding.get('description'),
                    'severity': finding.get('severity'),
                    'uri': finding.get('uri'),
                    'attributes': finding.get('attributes', [])
                })
            
            return {
                'repository_name': repository_name,
                'image_digest': image_digest,
                'scan_status': response.get('imageScanStatus', {}).get('status'),
                'findings': processed_findings,
                'finding_counts': response.get('imageScanFindings', {}).get('findingCounts', {}),
                'scan_completed_at': response.get('imageScanStatus', {}).get('completedAt')
            }
            
        except Exception as e:
            logger.error(f"Error getting image scan findings: {str(e)}")
            return {}
    
    def start_image_scan(self, repository_name: str, image_tag: str) -> bool:
        """Start image vulnerability scan."""
        try:
            logger.info(f"Starting image scan for {repository_name}:{image_tag}")
            
            response = self.ecr_client.start_image_scan(
                repositoryName=repository_name,
                imageId={'imageTag': image_tag}
            )
            
            logger.info(f"Image scan started for {repository_name}:{image_tag}")
            return True
            
        except Exception as e:
            logger.error(f"Error starting image scan: {str(e)}")
            return False
    
    def delete_image(self, repository_name: str, image_digest: str) -> bool:
        """Delete image from repository."""
        try:
            logger.info(f"Deleting image {image_digest} from {repository_name}")
            
            response = self.ecr_client.batch_delete_image(
                repositoryName=repository_name,
                imageIds=[{'imageDigest': image_digest}]
            )
            
            logger.info(f"Image {image_digest} deleted from {repository_name}")
            return True
            
        except Exception as e:
            logger.error(f"Error deleting image: {str(e)}")
            return False
    
    def delete_images_by_tag(self, repository_name: str, image_tag: str) -> bool:
        """Delete all images with specific tag."""
        try:
            logger.info(f"Deleting images with tag {image_tag} from {repository_name}")
            
            # Get images with the tag
            images = self.list_images(repository_name)
            images_to_delete = []
            
            for image in images:
                if image_tag in image['image_tags']:
                    images_to_delete.append({
                        'imageDigest': image['image_digest']
                    })
            
            if not images_to_delete:
                logger.info(f"No images found with tag {image_tag}")
                return True
            
            # Delete images
            response = self.ecr_client.batch_delete_image(
                repositoryName=repository_name,
                imageIds=images_to_delete
            )
            
            logger.info(f"Deleted {len(images_to_delete)} images with tag {image_tag}")
            return True
            
        except Exception as e:
            logger.error(f"Error deleting images by tag: {str(e)}")
            return False
    
    def set_lifecycle_policy(self, repository_name: str, lifecycle_policy: Dict[str, Any]) -> bool:
        """Set repository lifecycle policy."""
        try:
            logger.info(f"Setting lifecycle policy for {repository_name}")
            
            self.ecr_client.put_lifecycle_policy(
                repositoryName=repository_name,
                lifecyclePolicyText=json.dumps(lifecycle_policy)
            )
            
            logger.info(f"Lifecycle policy set for {repository_name}")
            return True
            
        except Exception as e:
            logger.error(f"Error setting lifecycle policy: {str(e)}")
            return False
    
    def get_lifecycle_policy(self, repository_name: str) -> Dict[str, Any]:
        """Get repository lifecycle policy."""
        try:
            response = self.ecr_client.get_lifecycle_policy(
                repositoryName=repository_name
            )
            
            return json.loads(response['lifecyclePolicyText'])
            
        except self.ecr_client.exceptions.LifecyclePolicyNotFoundException:
            return {}
        except Exception as e:
            logger.error(f"Error getting lifecycle policy: {str(e)}")
            return {}
    
    def set_repository_policy(self, repository_name: str, repository_policy: Dict[str, Any]) -> bool:
        """Set repository policy."""
        try:
            logger.info(f"Setting repository policy for {repository_name}")
            
            self.ecr_client.set_repository_policy(
                repositoryName=repository_name,
                policyText=json.dumps(repository_policy)
            )
            
            logger.info(f"Repository policy set for {repository_name}")
            return True
            
        except Exception as e:
            logger.error(f"Error setting repository policy: {str(e)}")
            return False
    
    def get_repository_policy(self, repository_name: str) -> Dict[str, Any]:
        """Get repository policy."""
        try:
            response = self.ecr_client.get_repository_policy(
                repositoryName=repository_name
            )
            
            return json.loads(response['policyText'])
            
        except self.ecr_client.exceptions.RepositoryPolicyNotFoundException:
            return {}
        except Exception as e:
            logger.error(f"Error getting repository policy: {str(e)}")
            return {}
    
    def get_authorization_token(self) -> Dict[str, str]:
        """Get ECR authorization token for Docker login."""
        try:
            response = self.ecr_client.get_authorization_token()
            
            token_data = response['authorizationData'][0]
            token = token_data['authorizationToken']
            proxy_endpoint = token_data['proxyEndpoint']
            
            # Decode token
            decoded_token = base64.b64decode(token).decode('utf-8')
            username, password = decoded_token.split(':')
            
            return {
                'username': username,
                'password': password,
                'proxy_endpoint': proxy_endpoint,
                'registry_url': proxy_endpoint.replace('https://', '')
            }
            
        except Exception as e:
            logger.error(f"Error getting authorization token: {str(e)}")
            return {}
    
    def create_default_lifecycle_policy(self) -> Dict[str, Any]:
        """Create default lifecycle policy for cost optimization."""
        return {
            "rules": [
                {
                    "rulePriority": 1,
                    "description": "Keep last 10 production images",
                    "selection": {
                        "tagStatus": "tagged",
                        "tagPrefixList": ["prod", "production"],
                        "countType": "imageCountMoreThan",
                        "countNumber": 10
                    },
                    "action": {
                        "type": "expire"
                    }
                },
                {
                    "rulePriority": 2,
                    "description": "Keep last 5 staging images",
                    "selection": {
                        "tagStatus": "tagged",
                        "tagPrefixList": ["staging", "stage"],
                        "countType": "imageCountMoreThan",
                        "countNumber": 5
                    },
                    "action": {
                        "type": "expire"
                    }
                },
                {
                    "rulePriority": 3,
                    "description": "Keep last 3 development images",
                    "selection": {
                        "tagStatus": "tagged",
                        "tagPrefixList": ["dev", "development"],
                        "countType": "imageCountMoreThan",
                        "countNumber": 3
                    },
                    "action": {
                        "type": "expire"
                    }
                },
                {
                    "rulePriority": 4,
                    "description": "Delete untagged images older than 1 day",
                    "selection": {
                        "tagStatus": "untagged",
                        "countType": "sinceImagePushed",
                        "countUnit": "days",
                        "countNumber": 1
                    },
                    "action": {
                        "type": "expire"
                    }
                }
            ]
        }
    
    def create_public_repository(self, repository_name: str, repository_config: Dict[str, Any] = None) -> Optional[str]:
        """Create ECR public repository."""
        try:
            logger.info(f"Creating ECR public repository: {repository_name}")
            
            # Default configuration
            config = repository_config or {}
            
            # Build repository parameters
            repo_params = {
                'repositoryName': repository_name,
                'imageTagMutability': config.get('image_tag_mutability', 'MUTABLE'),
                'imageScanningConfiguration': {
                    'scanOnPush': config.get('scan_on_push', True)
                }
            }
            
            # Create public repository
            response = self.ecr_public_client.create_repository(**repo_params)
            
            repository_uri = response['repository']['repositoryUri']
            logger.info(f"ECR public repository {repository_name} created successfully: {repository_uri}")
            return repository_uri
            
        except self.ecr_public_client.exceptions.RepositoryAlreadyExistsException:
            logger.info(f"ECR public repository {repository_name} already exists")
            return f"public.ecr.aws/{self._get_account_id()}/{repository_name}"
        except Exception as e:
            logger.error(f"Error creating ECR public repository: {str(e)}")
            return None
    
    def delete_repository(self, repository_name: str, force: bool = False) -> bool:
        """Delete ECR repository."""
        try:
            logger.info(f"Deleting ECR repository: {repository_name}")
            
            self.ecr_client.delete_repository(
                repositoryName=repository_name,
                force=force
            )
            
            logger.info(f"ECR repository {repository_name} deleted successfully")
            return True
            
        except self.ecr_client.exceptions.RepositoryNotFoundException:
            logger.info(f"ECR repository {repository_name} not found")
            return True
        except Exception as e:
            logger.error(f"Error deleting repository: {str(e)}")
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
    """Main function for testing ECRManager."""
    # Example usage
    ecr_manager = ECRManager()
    
    # Create repository
    repo_config = {
        'image_tag_mutability': 'MUTABLE',
        'scan_on_push': True,
        'lifecycle_policy': ecr_manager.create_default_lifecycle_policy()
    }
    
    repo_uri = ecr_manager.create_repository('test-repo', repo_config)
    if repo_uri:
        print(f"Repository created: {repo_uri}")
        
        # Get repository info
        info = ecr_manager.get_repository_info('test-repo')
        print(f"Repository info: {info}")
        
        # List repositories
        repos = ecr_manager.list_repositories()
        print(f"All repositories: {repos}")


if __name__ == "__main__":
    main()