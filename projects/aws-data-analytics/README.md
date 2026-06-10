# AWS Data & Analytics Platform

A comprehensive AWS-based data analytics platform that provides end-to-end data processing capabilities including data ingestion, storage, processing, analytics, and machine learning.

## Architecture Overview

The platform consists of the following key components:

### Data Ingestion
- **Amazon Kinesis Data Streams**: Real-time data streaming
- **Amazon Kinesis Data Firehose**: Data delivery to S3
- **Amazon S3**: Data lake storage with lifecycle policies

### Data Storage
- **Amazon S3 Data Lake**: Centralized data storage with zones (raw, processed, curated)
- **Amazon Redshift**: Data warehouse for analytics
- **AWS Glue Data Catalog**: Metadata management

### Data Processing
- **AWS Glue**: ETL jobs and data transformation
- **AWS Step Functions**: Workflow orchestration
- **Amazon EMR**: Big data processing (optional)

### Analytics & ML
- **Amazon SageMaker**: Machine learning platform
- **Amazon QuickSight**: Business intelligence and visualization
- **Amazon Redshift**: SQL analytics and reporting

### Monitoring & Security
- **Amazon CloudWatch**: Monitoring and logging
- **AWS KMS**: Encryption key management
- **AWS IAM**: Access control and permissions

## Project Structure

```
aws-data-analytics/
├── README.md                           # This file
├── requirements.txt                    # Python dependencies
├── cloudformation/                     # CloudFormation templates
│   └── data-analytics-platform.json   # Main infrastructure template
├── terraform/                          # Terraform infrastructure
│   ├── main.tf                        # Main configuration
│   ├── variables.tf                   # Input variables
│   ├── outputs.tf                     # Output values
│   └── terraform.tfvars.example       # Example variables file
├── python/                            # Python automation scripts
│   ├── data_ingestion/                # Data ingestion modules
│   │   └── data_lake_manager.py       # S3, Glue, Lake Formation management
│   ├── etl_pipelines/                 # ETL pipeline modules
│   │   └── etl_manager.py             # Glue jobs and Step Functions
│   ├── streaming/                      # Streaming data modules
│   │   └── kinesis_manager.py         # Kinesis Data Streams management
│   ├── analytics/                      # Analytics modules
│   │   └── redshift_manager.py        # Redshift cluster management
│   └── ml/                            # Machine learning modules
│       └── sagemaker_manager.py       # SageMaker operations
└── scripts/                           # Deployment scripts
    └── deploy_data_analytics.sh       # Platform deployment script
```

## Features

### Data Lake Management
- Automated S3 bucket creation with proper security settings
- Data zone organization (raw, processed, curated)
- Lifecycle policies for cost optimization
- Encryption at rest and in transit

### Real-time Data Streaming
- Kinesis Data Streams for real-time data ingestion
- Kinesis Data Firehose for data delivery to S3
- Configurable sharding and retention policies
- Monitoring and alerting

### ETL Pipelines
- Glue job management for data transformation
- Step Functions for workflow orchestration
- Support for multiple data sources and formats
- Error handling and retry mechanisms

### Data Warehouse
- Redshift cluster management
- Automated backup and recovery
- Query optimization and performance tuning
- Integration with data lake

### Machine Learning
- SageMaker notebook instances for development
- Model training and deployment capabilities
- Integration with data lake and warehouse
- MLOps workflows

### Monitoring & Security
- Comprehensive CloudWatch monitoring
- Custom metrics and alarms
- IAM roles and policies
- KMS encryption

## Prerequisites

- AWS CLI configured with appropriate permissions
- Terraform >= 1.0
- Python 3.8+
- Required Python packages (see requirements.txt)

## Quick Start

### 1. Clone and Setup

```bash
git clone <repository-url>
cd aws-data-analytics
pip install -r requirements.txt
```

### 2. Configure Variables

Copy the example variables file and update with your values:

```bash
cp terraform/terraform.tfvars.example terraform/terraform.tfvars
```

Edit `terraform/terraform.tfvars` with your specific configuration:

```hcl
aws_region = "us-east-1"
project_name = "my-data-analytics"
data_lake_bucket_name = "my-unique-bucket-name"
vpc_id = "vpc-12345678"
redshift_subnet_ids = ["subnet-12345678", "subnet-87654321"]
redshift_master_password = "YourSecurePassword123!"
```

### 3. Deploy Infrastructure

#### Option A: Using the Deployment Script

```bash
./scripts/deploy_data_analytics.sh \
  --bucket-name my-data-lake-bucket \
  --vpc-id vpc-12345678 \
  --subnet-ids subnet-12345678,subnet-87654321 \
  --password YourSecurePassword123!
```

#### Option B: Using Terraform Directly

```bash
cd terraform
terraform init
terraform plan
terraform apply
```

### 4. Verify Deployment

Check that all resources are created successfully:

```bash
aws s3 ls s3://your-data-lake-bucket
aws kinesis list-streams
aws redshift describe-clusters --cluster-identifier your-cluster-name
aws sagemaker list-notebook-instances
```

