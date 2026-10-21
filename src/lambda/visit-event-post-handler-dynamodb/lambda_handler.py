import logging
from visit_events import VisitEvents
import boto3

from config import get_config


# Configure logging
logging.basicConfig(level=logging.INFO, format="%(levelname)s: %(message)s")
logger = logging.getLogger(__name__)


def lambda_hander(event, context):
  logger.info(event)
  print("EVENT: ", event)

  config = get_config()
  dynamodb = boto3.resource("dynamodb", region_name = config.region)
  visit_events = VisitEvents(dynamodb)

  table_exists = visit_events.exists(config.table_name)

  if not table_exists:
    visit_events.create_table(config.table_name)

  visit_events.add_event(event)