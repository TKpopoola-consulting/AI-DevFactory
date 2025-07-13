resource "aws_s3_bucket" "assets" {
  bucket = "${var.app_name}-assets-${random_id.bucket_suffix.hex}"
  acl    = "private"

  versioning {
    enabled = true
  }

  server_side_encryption_configuration {
    rule {
      apply_server_side_encryption_by_default {
        sse_algorithm = "AES256"
      }
    }
  }
}

resource "random_id" "bucket_suffix" {
  byte_length = 8
}

resource "aws_s3_bucket_policy" "cloudfront" {
  bucket = aws_s3_bucket.assets.id
  policy = data.aws_iam_policy_document.cloudfront.json
}

data "aws_iam_policy_document" "cloudfront" {
  statement {
    actions   = ["s3:GetObject"]
    resources = ["${aws_s3_bucket.assets.arn}/*"]
    
    principals {
      type        = "AWS"
      identifiers = [aws_cloudfront_origin_access_identity.assets.iam_arn]
    }
  }
}