## Usage Examples

### Data Ingestion

```python
from python.data_ingestion.data_lake_manager import DataLakeManager

# Initialize manager
dlm = DataLakeManager()

# Create data lake structure
dlm.create_data_lake_structure("my-data-lake")

# Ingest data
dlm.ingest_data("s3://source-bucket/data.csv", "raw/2024/01/01/")
```

### Real-time Streaming

```python
from python.streaming.kinesis_manager import KinesisManager

# Initialize manager
km = KinesisManager()

# Create stream
km.create_stream("my-data-stream", shard_count=2)

# Send data
data = {"timestamp": "2024-01-01T00:00:00Z", "value": 100}
km.put_record("my-data-stream", data)
```

### ETL Processing

```python
from python.etl_pipelines.etl_manager import ETLPipelineManager

# Initialize manager
etl = ETLPipelineManager()

# Create Glue job
job_config = {
    'script_location': 's3://my-bucket/scripts/etl_script.py',
    'max_capacity': 2.0,
    'worker_type': 'Standard'
}
etl.create_glue_job('my-etl-job', job_config)
```

### Analytics

```python
from python.analytics.redshift_manager import RedshiftManager

# Initialize manager
rm = RedshiftManager()

# Execute query
results = rm.execute_query(
    cluster_identifier="my-cluster",
    query="SELECT * FROM sales WHERE date >= '2024-01-01'",
    password="your-password"
)
```

### Machine Learning

```python
from python.ml.sagemaker_manager import SageMakerManager

# Initialize manager
sm = SageMakerManager()

# Create notebook instance
notebook_config = {
    'instance_name': 'ml-notebook',
    'instance_type': 'ml.t3.medium'
}
sm.create_notebook_instance(notebook_config)
```

## Configuration

### Environment Variables

Set the following environment variables for configuration:

```bash
export AWS_REGION=us-east-1
export AWS_PROFILE=your-profile
export DATA_LAKE_BUCKET=your-data-lake-bucket
```

### Terraform Variables

Key variables that can be customized:

- `aws_region`: AWS region for deployment
- `project_name`: Project identifier
- `data_lake_bucket_name`: S3 bucket for data lake
- `redshift_node_type`: Redshift instance type
- `kinesis_shard_count`: Number of Kinesis shards
- `sagemaker_instance_type`: SageMaker notebook instance type

## Monitoring

### CloudWatch Dashboards

The platform creates several CloudWatch dashboards:

- Data Lake Metrics: S3 storage and request metrics
- Kinesis Metrics: Stream throughput and error rates
- Redshift Metrics: Cluster performance and utilization
- Glue Metrics: Job execution and success rates

### Alarms

Key alarms are configured:

- Kinesis incoming records threshold
- Redshift CPU utilization
- Glue job failure rates
- S3 storage costs

## Security

### IAM Roles

The platform creates specific IAM roles for each service:

- `{project}-glue-crawler-role`: Glue crawler permissions
- `{project}-firehose-role`: Firehose delivery permissions
- `{project}-sagemaker-role`: SageMaker execution permissions
- `{project}-redshift-role`: Redshift cluster permissions

### Encryption

- S3 buckets encrypted with AES-256
- Kinesis streams encrypted with KMS
- Redshift clusters encrypted at rest
- All data in transit encrypted with TLS

## Cost Optimization

### S3 Lifecycle Policies

- Move data to IA after 30 days
- Move to Glacier after 90 days
- Move to Deep Archive after 365 days

### Redshift Optimization

- Automated snapshot retention
- Pause/resume capabilities
- Right-sizing recommendations

### Kinesis Optimization

- Configurable shard count
- Data retention policies
- Compression for Firehose

## Troubleshooting

### Common Issues

1. **S3 Bucket Name Conflicts**
   - Ensure bucket name is globally unique
   - Check for existing buckets in the region

2. **VPC Configuration**
   - Verify VPC ID exists
   - Check subnet IDs are valid
   - Ensure security groups allow required traffic

3. **Redshift Connection Issues**
   - Verify security group rules
   - Check subnet group configuration
   - Validate password requirements

4. **Permission Errors**
   - Ensure IAM roles have required permissions
   - Check service-linked roles are created
   - Verify cross-service access policies

### Logs and Debugging

- CloudWatch Logs: `/aws/data-analytics/{project-name}`
- Glue Job Logs: `/aws-glue/jobs/logs-v2`
- SageMaker Logs: `/aws/sagemaker/NotebookInstances`

## Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests if applicable
5. Submit a pull request

## License

This project is licensed under the MIT License - see the LICENSE file for details.

## Support

For issues and questions:

1. Check the troubleshooting section
2. Review AWS documentation
3. Create an issue in the repository
4. Contact the development team

## Changelog

### Version 1.0.0
- Initial release
- Complete data analytics platform
- Terraform and CloudFormation support
- Python automation scripts
- Comprehensive documentation