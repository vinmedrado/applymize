from starlette.websockets import WebSocketDisconnect


def _token(auth_headers: dict[str, str]) -> str:
    return auth_headers["Authorization"].split(" ", 1)[1]


def test_dashboard_websocket_authenticates_in_first_message(client, auth_headers):
    with client.websocket_connect("/api/dashboard/realtime") as websocket:
        websocket.send_json({"token": _token(auth_headers)})
        payload = websocket.receive_json()

    assert payload["realtime"] is True
    assert payload["push_version"] >= 0


def test_dashboard_websocket_closes_when_account_is_deleted(client, auth_headers):
    with client.websocket_connect("/api/dashboard/realtime") as websocket:
        websocket.send_json({"token": _token(auth_headers)})
        websocket.receive_json()

        deleted = client.delete("/api/user/delete-account", headers=auth_headers)
        assert deleted.status_code == 200, deleted.text

        try:
            websocket.receive_json()
        except WebSocketDisconnect as exc:
            assert exc.code == 1008
        else:
            raise AssertionError("WebSocket permaneceu aberto após a exclusão da conta")
