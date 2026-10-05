terraform {
  required_version = ">= 1.14.6, < 2.0.0"
  required_providers {
    aws = {
      source  = "hashicorp/aws"
      version = "~> 6.0"
    }
  }
  backend "s3" {}
}

provider "aws" {
  region = var.aws_region
  default_tags {
    tags = {
      Project   = "releaseops"
      ManagedBy = "Terraform"
      Purpose   = "portfolio-lab"
    }
  }
}
