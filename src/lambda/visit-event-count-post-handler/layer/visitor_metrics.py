from decimal import Decimal
import logging
from botocore.exceptions import ClientError

# Configure logging
logging.basicConfig(level=logging.INFO, format="%(levelname)s: %(message)s")
logger = logging.getLogger(__name__)


class VisitEventMetrics:
	"""Encapsulates an Amazon DynamoDB table of visit event data.

	Example data structure for a visit event record in this table:
		{
			"name": "count"",
			"value": Decimal('123')
		}
	"""

	def __init__(self, dyn_resource):
		"""
		:param dyn_resource: A Boto3 DynamoDB resource.
		"""
		self.dyn_resource = dyn_resource
		# The table variable is set during the scenario in the call to
		# 'exists' if the table exists.
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
			return response["Item"]
		
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