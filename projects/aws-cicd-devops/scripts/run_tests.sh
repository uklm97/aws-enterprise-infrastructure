#!/bin/bash

# AWS CI/CD Test Runner Script
# This script runs comprehensive tests for the CI/CD pipeline

set -e

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Configuration
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(dirname "$(dirname "$SCRIPT_DIR")")"
PYTHON_DIR="$PROJECT_ROOT/python"

# Default values
TEST_TYPE="all"
PROJECT_PATH="."
TARGET_URL=""
VERBOSE=false
PARALLEL=false

# Function to print colored output
print_status() {
    echo -e "${BLUE}[INFO]${NC} $1"
}

print_success() {
    echo -e "${GREEN}[SUCCESS]${NC} $1"
}

print_warning() {
    echo -e "${YELLOW}[WARNING]${NC} $1"
}

print_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

# Function to show usage
show_usage() {
    cat << EOF
Usage: $0 [OPTIONS]

Run comprehensive tests for CI/CD pipeline

OPTIONS:
    -t, --test-type TYPE        Test type: unit, integration, security, performance, load, all (default: all)
    -p, --project-path PATH     Project path to test (default: current directory)
    -u, --target-url URL        Target URL for load tests
    -v, --verbose              Enable verbose output
    -P, --parallel             Run tests in parallel
    -h, --help                 Show this help message

EXAMPLES:
    # Run all tests
    $0

    # Run only unit tests
    $0 --test-type unit

    # Run security tests with verbose output
    $0 --test-type security --verbose

    # Run load tests against specific URL
    $0 --test-type load --target-url http://example.com

    # Run tests in parallel
    $0 --parallel
EOF
}

# Function to check prerequisites
check_prerequisites() {
    print_status "Checking prerequisites..."
    
    # Check if Python is installed
    if ! command -v python3 &> /dev/null; then
        print_error "Python 3 is not installed. Please install it first."
        exit 1
    fi
    
    # Check if pip is installed
    if ! command -v pip3 &> /dev/null; then
        print_error "pip3 is not installed. Please install it first."
        exit 1
    fi
    
    # Check if required Python packages are installed
    python3 -c "import pytest, bandit, safety" 2>/dev/null || {
        print_warning "Some required Python packages are missing. Installing..."
        pip3 install pytest bandit safety semgrep pip-audit locust pytest-benchmark
    }
    
    print_success "All prerequisites met"
}

# Function to run unit tests
run_unit_tests() {
    print_status "Running unit tests..."
    
    cd "$PROJECT_PATH"
    
    if [ -d "tests/unit" ]; then
        if [ "$PARALLEL" = true ]; then
            python3 -m pytest tests/unit/ -v --numprocesses=auto
        else
            python3 -m pytest tests/unit/ -v
        fi
        print_success "Unit tests completed"
    else
        print_warning "No unit tests found in tests/unit/"
    fi
}

# Function to run integration tests
run_integration_tests() {
    print_status "Running integration tests..."
    
    cd "$PROJECT_PATH"
    
    if [ -d "tests/integration" ]; then
        if [ "$PARALLEL" = true ]; then
            python3 -m pytest tests/integration/ -v --numprocesses=auto
        else
            python3 -m pytest tests/integration/ -v
        fi
        print_success "Integration tests completed"
    else
        print_warning "No integration tests found in tests/integration/"
    fi
}

# Function to run security tests
run_security_tests() {
    print_status "Running security tests..."
    
    cd "$PROJECT_PATH"
    
    # Run Bandit security linter
    print_status "Running Bandit security linter..."
    bandit -r . -f json -o bandit-report.json || true
    
    # Run Safety dependency check
    print_status "Running Safety dependency check..."
    safety check --json --output safety-report.json || true
    
    # Run Semgrep static analysis
    print_status "Running Semgrep static analysis..."
    semgrep --config=auto --json --output semgrep-report.json . || true
    
    # Run pip-audit
    print_status "Running pip-audit..."
    pip-audit --format=json --output pip-audit-report.json || true
    
    print_success "Security tests completed"
}

# Function to run performance tests
run_performance_tests() {
    print_status "Running performance tests..."
    
    cd "$PROJECT_PATH"
    
    if [ -d "tests/performance" ]; then
        # Run benchmark tests
        print_status "Running benchmark tests..."
        python3 -m pytest tests/performance/ --benchmark-json=benchmark-report.json || true
        
        # Run memory profiling if available
        if [ -f "tests/performance/memory_test.py" ]; then
            print_status "Running memory profiling..."
            python3 -m memory_profiler tests/performance/memory_test.py || true
        fi
        
        print_success "Performance tests completed"
    else
        print_warning "No performance tests found in tests/performance/"
    fi
}

