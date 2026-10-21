import logging
import json
from config import get_config
from firehose_client import FirehoseClient

# Configure logging
logging.basicConfig(level=logging.INFO, format="%(levelname)s: %(message)s")
logger = logging.getLogger(__name__)


def lambda_handler(event, context):
	logger.info(event)

	headers = { "Content-Type": "application/json" }

	config = get_config()
	client = FirehoseClient(config)

	try:
		client.put_record(event)
	except Exception as err:
		logger.info(f"Put record failed after retries and backoff: {err}")
		return {
			'statusCode': 500,
			'headers': headers,
			'body': json.dumps({
				'message': err.response["Error"]["Code"],
				'error': err.response["Error"]["Message"],
			}),
		}

	client.monitor_metrics()
	
	return {
		"statusCode": 200,
		"headers": headers,
		"body": json.dumps(event)
	}