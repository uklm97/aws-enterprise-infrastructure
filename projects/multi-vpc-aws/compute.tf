# Data sources for AMI and key pair
data "aws_ami" "amazon_linux" {
  most_recent = true
  owners      = ["amazon"]

  filter {
    name   = "name"
    values = ["amzn2-ami-hvm-*-x86_64-gp2"]
  }
}

# Key Pair
resource "aws_key_pair" "main" {
  key_name   = "${var.project_name}-key"
  public_key = file("${path.module}/ssh_key.pub")
}

# Launch Templates
resource "aws_launch_template" "production" {
  name_prefix   = "${var.project_name}-production-"
  image_id      = data.aws_ami.amazon_linux.id
  instance_type = var.instance_type

  key_name = aws_key_pair.main.key_name

  network_interfaces {
    associate_public_ip_address = false
    security_groups             = [aws_security_group.production_web.id]
  }

  user_data = base64encode(templatefile("${path.module}/user_data.sh", {
    environment = "production"
  }))

  tag_specifications {
    resource_type = "instance"
    tags = {
      Name = "${var.project_name}-production-instance"
    }
  }
}

resource "aws_launch_template" "development" {
  name_prefix   = "${var.project_name}-development-"
  image_id      = data.aws_ami.amazon_linux.id
  instance_type = var.instance_type

  key_name = aws_key_pair.main.key_name

  network_interfaces {
    associate_public_ip_address = false
    security_groups             = [aws_security_group.development_web.id]
  }

  user_data = base64encode(templatefile("${path.module}/user_data.sh", {
    environment = "development"
  }))

  tag_specifications {
    resource_type = "instance"
    tags = {
      Name = "${var.project_name}-development-instance"
    }
  }
}

# Auto Scaling Groups
resource "aws_autoscaling_group" "production" {
  name                = "${var.project_name}-production-asg"
  desired_capacity    = 2
  max_size            = 4
  min_size            = 1
  target_group_arns   = [aws_lb_target_group.production.arn]
  vpc_zone_identifier = [for subnet in aws_subnet.private : subnet.id if split("-", subnet.tags["Name"])[1] == "production"]

  launch_template {
    id      = aws_launch_template.production.id
    version = "$Latest"
  }

  tag {
    key                 = "Name"
    value               = "${var.project_name}-production-instance"
    propagate_at_launch = true
  }
}

resource "aws_autoscaling_group" "development" {
  name                = "${var.project_name}-development-asg"
  desired_capacity    = 1
  max_size            = 2
  min_size            = 1
  target_group_arns   = [aws_lb_target_group.development.arn]
  vpc_zone_identifier = [for subnet in aws_subnet.private : subnet.id if split("-", subnet.tags["Name"])[1] == "development"]

  launch_template {
    id      = aws_launch_template.development.id
    version = "$Latest"
  }

  tag {
    key                 = "Name"
    value               = "${var.project_name}-development-instance"
    propagate_at_launch = true
  }
}

# Application Load Balancers
resource "aws_lb" "production" {
  name               = "${var.project_name}-production-alb"
  internal           = false
  load_balancer_type = "application"
  security_groups    = [aws_security_group.production_alb.id]
  subnets            = [for subnet in aws_subnet.public : subnet.id if split("-", subnet.tags["Name"])[1] == "production"]

  enable_deletion_protection = false

  tags = {
    Name = "${var.project_name}-production-alb"
  }
}

resource "aws_lb" "development" {
  name               = "${var.project_name}-development-alb"
  internal           = false
  load_balancer_type = "application"
  security_groups    = [aws_security_group.development_alb.id]
  subnets            = [for subnet in aws_subnet.public : subnet.id if split("-", subnet.tags["Name"])[1] == "development"]

  enable_deletion_protection = false

  tags = {
    Name = "${var.project_name}-development-alb"
  }
}

# Target Groups
resource "aws_lb_target_group" "production" {
  name     = "${var.project_name}-production-tg"
  port     = 80
  protocol = "HTTP"
  vpc_id   = aws_vpc.main["production"].id

  health_check {
    enabled             = true
    healthy_threshold   = 2
    interval            = 30
    matcher             = "200"
    path                = "/"
    port                = "traffic-port"
    protocol            = "HTTP"
    timeout             = 5
    unhealthy_threshold = 2
  }
}

resource "aws_lb_target_group" "development" {
  name     = "${var.project_name}-development-tg"
  port     = 80
  protocol = "HTTP"
  vpc_id   = aws_vpc.main["development"].id

  health_check {
    enabled             = true
    healthy_threshold   = 2
    interval            = 30
    matcher             = "200"
    path                = "/"
    port                = "traffic-port"
    protocol            = "HTTP"
    timeout             = 5
    unhealthy_threshold = 2
  }
}