# Function to run load tests
run_load_tests() {
    print_status "Running load tests..."
    
    if [ -z "$TARGET_URL" ]; then
        print_error "Target URL is required for load tests. Use --target-url option."
        return 1
    fi
    
    cd "$PROJECT_PATH"
    
    # Check if locustfile exists
    if [ -f "locustfile.py" ]; then
        print_status "Running Locust load tests against $TARGET_URL..."
        locust --host="$TARGET_URL" --headless --users=100 --spawn-rate=10 --run-time=300s --html=load-test-report.html || true
        print_success "Load tests completed"
    else
        print_warning "No locustfile.py found. Creating sample load test..."
        create_sample_load_test
        locust --host="$TARGET_URL" --headless --users=100 --spawn-rate=10 --run-time=300s --html=load-test-report.html || true
        print_success "Load tests completed"
    fi
}

# Function to create sample load test
create_sample_load_test() {
    cat > locustfile.py << 'EOF'
from locust import HttpUser, task, between

class WebsiteUser(HttpUser):
    wait_time = between(1, 5)
    
    @task(3)
    def index_page(self):
        self.client.get("/")
    
    @task(2)
    def about_page(self):
        self.client.get("/about")
    
    @task(1)
    def contact_page(self):
        self.client.get("/contact")
EOF
    print_status "Sample load test created"
}

# Function to generate test report
generate_test_report() {
    print_status "Generating test report..."
    
    cd "$PROJECT_PATH"
    
    # Create HTML report
    cat > test-report.html << EOF
<!DOCTYPE html>
<html>
<head>
    <title>Test Report</title>
    <style>
        body { font-family: Arial, sans-serif; margin: 20px; }
        .header { background-color: #f0f0f0; padding: 20px; border-radius: 5px; }
        .section { margin: 20px 0; }
        .passed { color: green; }
        .failed { color: red; }
        .warning { color: orange; }
        pre { background-color: #f5f5f5; padding: 10px; border-radius: 3px; overflow-x: auto; }
    </style>
</head>
<body>
    <div class="header">
        <h1>Test Report</h1>
        <p>Generated: $(date)</p>
        <p>Project: $PROJECT_PATH</p>
    </div>
    
    <div class="section">
        <h2>Test Summary</h2>
        <p>Test Type: $TEST_TYPE</p>
        <p>Target URL: ${TARGET_URL:-"N/A"}</p>
        <p>Parallel: $PARALLEL</p>
    </div>
    
    <div class="section">
        <h2>Test Results</h2>
        <p>Check individual test output files for detailed results.</p>
    </div>
</body>
</html>
EOF
    
    print_success "Test report generated: test-report.html"
}

# Function to upload test results
upload_test_results() {
    if [ -n "$S3_BUCKET" ]; then
        print_status "Uploading test results to S3..."
        
        timestamp=$(date +%Y%m%d_%H%M%S)
        
        # Upload all report files
        for file in *.json *.html; do
            if [ -f "$file" ]; then
                aws s3 cp "$file" "s3://$S3_BUCKET/test-results/$timestamp/$file" || true
            fi
        done
        
        print_success "Test results uploaded to S3"
    else
        print_warning "S3_BUCKET not set, skipping upload"
    fi
}

# Parse command line arguments
while [[ $# -gt 0 ]]; do
    case $1 in
        -t|--test-type)
            TEST_TYPE="$2"
            shift 2
            ;;
        -p|--project-path)
            PROJECT_PATH="$2"
            shift 2
            ;;
        -u|--target-url)
            TARGET_URL="$2"
            shift 2
            ;;
        -v|--verbose)
            VERBOSE=true
            shift
            ;;
        -P|--parallel)
            PARALLEL=true
            shift
            ;;
        -h|--help)
            show_usage
            exit 0
            ;;
        *)
            print_error "Unknown option: $1"
            show_usage
            exit 1
            ;;
    esac
done

# Main execution
main() {
    print_status "Starting test execution..."
    
    # Check prerequisites
    check_prerequisites
    
    # Run tests based on type
    case $TEST_TYPE in
        unit)
            run_unit_tests
            ;;
        integration)
            run_integration_tests
            ;;
        security)
            run_security_tests
            ;;
        performance)
            run_performance_tests
            ;;
        load)
            run_load_tests
            ;;
        all)
            run_unit_tests
            run_integration_tests
            run_security_tests
            run_performance_tests
            if [ -n "$TARGET_URL" ]; then
                run_load_tests
            fi
            ;;
        *)
            print_error "Unknown test type: $TEST_TYPE"
            show_usage
            exit 1
            ;;
    esac
    
    # Generate test report
    generate_test_report
    
    # Upload test results
    upload_test_results
    
    print_success "Test execution completed successfully!"
}

# Run main function
main "$@"