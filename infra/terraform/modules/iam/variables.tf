variable "name_prefix" {
  type = string
}

variable "knowledge_bucket_arn" {
  type = string
}

variable "incidents_table_arn" {
  type = string
}

variable "bedrock_model_id" {
  type = string
}

variable "knowledge_base_collection_arn" {
  type = string
}

variable "embedding_model_arn" {
  type    = string
  default = "arn:aws:bedrock:us-east-1::foundation-model/amazon.titan-embed-text-v2:0"
}

variable "tags" {
  type = map(string)
}