# Listener Rules
resource "aws_lb_listener" "production" {
  load_balancer_arn = aws_lb.production.arn
  port              = "80"
  protocol          = "HTTP"

  default_action {
    type             = "forward"
    target_group_arn = aws_lb_target_group.production.arn
  }
}

resource "aws_lb_listener" "development" {
  load_balancer_arn = aws_lb.development.arn
  port              = "80"
  protocol          = "HTTP"

  default_action {
    type             = "forward"
    target_group_arn = aws_lb_target_group.development.arn
  }
}

# Bastion Host
resource "aws_instance" "bastion" {
  ami           = data.aws_ami.amazon_linux.id
  instance_type = "t3.micro"
  key_name      = aws_key_pair.main.key_name

  subnet_id                   = aws_subnet.public["dmz-0"].id
  vpc_security_group_ids      = [aws_security_group.bastion.id]
  associate_public_ip_address = true

  user_data = base64encode(templatefile("${path.module}/bastion_user_data.sh", {}))

  tags = {
    Name = "${var.project_name}-bastion-host"
  }
}

# Auto Scaling Policies
resource "aws_autoscaling_policy" "production_cpu" {
  name                   = "${var.project_name}-production-cpu-policy"
  scaling_adjustment     = 1
  adjustment_type        = "ChangeInCapacity"
  cooldown               = 300
  autoscaling_group_name = aws_autoscaling_group.production.name
}

resource "aws_autoscaling_policy" "production_cpu_down" {
  name                   = "${var.project_name}-production-cpu-down-policy"
  scaling_adjustment     = -1
  adjustment_type        = "ChangeInCapacity"
  cooldown               = 300
  autoscaling_group_name = aws_autoscaling_group.production.name
}

resource "aws_autoscaling_policy" "development_cpu" {
  name                   = "${var.project_name}-development-cpu-policy"
  scaling_adjustment     = 1
  adjustment_type        = "ChangeInCapacity"
  cooldown               = 300
  autoscaling_group_name = aws_autoscaling_group.development.name
}

resource "aws_autoscaling_policy" "development_cpu_down" {
  name                   = "${var.project_name}-development-cpu-down-policy"
  scaling_adjustment     = -1
  adjustment_type        = "ChangeInCapacity"
  cooldown               = 300
  autoscaling_group_name = aws_autoscaling_group.development.name
}

# CloudWatch Alarms for Auto Scaling
resource "aws_cloudwatch_metric_alarm" "production_cpu_high" {
  alarm_name          = "${var.project_name}-production-cpu-high"
  comparison_operator = "GreaterThanThreshold"
  evaluation_periods  = "2"
  metric_name         = "CPUUtilization"
  namespace           = "AWS/EC2"
  period              = "120"
  statistic           = "Average"
  threshold           = "80"
  alarm_description   = "This metric monitors production EC2 CPU utilization"
  alarm_actions       = [aws_autoscaling_policy.production_cpu.arn]

  dimensions = {
    AutoScalingGroupName = aws_autoscaling_group.production.name
  }
}

resource "aws_cloudwatch_metric_alarm" "production_cpu_low" {
  alarm_name          = "${var.project_name}-production-cpu-low"
  comparison_operator = "LessThanThreshold"
  evaluation_periods  = "2"
  metric_name         = "CPUUtilization"
  namespace           = "AWS/EC2"
  period              = "120"
  statistic           = "Average"
  threshold           = "20"
  alarm_description   = "This metric monitors production EC2 CPU utilization"
  alarm_actions       = [aws_autoscaling_policy.production_cpu_down.arn]

  dimensions = {
    AutoScalingGroupName = aws_autoscaling_group.production.name
  }
}

resource "aws_cloudwatch_metric_alarm" "development_cpu_high" {
  alarm_name          = "${var.project_name}-development-cpu-high"
  comparison_operator = "GreaterThanThreshold"
  evaluation_periods  = "2"
  metric_name         = "CPUUtilization"
  namespace           = "AWS/EC2"
  period              = "120"
  statistic           = "Average"
  threshold           = "80"
  alarm_description   = "This metric monitors development EC2 CPU utilization"
  alarm_actions       = [aws_autoscaling_policy.development_cpu.arn]

  dimensions = {
    AutoScalingGroupName = aws_autoscaling_group.development.name
  }
}

resource "aws_cloudwatch_metric_alarm" "development_cpu_low" {
  alarm_name          = "${var.project_name}-development-cpu-low"
  comparison_operator = "LessThanThreshold"
  evaluation_periods  = "2"
  metric_name         = "CPUUtilization"
  namespace           = "AWS/EC2"
  period              = "120"
  statistic           = "Average"
  threshold           = "20"
  alarm_description   = "This metric monitors development EC2 CPU utilization"
  alarm_actions       = [aws_autoscaling_policy.development_cpu_down.arn]

  dimensions = {
    AutoScalingGroupName = aws_autoscaling_group.development.name
  }
}
