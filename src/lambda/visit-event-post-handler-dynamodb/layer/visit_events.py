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
		"""
		try:
			table = self.dyn_resource.Table(table_name)
			table.load()
		except ClientError as err:
			if err.response["Error"]["Code"] == "ResourceNotFoundException":
				logger.error("Table %s does not exits.", table_name)
			else:
				logger.error(
					"Couldn't check for existence of %s. Here's why: %s: %s",
					table_name,
					err.response["Error"]["Code"],
					err.response["Error"]["Message"],
				)
			raise err
		else:
			self.table = table
			
	def add_event(self, event_dict):
		"""
		Adds a visit event to the table.

		:param event_dict: The plot summary of the movie.
		"""
		try:
			self.table.put_item(Item=event_dict)
		except ClientError as err:
			logger.error(
				"Couldn't add visit event to table %s. Here's why: %s: %s",
				self.table.name,
				err.response["Error"]["Code"],
				err.response["Error"]["Message"],
			)
			raise