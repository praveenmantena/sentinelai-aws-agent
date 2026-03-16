variable "api_name" {
  type = string
}

variable "lambda_invoke_arn" {
  type = string
}

variable "lambda_function_name" {
  type = string
}

variable "cors_allow_origins" {
  type    = list(string)
  default = ["*"]
}

variable "tags" {
  type = map(string)
}
