variable "aws_region" {
  type    = string
  default = "eu-west-2"
}

variable "app_version" {
  type    = string
  default = "local"
  validation {
    condition     = can(regex("^[A-Za-z0-9._-]{1,64}$", var.app_version))
    error_message = "Use a commit SHA or short version string."
  }
}

variable "alarm_topic_arn" {
  description = "Optional existing SNS topic ARN; empty means alarms have no notifications."
  type        = string
  default     = ""
}
