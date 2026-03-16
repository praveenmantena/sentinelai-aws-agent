variable "function_name" {
  type = string
}

variable "lambda_role_arn" {
  type = string
}

variable "package_path" {
  type = string
}

variable "source_code_hash" {
  type = string
}

variable "log_retention_days" {
  type = number
}

variable "environment_variables" {
  type = map(string)
}

variable "tags" {
  type = map(string)
}
