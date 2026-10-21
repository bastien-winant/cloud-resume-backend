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
  print("EVENT: ", event)
  
  headers = { "Content-Type": "application/json" }

  config = get_config()
  dynamodb = boto3.resource("dynamodb", region_name = config.region)
  visit_events = VisitEvents(dynamodb)

  try:
    table_exists = visit_events.exists(config.table_name)

    if not table_exists:
      raise Exception(f"Table {config.table_name} does not exist.")

    count = visit_events.get_item_count(config.table_name)
    
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
    'statusCode': 200,
    'headers': headers,
    'body': json.dumps({"count": str(count)}),
  }