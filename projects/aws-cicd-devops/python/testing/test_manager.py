#!/usr/bin/env python3
"""
AWS CI/CD Testing Manager for automated testing.

This module provides comprehensive testing capabilities including
unit tests, integration tests, security tests, and performance tests.
"""

import boto3
import subprocess
import logging
import json
import os
import time
from typing import List, Dict, Any, Optional
from datetime import datetime
import xml.etree.ElementTree as ET

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class TestManager:
    """
    AWS CI/CD Testing Manager for automated testing.
    """
    
    def __init__(self, region: str = 'us-east-1'):
        """Initialize TestManager with AWS clients."""
        self.region = region
        self.codebuild_client = boto3.client('codebuild', region_name=region)
        self.s3_client = boto3.client('s3', region_name=region)
        self.cloudwatch_client = boto3.client('cloudwatch', region_name=region)
        
    def run_unit_tests(self, project_path: str, test_command: str = "pytest") -> Dict[str, Any]:
        """Run unit tests for the project."""
        try:
            logger.info(f"Running unit tests in {project_path}")
            
            # Change to project directory
            original_dir = os.getcwd()
            os.chdir(project_path)
            
            # Run unit tests
            result = subprocess.run(
                test_command.split(),
                capture_output=True,
                text=True,
                timeout=300
            )
            
            # Parse test results
            test_results = self._parse_pytest_results(result.stdout, result.stderr)
            test_results['return_code'] = result.returncode
            test_results['command'] = test_command
            
            # Upload test results to S3
            if 'test_results_bucket' in os.environ:
                self._upload_test_results('unit-tests', test_results)
            
            os.chdir(original_dir)
            
            logger.info(f"Unit tests completed with return code: {result.returncode}")
            return test_results
            
        except subprocess.TimeoutExpired:
            logger.error("Unit tests timed out after 5 minutes")
            return {'error': 'Test timeout', 'return_code': -1}
        except Exception as e:
            logger.error(f"Error running unit tests: {str(e)}")
            return {'error': str(e), 'return_code': -1}
    
    def run_integration_tests(self, project_path: str, test_command: str = "pytest tests/integration/") -> Dict[str, Any]:
        """Run integration tests for the project."""
        try:
            logger.info(f"Running integration tests in {project_path}")
            
            # Change to project directory
            original_dir = os.getcwd()
            os.chdir(project_path)
            
            # Run integration tests
            result = subprocess.run(
                test_command.split(),
                capture_output=True,
                text=True,
                timeout=600
            )
            
            # Parse test results
            test_results = self._parse_pytest_results(result.stdout, result.stderr)
            test_results['return_code'] = result.returncode
            test_results['command'] = test_command
            test_results['test_type'] = 'integration'
            
            # Upload test results to S3
            if 'test_results_bucket' in os.environ:
                self._upload_test_results('integration-tests', test_results)
            
            os.chdir(original_dir)
            
            logger.info(f"Integration tests completed with return code: {result.returncode}")
            return test_results
            
        except subprocess.TimeoutExpired:
            logger.error("Integration tests timed out after 10 minutes")
            return {'error': 'Test timeout', 'return_code': -1}
        except Exception as e:
            logger.error(f"Error running integration tests: {str(e)}")
            return {'error': str(e), 'return_code': -1}
    
    def run_security_tests(self, project_path: str) -> Dict[str, Any]:
        """Run security tests for the project."""
        try:
            logger.info(f"Running security tests in {project_path}")
            
            security_results = {}
            
            # Run bandit security linter
            bandit_result = self._run_bandit(project_path)
            security_results['bandit'] = bandit_result
            
            # Run safety for dependency vulnerabilities
            safety_result = self._run_safety(project_path)
            security_results['safety'] = safety_result
            
            # Run semgrep for static analysis
            semgrep_result = self._run_semgrep(project_path)
            security_results['semgrep'] = semgrep_result
            
            # Run OWASP ZAP if available
            zap_result = self._run_owasp_zap(project_path)
            security_results['owasp_zap'] = zap_result
            
            # Upload security results to S3
            if 'test_results_bucket' in os.environ:
                self._upload_test_results('security-tests', security_results)
            
            logger.info("Security tests completed")
            return security_results
            
        except Exception as e:
            logger.error(f"Error running security tests: {str(e)}")
            return {'error': str(e)}
    
    def _run_bandit(self, project_path: str) -> Dict[str, Any]:
        """Run bandit security linter."""
        try:
            result = subprocess.run(
                ['bandit', '-r', project_path, '-f', 'json'],
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
            return {'status': 'timeout', 'error': 'Bandit timed out'}
        except Exception as e:
            return {'status': 'error', 'error': str(e)}
    
    def _run_safety(self, project_path: str) -> Dict[str, Any]:
        """Run safety for dependency vulnerabilities."""
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
            return {'status': 'timeout', 'error': 'Safety timed out'}
        except Exception as e:
            return {'status': 'error', 'error': str(e)}
    
    def _run_semgrep(self, project_path: str) -> Dict[str, Any]:
        """Run semgrep for static analysis."""
        try:
            result = subprocess.run(
                ['semgrep', '--config=auto', '--json', project_path],
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
            return {'status': 'timeout', 'error': 'Semgrep timed out'}
        except Exception as e:
            return {'status': 'error', 'error': str(e)}
    
    def _run_owasp_zap(self, project_path: str) -> Dict[str, Any]:
        """Run OWASP ZAP security testing."""
        try:
            # This is a placeholder - OWASP ZAP requires more complex setup
            # In a real implementation, you would configure ZAP to scan your application
            return {
                'status': 'skipped',
                'message': 'OWASP ZAP requires application URL and proper configuration'
            }
        except Exception as e:
            return {'status': 'error', 'error': str(e)}
    
    def run_performance_tests(self, project_path: str, test_command: str = "pytest tests/performance/") -> Dict[str, Any]:
        """Run performance tests for the project."""
        try:
            logger.info(f"Running performance tests in {project_path}")
            
            # Change to project directory
            original_dir = os.getcwd()
            os.chdir(project_path)
            
            # Run performance tests
            result = subprocess.run(
                test_command.split(),
                capture_output=True,
                text=True,
                timeout=1800  # 30 minutes for performance tests
            )
            
            # Parse test results
            test_results = self._parse_pytest_results(result.stdout, result.stderr)
            test_results['return_code'] = result.returncode
            test_results['command'] = test_command
            test_results['test_type'] = 'performance'
            
            # Upload test results to S3
            if 'test_results_bucket' in os.environ:
                self._upload_test_results('performance-tests', test_results)
            
            os.chdir(original_dir)
            
            logger.info(f"Performance tests completed with return code: {result.returncode}")
            return test_results
            
        except subprocess.TimeoutExpired:
            logger.error("Performance tests timed out after 30 minutes")
            return {'error': 'Test timeout', 'return_code': -1}
        except Exception as e:
            logger.error(f"Error running performance tests: {str(e)}")
            return {'error': str(e), 'return_code': -1}
    
    def run_load_tests(self, project_path: str, target_url: str = None) -> Dict[str, Any]:
        """Run load tests using locust or similar tools."""
        try:
            logger.info(f"Running load tests for {target_url}")
            
            if not target_url:
                return {'error': 'Target URL is required for load tests'}
            
            # Change to project directory
            original_dir = os.getcwd()
            os.chdir(project_path)
            
            # Run locust load tests
            result = subprocess.run([
                'locust', 
                '--host', target_url,
                '--headless',
                '--users', '100',
                '--spawn-rate', '10',
                '--run-time', '300s',
                '--html', 'load_test_report.html'
            ], capture_output=True, text=True, timeout=600)
            
            load_test_results = {
                'return_code': result.returncode,
                'target_url': target_url,
                'stdout': result.stdout,
                'stderr': result.stderr,
                'test_type': 'load'
            }
            
            # Upload load test results to S3
            if 'test_results_bucket' in os.environ:
                self._upload_test_results('load-tests', load_test_results)
            
            os.chdir(original_dir)
            
            logger.info(f"Load tests completed with return code: {result.returncode}")
            return load_test_results
            
        except subprocess.TimeoutExpired:
            logger.error("Load tests timed out after 10 minutes")
            return {'error': 'Test timeout', 'return_code': -1}
        except Exception as e:
            logger.error(f"Error running load tests: {str(e)}")
            return {'error': str(e), 'return_code': -1}
    
    def _parse_pytest_results(self, stdout: str, stderr: str) -> Dict[str, Any]:
        """Parse pytest results from stdout and stderr."""
        try:
            # Try to parse JSON output if available
            if '--json-report' in stdout:
                # Look for JSON report file
                pass
            
            # Parse summary from stdout
            lines = stdout.split('\n')
            summary = {}
            
            for line in lines:
                if 'failed' in line and 'passed' in line:
                    # Extract numbers from summary line
                    import re
                    numbers = re.findall(r'\d+', line)
                    if len(numbers) >= 2:
                        summary['passed'] = int(numbers[0])
                        summary['failed'] = int(numbers[1])
                elif 'warnings' in line:
                    import re
                    numbers = re.findall(r'\d+', line)
                    if numbers:
                        summary['warnings'] = int(numbers[0])
            
            return {
                'summary': summary,
                'stdout': stdout,
                'stderr': stderr,
                'timestamp': datetime.now().isoformat()
            }
            
        except Exception as e:
            logger.error(f"Error parsing pytest results: {str(e)}")
            return {
                'summary': {},
                'stdout': stdout,
                'stderr': stderr,
                'timestamp': datetime.now().isoformat(),
                'parse_error': str(e)
            }
    
    def _upload_test_results(self, test_type: str, results: Dict[str, Any]) -> bool:
        """Upload test results to S3."""
        try:
            bucket_name = os.environ['test_results_bucket']
            timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
            key = f"test-results/{test_type}/{timestamp}.json"
            
            self.s3_client.put_object(
                Bucket=bucket_name,
                Key=key,
                Body=json.dumps(results, indent=2),
                ContentType='application/json'
            )
            
            logger.info(f"Test results uploaded to s3://{bucket_name}/{key}")
            return True
            
        except Exception as e:
            logger.error(f"Error uploading test results: {str(e)}")
            return False
    
    def create_test_report(self, test_results: Dict[str, Any]) -> str:
        """Create HTML test report from test results."""
        try:
            html_content = f"""
            <!DOCTYPE html>
            <html>
            <head>
                <title>Test Report</title>
                <style>
                    body {{ font-family: Arial, sans-serif; margin: 20px; }}
                    .header {{ background-color: #f0f0f0; padding: 20px; border-radius: 5px; }}
                    .section {{ margin: 20px 0; }}
                    .passed {{ color: green; }}
                    .failed {{ color: red; }}
                    .error {{ color: orange; }}
                    pre {{ background-color: #f5f5f5; padding: 10px; border-radius: 3px; overflow-x: auto; }}
                </style>
            </head>
            <body>
                <div class="header">
                    <h1>Test Report</h1>
                    <p>Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}</p>
                </div>
                
                <div class="section">
                    <h2>Summary</h2>
                    <p>Return Code: <span class="{'passed' if test_results.get('return_code') == 0 else 'failed'}">{test_results.get('return_code', 'N/A')}</span></p>
                    <p>Test Type: {test_results.get('test_type', 'N/A')}</p>
                </div>
                
                <div class="section">
                    <h2>Output</h2>
                    <pre>{test_results.get('stdout', 'No output')}</pre>
                </div>
                
                <div class="section">
                    <h2>Errors</h2>
                    <pre>{test_results.get('stderr', 'No errors')}</pre>
                </div>
            </body>
            </html>
            """
            
            return html_content
            
        except Exception as e:
            logger.error(f"Error creating test report: {str(e)}")
            return f"<html><body><h1>Error creating report: {str(e)}</h1></body></html>"
    
    def send_test_notifications(self, test_results: Dict[str, Any], notification_config: Dict[str, Any]) -> bool:
        """Send test result notifications."""
        try:
            # This would integrate with SNS, Slack, email, etc.
            # For now, just log the notification
            logger.info(f"Test notification: {test_results.get('summary', {})}")
            return True
            
        except Exception as e:
            logger.error(f"Error sending test notifications: {str(e)}")
            return False


def main():
    """Main function for testing TestManager."""
    # Example usage
    test_manager = TestManager()
    
    # Run unit tests
    unit_results = test_manager.run_unit_tests('.', 'pytest tests/unit/')
    print(f"Unit test results: {unit_results}")
    
    # Run security tests
    security_results = test_manager.run_security_tests('.')
    print(f"Security test results: {security_results}")


if __name__ == "__main__":
    main()