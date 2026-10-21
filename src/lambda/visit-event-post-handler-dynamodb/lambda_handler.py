import logging
from visit_events import VisitEvents
import boto3

_TABLE_NAME = "cloud-resume-visit-events"
_REGION = "eu-central-1"


# Configure logging
logging.basicConfig(level=logging.INFO, format="%(levelname)s: %(message)s")
logger = logging.getLogger(__name__)


def lambda_hander(event, context):
  logger.info(event)
  print("EVENT: ", event)

  dynamodb = boto3.resource("dynamodb", region_name = _REGION)
  visit_events = VisitEvents(dynamodb)

  table_exists = visit_events.exists(_TABLE_NAME)

  if not table_exists:
    visit_events.create_table(_TABLE_NAME)

  visit_events.add_event(event)