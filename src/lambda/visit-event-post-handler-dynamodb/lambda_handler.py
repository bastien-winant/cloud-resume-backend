import logging
from visit_events import VisitEvents
import boto3
import json

from config import get_config


# Configure logging
logging.basicConfig(level=logging.INFO, format="%(levelname)s: %(message)s")
logger = logging.getLogger(__name__)


def lambda_hander(event, context):
  logger.info(event)

  headers = { "Content-Type": "application/json" }

  config = get_config()
  dynamodb = boto3.resource("dynamodb", region_name = config.region)
  visit_events = VisitEvents(dynamodb)

  try:
    # ensure the dynamodb table exists
    visit_events.exists(config.table_name)

    headers = event.get("headers", {})
    request_context = event.get("requestContext", {})

    request_id = request_context["requestId"]
    timestamp = request_context["time"]
    source_ip = headers["x-forwarded-for"]
    user_agent = headers["user-agent"]

    record = {
      "requestId": request_id,
      "timestamp": timestamp,
      "sourceIp": source_ip,
      "userAgent": user_agent
    }

    # save the record to dynamodb
    visit_events.add_event(record)
  except Exception as err:
    return {
      'statusCode': 500,
      'headers': headers,
      'body': json.dumps({
        'message': err.response["Error"]["Code"],
        'error': err.response["Error"]["Message"],
      }),
    }

  return {
    "statusCode": 200,
    "headers": headers,
    "body": json.dumps(event)
  }