# Create VPCs
resource "aws_vpc" "main" {
  for_each = var.vpc_cidr_blocks

  cidr_block           = each.value
  enable_dns_hostnames = true
  enable_dns_support   = true

  tags = {
    Name = "${var.project_name}-${each.key}-vpc"
    Type = each.key
  }
}

# Create Internet Gateways
resource "aws_internet_gateway" "main" {
  for_each = aws_vpc.main

  vpc_id = each.value.id

  tags = {
    Name = "${var.project_name}-${each.key}-igw"
  }
}

# Create EIPs for NAT Gateways
resource "aws_eip" "nat" {
  for_each = var.enable_nat_gateway ? aws_vpc.main : {}

  domain = "vpc"
  depends_on = [aws_internet_gateway.main]

  tags = {
    Name = "${var.project_name}-${each.key}-nat-eip"
  }
}

# Create NAT Gateways
resource "aws_nat_gateway" "main" {
  for_each = var.enable_nat_gateway ? aws_vpc.main : {}

  allocation_id = aws_eip.nat[each.key].id
  subnet_id     = aws_subnet.public[each.key][0].id

  tags = {
    Name = "${var.project_name}-${each.key}-nat"
  }

  depends_on = [aws_internet_gateway.main]
}

# Create Public Subnets
resource "aws_subnet" "public" {
  for_each = {
    for pair in setproduct(keys(var.public_subnet_cidrs), range(length(var.public_subnet_cidrs[keys(var.public_subnet_cidrs)[0]]))) : 
    "${pair[0]}-${pair[1]}" => {
      vpc_key = pair[0]
      az_index = pair[1]
      cidr = var.public_subnet_cidrs[pair[0]][pair[1]]
    }
  }

  vpc_id                  = aws_vpc.main[each.value.vpc_key].id
  cidr_block              = each.value.cidr
  availability_zone       = data.aws_availability_zones.available.names[each.value.az_index]
  map_public_ip_on_launch = true

  tags = {
    Name = "${var.project_name}-${each.value.vpc_key}-public-${each.value.az_index + 1}"
    Type = "public"
  }
}

# Create Private Subnets
resource "aws_subnet" "private" {
  for_each = {
    for pair in setproduct(keys(var.private_subnet_cidrs), range(length(var.private_subnet_cidrs[keys(var.private_subnet_cidrs)[0]]))) : 
    "${pair[0]}-${pair[1]}" => {
      vpc_key = pair[0]
      az_index = pair[1]
      cidr = var.private_subnet_cidrs[pair[0]][pair[1]]
    }
  }

  vpc_id            = aws_vpc.main[each.value.vpc_key].id
  cidr_block        = each.value.cidr
  availability_zone = data.aws_availability_zones.available.names[each.value.az_index]

  tags = {
    Name = "${var.project_name}-${each.value.vpc_key}-private-${each.value.az_index + 1}"
    Type = "private"
  }
}

# Create Database Subnets
resource "aws_subnet" "database" {
  for_each = {
    for pair in setproduct(keys(var.database_subnet_cidrs), range(length(var.database_subnet_cidrs[keys(var.database_subnet_cidrs)[0]]))) : 
    "${pair[0]}-${pair[1]}" => {
      vpc_key = pair[0]
      az_index = pair[1]
      cidr = var.database_subnet_cidrs[pair[0]][pair[1]]
    }
  }

  vpc_id            = aws_vpc.main[each.value.vpc_key].id
  cidr_block        = each.value.cidr
  availability_zone = data.aws_availability_zones.available.names[each.value.az_index]

  tags = {
    Name = "${var.project_name}-${each.value.vpc_key}-database-${each.value.az_index + 1}"
    Type = "database"
  }
}

# Create Database Subnet Groups
resource "aws_db_subnet_group" "main" {
  for_each = aws_vpc.main

  name       = "${var.project_name}-${each.key}-db-subnet-group"
  subnet_ids = [for subnet in aws_subnet.database : subnet.id if split("-", subnet.tags["Name"])[1] == each.key]

  tags = {
    Name = "${var.project_name}-${each.key}-db-subnet-group"
  }
}

# Create Public Route Tables
resource "aws_route_table" "public" {
  for_each = aws_vpc.main

  vpc_id = each.value.id

  route {
    cidr_block = "0.0.0.0/0"
    gateway_id = aws_internet_gateway.main[each.key].id
  }

  tags = {
    Name = "${var.project_name}-${each.key}-public-rt"
  }
}

# Create Private Route Tables
resource "aws_route_table" "private" {
  for_each = var.enable_nat_gateway ? aws_vpc.main : {}

  vpc_id = each.value.id

  route {
    cidr_block     = "0.0.0.0/0"
    nat_gateway_id = aws_nat_gateway.main[each.key].id
  }

  tags = {
    Name = "${var.project_name}-${each.key}-private-rt"
  }
}

# Associate Public Subnets with Public Route Tables
resource "aws_route_table_association" "public" {
  for_each = aws_subnet.public

  subnet_id      = each.value.id
  route_table_id = aws_route_table.public[split("-", each.key)[0]].id
}

# Associate Private Subnets with Private Route Tables
resource "aws_route_table_association" "private" {
  for_each = var.enable_nat_gateway ? aws_subnet.private : {}

  subnet_id      = each.value.id
  route_table_id = aws_route_table.private[split("-", each.key)[0]].id
}

# Associate Database Subnets with Private Route Tables
resource "aws_route_table_association" "database" {
  for_each = var.enable_nat_gateway ? aws_subnet.database : {}

  subnet_id      = each.value.id
  route_table_id = aws_route_table.private[split("-", each.key)[0]].id
}

# VPC Flow Logs
resource "aws_flow_log" "main" {
  for_each = var.enable_vpc_flow_logs ? aws_vpc.main : {}

  log_destination_type = "cloud-watch-logs"
  log_group_name       = "/aws/vpc/${each.value.id}/flow-logs"
  traffic_type         = "ALL"
  vpc_id               = each.value.id

  tags = {
    Name = "${var.project_name}-${each.key}-flow-logs"
  }
}

# CloudWatch Log Group for VPC Flow Logs
resource "aws_cloudwatch_log_group" "vpc_flow_logs" {
  for_each = var.enable_vpc_flow_logs ? aws_vpc.main : {}

  name              = "/aws/vpc/${each.value.id}/flow-logs"
  retention_in_days = 7

  tags = {
    Name = "${var.project_name}-${each.key}-flow-logs"
  }
}
