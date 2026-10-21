import logging
from botocore.exceptions import ClientError

# Configure logging
logging.basicConfig(level=logging.INFO, format="%(levelname)s: %(message)s")
logger = logging.getLogger(__name__)


class VisitEvents:
	"""Encapsulates an Amazon DynamoDB table of website visit events.

	Example data structure for a visit event record in this table:
			{
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

	def get_item_count(self, table_name):
		try:
			response = self.dyn_resource.describe_table(table_name)
			count = response['Table']['ItemCount']

			return count
		except ClientError as err:
			logger.error(
				"Couldn't retrieve item count from table %s. Here's why: %s: %s",
				table_name,
				err.response["Error"]["Code"],
				err.response["Error"]["Message"],
			)
			raise