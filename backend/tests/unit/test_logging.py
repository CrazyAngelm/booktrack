import pytest
import logging
from datetime import datetime
from core.logging import audit_logger

def test_audit_logger_emits_info(caplog):
    # Tell caplog to capture INFO+ on the “audit” logger
    caplog.set_level(logging.INFO, logger=audit_logger.name)

    # Emit a test message
    test_msg = "Unit test audit entry"
    audit_logger.info(test_msg)

    # Look through the captured records for one that matches
    matched = [
        rec for rec in caplog.records
        if rec.name == audit_logger.name
        and rec.levelname == "INFO"
        and test_msg in rec.message
    ]
    assert matched, f"No INFO record with '{test_msg}' found in {caplog.records}"