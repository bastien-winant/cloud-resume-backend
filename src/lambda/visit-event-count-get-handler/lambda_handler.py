import json
import logging
import boto3
from config import get_config
from visitor_metrics import VisitEventMetrics


# Configure logging
logging.basicConfig(level=logging.INFO, format="%(levelname)s: %(message)s")
logger = logging.getLogger(__name__)


def lambda_handler(event, context):
	logger.info(event)

	headers = { "Content-Type": "application/json" }

	config = get_config()

	table_name = config.table_name
	region = config.region

	try:
		dynamodb = boto3.resource("dynamodb", region_name=region)
		client = VisitEventMetrics(dynamodb)

		table_exists = client.exists(table_name)
		if not table_exists:
			raise Exception(f"Table {table_name} does not exist.")

		# retrieve current count from the database
		metric = client.get_metric("count")
		current_count = metric["value"]
	except Exception as err:
		logger.info(f"Put record failed: {err}")
		return {
			'statusCode': 500,
			'headers': headers,
			'body': json.dumps({'error': f"Put record failed: {err}"}),
		}
	else:
		return {
			'statusCode': 200,
			'headers': headers,
			'body': json.dumps({'count': str(current_count)}),
		}