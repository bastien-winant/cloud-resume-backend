import logging
import json
from config import get_config
from firehose_client import FirehoseClient

# Configure logging
logging.basicConfig(level=logging.INFO, format="%(levelname)s: %(message)s")
logger = logging.getLogger(__name__)


def lambda_handler(event, context):
	logger.info(event)
	print("EVENT: ", event)

	status_code = 200
	headers = { "Content-Type": "application/json" }

	config = get_config()
	client = FirehoseClient(config)

	try:
		client.put_record(event)
	except Exception as e:
		status_code = 500
		logger.info(f"Put record failed after retries and backoff: {e}")

	client.monitor_metrics()
	
	return {
		"statusCode": status_code,
		"headers": headers,
		"body": json.dumps(event)
	}