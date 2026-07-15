from __future__ import annotations

import base64
import re
import time
from datetime import datetime
from typing import Any

import requests
from sqlalchemy.orm import Session

from backend.core.config import settings
from backend.core.logging import get_logger
from backend.models.whatsapp_session import WhatsAppSession

logger = get_logger(__name__)


class WhatsAppSessionService:
    def __init__(self, db: Session | None = None) -> None:
        self.db = db
        self.base_url = (settings.evolution_api_url or "").rstrip("/")
        self.api_key = settings.evolution_api_key or ""

    def is_configured(self) -> bool:
        return bool(settings.whatsapp_enabled and self.base_url and self.api_key)

    def headers(self) -> dict[str, str]:
        return {"apikey": self.api_key, "Content-Type": "application/json"}

    def build_instance_name(self, tenant_id: int, user_id: int) -> str:
        prefix = re.sub(r"[^a-zA-Z0-9_-]+", "_", settings.evolution_instance_prefix or "applymize").strip("_")
        return f"{prefix}_{tenant_id}_{user_id}"

    def build_instance_id(self, user_id: int | None = None, tenant_id: int | None = None) -> str:
        if user_id is None or tenant_id is None:
            return settings.evolution_instance_id or ""
        return self.build_instance_name(tenant_id, user_id)

    def normalize_phone_number(self, phone_number: str | None) -> str:
        number = re.sub(r"\D+", "", phone_number or "")
        if not number:
            return ""
        country = re.sub(r"\D+", "", settings.evolution_default_country_code or "55") or "55"
        if not number.startswith(country):
            number = f"{country}{number}"
        return number

    def validate_phone_number(self, phone_number: str) -> None:
        if not phone_number or len(phone_number) < 11 or len(phone_number) > 15:
            raise ValueError("Telefone inválido. Use DDI + DDD + número. Ex: 5511999999999.")

    def get_session(self, user_id: int, tenant_id: int, create: bool = True) -> WhatsAppSession | None:
        if not self.db:
            return None
        session = self.db.query(WhatsAppSession).filter(
            WhatsAppSession.tenant_id == tenant_id,
            WhatsAppSession.user_id == user_id,
        ).first()
        instance_name = self.build_instance_name(tenant_id, user_id)
        if not session and create:
            session = WhatsAppSession(
                tenant_id=tenant_id,
                user_id=user_id,
                instance_name=instance_name,
                status="not_configured",
                connected=False,
            )
            self.db.add(session)
            self.db.commit()
            self.db.refresh(session)
        elif session and session.instance_name != instance_name:
            session.instance_name = instance_name
            session.updated_at = datetime.utcnow()
            self.db.commit()
            self.db.refresh(session)
        return session

    # Compatibility with older code/tests
    def get_connection(self, user_id: int | None = None, tenant_id: int | None = None):
        if user_id is None or tenant_id is None:
            return None
        return self.get_session(user_id, tenant_id)

    def request(self, method: str, path: str, **kwargs: Any) -> tuple[bool, Any]:
        if not self.is_configured():
            return False, {"error": "Evolution API não configurada."}
        url = f"{self.base_url}/{path.lstrip('/')}"
        try:
            response = requests.request(method, url, headers=self.headers(), timeout=25, **kwargs)
            if response.status_code >= 400:
                return False, {"error": f"Evolution API retornou HTTP {response.status_code}", "detail": response.text[:500]}
            if not response.text:
                return True, {}
            try:
                return True, response.json()
            except Exception:
                return True, response.text
        except requests.exceptions.ConnectionError:
            return False, {"error": "Evolution API offline ou inacessível."}
        except requests.exceptions.Timeout:
            return False, {"error": "Timeout ao chamar Evolution API."}
        except Exception as exc:
            logger.warning("evolution_request_failed path=%s error=%s", path, exc)
            return False, {"error": str(exc)}

    def sanitize_payload(self, payload: Any) -> Any:
        if isinstance(payload, dict):
            return {k: ("***" if any(x in k.lower() for x in ["key", "token", "apikey", "authorization"]) else self.sanitize_payload(v)) for k, v in payload.items()}
        if isinstance(payload, list):
            return [self.sanitize_payload(item) for item in payload]
        if isinstance(payload, str) and self.api_key and self.api_key in payload:
            return payload.replace(self.api_key, "***")
        return payload

    def safe_response(self, session: WhatsAppSession | None, status: str | None = None, message: str = "", **extra: Any) -> dict[str, Any]:
        status_value = status or (session.status if session else "not_configured")
        qrcode = session.qrcode if session else ""
        qrcode_type = session.qrcode_type if session else "none"
        instance_name = session.instance_name if session else ""
        phone_number = session.phone_number if session else ""
        connected = bool(session.connected) if session else False
        return {
            "configured": self.is_configured(),
            "session_id": session.id if session else None,
            "instance_name": instance_name,
            "instance_id": instance_name,  # backward-compatible alias
            "phone_number": phone_number,
            "target_number_configured": bool(phone_number),
            "status": status_value,
            "message": message or self.message_for_status(status_value),
            "connected": connected,
            "qrcode": qrcode or "",
            "qrcode_type": qrcode_type or "none",
            "qr_code": qrcode or "",
            "qr_type": qrcode_type or "none",
            "last_error": session.last_error if session else "",
            **extra,
        }

    def message_for_status(self, status: str) -> str:
        return {
            "not_configured": "Sessão ainda não configurada.",
            "phone_saved": "Telefone salvo com sucesso.",
            "waiting_qr": "Instância aguardando leitura do QR Code.",
            "waiting_qrcode": "QR Code ainda não foi gerado pela Evolution.",
            "connected": "WhatsApp conectado e estável.",
            "disconnected": "WhatsApp desconectado.",
            "error": "Erro na integração WhatsApp.",
            "phone_missing": "Salve seu telefone antes de criar a conexão.",
        }.get(status, "Status atualizado.")

    def is_connected_cache_valid(self, session: WhatsAppSession | None) -> bool:
        if not session or not session.connected or session.status != "connected" or not session.updated_at:
            return False
        try:
            age_seconds = (datetime.utcnow() - session.updated_at).total_seconds()
        except Exception:
            return False
        return age_seconds <= max(30, int(settings.whatsapp_connected_cache_seconds or 600))

    def connected_cached_response(self, session: WhatsAppSession, message: str | None = None) -> dict[str, Any]:
        result = self.safe_response(
            session,
            "connected",
            message or "WhatsApp conectado. Status mantido em cache para evitar sincronizações desnecessárias.",
        )
        result["cached"] = True
        result["last_checked_at"] = session.updated_at.isoformat() if session.updated_at else None
        result["connected_at"] = session.connected_at.isoformat() if session.connected_at else None
        return result

    def normalize_connection_status(self, payload: Any) -> tuple[str, bool, str]:
        raw = str(payload or "").lower()
        if any(item in raw for item in ["open", "connected", "conectado", "online"]):
            return "connected", True, "Instância conectada."
        if any(item in raw for item in ["qrcode", "qr", "pairing", "connecting", "created"]):
            return "waiting_qr", False, "Instância aguardando leitura do QR Code."
        if any(item in raw for item in ["close", "closed", "disconnected", "desconectado", "offline"]):
            return "disconnected", False, "Instância desconectada."
        return "unknown", False, "Status recebido, mas não normalizado."

    def persist_status(self, session: WhatsAppSession | None, status: str, connected: bool, qrcode: str | None = None, qrcode_type: str | None = None, last_error: str = "") -> None:
        if not self.db or not session:
            return
        now = datetime.utcnow()
        session.status = status
        session.connected = connected
        session.updated_at = now
        session.last_error = last_error or ""
        if qrcode is not None:
            session.qrcode = qrcode
            session.qrcode_type = qrcode_type or "none"
            if qrcode:
                session.last_qr_at = now
        if connected:
            session.connected_at = session.connected_at or now
            session.disconnected_at = None
        elif status == "disconnected":
            session.disconnected_at = now
        self.db.commit()
        self.db.refresh(session)

    def save_phone_number(self, user_id: int, tenant_id: int, phone_number: str) -> dict[str, Any]:
        normalized = self.normalize_phone_number(phone_number)
        self.validate_phone_number(normalized)
        session = self.get_session(user_id, tenant_id)
        assert session is not None
        session.phone_number = normalized
        session.status = "phone_saved"
        session.updated_at = datetime.utcnow()
        session.last_error = ""
        self.db.commit()
        self.db.refresh(session)
        return self.safe_response(session, "phone_saved", "Telefone salvo com sucesso.")

    def get_status(self, user_id: int, tenant_id: int, force_refresh: bool = False) -> dict[str, Any]:
        session = self.get_session(user_id, tenant_id)
        if not self.is_configured():
            return self.safe_response(session, "not_configured", "Integração do WhatsApp não configurada no servidor.")
        assert session is not None
        if not session.phone_number:
            return self.safe_response(session, "phone_missing", "Salve seu telefone antes de criar a conexão.")

        # Once the instance is connected, avoid repeatedly calling Evolution on every page load.
        # This prevents the WhatsApp app from constantly showing “sincronizando” even when the
        # session is already healthy. Manual buttons and QR flows can still force refresh.
        if not force_refresh and self.is_connected_cache_valid(session):
            logger.info(
                "whatsapp_status_cache_hit tenant_id=%s user_id=%s instance=%s",
                tenant_id,
                user_id,
                session.instance_name,
            )
            return self.connected_cached_response(session)

        last_error = None
        for path in [f"instance/connectionState/{session.instance_name}", "instance/fetchInstances"]:
            ok, payload = self.request("GET", path)
            if ok:
                status, connected, message = self.normalize_connection_status(payload)
                # Do not downgrade a recently connected session to waiting/syncing based on a transient
                # Evolution payload. Only closed/disconnected should mark it offline.
                if session.connected and status in {"waiting_qr", "unknown"}:
                    logger.info(
                        "whatsapp_transient_status_ignored tenant_id=%s user_id=%s previous=connected received=%s",
                        tenant_id,
                        user_id,
                        status,
                    )
                    return self.connected_cached_response(session, "WhatsApp conectado. Sincronização transitória ignorada.")
                self.persist_status(session, status, connected)
                result = self.safe_response(session, status, message)
                result["raw"] = self.sanitize_payload(payload)
                result["cached"] = False
                return result
            last_error = payload
        safe_error = str(self.sanitize_payload(last_error))[:500]
        # Preserve an already connected state if the Evolution status endpoint has a temporary issue.
        if session.connected:
            logger.warning(
                "whatsapp_status_refresh_failed_preserving_connected tenant_id=%s user_id=%s error=%s",
                tenant_id,
                user_id,
                safe_error,
            )
            return self.connected_cached_response(session, "WhatsApp conectado. Não foi possível atualizar agora, mantendo último status estável.")
        self.persist_status(session, "error", False, last_error=safe_error)
        return self.safe_response(session, "error", f"Não foi possível consultar status: {safe_error}")

    def create_session(self, user_id: int, tenant_id: int, phone_number: str | None = None) -> dict[str, Any]:
        session = self.get_session(user_id, tenant_id)
        assert session is not None
        if phone_number is not None:
            self.save_phone_number(user_id, tenant_id, phone_number)
            session = self.get_session(user_id, tenant_id)
        return self.safe_response(session, session.status, "Sessão carregada/criada para este usuário.")

    def create_instance(self, user_id: int, tenant_id: int) -> dict[str, Any]:
        session = self.get_session(user_id, tenant_id)
        if not self.is_configured():
            return self.safe_response(session, "not_configured", "Evolution API não configurada.")
        assert session is not None
        if not session.phone_number:
            return self.safe_response(session, "phone_missing", "Salve seu telefone antes de criar a conexão.")
        if session.connected and session.status == "connected":
            logger.info("whatsapp_create_skipped_already_connected tenant_id=%s user_id=%s instance=%s", tenant_id, user_id, session.instance_name)
            return self.connected_cached_response(session, "WhatsApp já está conectado. Nenhuma nova sincronização foi iniciada.")
        payloads = [
            {"instanceName": session.instance_name, "qrcode": True, "integration": "WHATSAPP-BAILEYS"},
            {"instanceName": session.instance_name, "qrcode": True},
        ]
        last_error = None
        for body in payloads:
            ok, payload = self.request("POST", "instance/create", json=body)
            if ok:
                qr = self.extract_qrcode(payload)

                if qr.get("qrcode"):
                    self.persist_status(
                        session,
                        "waiting_qr",
                        False,
                        qr.get("qrcode", ""),
                        qr.get("type", "none"),
                    )
                    result = self.safe_response(
                        session,
                        "waiting_qr",
                        "QR Code obtido. Escaneie com o WhatsApp.",
                    )
                    result["raw"] = self.sanitize_payload(payload)
                    return result

                self.persist_status(session, "waiting_qrcode", False, "", "none")
                result = self.safe_response(
                    session,
                    "waiting_qrcode",
                    "Instância criada/preparada. Clique em Atualizar QR Code.",
                )
                result["raw"] = self.sanitize_payload(payload)
                return result
            last_error = payload
        status = self.get_status(user_id, tenant_id)
        if status.get("status") != "error":
            status["message"] = "Instância já existe ou está preparada."
            return status
        safe_error = str(self.sanitize_payload(last_error))[:500]
        self.persist_status(session, "error", False, last_error=safe_error)
        return self.safe_response(session, "error", f"Falha ao criar instância: {safe_error}")

    def connect_or_create(self, user_id: int, tenant_id: int) -> dict[str, Any]:
        session = self.get_session(user_id, tenant_id)
        if session and session.connected and session.status == "connected":
            logger.info("whatsapp_connect_skipped_already_connected tenant_id=%s user_id=%s instance=%s", tenant_id, user_id, session.instance_name)
            return self.connected_cached_response(session, "WhatsApp já está conectado. Não foi necessário reconectar.")
        created = self.create_instance(user_id, tenant_id)
        if created.get("status") == "error" or created.get("connected"):
            return created
        return self.get_qrcode(user_id, tenant_id, force_refresh=True)

    def recreate_instance_for_qr(self, session: WhatsAppSession) -> Any:
        logger.info(
            "evolution_instance_delete_before_recreate instance=%s",
            session.instance_name,
        )
        ok_delete, delete_payload = self.request(
            "DELETE",
            f"instance/delete/{session.instance_name}",
        )
        if not ok_delete:
            safe_delete_error = str(self.sanitize_payload(delete_payload)).lower()
            if "404" not in safe_delete_error and "not found" not in safe_delete_error and "inexist" not in safe_delete_error:
                logger.info(
                    "evolution_instance_delete_before_recreate instance=%s ignored_error=%s",
                    session.instance_name,
                    str(self.sanitize_payload(delete_payload))[:500],
                )

        time.sleep(1)

        payloads = [
            {"instanceName": session.instance_name, "qrcode": True, "integration": "WHATSAPP-BAILEYS"},
            {"instanceName": session.instance_name, "qrcode": True},
        ]
        last_payload: Any = None
        for body in payloads:
            ok, payload = self.request("POST", "instance/create", json=body)
            last_payload = payload
            if ok:
                logger.info(
                    "evolution_instance_recreate_success instance=%s fallback=%s keys=%s",
                    session.instance_name,
                    "integration" not in body,
                    list(payload.keys()) if isinstance(payload, dict) else type(payload).__name__,
                )
                return payload

        logger.warning(
            "evolution_instance_recreate_failed instance=%s error=%s",
            session.instance_name,
            str(self.sanitize_payload(last_payload))[:500],
        )
        return last_payload or {}

    @staticmethod
    def looks_like_base64_image(value: str) -> bool:
        compact = re.sub(r"\s+", "", value or "")
        if compact.startswith("data:image"):
            return True
        if len(compact) < 80:
            return False
        try:
            base64.b64decode(compact + "==", validate=False)
            return True
        except Exception:
            return False

    def extract_qrcode(self, payload: Any) -> dict[str, str]:
        def is_instance_identifier(value: str) -> bool:
            clean = value.strip()
            return clean == "" or clean.startswith("applymize_") or clean == settings.evolution_instance_id

        def normalize_base64_qr(value: str) -> dict[str, str]:
            clean = value.strip()
            if not clean or is_instance_identifier(clean):
                return {"qrcode": "", "type": "none"}
            if clean.startswith("data:image"):
                return {"qrcode": clean, "type": "base64"}
            if self.looks_like_base64_image(clean):
                return {"qrcode": f"data:image/png;base64,{clean}", "type": "base64"}
            if len(clean) >= 80:
                return {"qrcode": clean, "type": "string"}
            return {"qrcode": "", "type": "none"}

        if isinstance(payload, str):
            return normalize_base64_qr(payload)

        if isinstance(payload, list):
            pairing_code = ""
            for item in payload:
                found = self.extract_qrcode(item)
                if found.get("qrcode"):
                    return found
                pairing_code = pairing_code or found.get("pairing_code", "")
            if pairing_code:
                return {"qrcode": "", "type": "none", "pairing_code": pairing_code}
            return {"qrcode": "", "type": "none"}

        if isinstance(payload, dict):
            if "qrcode" in payload:
                qrcode_payload = payload.get("qrcode")
                logger.info(
                    "evolution_qrcode_payload_shape type=%s keys=%s",
                    type(qrcode_payload).__name__,
                    list(qrcode_payload.keys()) if isinstance(qrcode_payload, dict) else [],
                )

            # Base64/image fields are the only values persisted as scannable QR.
            for key in ["base64", "qr", "qrCode", "qrcode"]:
                value = payload.get(key)
                if isinstance(value, str) and value.strip():
                    found = normalize_base64_qr(value)
                    if found.get("qrcode"):
                        return found
                elif isinstance(value, (dict, list)):
                    found = self.extract_qrcode(value)
                    if found.get("qrcode"):
                        return found

            # code/pairingCode are useful diagnostics, but they are not a scannable QR image.
            for key in ["code", "pairingCode"]:
                value = payload.get(key)
                if isinstance(value, str) and value.strip():
                    return {"qrcode": "", "type": "none", "pairing_code": value.strip()}

            pairing_code = ""
            for value in payload.values():
                if isinstance(value, (dict, list)):
                    found = self.extract_qrcode(value)
                    if found.get("qrcode"):
                        return found
                    pairing_code = pairing_code or found.get("pairing_code", "")
            if pairing_code:
                return {"qrcode": "", "type": "none", "pairing_code": pairing_code}

        return {"qrcode": "", "type": "none"}

    def get_qrcode(self, user_id: int, tenant_id: int, force_refresh: bool = False) -> dict[str, Any]:
        session = self.get_session(user_id, tenant_id)
        if not self.is_configured():
            return self.safe_response(session, "not_configured", "Evolution API não configurada.")
        assert session is not None
        if not session.phone_number:
            return self.safe_response(session, "phone_missing", "Salve seu telefone antes de obter QR Code.")
        if session.connected and session.status == "connected" and not force_refresh:
            logger.info("whatsapp_qrcode_skipped_already_connected tenant_id=%s user_id=%s instance=%s", tenant_id, user_id, session.instance_name)
            return self.connected_cached_response(session, "WhatsApp já está conectado. QR Code não é necessário.")

        last_payload: Any = None
        last_error: Any = None
        connect_path = f"instance/connect/{session.instance_name}"

        for attempt in range(3):
            ok, payload = self.request("GET", connect_path)
            logger.info(
                "evolution_qrcode_connect method=%s endpoint=%s attempt=%s ok=%s keys=%s",
                "GET",
                connect_path,
                attempt + 1,
                ok,
                list(payload.keys()) if isinstance(payload, dict) else type(payload).__name__,
            )

            if ok:
                last_payload = payload
                qr = self.extract_qrcode(payload)
                status, connected, message = self.normalize_connection_status(payload)

                if qr.get("qrcode"):
                    if not connected:
                        status, message = "waiting_qr", "QR Code obtido. Escaneie com o WhatsApp."
                    self.persist_status(
                        session,
                        status,
                        connected,
                        qr.get("qrcode", ""),
                        qr.get("type", "none"),
                    )
                    result = self.safe_response(session, status, message)
                    result["raw"] = self.sanitize_payload(payload)
                    return result

                if isinstance(payload, dict) and payload.get("count") == 0:
                    logger.info(
                        "evolution_qrcode_count_zero_waiting method=%s endpoint=%s attempt=%s keys=%s",
                        "GET",
                        connect_path,
                        attempt + 1,
                        list(payload.keys()),
                    )
                    self.persist_status(session, "waiting_qrcode", False, "", "none")
                    result = self.safe_response(
                        session,
                        "waiting_qrcode",
                        "A Evolution ainda está gerando o QR Code. Aguarde alguns segundos e clique em Atualizar QR Code.",
                    )
                    result["raw"] = self.sanitize_payload(payload)
                    return result

                if connected:
                    self.persist_status(session, status, connected, "", "none")
                    result = self.safe_response(session, status, message)
                    result["raw"] = self.sanitize_payload(payload)
                    return result
            else:
                last_error = payload

            if attempt < 2:
                time.sleep(2)

        for method, path in [
            ("GET", f"instance/connectionState/{session.instance_name}"),
            ("GET", "instance/fetchInstances"),
        ]:
            ok, payload = self.request(method, path)
            if ok:
                last_payload = payload
                qr = self.extract_qrcode(payload)
                status, connected, message = self.normalize_connection_status(payload)
                if qr.get("qrcode") and not connected:
                    status, message = "waiting_qr", "QR Code obtido. Escaneie com o WhatsApp."
                if qr.get("qrcode") or connected:
                    self.persist_status(
                        session,
                        status,
                        connected,
                        qr.get("qrcode", ""),
                        qr.get("type", "none"),
                    )
                    result = self.safe_response(session, status, message)
                    result["raw"] = self.sanitize_payload(payload)
                    return result
            else:
                last_error = payload

        self.persist_status(session, "waiting_qrcode", False, "", "none")
        result = self.safe_response(
            session,
            "waiting_qrcode",
            "QR Code ainda não foi gerado pela Evolution. Clique em atualizar novamente.",
        )
        result["raw"] = self.sanitize_payload(last_payload if last_payload is not None else last_error)
        return result

    def send_test_message(self, user_id: int, tenant_id: int, target_number: str | None = None) -> dict[str, Any]:
        session = self.get_session(user_id, tenant_id)
        if not self.is_configured():
            return {**self.safe_response(session, "not_configured", "Evolution API não configurada."), "sent": False}
        assert session is not None
        number = self.normalize_phone_number(target_number or session.phone_number)
        if not number:
            return {**self.safe_response(session, "phone_missing", "Salve seu telefone antes de enviar teste."), "sent": False}
        status = self.get_status(user_id, tenant_id)
        if not status.get("connected"):
            return {**status, "sent": False, "message": "WhatsApp não conectado. Faça o pareamento pelo QR Code antes de enviar teste."}
        ok, response = self.request(
            "POST",
            f"message/sendText/{session.instance_name}",
            json={"number": number, "text": "✅ Teste Applymize: WhatsApp pareado e pronto para alertas controlados."},
        )
        if ok:
            return {**self.safe_response(session, "connected", "Mensagem de teste enviada."), "sent": True, "raw": self.sanitize_payload(response)}
        safe_error = str(self.sanitize_payload(response))[:500]
        return {**self.safe_response(session, "error", f"Falha ao enviar mensagem: {safe_error}"), "sent": False}

    def disconnect(self, user_id: int, tenant_id: int) -> dict[str, Any]:
        session = self.get_session(user_id, tenant_id)
        if not self.is_configured():
            return self.safe_response(session, "not_configured", "Evolution API não configurada.")
        assert session is not None
        last_error = None
        for method, path in [("DELETE", f"instance/logout/{session.instance_name}"), ("POST", f"instance/logout/{session.instance_name}"), ("DELETE", f"instance/delete/{session.instance_name}")]:
            ok, payload = self.request(method, path)
            if ok:
                self.persist_status(session, "disconnected", False, "", "none")
                result = self.safe_response(session, "disconnected", "Instância desconectada/removida com sucesso.")
                result["raw"] = self.sanitize_payload(payload)
                return result
            last_error = payload
        safe_error = str(self.sanitize_payload(last_error))[:500]
        self.persist_status(session, "error", False, last_error=safe_error)
        return self.safe_response(session, "error", f"Falha ao desconectar: {safe_error}")

    def delete_session(self, user_id: int, tenant_id: int) -> dict[str, Any]:
        session = self.get_session(user_id, tenant_id, create=False)
        if not session:
            return {"deleted": True, "message": "Nenhuma sessão WhatsApp encontrada para este usuário."}
        if self.is_configured():
            self.disconnect(user_id, tenant_id)
            session = self.get_session(user_id, tenant_id, create=False)
        if session:
            self.db.delete(session)
            self.db.commit()
        return {"deleted": True, "message": "Sessão WhatsApp removida deste usuário."}

    def send_notification_message(self, session: WhatsAppSession, message: str) -> tuple[bool, str]:
        if not self.is_configured():
            return False, "Evolution API não configurada."
        if not session.phone_number:
            return False, "Telefone do usuário não configurado."
        if not session.connected:
            status = self.get_status(session.user_id, session.tenant_id)
            if not status.get("connected"):
                return False, "WhatsApp desconectado. Faça o pareamento na tela WhatsApp / Pareamento."
        ok, response = self.request("POST", f"message/sendText/{session.instance_name}", json={"number": session.phone_number, "text": message})
        if ok:
            return True, ""
        return False, str(self.sanitize_payload(response))[:500]
