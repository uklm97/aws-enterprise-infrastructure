#!/usr/bin/env python3
"""
AWS Cloud Environment Infrastructure Audit Framework

A comprehensive audit solution for AWS infrastructure including security,
compliance, cost, and performance auditing.

Author: AWS Audit Framework
Version: 1.0.0
"""

import argparse
import json
import logging
import os
import sys
import yaml
from datetime import datetime, timedelta
from pathlib import Path
from typing import Dict, List, Any, Optional

# Import audit modules (lazy import SecurityAuditor to avoid hard dependency on boto3 at import time)
from cost_audit import CostAuditor
from performance_audit import PerformanceAuditor
from compliance_audit import ComplianceAuditor
from infrastructure_audit import InfrastructureAuditor

# Import utility modules
from utils.aws_client import AWSClientManager
from utils.report_generator import ReportGenerator
from utils.config import ConfigManager


class AWSAuditFramework:
    """
    Main AWS Audit Framework class that orchestrates all audit modules.
    """
    
    def __init__(self, config_file: str = 'config/audit_config.yaml'):
        """
        Initialize the AWS Audit Framework.
        
        Args:
            config_file (str): Path to the configuration file
        """
        self.config_manager = ConfigManager(config_file)
        self.config = self.config_manager.load_config()
        self.aws_client_manager = AWSClientManager(self.config)
        self.clients = self.aws_client_manager.initialize_clients()
        self.report_generator = ReportGenerator(self.config)
        self.reports = {}
        self.logger = self._setup_logging()
        
        # Validate configuration
        self._validate_config()
    
    def _setup_logging(self) -> logging.Logger:
        """Setup logging configuration."""
        logger = logging.getLogger('aws_audit_framework')
        logger.setLevel(logging.INFO)
        
        # Create handlers
        c_handler = logging.StreamHandler()
        f_handler = logging.FileHandler('audit_framework.log')
        c_handler.setLevel(logging.INFO)
        f_handler.setLevel(logging.DEBUG)
        
        # Create formatters and add it to handlers
        c_format = logging.Formatter('%(name)s - %(levelname)s - %(message)s')
        f_format = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
        c_handler.setFormatter(c_format)
        f_handler.setFormatter(f_format)
        
        # Add handlers to the logger
        logger.addHandler(c_handler)
        logger.addHandler(f_handler)
        
        return logger
    
    def _validate_config(self):
        """Validate the configuration file."""
        required_keys = ['aws_region', 'audit_modules', 'reporting']
        for key in required_keys:
            if key not in self.config:
                raise ValueError(f"Missing required configuration key: {key}")
        
        self.logger.info("Configuration validation completed successfully")
    
    def run_comprehensive_audit(self) -> Dict[str, Any]:
        """
        Run all audit modules for a comprehensive assessment.
        
        Returns:
            Dict containing all audit results
        """
        self.logger.info("Starting comprehensive AWS infrastructure audit")
        start_time = datetime.now()
        
        try:
            # Run all audit modules
            self.run_security_audit()
            self.run_cost_audit()
            self.run_performance_audit()
            self.run_compliance_audit()
            self.run_infrastructure_audit()
            
            # Generate comprehensive reports
            self.generate_reports()
            
            end_time = datetime.now()
            duration = end_time - start_time
            
            self.logger.info(f"Comprehensive audit completed in {duration}")
            
            return {
                'status': 'success',
                'duration': str(duration),
                'reports': self.reports,
                'summary': self._generate_summary()
            }
            
        except Exception as e:
            self.logger.error(f"Comprehensive audit failed: {str(e)}")
            return {
                'status': 'error',
                'error': str(e),
                'reports': self.reports
            }
    
    def run_security_audit(self) -> Dict[str, Any]:
        """
        Run security audit modules.
        
        Returns:
            Dict containing security audit results
        """
        self.logger.info("Starting security audit")
        
        try:
            # Lazy import to allow running without boto3 for other modules
            from security_audit import SecurityAuditor  # type: ignore
            security_auditor = SecurityAuditor(self.clients, self.config)
            self.reports['security'] = security_auditor.run_audit()
            
            self.logger.info("Security audit completed successfully")
            return self.reports['security']
            
        except Exception as e:
            self.logger.error(f"Security audit failed: {str(e)}")
            self.reports['security'] = {'error': str(e)}
            return self.reports['security']
    
    def run_cost_audit(self) -> Dict[str, Any]:
        """
        Run cost audit modules.
        
        Returns:
            Dict containing cost audit results
        """
        self.logger.info("Starting cost audit")
        
        try:
            cost_auditor = CostAuditor(self.clients, self.config)
            self.reports['cost'] = cost_auditor.run_audit()
            
            self.logger.info("Cost audit completed successfully")
            return self.reports['cost']
            
        except Exception as e:
            self.logger.error(f"Cost audit failed: {str(e)}")
            self.reports['cost'] = {'error': str(e)}
            return self.reports['cost']
    
    def run_performance_audit(self) -> Dict[str, Any]:
        """
        Run performance audit modules.
        
        Returns:
            Dict containing performance audit results
        """
        self.logger.info("Starting performance audit")
        
        try:
            performance_auditor = PerformanceAuditor(self.clients, self.config)
            self.reports['performance'] = performance_auditor.run_audit()
            
            self.logger.info("Performance audit completed successfully")
            return self.reports['performance']
            
        except Exception as e:
            self.logger.error(f"Performance audit failed: {str(e)}")
            self.reports['performance'] = {'error': str(e)}
            return self.reports['performance']
    
    def run_compliance_audit(self) -> Dict[str, Any]:
        """
        Run compliance audit modules.
        
        Returns:
            Dict containing compliance audit results
        """
        self.logger.info("Starting compliance audit")
        
        try:
            compliance_auditor = ComplianceAuditor(self.clients, self.config)
            self.reports['compliance'] = compliance_auditor.run_audit()
            
            self.logger.info("Compliance audit completed successfully")
            return self.reports['compliance']
            
        except Exception as e:
            self.logger.error(f"Compliance audit failed: {str(e)}")
            self.reports['compliance'] = {'error': str(e)}
            return self.reports['compliance']
    
    def run_infrastructure_audit(self) -> Dict[str, Any]:
        """
        Run infrastructure audit modules.
        
        Returns:
            Dict containing infrastructure audit results
        """
        self.logger.info("Starting infrastructure audit")
        
        try:
            infrastructure_auditor = InfrastructureAuditor(self.clients, self.config)
            self.reports['infrastructure'] = infrastructure_auditor.run_audit()
            
            self.logger.info("Infrastructure audit completed successfully")
            return self.reports['infrastructure']
            
        except Exception as e:
            self.logger.error(f"Infrastructure audit failed: {str(e)}")
            self.reports['infrastructure'] = {'error': str(e)}
            return self.reports['infrastructure']
    
    def generate_reports(self):
        """Generate comprehensive audit reports."""
        self.logger.info("Generating audit reports")
        
        try:
            # Generate different report formats
            self.report_generator.generate_html_report(self.reports)
            self.report_generator.generate_pdf_report(self.reports)
            self.report_generator.generate_json_report(self.reports)
            self.report_generator.generate_csv_report(self.reports)
            
            self.logger.info("Audit reports generated successfully")
            
        except Exception as e:
            self.logger.error(f"Report generation failed: {str(e)}")
    
    def _generate_summary(self) -> Dict[str, Any]:
        """
        Generate a summary of all audit results.
        
        Returns:
            Dict containing audit summary
        """
        summary = {
            'total_findings': 0,
            'critical_findings': 0,
            'high_findings': 0,
            'medium_findings': 0,
            'low_findings': 0,
            'compliance_score': 0,
            'cost_optimization_opportunities': 0,
            'security_issues': 0,
            'performance_issues': 0
        }
        
        # Aggregate findings from all audit modules
        for module_name, module_results in self.reports.items():
            if isinstance(module_results, dict) and 'error' not in module_results:
                if 'findings' in module_results:
                    for finding in module_results['findings']:
                        summary['total_findings'] += 1
                        severity = finding.get('severity', 'low').lower()
                        if severity == 'critical':
                            summary['critical_findings'] += 1
                        elif severity == 'high':
                            summary['high_findings'] += 1
                        elif severity == 'medium':
                            summary['medium_findings'] += 1
                        else:
                            summary['low_findings'] += 1
                
                # Module-specific metrics
                if module_name == 'security':
                    summary['security_issues'] = module_results.get('total_issues', 0)
                elif module_name == 'performance':
                    summary['performance_issues'] = module_results.get('total_issues', 0)
                elif module_name == 'cost':
                    summary['cost_optimization_opportunities'] = module_results.get('optimization_opportunities', 0)
                elif module_name == 'compliance':
                    summary['compliance_score'] = module_results.get('compliance_score', 0)
        
        return summary
    
    def validate_config(self) -> bool:
        """
        Validate the audit configuration.
        
        Returns:
            bool: True if configuration is valid, False otherwise
        """
        self.logger.info("Validating audit configuration")
        
        try:
            # Validate AWS credentials
            sts_client = self.clients.get('sts')
            if sts_client:
                identity = sts_client.get_caller_identity()
                self.logger.info(f"AWS Account: {identity['Account']}")
                self.logger.info(f"AWS User/Role: {identity['Arn']}")
            
            # Validate required services
            required_services = ['iam', 'ec2', 's3', 'rds', 'cloudwatch']
            for service in required_services:
                if service in self.clients:
                    self.logger.info(f"✓ {service.upper()} client initialized")
                else:
                    self.logger.warning(f"✗ {service.upper()} client not available")
            
            self.logger.info("Configuration validation completed successfully")
            return True
            
        except Exception as e:
            self.logger.error(f"Configuration validation failed: {str(e)}")
            return False


