class Config:
  def __init__(self):
    self.delivery_stream_name = "cloud-resume-visit-event-stream"
    self.region = "eu-central-1"


def get_config():
	return Config()
