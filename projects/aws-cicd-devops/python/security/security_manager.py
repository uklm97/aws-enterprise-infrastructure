#!/usr/bin/env python3
"""
AWS CI/CD Security Manager for security scanning and compliance.

This module provides comprehensive security capabilities including
vulnerability scanning, compliance checks, and security monitoring.
"""

import boto3
import subprocess
import logging
import json
import os
import time
from typing import List, Dict, Any, Optional
from datetime import datetime
import yaml

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class SecurityManager:
    """
    AWS CI/CD Security Manager for security scanning and compliance.
    """
    
    def __init__(self, region: str = 'us-east-1'):
        """Initialize SecurityManager with AWS clients."""
        self.region = region
        self.ecr_client = boto3.client('ecr', region_name=region)
        self.inspector_client = boto3.client('inspector2', region_name=region)
        self.securityhub_client = boto3.client('securityhub', region_name=region)
        self.guardduty_client = boto3.client('guardduty', region_name=region)
        self.s3_client = boto3.client('s3', region_name=region)
        self.iam_client = boto3.client('iam', region_name=region)
        
    def scan_container_image(self, repository_name: str, image_tag: str) -> Dict[str, Any]:
        """Scan container image for vulnerabilities."""
        try:
            logger.info(f"Scanning container image {repository_name}:{image_tag}")
            
            # Start image scan
            response = self.ecr_client.start_image_scan(
                repositoryName=repository_name,
                imageId={'imageTag': image_tag}
            )
            
            # Wait for scan to complete
            scan_results = self._wait_for_scan_completion(repository_name, image_tag)
            
            # Get detailed findings
            findings = self._get_scan_findings(repository_name, image_tag)
            
            result = {
                'repository_name': repository_name,
                'image_tag': image_tag,
                'scan_status': scan_results.get('imageScanStatus', {}).get('status'),
                'findings': findings,
                'timestamp': datetime.now().isoformat()
            }
            
            logger.info(f"Container scan completed for {repository_name}:{image_tag}")
            return result
            
        except Exception as e:
            logger.error(f"Error scanning container image: {str(e)}")
            return {'error': str(e)}
    
    def _wait_for_scan_completion(self, repository_name: str, image_tag: str, timeout: int = 1800) -> Dict[str, Any]:
        """Wait for image scan to complete."""
        start_time = time.time()
        
        while time.time() - start_time < timeout:
            try:
                response = self.ecr_client.describe_image_scan_findings(
                    repositoryName=repository_name,
                    imageId={'imageTag': image_tag}
                )
                
                scan_status = response.get('imageScanStatus', {}).get('status')
                
                if scan_status == 'COMPLETE':
                    return response
                elif scan_status == 'FAILED':
                    return {'error': 'Scan failed'}
                
                time.sleep(30)
                
            except Exception as e:
                logger.error(f"Error checking scan status: {str(e)}")
                return {'error': str(e)}
        
        return {'error': 'Scan timeout'}
    
    def _get_scan_findings(self, repository_name: str, image_tag: str) -> List[Dict[str, Any]]:
        """Get detailed scan findings."""
        try:
            response = self.ecr_client.describe_image_scan_findings(
                repositoryName=repository_name,
                imageId={'imageTag': image_tag}
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
            
            return processed_findings
            
        except Exception as e:
            logger.error(f"Error getting scan findings: {str(e)}")
            return []
    
    def run_dependency_scan(self, project_path: str) -> Dict[str, Any]:
        """Run dependency vulnerability scan."""
        try:
            logger.info(f"Running dependency scan in {project_path}")
            
            # Change to project directory
            original_dir = os.getcwd()
            os.chdir(project_path)
            
            # Run safety check
            safety_result = self._run_safety_scan()
            
            # Run pip-audit
            pip_audit_result = self._run_pip_audit()
            
            # Run npm audit if package.json exists
            npm_audit_result = self._run_npm_audit()
            
            os.chdir(original_dir)
            
            return {
                'safety': safety_result,
                'pip_audit': pip_audit_result,
                'npm_audit': npm_audit_result,
                'timestamp': datetime.now().isoformat()
            }
            
        except Exception as e:
            logger.error(f"Error running dependency scan: {str(e)}")
            return {'error': str(e)}
    
    def _run_safety_scan(self) -> Dict[str, Any]:
        """Run safety dependency scan."""
        try:
            result = subprocess.run(
                ['safety', 'check', '--json'],
                capture_output=True,
                text=True,
                timeout=300
            )
            
            if result.returncode == 0:
                return {'status': 'passed', 'vulnerabilities': []}
            else:
                try:
                    vulnerabilities = json.loads(result.stdout)
                    return {
                        'status': 'failed',
                        'vulnerabilities': vulnerabilities,
                        'return_code': result.returncode
                    }
                except json.JSONDecodeError:
                    return {
                        'status': 'error',
                        'error': result.stderr,
                        'return_code': result.returncode
                    }
        except subprocess.TimeoutExpired:
            return {'status': 'timeout', 'error': 'Safety scan timed out'}
        except Exception as e:
            return {'status': 'error', 'error': str(e)}
    
    def _run_pip_audit(self) -> Dict[str, Any]:
        """Run pip-audit dependency scan."""
        try:
            result = subprocess.run(
                ['pip-audit', '--format=json'],
                capture_output=True,
                text=True,
                timeout=300
            )
            
            if result.returncode == 0:
                return {'status': 'passed', 'vulnerabilities': []}
            else:
                try:
                    vulnerabilities = json.loads(result.stdout)
                    return {
                        'status': 'failed',
                        'vulnerabilities': vulnerabilities,
                        'return_code': result.returncode
                    }
                except json.JSONDecodeError:
                    return {
                        'status': 'error',
                        'error': result.stderr,
                        'return_code': result.returncode
                    }
        except subprocess.TimeoutExpired:
            return {'status': 'timeout', 'error': 'Pip-audit scan timed out'}
        except Exception as e:
            return {'status': 'error', 'error': str(e)}
    
    def _run_npm_audit(self) -> Dict[str, Any]:
        """Run npm audit dependency scan."""
        try:
            if not os.path.exists('package.json'):
                return {'status': 'skipped', 'message': 'No package.json found'}
            
            result = subprocess.run(
                ['npm', 'audit', '--json'],
                capture_output=True,
                text=True,
                timeout=300
            )
            
            try:
                audit_data = json.loads(result.stdout)
                return {
                    'status': 'completed',
                    'vulnerabilities': audit_data.get('vulnerabilities', {}),
                    'metadata': audit_data.get('metadata', {}),
                    'return_code': result.returncode
                }
            except json.JSONDecodeError:
                return {
                    'status': 'error',
                    'error': result.stderr,
                    'return_code': result.returncode
                }
        except subprocess.TimeoutExpired:
            return {'status': 'timeout', 'error': 'NPM audit timed out'}
        except Exception as e:
            return {'status': 'error', 'error': str(e)}
    
    def run_static_code_analysis(self, project_path: str) -> Dict[str, Any]:
        """Run static code analysis for security issues."""
        try:
            logger.info(f"Running static code analysis in {project_path}")
            
            # Change to project directory
            original_dir = os.getcwd()
            os.chdir(project_path)
            
            # Run bandit
            bandit_result = self._run_bandit_scan()
            
            # Run semgrep
            semgrep_result = self._run_semgrep_scan()
            
            # Run sonarqube if available
            sonarqube_result = self._run_sonarqube_scan()
            
            os.chdir(original_dir)
            
            return {
                'bandit': bandit_result,
                'semgrep': semgrep_result,
                'sonarqube': sonarqube_result,
                'timestamp': datetime.now().isoformat()
            }
            
        except Exception as e:
            logger.error(f"Error running static code analysis: {str(e)}")
            return {'error': str(e)}
    
    def _run_bandit_scan(self) -> Dict[str, Any]:
        """Run bandit security linter."""
        try:
            result = subprocess.run(
                ['bandit', '-r', '.', '-f', 'json'],
                capture_output=True,
                text=True,
                timeout=300
            )
            
            if result.returncode == 0:
                return {'status': 'passed', 'issues': []}
            else:
                try:
                    issues = json.loads(result.stdout)
                    return {
                        'status': 'failed',
                        'issues': issues,
                        'return_code': result.returncode
                    }
                except json.JSONDecodeError:
                    return {
                        'status': 'error',
                        'error': result.stderr,
                        'return_code': result.returncode
                    }
        except subprocess.TimeoutExpired:
            return {'status': 'timeout', 'error': 'Bandit scan timed out'}
        except Exception as e:
            return {'status': 'error', 'error': str(e)}
    
    def _run_semgrep_scan(self) -> Dict[str, Any]:
        """Run semgrep static analysis."""
        try:
            result = subprocess.run(
                ['semgrep', '--config=auto', '--json', '.'],
                capture_output=True,
                text=True,
                timeout=300
            )
            
            if result.returncode == 0:
                return {'status': 'passed', 'findings': []}
            else:
                try:
                    findings = json.loads(result.stdout)
                    return {
                        'status': 'failed',
                        'findings': findings,
                        'return_code': result.returncode
                    }
                except json.JSONDecodeError:
                    return {
                        'status': 'error',
                        'error': result.stderr,
                        'return_code': result.returncode
                    }
        except subprocess.TimeoutExpired:
            return {'status': 'timeout', 'error': 'Semgrep scan timed out'}
        except Exception as e:
            return {'status': 'error', 'error': str(e)}
    
    def _run_sonarqube_scan(self) -> Dict[str, Any]:
        """Run SonarQube scan if available."""
        try:
            # Check if sonar-scanner is available
            result = subprocess.run(
                ['sonar-scanner', '--version'],
                capture_output=True,
                text=True,
                timeout=30
            )
            
            if result.returncode != 0:
                return {'status': 'skipped', 'message': 'SonarQube scanner not available'}
            
            # Run sonar-scanner
            result = subprocess.run(
                ['sonar-scanner'],
                capture_output=True,
                text=True,
                timeout=600
            )
            
            return {
                'status': 'completed',
                'return_code': result.returncode,
                'stdout': result.stdout,
                'stderr': result.stderr
            }
            
        except subprocess.TimeoutExpired:
            return {'status': 'timeout', 'error': 'SonarQube scan timed out'}
        except Exception as e:
            return {'status': 'error', 'error': str(e)}
    
    def check_iam_permissions(self, role_name: str) -> Dict[str, Any]:
        """Check IAM role permissions for security issues."""
        try:
            logger.info(f"Checking IAM permissions for role: {role_name}")
            
            # Get role policies
            attached_policies = self.iam_client.list_attached_role_policies(RoleName=role_name)
            inline_policies = self.iam_client.list_role_policies(RoleName=role_name)
            
            # Analyze policies for security issues
            security_issues = []
            
            # Check for overly permissive policies
            for policy in attached_policies['AttachedPolicies']:
                policy_doc = self.iam_client.get_policy(PolicyArn=policy['PolicyArn'])
                policy_version = self.iam_client.get_policy_version(
                    PolicyArn=policy['PolicyArn'],
                    VersionId=policy_doc['Policy']['DefaultVersionId']
                )
                
                issues = self._analyze_policy_document(policy_version['PolicyVersion']['Document'])
                security_issues.extend(issues)
            
            # Check inline policies
            for policy_name in inline_policies['PolicyNames']:
                policy_doc = self.iam_client.get_role_policy(
                    RoleName=role_name,
                    PolicyName=policy_name
                )
                
                issues = self._analyze_policy_document(policy_doc['PolicyDocument'])
                security_issues.extend(issues)
            
            return {
                'role_name': role_name,
                'security_issues': security_issues,
                'attached_policies': [p['PolicyName'] for p in attached_policies['AttachedPolicies']],
                'inline_policies': inline_policies['PolicyNames'],
                'timestamp': datetime.now().isoformat()
            }
            
        except Exception as e:
            logger.error(f"Error checking IAM permissions: {str(e)}")
            return {'error': str(e)}
    
    def _analyze_policy_document(self, policy_doc: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Analyze IAM policy document for security issues."""
        issues = []
        
        try:
            statements = policy_doc.get('Statement', [])
            
            for statement in statements:
                # Check for wildcard permissions
                if statement.get('Effect') == 'Allow':
                    actions = statement.get('Action', [])
                    resources = statement.get('Resource', [])
                    
                    # Check for wildcard actions
                    if '*' in actions or 's3:*' in actions:
                        issues.append({
                            'type': 'wildcard_action',
                            'severity': 'high',
                            'message': 'Policy contains wildcard actions',
                            'statement': statement
                        })
                    
                    # Check for wildcard resources
                    if '*' in resources:
                        issues.append({
                            'type': 'wildcard_resource',
                            'severity': 'high',
                            'message': 'Policy contains wildcard resources',
                            'statement': statement
                        })
                    
                    # Check for overly permissive S3 actions
                    s3_permissive_actions = ['s3:GetObject', 's3:PutObject', 's3:DeleteObject']
                    if any(action in actions for action in s3_permissive_actions):
                        if '*' in resources or 'arn:aws:s3:::*' in resources:
                            issues.append({
                                'type': 's3_wildcard_access',
                                'severity': 'critical',
                                'message': 'Policy allows S3 access to all resources',
                                'statement': statement
                            })
            
        except Exception as e:
            logger.error(f"Error analyzing policy document: {str(e)}")
            issues.append({
                'type': 'analysis_error',
                'severity': 'medium',
                'message': f'Error analyzing policy: {str(e)}'
            })
        
        return issues
    
    def run_compliance_check(self, compliance_standard: str = 'CIS') -> Dict[str, Any]:
        """Run compliance check against security standards."""
        try:
            logger.info(f"Running compliance check for {compliance_standard}")
            
            compliance_results = {
                'standard': compliance_standard,
                'checks': [],
                'timestamp': datetime.now().isoformat()
            }
            
            if compliance_standard.upper() == 'CIS':
                compliance_results['checks'] = self._run_cis_checks()
            elif compliance_standard.upper() == 'NIST':
                compliance_results['checks'] = self._run_nist_checks()
            elif compliance_standard.upper() == 'SOC2':
                compliance_results['checks'] = self._run_soc2_checks()
            else:
                compliance_results['error'] = f'Unsupported compliance standard: {compliance_standard}'
            
            return compliance_results
            
        except Exception as e:
            logger.error(f"Error running compliance check: {str(e)}")
            return {'error': str(e)}
    
    def _run_cis_checks(self) -> List[Dict[str, Any]]:
        """Run CIS (Center for Internet Security) compliance checks."""
        checks = []
        
        try:
            # Check for MFA on root account
            mfa_check = self._check_root_mfa()
            checks.append(mfa_check)
            
            # Check for unused access keys
            access_key_check = self._check_unused_access_keys()
            checks.append(access_key_check)
            
            # Check for public S3 buckets
            s3_check = self._check_public_s3_buckets()
            checks.append(s3_check)
            
            # Check for security groups with unrestricted access
            sg_check = self._check_unrestricted_security_groups()
            checks.append(sg_check)
            
        except Exception as e:
            logger.error(f"Error running CIS checks: {str(e)}")
            checks.append({
                'id': 'CIS_ERROR',
                'status': 'error',
                'message': f'Error running CIS checks: {str(e)}'
            })
        
        return checks
    
    def _check_root_mfa(self) -> Dict[str, Any]:
        """Check if MFA is enabled for root account."""
        try:
            response = self.iam_client.get_account_summary()
            mfa_enabled = response['SummaryMap'].get('AccountMFAEnabled', False)
            
            return {
                'id': 'CIS_1.1',
                'title': 'Ensure MFA is enabled for root account',
                'status': 'pass' if mfa_enabled else 'fail',
                'message': 'MFA is enabled for root account' if mfa_enabled else 'MFA is not enabled for root account'
            }
        except Exception as e:
            return {
                'id': 'CIS_1.1',
                'title': 'Ensure MFA is enabled for root account',
                'status': 'error',
                'message': f'Error checking root MFA: {str(e)}'
            }
    
    def _check_unused_access_keys(self) -> Dict[str, Any]:
        """Check for unused access keys."""
        try:
            # This is a simplified check - in practice, you'd need to check last used dates
            return {
                'id': 'CIS_1.4',
                'title': 'Ensure access keys are rotated every 90 days',
                'status': 'info',
                'message': 'Manual review required for access key rotation'
            }
        except Exception as e:
            return {
                'id': 'CIS_1.4',
                'title': 'Ensure access keys are rotated every 90 days',
                'status': 'error',
                'message': f'Error checking access keys: {str(e)}'
            }
    
    def _check_public_s3_buckets(self) -> Dict[str, Any]:
        """Check for public S3 buckets."""
        try:
            s3_client = boto3.client('s3', region_name=self.region)
            response = s3_client.list_buckets()
            
            public_buckets = []
            for bucket in response['Buckets']:
                try:
                    acl = s3_client.get_bucket_acl(Bucket=bucket['Name'])
                    for grant in acl.get('Grants', []):
                        if grant.get('Grantee', {}).get('URI') == 'http://acs.amazonaws.com/groups/global/AllUsers':
                            public_buckets.append(bucket['Name'])
                            break
                except:
                    pass
            
            return {
                'id': 'CIS_2.1',
                'title': 'Ensure S3 buckets are not publicly accessible',
                'status': 'pass' if not public_buckets else 'fail',
                'message': f'Found {len(public_buckets)} public buckets: {public_buckets}' if public_buckets else 'No public buckets found'
            }
        except Exception as e:
            return {
                'id': 'CIS_2.1',
                'title': 'Ensure S3 buckets are not publicly accessible',
                'status': 'error',
                'message': f'Error checking S3 buckets: {str(e)}'
            }
    
    def _check_unrestricted_security_groups(self) -> Dict[str, Any]:
        """Check for security groups with unrestricted access."""
        try:
            ec2_client = boto3.client('ec2', region_name=self.region)
            response = ec2_client.describe_security_groups()
            
            unrestricted_sgs = []
            for sg in response['SecurityGroups']:
                for rule in sg.get('IpPermissions', []):
                    for ip_range in rule.get('IpRanges', []):
                        if ip_range.get('CidrIp') == '0.0.0.0/0':
                            unrestricted_sgs.append(sg['GroupId'])
                            break
            
            return {
                'id': 'CIS_4.1',
                'title': 'Ensure no security groups allow unrestricted access',
                'status': 'pass' if not unrestricted_sgs else 'fail',
                'message': f'Found {len(unrestricted_sgs)} security groups with unrestricted access: {unrestricted_sgs}' if unrestricted_sgs else 'No unrestricted security groups found'
            }
        except Exception as e:
            return {
                'id': 'CIS_4.1',
                'title': 'Ensure no security groups allow unrestricted access',
                'status': 'error',
                'message': f'Error checking security groups: {str(e)}'
            }
    
    def _run_nist_checks(self) -> List[Dict[str, Any]]:
        """Run NIST compliance checks."""
        # Placeholder for NIST checks
        return [{'id': 'NIST_PLACEHOLDER', 'status': 'info', 'message': 'NIST checks not implemented'}]
    
    def _run_soc2_checks(self) -> List[Dict[str, Any]]:
        """Run SOC2 compliance checks."""
        # Placeholder for SOC2 checks
        return [{'id': 'SOC2_PLACEHOLDER', 'status': 'info', 'message': 'SOC2 checks not implemented'}]
    
    def generate_security_report(self, scan_results: Dict[str, Any]) -> str:
        """Generate comprehensive security report."""
        try:
            report = f"""
# Security Scan Report
Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}

## Summary
- Scan Type: {scan_results.get('scan_type', 'Unknown')}
- Status: {scan_results.get('status', 'Unknown')}
- Critical Issues: {len([r for r in scan_results.get('findings', []) if r.get('severity') == 'CRITICAL'])}
- High Issues: {len([r for r in scan_results.get('findings', []) if r.get('severity') == 'HIGH'])}
- Medium Issues: {len([r for r in scan_results.get('findings', []) if r.get('severity') == 'MEDIUM'])}
- Low Issues: {len([r for r in scan_results.get('findings', []) if r.get('severity') == 'LOW'])}

## Detailed Findings
"""
            
            for finding in scan_results.get('findings', []):
                report += f"""
### {finding.get('name', 'Unknown Issue')}
- **Severity**: {finding.get('severity', 'Unknown')}
- **Description**: {finding.get('description', 'No description')}
- **URI**: {finding.get('uri', 'N/A')}
"""
            
            return report
            
        except Exception as e:
            logger.error(f"Error generating security report: {str(e)}")
            return f"Error generating report: {str(e)}"


def main():
    """Main function for testing SecurityManager."""
    # Example usage
    security_manager = SecurityManager()
    
    # Run dependency scan
    dep_results = security_manager.run_dependency_scan('.')
    print(f"Dependency scan results: {dep_results}")
    
    # Run static code analysis
    static_results = security_manager.run_static_code_analysis('.')
    print(f"Static analysis results: {static_results}")


if __name__ == "__main__":
    main()