def main():
    """Main function to run the AWS Audit Framework."""
    parser = argparse.ArgumentParser(
        description='AWS Cloud Environment Infrastructure Audit Framework',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python audit_framework.py --comprehensive
  python audit_framework.py --security
  python audit_framework.py --cost --performance
  python audit_framework.py --validate-config
        """
    )
    
    # Audit type arguments
    parser.add_argument('--comprehensive', action='store_true',
                       help='Run comprehensive audit (all modules)')
    parser.add_argument('--security', action='store_true',
                       help='Run security audit only')
    parser.add_argument('--cost', action='store_true',
                       help='Run cost audit only')
    parser.add_argument('--performance', action='store_true',
                       help='Run performance audit only')
    parser.add_argument('--compliance', action='store_true',
                       help='Run compliance audit only')
    parser.add_argument('--infrastructure', action='store_true',
                       help='Run infrastructure audit only')
    
    # Configuration arguments
    parser.add_argument('--config', type=str, default='config/audit_config.yaml',
                       help='Path to configuration file (default: config/audit_config.yaml)')
    parser.add_argument('--validate-config', action='store_true',
                       help='Validate configuration only')
    parser.add_argument('--output-format', choices=['json', 'html', 'pdf', 'csv'],
                       default='json', help='Output format for reports (default: json)')
    parser.add_argument('--output-dir', type=str, default='reports',
                       help='Output directory for reports (default: reports)')
    
    # AWS configuration arguments
    parser.add_argument('--region', type=str,
                       help='AWS region (overrides config file)')
    parser.add_argument('--profile', type=str,
                       help='AWS profile to use')
    
    # Verbosity arguments
    parser.add_argument('--verbose', '-v', action='store_true',
                       help='Enable verbose logging')
    parser.add_argument('--debug', action='store_true',
                       help='Enable debug logging')
    
    args = parser.parse_args()
    
    # Setup logging based on verbosity
    if args.debug:
        logging.getLogger().setLevel(logging.DEBUG)
    elif args.verbose:
        logging.getLogger().setLevel(logging.INFO)
    else:
        logging.getLogger().setLevel(logging.WARNING)
    
    try:
        # Initialize audit framework
        audit_framework = AWSAuditFramework(args.config)
        
        # Override region if specified
        if args.region:
            audit_framework.config['aws_region'] = args.region
        
        # Validate configuration if requested
        if args.validate_config:
            if audit_framework.validate_config():
                print("✓ Configuration validation successful")
                sys.exit(0)
            else:
                print("✗ Configuration validation failed")
                sys.exit(1)
        
        # Run audits based on arguments
        if args.comprehensive:
            print("Running comprehensive audit...")
            results = audit_framework.run_comprehensive_audit()
        elif any([args.security, args.cost, args.performance, args.compliance, args.infrastructure]):
            results = {}
            if args.security:
                print("Running security audit...")
                results['security'] = audit_framework.run_security_audit()
            if args.cost:
                print("Running cost audit...")
                results['cost'] = audit_framework.run_cost_audit()
            if args.performance:
                print("Running performance audit...")
                results['performance'] = audit_framework.run_performance_audit()
            if args.compliance:
                print("Running compliance audit...")
                results['compliance'] = audit_framework.run_compliance_audit()
            if args.infrastructure:
                print("Running infrastructure audit...")
                results['infrastructure'] = audit_framework.run_infrastructure_audit()
        else:
            print("No audit type specified. Use --help for usage information.")
            sys.exit(1)
        
        # Generate reports
        audit_framework.reports = results
        audit_framework.generate_reports()
        
        # Print summary
        if 'summary' in results:
            summary = results['summary']
            print("\n" + "="*50)
            print("AUDIT SUMMARY")
            print("="*50)
            print(f"Total Findings: {summary['total_findings']}")
            print(f"Critical: {summary['critical_findings']}")
            print(f"High: {summary['high_findings']}")
            print(f"Medium: {summary['medium_findings']}")
            print(f"Low: {summary['low_findings']}")
            print(f"Compliance Score: {summary['compliance_score']}%")
            print(f"Cost Optimization Opportunities: {summary['cost_optimization_opportunities']}")
            print(f"Security Issues: {summary['security_issues']}")
            print(f"Performance Issues: {summary['performance_issues']}")
            print("="*50)
        
        print(f"\nAudit completed successfully. Reports saved to: {args.output_dir}")
        
    except KeyboardInterrupt:
        print("\nAudit interrupted by user")
        sys.exit(1)
    except Exception as e:
        print(f"Audit failed: {str(e)}")
        if args.debug:
            import traceback
            traceback.print_exc()
        sys.exit(1)


if __name__ == '__main__':
    main()
