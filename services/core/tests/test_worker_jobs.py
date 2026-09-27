import logging

import pytest

from worker.jobs import provision_project


def test_provision_project_logs_lifecycle(caplog: pytest.LogCaptureFixture) -> None:
    with caplog.at_level(logging.INFO):
        result = provision_project("example-project", provider="placeholder")

    assert result == {"project_id": "example-project", "status": "completed"}
    messages = [record.message for record in caplog.records]
    assert messages == ["Received provision_project job", "Completed provision_project job"]
