#!/usr/bin/env python3
"""
Security Audit Module for AWS Infrastructure

This module performs comprehensive security auditing of AWS infrastructure
including IAM analysis, security group review, VPC configuration, and
encryption status checks.

Author: AWS Audit Framework
Version: 1.0.0
"""

import json
import logging
from datetime import datetime, timedelta
from typing import Dict, List, Any, Optional

import boto3
from botocore.exceptions import ClientError, NoCredentialsError


class SecurityAuditor:
    """
    Security Auditor class for AWS infrastructure security analysis.
    """
    
    def __init__(self, clients: Dict[str, Any], config: Dict[str, Any]):
        """
        Initialize the Security Auditor.
        
        Args:
            clients (Dict): AWS service clients
            config (Dict): Configuration dictionary
        """
        self.clients = clients
        self.config = config
        self.logger = logging.getLogger(__name__)
        
        # Initialize AWS clients
        self.iam_client = clients.get('iam')
        self.ec2_client = clients.get('ec2')
        self.s3_client = clients.get('s3')
        self.rds_client = clients.get('rds')
        self.kms_client = clients.get('kms')
        self.cloudtrail_client = clients.get('cloudtrail')
        self.guardduty_client = clients.get('guardduty')
        self.securityhub_client = clients.get('securityhub')
        
        # Initialize findings
        self.findings = []
        self.total_issues = 0
    
    def run_audit(self) -> Dict[str, Any]:
        """
        Run comprehensive security audit.
        
        Returns:
            Dict containing security audit results
        """
        self.logger.info("Starting security audit")
        
        try:
            audit_results = {
                'timestamp': datetime.now().isoformat(),
                'iam_analysis': self.audit_iam(),
                'security_groups': self.audit_security_groups(),
                'vpc_configuration': self.audit_vpc_configuration(),
                'encryption_status': self.audit_encryption_status(),
                'compliance_checks': self.audit_compliance_checks(),
                'findings': self.findings,
                'total_issues': self.total_issues,
                'summary': self._generate_security_summary()
            }
            
            self.logger.info(f"Security audit completed. Found {self.total_issues} issues.")
            return audit_results
            
        except Exception as e:
            self.logger.error(f"Security audit failed: {str(e)}")
            return {
                'error': str(e),
                'timestamp': datetime.now().isoformat()
            }
    
    def audit_iam(self) -> Dict[str, Any]:
        """
        Audit IAM users, roles, and policies.
        
        Returns:
            Dict containing IAM audit results
        """
        self.logger.info("Auditing IAM configuration")
        
        results = {
            'users': self.analyze_iam_users(),
            'roles': self.analyze_iam_roles(),
            'policies': self.analyze_iam_policies(),
            'access_keys': self.analyze_access_keys(),
            'mfa_status': self.analyze_mfa_status(),
            'password_policy': self.analyze_password_policy(),
            'root_account': self.analyze_root_account()
        }
        
        return results
    
    def analyze_iam_users(self) -> List[Dict[str, Any]]:
        """
        Analyze IAM users for security issues.
        
        Returns:
            List of user analysis results
        """
        if not self.iam_client:
            self.logger.warning("IAM client not available")
            return []
        
        try:
            users = self.iam_client.list_users()
            user_analysis = []
            
            for user in users['Users']:
                user_info = {
                    'username': user['UserName'],
                    'arn': user['Arn'],
                    'create_date': user['CreateDate'].isoformat(),
                    'password_last_used': user.get('PasswordLastUsed', {}).get('isoformat') if user.get('PasswordLastUsed') else None,
                    'mfa_enabled': self.check_mfa_enabled(user['UserName']),
                    'access_keys': self.get_user_access_keys(user['UserName']),
                    'attached_policies': self.get_attached_policies(user['UserName']),
                    'inline_policies': self.get_inline_policies(user['UserName']),
                    'groups': self.get_user_groups(user['UserName']),
                    'security_issues': []
                }
                
                # Check for security issues
                security_issues = self._check_user_security_issues(user_info)
                user_info['security_issues'] = security_issues
                self.total_issues += len(security_issues)
                
                user_analysis.append(user_info)
            
            return user_analysis
            
        except ClientError as e:
            self.logger.error(f"Error analyzing IAM users: {str(e)}")
            return []
    
    def analyze_iam_roles(self) -> List[Dict[str, Any]]:
        """
        Analyze IAM roles for security issues.
        
        Returns:
            List of role analysis results
        """
        if not self.iam_client:
            self.logger.warning("IAM client not available")
            return []
        
        try:
            roles = self.iam_client.list_roles()
            role_analysis = []
            
            for role in roles['Roles']:
                role_info = {
                    'role_name': role['RoleName'],
                    'arn': role['Arn'],
                    'create_date': role['CreateDate'].isoformat(),
                    'description': role.get('Description', ''),
                    'max_session_duration': role.get('MaxSessionDuration'),
                    'attached_policies': self.get_role_attached_policies(role['RoleName']),
                    'inline_policies': self.get_role_inline_policies(role['RoleName']),
                    'trust_policy': self.get_role_trust_policy(role['RoleName']),
                    'security_issues': []
                }
                
                # Check for security issues
                security_issues = self._check_role_security_issues(role_info)
                role_info['security_issues'] = security_issues
                self.total_issues += len(security_issues)
                
                role_analysis.append(role_info)
            
            return role_analysis
            
        except ClientError as e:
            self.logger.error(f"Error analyzing IAM roles: {str(e)}")
            return []
    
    def analyze_iam_policies(self) -> List[Dict[str, Any]]:
        """
        Analyze IAM policies for security issues.
        
        Returns:
            List of policy analysis results
        """
        if not self.iam_client:
            self.logger.warning("IAM client not available")
            return []
        
        try:
            policies = self.iam_client.list_policies(Scope='Local')
            policy_analysis = []
            
            for policy in policies['Policies']:
                policy_info = {
                    'policy_name': policy['PolicyName'],
                    'arn': policy['Arn'],
                    'create_date': policy['CreateDate'].isoformat(),
                    'update_date': policy['UpdateDate'].isoformat(),
                    'attachment_count': policy['AttachmentCount'],
                    'policy_document': self.get_policy_document(policy['Arn']),
                    'security_issues': []
                }
                
                # Check for security issues
                security_issues = self._check_policy_security_issues(policy_info)
                policy_info['security_issues'] = security_issues
                self.total_issues += len(security_issues)
                
                policy_analysis.append(policy_info)
            
            return policy_analysis
            
        except ClientError as e:
            self.logger.error(f"Error analyzing IAM policies: {str(e)}")
            return []
    
    def analyze_access_keys(self) -> List[Dict[str, Any]]:
        """
        Analyze access keys for security issues.
        
        Returns:
            List of access key analysis results
        """
        if not self.iam_client:
            self.logger.warning("IAM client not available")
            return []
        
        try:
            users = self.iam_client.list_users()
            access_key_analysis = []
            
            for user in users['Users']:
                try:
                    access_keys = self.iam_client.list_access_keys(UserName=user['UserName'])
                    
                    for key in access_keys['AccessKeyMetadata']:
                        key_info = {
                            'username': user['UserName'],
                            'access_key_id': key['AccessKeyId'],
                            'status': key['Status'],
                            'create_date': key['CreateDate'].isoformat(),
                            'last_used': self.get_access_key_last_used(key['AccessKeyId']),
                            'security_issues': []
                        }
                        
                        # Check for security issues
                        security_issues = self._check_access_key_security_issues(key_info)
                        key_info['security_issues'] = security_issues
                        self.total_issues += len(security_issues)
                        
                        access_key_analysis.append(key_info)
                        
                except ClientError as e:
                    self.logger.warning(f"Could not analyze access keys for user {user['UserName']}: {str(e)}")
                    continue
            
            return access_key_analysis
            
        except ClientError as e:
            self.logger.error(f"Error analyzing access keys: {str(e)}")
            return []
    
    def analyze_mfa_status(self) -> Dict[str, Any]:
        """
        Analyze MFA status across the account.
        
        Returns:
            Dict containing MFA analysis results
        """
        if not self.iam_client:
            self.logger.warning("IAM client not available")
            return {}
        
        try:
            users = self.iam_client.list_users()
            mfa_analysis = {
                'total_users': len(users['Users']),
                'mfa_enabled_users': 0,
                'mfa_disabled_users': 0,
                'users_without_mfa': [],
                'mfa_devices': {}
            }
            
            for user in users['Users']:
                try:
                    mfa_devices = self.iam_client.list_mfa_devices(UserName=user['UserName'])
                    
                    if mfa_devices['MFADevices']:
                        mfa_analysis['mfa_enabled_users'] += 1
                        mfa_analysis['mfa_devices'][user['UserName']] = mfa_devices['MFADevices']
                    else:
                        mfa_analysis['mfa_disabled_users'] += 1
                        mfa_analysis['users_without_mfa'].append(user['UserName'])
                        
                        # Add finding for users without MFA
                        self.findings.append({
                            'type': 'security',
                            'severity': 'high',
                            'category': 'iam',
                            'title': 'User without MFA',
                            'description': f"User {user['UserName']} does not have MFA enabled",
                            'resource': user['Arn'],
                            'recommendation': 'Enable MFA for all IAM users'
                        })
                        
                except ClientError as e:
                    self.logger.warning(f"Could not check MFA for user {user['UserName']}: {str(e)}")
                    continue
            
            return mfa_analysis
            
        except ClientError as e:
            self.logger.error(f"Error analyzing MFA status: {str(e)}")
            return {}
    
    def analyze_password_policy(self) -> Dict[str, Any]:
        """
        Analyze account password policy.
        
        Returns:
            Dict containing password policy analysis
        """
        if not self.iam_client:
            self.logger.warning("IAM client not available")
            return {}
        
        try:
            password_policy = self.iam_client.get_account_password_policy()
            policy = password_policy['PasswordPolicy']
            
            policy_analysis = {
                'minimum_password_length': policy.get('MinimumPasswordLength'),
                'require_symbols': policy.get('RequireSymbols'),
                'require_numbers': policy.get('RequireNumbers'),
                'require_uppercase_characters': policy.get('RequireUppercaseCharacters'),
                'require_lowercase_characters': policy.get('RequireLowercaseCharacters'),
                'allow_users_to_change_password': policy.get('AllowUsersToChangePassword'),
                'expire_passwords': policy.get('ExpirePasswords'),
                'max_password_age': policy.get('MaxPasswordAge'),
                'password_reuse_prevention': policy.get('PasswordReusePrevention'),
                'hard_expiry': policy.get('HardExpiry'),
                'security_issues': []
            }
            
            # Check for security issues
            security_issues = self._check_password_policy_issues(policy_analysis)
            policy_analysis['security_issues'] = security_issues
            self.total_issues += len(security_issues)
            
            return policy_analysis
            
        except ClientError as e:
            if e.response['Error']['Code'] == 'NoSuchEntity':
                # No password policy configured
                self.findings.append({
                    'type': 'security',
                    'severity': 'critical',
                    'category': 'iam',
                    'title': 'No password policy configured',
                    'description': 'Account does not have a password policy configured',
                    'resource': 'Account',
                    'recommendation': 'Configure a strong password policy'
                })
                return {'error': 'No password policy configured'}
            else:
                self.logger.error(f"Error analyzing password policy: {str(e)}")
                return {}
    
    def analyze_root_account(self) -> Dict[str, Any]:
        """
        Analyze root account security.
        
        Returns:
            Dict containing root account analysis
        """
        if not self.iam_client:
            self.logger.warning("IAM client not available")
            return {}
        
        try:
            account_summary = self.iam_client.get_account_summary()
            summary = account_summary['SummaryMap']
            
            root_analysis = {
                'access_keys_per_root': summary.get('AccessKeysPerUserQuota'),
                'account_access_keys_present': summary.get('AccountAccessKeysPresent'),
                'account_mfa_enabled': summary.get('AccountMFAEnabled'),
                'account_signing_certificates_present': summary.get('AccountSigningCertificatesPresent'),
                'attached_policies_per_group_quota': summary.get('AttachedPoliciesPerGroupQuota'),
                'attached_policies_per_role_quota': summary.get('AttachedPoliciesPerRoleQuota'),
                'attached_policies_per_user_quota': summary.get('AttachedPoliciesPerUserQuota'),
                'global_endpoint_token_version': summary.get('GlobalEndpointTokenVersion'),
                'group_policy_size_quota': summary.get('GroupPolicySizeQuota'),
                'groups': summary.get('Groups'),
                'groups_per_user_quota': summary.get('GroupsPerUserQuota'),
                'groups_quota': summary.get('GroupsQuota'),
                'mfa_devices': summary.get('MFADevices'),
                'mfa_devices_in_use': summary.get('MFADevicesInUse'),
                'policies': summary.get('Policies'),
                'policies_quota': summary.get('PoliciesQuota'),
                'policy_size_quota': summary.get('PolicySizeQuota'),
                'policy_versions_in_use': summary.get('PolicyVersionsInUse'),
                'policy_versions_in_use_quota': summary.get('PolicyVersionsInUseQuota'),
                'server_certificates': summary.get('ServerCertificates'),
                'server_certificates_quota': summary.get('ServerCertificatesQuota'),
                'signing_certificates_per_user_quota': summary.get('SigningCertificatesPerUserQuota'),
                'users': summary.get('Users'),
                'users_quota': summary.get('UsersQuota'),
                'versions_per_policy_quota': summary.get('VersionsPerPolicyQuota'),
                'security_issues': []
            }
            
            # Check for security issues
            security_issues = self._check_root_account_issues(root_analysis)
            root_analysis['security_issues'] = security_issues
            self.total_issues += len(security_issues)
            
            return root_analysis
            
        except ClientError as e:
            self.logger.error(f"Error analyzing root account: {str(e)}")
            return {}
    
    def audit_security_groups(self) -> List[Dict[str, Any]]:
        """
        Audit security groups for security issues.
        
        Returns:
            List of security group analysis results
        """
        if not self.ec2_client:
            self.logger.warning("EC2 client not available")
            return []
        
        try:
            security_groups = self.ec2_client.describe_security_groups()
            sg_analysis = []
            
            for sg in security_groups['SecurityGroups']:
                sg_info = {
                    'group_id': sg['GroupId'],
                    'group_name': sg['GroupName'],
                    'description': sg.get('Description', ''),
                    'vpc_id': sg['VpcId'],
                    'ingress_rules': sg['IpPermissions'],
                    'egress_rules': sg['IpPermissionsEgress'],
                    'security_issues': []
                }
                
                # Check for security issues
                security_issues = self._check_security_group_issues(sg_info)
                sg_info['security_issues'] = security_issues
                self.total_issues += len(security_issues)
                
                sg_analysis.append(sg_info)
            
            return sg_analysis
            
        except ClientError as e:
            self.logger.error(f"Error auditing security groups: {str(e)}")
            return []
    
    def audit_vpc_configuration(self) -> List[Dict[str, Any]]:
        """
        Audit VPC configuration for security issues.
        
        Returns:
            List of VPC analysis results
        """
        if not self.ec2_client:
            self.logger.warning("EC2 client not available")
            return []
        
        try:
            vpcs = self.ec2_client.describe_vpcs()
            vpc_analysis = []
            
            for vpc in vpcs['Vpcs']:
                vpc_info = {
                    'vpc_id': vpc['VpcId'],
                    'cidr_block': vpc['CidrBlock'],
                    'state': vpc['State'],
                    'is_default': vpc['IsDefault'],
                    'flow_logs': self.get_vpc_flow_logs(vpc['VpcId']),
                    'network_acls': self.get_vpc_network_acls(vpc['VpcId']),
                    'security_issues': []
                }
                
                # Check for security issues
                security_issues = self._check_vpc_security_issues(vpc_info)
                vpc_info['security_issues'] = security_issues
                self.total_issues += len(security_issues)
                
                vpc_analysis.append(vpc_info)
            
            return vpc_analysis
            
        except ClientError as e:
            self.logger.error(f"Error auditing VPC configuration: {str(e)}")
            return []
    
    def audit_encryption_status(self) -> Dict[str, Any]:
        """
        Audit encryption status across AWS services.
        
        Returns:
            Dict containing encryption analysis results
        """
        encryption_analysis = {
            's3_buckets': self.audit_s3_encryption(),
            'ebs_volumes': self.audit_ebs_encryption(),
            'rds_instances': self.audit_rds_encryption(),
            'kms_keys': self.audit_kms_keys(),
            'security_issues': []
        }
        
        # Check for security issues
        security_issues = self._check_encryption_issues(encryption_analysis)
        encryption_analysis['security_issues'] = security_issues
        self.total_issues += len(security_issues)
        
        return encryption_analysis
    
    def audit_s3_encryption(self) -> List[Dict[str, Any]]:
        """
        Audit S3 bucket encryption.
        
        Returns:
            List of S3 encryption analysis results
        """
        if not self.s3_client:
            self.logger.warning("S3 client not available")
            return []
        
        try:
            buckets = self.s3_client.list_buckets()
            s3_encryption_analysis = []
            
            for bucket in buckets['Buckets']:
                try:
                    encryption = self.s3_client.get_bucket_encryption(Bucket=bucket['Name'])
                    encryption_info = {
                        'bucket_name': bucket['Name'],
                        'encryption_enabled': True,
                        'encryption_config': encryption.get('ServerSideEncryptionConfiguration', {}),
                        'security_issues': []
                    }
                except ClientError as e:
                    if e.response['Error']['Code'] == 'ServerSideEncryptionConfigurationNotFoundError':
                        encryption_info = {
                            'bucket_name': bucket['Name'],
                            'encryption_enabled': False,
                            'encryption_config': {},
                            'security_issues': [{
                                'type': 'security',
                                'severity': 'high',
                                'category': 'encryption',
                                'title': 'S3 bucket not encrypted',
                                'description': f"Bucket {bucket['Name']} does not have server-side encryption enabled",
                                'resource': bucket['Name'],
                                'recommendation': 'Enable server-side encryption for the bucket'
                            }]
                        }
                    else:
                        self.logger.warning(f"Could not check encryption for bucket {bucket['Name']}: {str(e)}")
                        continue
                
                s3_encryption_analysis.append(encryption_info)
            
            return s3_encryption_analysis
            
        except ClientError as e:
            self.logger.error(f"Error auditing S3 encryption: {str(e)}")
            return []
    
    def audit_ebs_encryption(self) -> List[Dict[str, Any]]:
        """
        Audit EBS volume encryption.
        
        Returns:
            List of EBS encryption analysis results
        """
        if not self.ec2_client:
            self.logger.warning("EC2 client not available")
            return []
        
        try:
            volumes = self.ec2_client.describe_volumes()
            ebs_encryption_analysis = []
            
            for volume in volumes['Volumes']:
                encryption_info = {
                    'volume_id': volume['VolumeId'],
                    'encrypted': volume['Encrypted'],
                    'kms_key_id': volume.get('KmsKeyId'),
                    'volume_type': volume['VolumeType'],
                    'state': volume['State'],
                    'security_issues': []
                }
                
                if not volume['Encrypted']:
                    encryption_info['security_issues'].append({
                        'type': 'security',
                        'severity': 'high',
                        'category': 'encryption',
                        'title': 'EBS volume not encrypted',
                        'description': f"Volume {volume['VolumeId']} is not encrypted",
                        'resource': volume['VolumeId'],
                        'recommendation': 'Enable encryption for the EBS volume'
                    })
                
                ebs_encryption_analysis.append(encryption_info)
            
            return ebs_encryption_analysis
            
        except ClientError as e:
            self.logger.error(f"Error auditing EBS encryption: {str(e)}")
            return []
    
    def audit_rds_encryption(self) -> List[Dict[str, Any]]:
        """
        Audit RDS instance encryption.
        
        Returns:
            List of RDS encryption analysis results
        """
        if not self.rds_client:
            self.logger.warning("RDS client not available")
            return []
        
        try:
            instances = self.rds_client.describe_db_instances()
            rds_encryption_analysis = []
            
            for instance in instances['DBInstances']:
                encryption_info = {
                    'db_instance_identifier': instance['DBInstanceIdentifier'],
                    'storage_encrypted': instance['StorageEncrypted'],
                    'kms_key_id': instance.get('KmsKeyId'),
                    'engine': instance['Engine'],
                    'db_instance_class': instance['DBInstanceClass'],
                    'security_issues': []
                }
                
                if not instance['StorageEncrypted']:
                    encryption_info['security_issues'].append({
                        'type': 'security',
                        'severity': 'high',
                        'category': 'encryption',
                        'title': 'RDS instance not encrypted',
                        'description': f"RDS instance {instance['DBInstanceIdentifier']} storage is not encrypted",
                        'resource': instance['DBInstanceIdentifier'],
                        'recommendation': 'Enable storage encryption for the RDS instance'
                    })
                
                rds_encryption_analysis.append(encryption_info)
            
            return rds_encryption_analysis
            
        except ClientError as e:
            self.logger.error(f"Error auditing RDS encryption: {str(e)}")
            return []
    
    def audit_kms_keys(self) -> List[Dict[str, Any]]:
        """
        Audit KMS keys.
        
        Returns:
            List of KMS key analysis results
        """
        if not self.kms_client:
            self.logger.warning("KMS client not available")
            return []
        
        try:
            keys = self.kms_client.list_keys()
            kms_analysis = []
            
            for key in keys['Keys']:
                try:
                    key_description = self.kms_client.describe_key(KeyId=key['KeyId'])
                    key_info = key_description['KeyMetadata']
                    
                    key_analysis = {
                        'key_id': key_info['KeyId'],
                        'arn': key_info['Arn'],
                        'description': key_info.get('Description', ''),
                        'key_state': key_info['KeyState'],
                        'key_usage': key_info['KeyUsage'],
                        'origin': key_info['Origin'],
                        'creation_date': key_info['CreationDate'].isoformat(),
                        'enabled': key_info['Enabled'],
                        'key_manager': key_info['KeyManager'],
                        'security_issues': []
                    }
                    
                    # Check for security issues
                    security_issues = self._check_kms_key_issues(key_analysis)
                    key_analysis['security_issues'] = security_issues
                    
                    kms_analysis.append(key_analysis)
                    
                except ClientError as e:
                    self.logger.warning(f"Could not describe key {key['KeyId']}: {str(e)}")
                    continue
            
            return kms_analysis
            
        except ClientError as e:
            self.logger.error(f"Error auditing KMS keys: {str(e)}")
            return []
    
    def audit_compliance_checks(self) -> Dict[str, Any]:
        """
        Audit compliance with security standards.
        
        Returns:
            Dict containing compliance analysis results
        """
        compliance_analysis = {
            'cis_benchmarks': self.check_cis_benchmarks(),
            'security_hub_findings': self.get_security_hub_findings(),
            'guardduty_findings': self.get_guardduty_findings(),
            'cloudtrail_status': self.check_cloudtrail_status()
        }
        
        return compliance_analysis
    
    # Helper methods for IAM analysis
    def check_mfa_enabled(self, username: str) -> bool:
        """Check if MFA is enabled for a user."""
        try:
            mfa_devices = self.iam_client.list_mfa_devices(UserName=username)
            return len(mfa_devices['MFADevices']) > 0
        except ClientError:
            return False
    
    def get_user_access_keys(self, username: str) -> List[Dict[str, Any]]:
        """Get access keys for a user."""
        try:
            access_keys = self.iam_client.list_access_keys(UserName=username)
            return access_keys['AccessKeyMetadata']
        except ClientError:
            return []
    
    def get_attached_policies(self, username: str) -> List[Dict[str, Any]]:
        """Get attached policies for a user."""
        try:
            policies = self.iam_client.list_attached_user_policies(UserName=username)
            return policies['AttachedPolicies']
        except ClientError:
            return []
    
    def get_inline_policies(self, username: str) -> List[str]:
        """Get inline policies for a user."""
        try:
            policies = self.iam_client.list_user_policies(UserName=username)
            return policies['PolicyNames']
        except ClientError:
            return []
    
    def get_user_groups(self, username: str) -> List[Dict[str, Any]]:
        """Get groups for a user."""
        try:
            groups = self.iam_client.list_groups_for_user(UserName=username)
            return groups['Groups']
        except ClientError:
            return []
    
    def get_role_attached_policies(self, role_name: str) -> List[Dict[str, Any]]:
        """Get attached policies for a role."""
        try:
            policies = self.iam_client.list_attached_role_policies(RoleName=role_name)
            return policies['AttachedPolicies']
        except ClientError:
            return []
    
    def get_role_inline_policies(self, role_name: str) -> List[str]:
        """Get inline policies for a role."""
        try:
            policies = self.iam_client.list_role_policies(RoleName=role_name)
            return policies['PolicyNames']
        except ClientError:
            return []
    
    def get_role_trust_policy(self, role_name: str) -> Dict[str, Any]:
        """Get trust policy for a role."""
        try:
            role = self.iam_client.get_role(RoleName=role_name)
            return role['Role']['AssumeRolePolicyDocument']
        except ClientError:
            return {}
    
    def get_policy_document(self, policy_arn: str) -> Dict[str, Any]:
        """Get policy document for a policy."""
        try:
            policy_version = self.iam_client.get_policy_version(
                PolicyArn=policy_arn,
                VersionId=self.iam_client.get_policy(PolicyArn=policy_arn)['Policy']['DefaultVersionId']
            )
            return policy_version['PolicyVersion']['Document']
        except ClientError:
            return {}
    
    def get_access_key_last_used(self, access_key_id: str) -> Dict[str, Any]:
        """Get last used information for an access key."""
        try:
            last_used = self.iam_client.get_access_key_last_used(AccessKeyId=access_key_id)
            return last_used.get('AccessKeyLastUsed', {})
        except ClientError:
            return {}
    
    # Helper methods for VPC analysis
    def get_vpc_flow_logs(self, vpc_id: str) -> List[Dict[str, Any]]:
        """Get flow logs for a VPC."""
        try:
            flow_logs = self.ec2_client.describe_flow_logs(
                Filters=[{'Name': 'resource-id', 'Values': [vpc_id]}]
            )
            return flow_logs['FlowLogs']
        except ClientError:
            return []
    
    def get_vpc_network_acls(self, vpc_id: str) -> List[Dict[str, Any]]:
        """Get network ACLs for a VPC."""
        try:
            network_acls = self.ec2_client.describe_network_acls(
                Filters=[{'Name': 'vpc-id', 'Values': [vpc_id]}]
            )
            return network_acls['NetworkAcls']
        except ClientError:
            return []
    
    # Security issue checking methods
    def _check_user_security_issues(self, user_info: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Check for security issues in user configuration."""
        issues = []
        
        # Check for users without MFA
        if not user_info['mfa_enabled']:
            issues.append({
                'type': 'security',
                'severity': 'high',
                'category': 'iam',
                'title': 'User without MFA',
                'description': f"User {user_info['username']} does not have MFA enabled",
                'resource': user_info['arn'],
                'recommendation': 'Enable MFA for the user'
            })
        
        # Check for inactive access keys
        for key in user_info['access_keys']:
            if key['Status'] == 'Active':
                last_used = user_info.get('access_keys_last_used', {}).get(key['AccessKeyId'])
                if last_used:
                    last_used_date = datetime.fromisoformat(last_used['LastUsedDate'].replace('Z', '+00:00'))
                    if (datetime.now(last_used_date.tzinfo) - last_used_date).days > 90:
                        issues.append({
                            'type': 'security',
                            'severity': 'medium',
                            'category': 'iam',
                            'title': 'Inactive access key',
                            'description': f"Access key {key['AccessKeyId']} has not been used for more than 90 days",
                            'resource': key['AccessKeyId'],
                            'recommendation': 'Remove or rotate the access key'
                        })
        
        return issues
    
    def _check_role_security_issues(self, role_info: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Check for security issues in role configuration."""
        issues = []
        
        # Check for overly permissive trust policies
        trust_policy = role_info.get('trust_policy', {})
        if trust_policy:
            statements = trust_policy.get('Statement', [])
            for statement in statements:
                principal = statement.get('Principal', {})
                if principal.get('AWS') == '*':
                    issues.append({
                        'type': 'security',
                        'severity': 'critical',
                        'category': 'iam',
                        'title': 'Overly permissive trust policy',
                        'description': f"Role {role_info['role_name']} has a trust policy that allows any AWS account",
                        'resource': role_info['arn'],
                        'recommendation': 'Restrict the trust policy to specific accounts or services'
                    })
        
        return issues
    
    def _check_policy_security_issues(self, policy_info: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Check for security issues in policy configuration."""
        issues = []
        
        # Check for overly permissive policies
        policy_document = policy_info.get('policy_document', {})
        if policy_document:
            statements = policy_document.get('Statement', [])
            for statement in statements:
                if statement.get('Effect') == 'Allow':
                    action = statement.get('Action', [])
                    resource = statement.get('Resource', [])
                    
                    if isinstance(action, str):
                        action = [action]
                    if isinstance(resource, str):
                        resource = [resource]
                    
                    # Check for wildcard permissions
                    if '*' in action or any('*' in a for a in action):
                        if '*' in resource or any('*' in r for r in resource):
                            issues.append({
                                'type': 'security',
                                'severity': 'high',
                                'category': 'iam',
                                'title': 'Overly permissive policy',
                                'description': f"Policy {policy_info['policy_name']} allows all actions on all resources",
                                'resource': policy_info['arn'],
                                'recommendation': 'Restrict the policy to specific actions and resources'
                            })
        
        return issues
    
    def _check_access_key_security_issues(self, key_info: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Check for security issues in access key configuration."""
        issues = []
        
        # Check for old access keys
        if key_info['status'] == 'Active':
            create_date = datetime.fromisoformat(key_info['create_date'].replace('Z', '+00:00'))
            if (datetime.now(create_date.tzinfo) - create_date).days > 365:
                issues.append({
                    'type': 'security',
                    'severity': 'medium',
                    'category': 'iam',
                    'title': 'Old access key',
                    'description': f"Access key {key_info['access_key_id']} is more than 1 year old",
                    'resource': key_info['access_key_id'],
                    'recommendation': 'Rotate the access key'
                })
        
        return issues
    
    def _check_password_policy_issues(self, policy_info: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Check for security issues in password policy."""
        issues = []
        
        # Check minimum password length
        if policy_info.get('minimum_password_length', 0) < 12:
            issues.append({
                'type': 'security',
                'severity': 'medium',
                'category': 'iam',
                'title': 'Weak password policy',
                'description': 'Minimum password length is less than 12 characters',
                'resource': 'Account',
                'recommendation': 'Increase minimum password length to at least 12 characters'
            })
        
        # Check for required complexity
        if not policy_info.get('require_symbols'):
            issues.append({
                'type': 'security',
                'severity': 'medium',
                'category': 'iam',
                'title': 'Weak password policy',
                'description': 'Password policy does not require symbols',
                'resource': 'Account',
                'recommendation': 'Enable symbol requirement in password policy'
            })
        
        return issues
    
    def _check_root_account_issues(self, root_info: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Check for security issues in root account."""
        issues = []
        
        # Check for root access keys
        if root_info.get('account_access_keys_present', 0) > 0:
            issues.append({
                'type': 'security',
                'severity': 'critical',
                'category': 'iam',
                'title': 'Root access keys present',
                'description': 'Root account has access keys configured',
                'resource': 'Account',
                'recommendation': 'Remove all root access keys'
            })
        
        # Check for root MFA
        if not root_info.get('account_mfa_enabled'):
            issues.append({
                'type': 'security',
                'severity': 'critical',
                'category': 'iam',
                'title': 'Root account without MFA',
                'description': 'Root account does not have MFA enabled',
                'resource': 'Account',
                'recommendation': 'Enable MFA for root account'
            })
        
        return issues
    
    def _check_security_group_issues(self, sg_info: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Check for security issues in security group configuration."""
        issues = []
        
        # Check for overly permissive ingress rules
        for rule in sg_info['ingress_rules']:
            if rule.get('IpProtocol') == '-1':  # All protocols
                for ip_range in rule.get('IpRanges', []):
                    if ip_range.get('CidrIp') == '0.0.0.0/0':
                        issues.append({
                            'type': 'security',
                            'severity': 'high',
                            'category': 'network',
                            'title': 'Overly permissive security group',
                            'description': f"Security group {sg_info['group_name']} allows all traffic from anywhere",
                            'resource': sg_info['group_id'],
                            'recommendation': 'Restrict the security group rules to specific IP ranges and ports'
                        })
        
        return issues
    
    def _check_vpc_security_issues(self, vpc_info: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Check for security issues in VPC configuration."""
        issues = []
        
        # Check for flow logs
        if not vpc_info['flow_logs']:
            issues.append({
                'type': 'security',
                'severity': 'medium',
                'category': 'network',
                'title': 'VPC without flow logs',
                'description': f"VPC {vpc_info['vpc_id']} does not have flow logs enabled",
                'resource': vpc_info['vpc_id'],
                'recommendation': 'Enable VPC flow logs for network monitoring'
            })
        
        return issues
    
    def _check_encryption_issues(self, encryption_info: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Check for encryption-related security issues."""
        issues = []
        
        # Check for unencrypted S3 buckets
        for bucket in encryption_info.get('s3_buckets', []):
            if not bucket.get('encryption_enabled'):
                issues.append({
                    'type': 'security',
                    'severity': 'high',
                    'category': 'encryption',
                    'title': 'Unencrypted S3 bucket',
                    'description': f"Bucket {bucket['bucket_name']} is not encrypted",
                    'resource': bucket['bucket_name'],
                    'recommendation': 'Enable server-side encryption for the bucket'
                })
        
        # Check for unencrypted EBS volumes
        for volume in encryption_info.get('ebs_volumes', []):
            if not volume.get('encrypted'):
                issues.append({
                    'type': 'security',
                    'severity': 'high',
                    'category': 'encryption',
                    'title': 'Unencrypted EBS volume',
                    'description': f"Volume {volume['volume_id']} is not encrypted",
                    'resource': volume['volume_id'],
                    'recommendation': 'Enable encryption for the EBS volume'
                })
        
        return issues
    
    def _check_kms_key_issues(self, key_info: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Check for security issues in KMS key configuration."""
        issues = []
        
        # Check for disabled keys
        if not key_info.get('enabled'):
            issues.append({
                'type': 'security',
                'severity': 'medium',
                'category': 'encryption',
                'title': 'Disabled KMS key',
                'description': f"KMS key {key_info['key_id']} is disabled",
                'resource': key_info['key_id'],
                'recommendation': 'Enable the KMS key if it is still needed'
            })
        
        return issues
    
    # Compliance checking methods
    def check_cis_benchmarks(self) -> Dict[str, Any]:
        """Check CIS benchmark compliance."""
        # This would integrate with AWS Config or Security Hub
        return {'status': 'not_implemented'}
    
    def get_security_hub_findings(self) -> List[Dict[str, Any]]:
        """Get Security Hub findings."""
        if not self.securityhub_client:
            return []
        
        try:
            findings = self.securityhub_client.get_findings()
            return findings.get('Findings', [])
        except ClientError:
            return []
    
    def get_guardduty_findings(self) -> List[Dict[str, Any]]:
        """Get GuardDuty findings."""
        if not self.guardduty_client:
            return []
        
        try:
            findings = self.guardduty_client.list_findings()
            return findings.get('FindingIds', [])
        except ClientError:
            return []
    
    def check_cloudtrail_status(self) -> Dict[str, Any]:
        """Check CloudTrail status."""
        if not self.cloudtrail_client:
            return {'status': 'not_available'}
        
        try:
            trails = self.cloudtrail_client.list_trails()
            return {
                'status': 'available',
                'trails': trails.get('Trails', [])
            }
        except ClientError:
            return {'status': 'error'}
    
    def _generate_security_summary(self) -> Dict[str, Any]:
        """Generate a summary of security audit results."""
        summary = {
            'total_security_issues': self.total_issues,
            'critical_issues': len([f for f in self.findings if f.get('severity') == 'critical']),
            'high_issues': len([f for f in self.findings if f.get('severity') == 'high']),
            'medium_issues': len([f for f in self.findings if f.get('severity') == 'medium']),
            'low_issues': len([f for f in self.findings if f.get('severity') == 'low']),
            'categories': {}
        }
        
        # Count issues by category
        for finding in self.findings:
            category = finding.get('category', 'unknown')
            if category not in summary['categories']:
                summary['categories'][category] = 0
            summary['categories'][category] += 1
        
        return summary
