#!/usr/bin/env python3
"""
AWS EKS Cluster Manager for automated cluster management.

This module provides comprehensive EKS cluster management capabilities including
cluster creation, node group management, addon installation, and monitoring.
"""

import boto3
import json
import logging
import time
import subprocess
from typing import List, Dict, Any, Optional
from datetime import datetime
import yaml

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class EKSClusterManager:
    """
    AWS EKS Cluster Manager for automated cluster management.
    """
    
    def __init__(self, region: str = 'us-east-1'):
        """Initialize EKSClusterManager with AWS clients."""
        self.region = region
        self.eks_client = boto3.client('eks', region_name=region)
        self.ec2_client = boto3.client('ec2', region_name=region)
        self.iam_client = boto3.client('iam', region_name=region)
        self.autoscaling_client = boto3.client('autoscaling', region_name=region)
        self.elasticloadbalancing_client = boto3.client('elbv2', region_name=region)
        
    def create_cluster(self, cluster_name: str, cluster_config: Dict[str, Any]) -> Optional[str]:
        """Create EKS cluster with comprehensive configuration."""
        try:
            # Validate cluster configuration
            self._validate_cluster_config(cluster_config)
            
            # Create IAM roles if not exist
            cluster_role_arn = self._create_cluster_role(cluster_name)
            node_role_arn = self._create_node_role(cluster_name)
            
            # Get VPC configuration
            vpc_config = self._get_vpc_config(cluster_config)
            
            # Build cluster configuration
            cluster_params = {
                'name': cluster_name,
                'version': cluster_config.get('kubernetes_version', '1.27'),
                'roleArn': cluster_role_arn,
                'resourcesVpcConfig': vpc_config,
                'logging': {
                    'clusterLogging': [
                        {
                            'types': cluster_config.get('enabled_log_types', [
                                'api', 'audit', 'authenticator', 
                                'controllerManager', 'scheduler'
                            ]),
                            'enabled': True
                        }
                    ]
                },
                'tags': cluster_config.get('tags', {})
            }
            
            # Add encryption configuration
            if 'encryption_config' in cluster_config:
                cluster_params['encryptionConfig'] = cluster_config['encryption_config']
            
            # Add endpoint configuration
            if 'endpoint_config' in cluster_config:
                cluster_params['resourcesVpcConfig'].update(cluster_config['endpoint_config'])
            
            response = self.eks_client.create_cluster(**cluster_params)
            
            logger.info(f"EKS cluster {cluster_name} creation initiated")
            
            # Wait for cluster to be active
            if cluster_config.get('wait_for_active', True):
                self._wait_for_cluster_active(cluster_name)
            
            return response['cluster']['arn']
            
        except Exception as e:
            logger.error(f"Error creating EKS cluster: {str(e)}")
            return None
    
    def _validate_cluster_config(self, config: Dict[str, Any]) -> None:
        """Validate cluster configuration."""
        required_fields = ['subnet_ids']
        for field in required_fields:
            if field not in config:
                raise ValueError(f"Missing required field: {field}")
    
    def _create_cluster_role(self, cluster_name: str) -> str:
        """Create IAM role for EKS cluster."""
        role_name = f"{cluster_name}-cluster-role"
        
        try:
            # Check if role exists
            self.iam_client.get_role(RoleName=role_name)
            logger.info(f"Cluster role {role_name} already exists")
            return f"arn:aws:iam::{self._get_account_id()}:role/{role_name}"
            
        except self.iam_client.exceptions.NoSuchEntityException:
            # Create role
            assume_role_policy = {
                "Version": "2012-10-17",
                "Statement": [{
                    "Effect": "Allow",
                    "Principal": {"Service": "eks.amazonaws.com"},
                    "Action": "sts:AssumeRole"
                }]
            }
            
            self.iam_client.create_role(
                RoleName=role_name,
                AssumeRolePolicyDocument=json.dumps(assume_role_policy),
                Description=f"IAM role for {cluster_name} EKS cluster"
            )
            
            # Attach policies
            policies = [
                "arn:aws:iam::aws:policy/AmazonEKSClusterPolicy",
                "arn:aws:iam::aws:policy/AmazonEKSVPCResourceController"
            ]
            
            for policy_arn in policies:
                self.iam_client.attach_role_policy(
                    RoleName=role_name,
                    PolicyArn=policy_arn
                )
            
            logger.info(f"Created cluster role: {role_name}")
            return f"arn:aws:iam::{self._get_account_id()}:role/{role_name}"
    
    def _create_node_role(self, cluster_name: str) -> str:
        """Create IAM role for EKS node group."""
        role_name = f"{cluster_name}-node-role"
        
        try:
            # Check if role exists
            self.iam_client.get_role(RoleName=role_name)
            logger.info(f"Node role {role_name} already exists")
            return f"arn:aws:iam::{self._get_account_id()}:role/{role_name}"
            
        except self.iam_client.exceptions.NoSuchEntityException:
            # Create role
            assume_role_policy = {
                "Version": "2012-10-17",
                "Statement": [{
                    "Effect": "Allow",
                    "Principal": {"Service": "ec2.amazonaws.com"},
                    "Action": "sts:AssumeRole"
                }]
            }
            
            self.iam_client.create_role(
                RoleName=role_name,
                AssumeRolePolicyDocument=json.dumps(assume_role_policy),
                Description=f"IAM role for {cluster_name} EKS node group"
            )
            
            # Attach policies
            policies = [
                "arn:aws:iam::aws:policy/AmazonEKSWorkerNodePolicy",
                "arn:aws:iam::aws:policy/AmazonEKS_CNI_Policy",
                "arn:aws:iam::aws:policy/AmazonEC2ContainerRegistryReadOnlyAccess"
            ]
            
            for policy_arn in policies:
                self.iam_client.attach_role_policy(
                    RoleName=role_name,
                    PolicyArn=policy_arn
                )
            
            logger.info(f"Created node role: {role_name}")
            return f"arn:aws:iam::{self._get_account_id()}:role/{role_name}"
    
    def _get_vpc_config(self, config: Dict[str, Any]) -> Dict[str, Any]:
        """Get VPC configuration for cluster."""
        vpc_config = {
            'subnetIds': config['subnet_ids'],
            'endpointPublicAccess': config.get('endpoint_public_access', True),
            'endpointPrivateAccess': config.get('endpoint_private_access', True)
        }
        
        # Add security group IDs if provided
        if 'security_group_ids' in config:
            vpc_config['securityGroupIds'] = config['security_group_ids']
        
        # Add public access CIDRs if provided
        if 'public_access_cidrs' in config:
            vpc_config['publicAccessCidrs'] = config['public_access_cidrs']
        
        return vpc_config
    
    def _wait_for_cluster_active(self, cluster_name: str, timeout: int = 1200) -> bool:
        """Wait for cluster to become active."""
        logger.info(f"Waiting for cluster {cluster_name} to become active...")
        
        start_time = time.time()
        while time.time() - start_time < timeout:
            try:
                response = self.eks_client.describe_cluster(name=cluster_name)
                status = response['cluster']['status']
                
                if status == 'ACTIVE':
                    logger.info(f"Cluster {cluster_name} is now active")
                    return True
                elif status == 'FAILED':
                    logger.error(f"Cluster {cluster_name} creation failed")
                    return False
                
                logger.info(f"Cluster status: {status}, waiting...")
                time.sleep(30)
                
            except Exception as e:
                logger.error(f"Error checking cluster status: {str(e)}")
                time.sleep(30)
        
        logger.error(f"Timeout waiting for cluster {cluster_name} to become active")
        return False
    
    def create_nodegroup(self, cluster_name: str, nodegroup_name: str, 
                        nodegroup_config: Dict[str, Any]) -> Optional[str]:
        """Create EKS node group."""
        try:
            # Validate nodegroup configuration
            self._validate_nodegroup_config(nodegroup_config)
            
            # Get node role ARN
            node_role_arn = f"arn:aws:iam::{self._get_account_id()}:role/{cluster_name}-node-role"
            
            # Build nodegroup configuration
            nodegroup_params = {
                'clusterName': cluster_name,
                'nodegroupName': nodegroup_name,
                'nodeRole': node_role_arn,
                'subnets': nodegroup_config['subnet_ids'],
                'instanceTypes': nodegroup_config.get('instance_types', ['t3.medium']),
                'capacityType': nodegroup_config.get('capacity_type', 'ON_DEMAND'),
                'scalingConfig': {
                    'minSize': nodegroup_config.get('min_size', 1),
                    'maxSize': nodegroup_config.get('max_size', 3),
                    'desiredSize': nodegroup_config.get('desired_size', 2)
                },
                'updateConfig': {
                    'maxUnavailable': nodegroup_config.get('max_unavailable', 1)
                },
                'tags': nodegroup_config.get('tags', {})
            }
            
            # Add AMI type if provided
            if 'ami_type' in nodegroup_config:
                nodegroup_params['amiType'] = nodegroup_config['ami_type']
            
            # Add disk size if provided
            if 'disk_size' in nodegroup_config:
                nodegroup_params['diskSize'] = nodegroup_config['disk_size']
            
            # Add launch template if provided
            if 'launch_template' in nodegroup_config:
                nodegroup_params['launchTemplate'] = nodegroup_config['launch_template']
            
            # Add remote access if provided
            if 'remote_access' in nodegroup_config:
                nodegroup_params['remoteAccess'] = nodegroup_config['remote_access']
            
            # Add taints if provided
            if 'taints' in nodegroup_config:
                nodegroup_params['taints'] = nodegroup_config['taints']
            
            response = self.eks_client.create_nodegroup(**nodegroup_params)
            
            logger.info(f"Node group {nodegroup_name} creation initiated")
            
            # Wait for node group to be active
            if nodegroup_config.get('wait_for_active', True):
                self._wait_for_nodegroup_active(cluster_name, nodegroup_name)
            
            return response['nodegroup']['nodegroupArn']
            
        except Exception as e:
            logger.error(f"Error creating node group: {str(e)}")
            return None
    
    def _validate_nodegroup_config(self, config: Dict[str, Any]) -> None:
        """Validate nodegroup configuration."""
        required_fields = ['subnet_ids']
        for field in required_fields:
            if field not in config:
                raise ValueError(f"Missing required field: {field}")
    
    def _wait_for_nodegroup_active(self, cluster_name: str, nodegroup_name: str, 
                                  timeout: int = 1200) -> bool:
        """Wait for node group to become active."""
        logger.info(f"Waiting for node group {nodegroup_name} to become active...")
        
        start_time = time.time()
        while time.time() - start_time < timeout:
            try:
                response = self.eks_client.describe_nodegroup(
                    clusterName=cluster_name,
                    nodegroupName=nodegroup_name
                )
                status = response['nodegroup']['status']
                
                if status == 'ACTIVE':
                    logger.info(f"Node group {nodegroup_name} is now active")
                    return True
                elif status == 'CREATE_FAILED':
                    logger.error(f"Node group {nodegroup_name} creation failed")
                    return False
                
                logger.info(f"Node group status: {status}, waiting...")
                time.sleep(30)
                
            except Exception as e:
                logger.error(f"Error checking node group status: {str(e)}")
                time.sleep(30)
        
        logger.error(f"Timeout waiting for node group {nodegroup_name} to become active")
        return False
    
    def install_addon(self, cluster_name: str, addon_name: str, 
                     addon_config: Dict[str, Any]) -> Optional[str]:
        """Install EKS addon."""
        try:
            addon_params = {
                'clusterName': cluster_name,
                'addonName': addon_name,
                'addonVersion': addon_config.get('addon_version', 'latest'),
                'resolveConflicts': addon_config.get('resolve_conflicts', 'OVERWRITE')
            }
            
            # Add service account role ARN if provided
            if 'service_account_role_arn' in addon_config:
                addon_params['serviceAccountRoleArn'] = addon_config['service_account_role_arn']
            
            # Add tags if provided
            if 'tags' in addon_config:
                addon_params['tags'] = addon_config['tags']
            
            response = self.eks_client.create_addon(**addon_params)
            
            logger.info(f"Addon {addon_name} installation initiated")
            return response['addon']['addonArn']
            
        except Exception as e:
            logger.error(f"Error installing addon: {str(e)}")
            return None
    
    def update_kubeconfig(self, cluster_name: str, region: str = None) -> bool:
        """Update kubeconfig for cluster access."""
        try:
            if region is None:
                region = self.region
            
            subprocess.run([
                'aws', 'eks', 'update-kubeconfig',
                '--name', cluster_name,
                '--region', region
            ], check=True)
            
            logger.info(f"Kubeconfig updated for cluster {cluster_name}")
            return True
            
        except subprocess.CalledProcessError as e:
            logger.error(f"Error updating kubeconfig: {str(e)}")
            return False
    
    def get_cluster_status(self, cluster_name: str) -> Dict[str, Any]:
        """Get cluster status and information."""
        try:
            response = self.eks_client.describe_cluster(name=cluster_name)
            cluster = response['cluster']
            
            return {
                'name': cluster['name'],
                'arn': cluster['arn'],
                'version': cluster['version'],
                'status': cluster['status'],
                'endpoint': cluster['endpoint'],
                'platform_version': cluster['platformVersion'],
                'created_at': cluster['createdAt'].isoformat(),
                'role_arn': cluster['roleArn'],
                'vpc_config': cluster['resourcesVpcConfig'],
                'logging': cluster.get('logging', {}),
                'encryption_config': cluster.get('encryptionConfig', [])
            }
            
        except Exception as e:
            logger.error(f"Error getting cluster status: {str(e)}")
            return {}
    
    def get_nodegroup_status(self, cluster_name: str, nodegroup_name: str) -> Dict[str, Any]:
        """Get node group status and information."""
        try:
            response = self.eks_client.describe_nodegroup(
                clusterName=cluster_name,
                nodegroupName=nodegroup_name
            )
            nodegroup = response['nodegroup']
            
            return {
                'name': nodegroup['nodegroupName'],
                'arn': nodegroup['nodegroupArn'],
                'cluster_name': nodegroup['clusterName'],
                'status': nodegroup['status'],
                'capacity_type': nodegroup['capacityType'],
                'instance_types': nodegroup['instanceTypes'],
                'scaling_config': nodegroup['scalingConfig'],
                'created_at': nodegroup['createdAt'].isoformat(),
                'modified_at': nodegroup['modifiedAt'].isoformat(),
                'node_role': nodegroup['nodeRole'],
                'subnets': nodegroup['subnets'],
                'tags': nodegroup.get('tags', {})
            }
            
        except Exception as e:
            logger.error(f"Error getting node group status: {str(e)}")
            return {}
    
    def list_clusters(self) -> List[Dict[str, Any]]:
        """List all EKS clusters."""
        try:
            response = self.eks_client.list_clusters()
            
            clusters = []
            for cluster_name in response['clusters']:
                status = self.get_cluster_status(cluster_name)
                if status:
                    clusters.append(status)
            
            return clusters
            
        except Exception as e:
            logger.error(f"Error listing clusters: {str(e)}")
            return []
    
    def list_nodegroups(self, cluster_name: str) -> List[Dict[str, Any]]:
        """List all node groups for a cluster."""
        try:
            response = self.eks_client.list_nodegroups(clusterName=cluster_name)
            
            nodegroups = []
            for nodegroup_name in response['nodegroups']:
                status = self.get_nodegroup_status(cluster_name, nodegroup_name)
                if status:
                    nodegroups.append(status)
            
            return nodegroups
            
        except Exception as e:
            logger.error(f"Error listing node groups: {str(e)}")
            return []
    
    def delete_cluster(self, cluster_name: str) -> bool:
        """Delete EKS cluster."""
        try:
            # Delete all node groups first
            nodegroups = self.list_nodegroups(cluster_name)
            for nodegroup in nodegroups:
                self.delete_nodegroup(cluster_name, nodegroup['name'])
            
            # Delete cluster
            self.eks_client.delete_cluster(name=cluster_name)
            logger.info(f"Cluster {cluster_name} deletion initiated")
            return True
            
        except Exception as e:
            logger.error(f"Error deleting cluster: {str(e)}")
            return False
    
    def delete_nodegroup(self, cluster_name: str, nodegroup_name: str) -> bool:
        """Delete node group."""
        try:
            self.eks_client.delete_nodegroup(
                clusterName=cluster_name,
                nodegroupName=nodegroup_name
            )
            logger.info(f"Node group {nodegroup_name} deletion initiated")
            return True
            
        except Exception as e:
            logger.error(f"Error deleting node group: {str(e)}")
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
    """Main function for testing EKSClusterManager."""
    # Example usage
    cluster_manager = EKSClusterManager()
    
    # Example cluster configuration
    cluster_config = {
        'subnet_ids': ['subnet-12345', 'subnet-67890'],
        'kubernetes_version': '1.27',
        'endpoint_public_access': True,
        'endpoint_private_access': True,
        'enabled_log_types': ['api', 'audit', 'authenticator', 'controllerManager', 'scheduler'],
        'tags': {
            'Environment': 'production',
            'Project': 'my-project'
        }
    }
    
    # Create cluster
    cluster_arn = cluster_manager.create_cluster('my-eks-cluster', cluster_config)
    if cluster_arn:
        print(f"Cluster created: {cluster_arn}")
        
        # Create node group
        nodegroup_config = {
            'subnet_ids': ['subnet-12345', 'subnet-67890'],
            'instance_types': ['t3.medium'],
            'capacity_type': 'ON_DEMAND',
            'min_size': 1,
            'max_size': 3,
            'desired_size': 2
        }
        
        nodegroup_arn = cluster_manager.create_nodegroup('my-eks-cluster', 'my-nodegroup', nodegroup_config)
        if nodegroup_arn:
            print(f"Node group created: {nodegroup_arn}")
            
            # Update kubeconfig
            cluster_manager.update_kubeconfig('my-eks-cluster')
            
            # Get cluster status
            status = cluster_manager.get_cluster_status('my-eks-cluster')
            print(f"Cluster status: {json.dumps(status, indent=2, default=str)}")


if __name__ == "__main__":
    main()