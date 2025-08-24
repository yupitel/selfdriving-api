import os

from dotenv import load_dotenv

# environment variables
AWS_REGION = os.getenv("AWS_REGION", "us-west-2")
SQL_CLUSTER_ENDPOINT = os.getenv("SQL_CLUSTER_ENDPOINT", "http://localhost:5432")
BULK_INSERT_MAX_NUM = int(os.getenv("BULK_INSERT_MAX_NUM", 1000))

SSL_CERT_PATH = "./root.pem"
SCHEMA = "selfdriving"
