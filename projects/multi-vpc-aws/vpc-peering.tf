# VPC Peering Connections

# Production to Development VPC Peering
resource "aws_vpc_peering_connection" "prod_to_dev" {
  vpc_id      = aws_vpc.main["production"].id
  peer_vpc_id = aws_vpc.main["development"].id
  auto_accept = true

  tags = {
    Name = "${var.project_name}-prod-to-dev-peering"
  }
}

# Production to Shared Services VPC Peering
resource "aws_vpc_peering_connection" "prod_to_shared" {
  vpc_id      = aws_vpc.main["production"].id
  peer_vpc_id = aws_vpc.main["shared_services"].id
  auto_accept = true

  tags = {
    Name = "${var.project_name}-prod-to-shared-peering"
  }
}

# Development to Shared Services VPC Peering
resource "aws_vpc_peering_connection" "dev_to_shared" {
  vpc_id      = aws_vpc.main["development"].id
  peer_vpc_id = aws_vpc.main["shared_services"].id
  auto_accept = true

  tags = {
    Name = "${var.project_name}-dev-to-shared-peering"
  }
}

# Production to DMZ VPC Peering
resource "aws_vpc_peering_connection" "prod_to_dmz" {
  vpc_id      = aws_vpc.main["production"].id
  peer_vpc_id = aws_vpc.main["dmz"].id
  auto_accept = true

  tags = {
    Name = "${var.project_name}-prod-to-dmz-peering"
  }
}

# Development to DMZ VPC Peering
resource "aws_vpc_peering_connection" "dev_to_dmz" {
  vpc_id      = aws_vpc.main["development"].id
  peer_vpc_id = aws_vpc.main["dmz"].id
  auto_accept = true

  tags = {
    Name = "${var.project_name}-dev-to-dmz-peering"
  }
}

# Route Table Entries for VPC Peering

# Production Route Table - Route to Development
resource "aws_route" "prod_to_dev" {
  route_table_id            = aws_route_table.private["production"].id
  destination_cidr_block    = var.vpc_cidr_blocks["development"]
  vpc_peering_connection_id = aws_vpc_peering_connection.prod_to_dev.id
}

# Production Route Table - Route to Shared Services
resource "aws_route" "prod_to_shared" {
  route_table_id            = aws_route_table.private["production"].id
  destination_cidr_block    = var.vpc_cidr_blocks["shared_services"]
  vpc_peering_connection_id = aws_vpc_peering_connection.prod_to_shared.id
}

# Production Route Table - Route to DMZ
resource "aws_route" "prod_to_dmz" {
  route_table_id            = aws_route_table.private["production"].id
  destination_cidr_block    = var.vpc_cidr_blocks["dmz"]
  vpc_peering_connection_id = aws_vpc_peering_connection.prod_to_dmz.id
}

# Development Route Table - Route to Production
resource "aws_route" "dev_to_prod" {
  route_table_id            = aws_route_table.private["development"].id
  destination_cidr_block    = var.vpc_cidr_blocks["production"]
  vpc_peering_connection_id = aws_vpc_peering_connection.prod_to_dev.id
}

# Development Route Table - Route to Shared Services
resource "aws_route" "dev_to_shared" {
  route_table_id            = aws_route_table.private["development"].id
  destination_cidr_block    = var.vpc_cidr_blocks["shared_services"]
  vpc_peering_connection_id = aws_vpc_peering_connection.dev_to_shared.id
}

# Development Route Table - Route to DMZ
resource "aws_route" "dev_to_dmz" {
  route_table_id            = aws_route_table.private["development"].id
  destination_cidr_block    = var.vpc_cidr_blocks["dmz"]
  vpc_peering_connection_id = aws_vpc_peering_connection.dev_to_dmz.id
}

# Shared Services Route Table - Route to Production
resource "aws_route" "shared_to_prod" {
  route_table_id            = aws_route_table.private["shared_services"].id
  destination_cidr_block    = var.vpc_cidr_blocks["production"]
  vpc_peering_connection_id = aws_vpc_peering_connection.prod_to_shared.id
}

# Shared Services Route Table - Route to Development
resource "aws_route" "shared_to_dev" {
  route_table_id            = aws_route_table.private["shared_services"].id
  destination_cidr_block    = var.vpc_cidr_blocks["development"]
  vpc_peering_connection_id = aws_vpc_peering_connection.dev_to_shared.id
}

# DMZ Route Table - Route to Production
resource "aws_route" "dmz_to_prod" {
  route_table_id            = aws_route_table.public["dmz"].id
  destination_cidr_block    = var.vpc_cidr_blocks["production"]
  vpc_peering_connection_id = aws_vpc_peering_connection.prod_to_dmz.id
}

# DMZ Route Table - Route to Development
resource "aws_route" "dmz_to_dev" {
  route_table_id            = aws_route_table.public["dmz"].id
  destination_cidr_block    = var.vpc_cidr_blocks["development"]
  vpc_peering_connection_id = aws_vpc_peering_connection.dev_to_dmz.id
}

# DMZ Route Table - Route to Shared Services
resource "aws_route" "dmz_to_shared" {
  route_table_id            = aws_route_table.public["dmz"].id
  destination_cidr_block    = var.vpc_cidr_blocks["shared_services"]
  vpc_peering_connection_id = aws_vpc_peering_connection.dev_to_shared.id
}
