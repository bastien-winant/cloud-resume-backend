from decimal import Decimal
import json
import logging
import boto3
# from config import get_config
from botocore.exceptions import ClientError

class Config:
  def __init__(self):
    self.table_name = "CloudResumeVisitEventMetrics"
    self.region = "eu-central-1"


def get_config():
	return Config()

# Configure logging
logging.basicConfig(level=logging.INFO, format="%(levelname)s: %(message)s")
logger = logging.getLogger(__name__)


class VisitEvents:
	"""Encapsulates an Amazon DynamoDB table of visit event data.

	Example data structure for a visit event record in this table:
		{
			"name": "count"",
			"value": 123
		}
	"""

	def __init__(self, dyn_resource):
		"""
		:param dyn_resource: A Boto3 DynamoDB resource.
		"""
		self.dyn_resource = dyn_resource
		# The table variable is set during the scenario in the call to
		# 'exists' if the table exists. Otherwise, it is set by 'create_table'.
		self.table = None

	def exists(self, table_name):
		"""
		Determines whether a table exists. As a side effect, stores the table in
		a member variable.

		:param table_name: The name of the table to check.
		:return: True when the table exists; otherwise, False.
		"""
		try:
			table = self.dyn_resource.Table(table_name)
			table.load()
			exists = True
		except ClientError as err:
			if err.response["Error"]["Code"] == "ResourceNotFoundException":
				exists = False
			else:
				logger.error(
					"Couldn't check for existence of %s. Here's why: %s: %s",
					table_name,
					err.response["Error"]["Code"],
					err.response["Error"]["Message"],
				)
				raise
		else:
			self.table = table
		return exists

	def add_metric(self, name, value):
		"""
		Adds a metric to the table.

		:param name: The name of the metric.
		:param value: The initial value of the metric.
		"""
		try:
			self.table.put_item(
				Item={
					"name": name,
					"value": value,
				}
			)
		except ClientError as err:
			logger.error(
				"Couldn't add metric %s to table %s. Here's why: %s: %s",
				name,
				self.table.name,
				err.response["Error"]["Code"],
				err.response["Error"]["Message"],
			)
			raise

	def get_metric(self, name):
		"""
		Gets metric data from the table for a specific metric.

		:param name: The name of the metric.
		:return: The data about the requested metric.
		"""
		try:
			response = self.table.get_item(Key={"name": name})
		except ClientError as err:
			if err.response["Error"]["Code"] == "ResourceNotFoundException":
				return { "name": name, "value": Decimal() }
			logger.error(
					"Couldn't get metric %s from table %s. Here's why: %s: %s",
					name,
					self.table.name,
					err.response["Error"]["Code"],
					err.response["Error"]["Message"],
			)
			raise
		else:
			return response.get("Item")
		
	def update_metric(self, name, value):
			"""
			Updates rating and plot data for a metric in the table.

			:param name: The name of the metric to update.
			:param value: The value of the metric to update.
			:return: The fields that were updated, with their new values.
			"""
			try:
					response = self.table.update_item(
							Key={"name": name},
							UpdateExpression="SET #V = :v",
							ExpressionAttributeNames={"#V": "value"},
							ExpressionAttributeValues={":v": Decimal(str(value))},
							ReturnValues="UPDATED_NEW",
					)
			except ClientError as err:
					logger.error(
							"Couldn't update metric %s in table %s. Here's why: %s: %s",
							name,
							self.table.name,
							err.response["Error"]["Code"],
							err.response["Error"]["Message"],
					)
					raise
			else:
					return response["Attributes"]


def lambda_handler(event, context):
	logger.info(event)

	headers = { "Content-Type": "application/json" }

	config = get_config()

	try:
		dynamodb = boto3.resource("dynamodb", region_name=config.region)
		visit_events = VisitEvents(dynamodb)

		table_exists = visit_events.exists(config.table_name)

		if not table_exists:
			return {
				'statusCode': 404,
				'headers': headers,
				'body': json.dumps({
					'message': f"Table {config.table_table} does not exist.",
				}),
			}

		metric = visit_events.get_metric("count")
		current_count = metric["value"]
		print("CURRENT COUNT: ", current_count)

		response = visit_events.update_metric("count", current_count + 1)
		updated_count = response["value"]
		print("UPDATE RESPONSE: ", response)

		return {
			'statusCode': 200,
			'headers': headers,
			'body': json.dumps({'count': str(updated_count)}),
		}
	except Exception as err:
		print("ERROR: ", err)
		logger.info(f"Put record failed after retries and backoff: {err}")
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
		"body": json.dumps({"message": "The metric was retrieve successfully"})
	}