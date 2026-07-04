import pytest


@pytest.fixture(autouse=True)
def _send_notifications_synchronously(monkeypatch):
    """Run the assignment-email worker inline so mailoutbox is deterministic."""
    from apps.notifications import services

    monkeypatch.setattr(services, "_dispatch", lambda target, *args: target(*args))
