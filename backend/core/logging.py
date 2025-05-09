import logging
from logging.handlers import TimedRotatingFileHandler

handler = TimedRotatingFileHandler(
    "logs/audit.log",
    when="D",   # daily rotation
    interval=1,
    backupCount=7  # keep 7 days of logs
)
fmt = logging.Formatter(
    "%(asctime)s %(levelname)s %(name)s %(message)s"
)
handler.setFormatter(fmt)
audit_logger = logging.getLogger("audit")
audit_logger.setLevel(logging.INFO)
audit_logger.addHandler(handler)
