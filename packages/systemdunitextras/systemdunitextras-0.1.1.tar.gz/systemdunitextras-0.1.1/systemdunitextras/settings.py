import logging
from logging.handlers import SysLogHandler
import os

# watchdog_ping.py fail_handler.py
log = logging.getLogger(__name__)
logging.basicConfig(level=logging.DEBUG)
handler = SysLogHandler(address='/dev/log')
log.addHandler(handler)

# fail_handler.py
instance_hour = {  # (1)
    'example_instance': 10,
}
default_hour = 8  # (2)
db_path = '/var/lib/systemdunitextras/fail_handler.db'
db_dir = os.path.dirname(db_path)
if not os.path.exists(db_dir):
    os.makedirs(db_dir)


# Config notes:
# (1) 'name_of_systemd_instance': <integer_representing_hours>, where the hours specify the time span to wait, until
#     another notification about the failed systemd unit is allowed to be sent.
# (2) If no time span is configured for the instance within instance_hour, then the default_hour will be used as
#     time span.
