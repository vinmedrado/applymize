from backend.models.automation import AutomationSettings, JobNotification


def _user_fk_ondelete(model) -> str | None:
    user_id = model.__table__.c.user_id
    foreign_key = next(iter(user_id.foreign_keys))
    return foreign_key.ondelete


def test_automation_records_cascade_when_user_is_deleted():
    assert _user_fk_ondelete(AutomationSettings) == "CASCADE"
    assert _user_fk_ondelete(JobNotification) == "CASCADE"


def test_delete_account_succeeds(client, auth_headers):
    response = client.delete("/api/user/delete-account", headers=auth_headers)

    assert response.status_code == 200, response.text
    assert response.json()["success"] is True
    assert client.get("/api/auth/me", headers=auth_headers).status_code == 401
