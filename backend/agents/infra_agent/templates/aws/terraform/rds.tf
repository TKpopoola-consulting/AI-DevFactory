resource "aws_db_instance" "main" {
  identifier             = "${var.app_name}-db"
  engine                 = "postgres"
  engine_version         = "15.2"
  instance_class         = "db.t3.micro"
  allocated_storage      = 20
  storage_type           = "gp2"
  db_name                = var.db_name
  username               = var.db_username
  password               = var.db_password
  parameter_group_name   = "default.postgres15"
  skip_final_snapshot    = true
  vpc_security_group_ids = [aws_security_group.rds.id]
}

resource "aws_security_group" "rds" {
  name        = "${var.app_name}-rds-sg"
  description = "Allow inbound from ECS"
  
  ingress {
    from_port       = 5432
    to_port         = 5432
    protocol        = "tcp"
    security_groups = [var.ecs_security_group_id]
  }
  
  egress {
    from_port   = 0
    to_port     = 0
    protocol    = "-1"
    cidr_blocks = ["0.0.0.0/0"]
  }
}