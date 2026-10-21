class Config:
  def __init__(self):
    self.table_name = "cloud-resume-visit-events"
    self.region = "eu-central-1"


def get_config():
  return Config()