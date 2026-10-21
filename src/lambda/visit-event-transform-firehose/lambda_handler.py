import base64
import json
from ip_geolocation import get_ip_geolocation
import logging


# Configure logging
logging.basicConfig(level=logging.INFO, format="%(levelname)s: %(message)s")
logger = logging.getLogger(__name__)


def lambda_handler(event, context):
  logger.info('Request: %s', event)
  print("EVENT: ", event)
  
  output = []

  for record in event['records']:
    payload = base64.b64decode(record['data']).decode('utf-8')
    data = json.loads(payload)
    

    try:
      source_ip = data.get("sourceIp")
      geo_location = get_ip_geolocation(source_ip)
      data.update(geo_location)
    except Exception:
      logger.warning("Unable to retrieve geolocation data.")

    data_str = json.dumps(data)

    output_record = {
      'recordId': record['recordId'],
      'result': 'Ok',
      'data': base64.b64encode(data_str.encode('utf-8')).decode('utf-8')
    }
    output.append(output_record)

  return {'records': output}