import logging
import os

import boto3
from app.cords.config import AWS_REGION, SQL_CLUSTER_ENDPOINT, SSL_CERT_PATH, SCHEMA
from psycopg import pq
from sqlalchemy import event
from sqlmodel import Session, create_engine


CLUSTER_USER = "admin"

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


def create_sql_engine():
