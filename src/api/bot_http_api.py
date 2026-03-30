"""
机器人进程内 HTTP API：发消息、最近消息、调用日志、配置热更新等。
需与微信客户端同机运行（依赖 wxauto）。
"""

from __future__ import annotations

import logging
import threading
from collections import deque
from datetime import datetime
from typing import Any, Callable, Deque, Dict, List, Optional
import time
import random

from flask import Flask, jsonify, request

logger = logging.getLogger(__name__)

_api_logs_lock = threading.Lock()
_api_logs: Deque[Dict[str, Any]] = deque(maxlen=500)


def _log_api(
    method: str,
    path: str,
    status_code: int,
    detail: Optional[str] = None,
) -> None:
    entry = {
        "time": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        "method": method,
        "path": path,
        "status": status_code,
        "detail": detail or "",
    }
    with _api_logs_lock:
        _api_logs.append(entry)


def get_api_logs(limit: int = 200) -> List[Dict[str, Any]]:
    with _api_logs_lock:
        items = list(_api_logs)
    return items[-limit:] if limit else items


def _auth_ok() -> bool:
    from config import config

    token = (config.bot_api.token or "").strip()
    if not token:
        return True
    # Allow local requests without token for convenience
    if request.remote_addr == '127.0.0.1':
        return True
    auth = request.headers.get("Authorization", "")
    return auth == f"Bearer {token}"


def create_bot_app(
    message_handler,
    on_config_reload: Optional[Callable[[], None]] = None,
) -> Flask:
    app = Flask(__name__)

    @app.after_request
    def after(resp):
        try:
            _log_api(
                request.method,
                request.path,
                resp.status_code,
            )
        except Exception:
            pass
        return resp

    @app.before_request
    def require_auth():
        if not request.path.startswith("/api/v1/"):
            return None
        if request.path == "/api/v1/health":
            return None
        if not _auth_ok():
            return jsonify({"ok": False, "error": "unauthorized"}), 401
        return None

    @app.route("/api/v1/health")
    def health():
        return jsonify({"ok": True})

    @app.route("/api/v1/status")
    def status():
        try:
            from config import config

            wx = message_handler.wx
            name = getattr(getattr(wx, "A_MyIcon", None), "Name", "") or ""
            return jsonify(
                {
                    "ok": True,
                    "robot_name": name,
                    "config_path": config.config_path,
                    "listen_list": list(config.user.listen_list),
                    "api": {
                        "host": config.bot_api.host,
                        "port": config.bot_api.port,
                        "auth_required": bool((config.bot_api.token or "").strip()),
                    },
                }
            )
        except Exception as e:
            logger.error("status failed: %s", e, exc_info=True)
            return jsonify({"ok": False, "error": str(e)}), 500

    @app.route("/api/v1/logs")
    def logs():
        try:
            limit = int(request.args.get("limit", 200))
            limit = max(1, min(limit, 500))
            return jsonify({"ok": True, "logs": get_api_logs(limit)})
        except Exception as e:
            return jsonify({"ok": False, "error": str(e)}), 500

    @app.route("/api/v1/messages/recent")
    def messages_recent():
        try:
            from services.database import ChatMessage, Session

            limit = int(request.args.get("limit", 50))
            limit = max(1, min(limit, 200))
            chat_id = (request.args.get("chat_id") or "").strip()

            session = Session()
            try:
                q = session.query(ChatMessage).order_by(ChatMessage.id.desc())
                if chat_id:
                    q = q.filter(
                        (ChatMessage.sender_id == chat_id)
                        | (ChatMessage.sender_name == chat_id)
                    )
                rows = q.limit(limit).all()
                data = []
                for r in rows:
                    data.append(
                        {
                            "id": r.id,
                            "sender_id": r.sender_id,
                            "sender_name": r.sender_name,
                            "message": r.message,
                            "reply": r.reply,
                            "created_at": r.created_at.isoformat()
                            if r.created_at
                            else None,
                        }
                    )
                return jsonify({"ok": True, "messages": data})
            finally:
                session.close()
        except Exception as e:
            logger.error("messages_recent failed: %s", e, exc_info=True)
            return jsonify({"ok": False, "error": str(e)}), 500

    @app.route("/api/v1/send", methods=["POST"])
    def send():
        try:
            data = request.get_json(force=True, silent=True) or {}
            who = (data.get("who") or data.get("target") or "").strip()
            text = (data.get("text") or data.get("message") or "").strip()
            use_llm = bool(data.get("use_llm", True))
            is_group = bool(data.get("is_group", False))
            raw_at = data.get("at_names") or data.get("mention") or []
            if isinstance(raw_at, str):
                at_names = [raw_at] if raw_at.strip() else []
            else:
                at_names = [str(x).strip() for x in raw_at if str(x).strip()]

            if not who or not text:
                return (
                    jsonify(
                        {
                            "ok": False,
                            "error": "缺少参数 who 或 text",
                        }
                    ),
                    400,
                )

            if use_llm:
                message_handler.add_to_queue(
                    chat_id=who,
                    content=text,
                    sender_name=data.get("sender_name") or "API",
                    username=data.get("username") or "API",
                    is_group=is_group,
                    at_names=at_names or None,
                )
                return jsonify(
                    {
                        "ok": True,
                        "mode": "llm_queue",
                        "who": who,
                    }
                )

            msg = text
            if is_group and at_names:
                msg = "".join(f"@{n}\u2005" for n in at_names) + text
            _apply_reply_delay()
            message_handler.wx.SendMsg(msg=msg, who=who)
            return jsonify(
                {
                    "ok": True,
                    "mode": "direct",
                    "who": who,
                }
            )
        except Exception as e:
            logger.error("send failed: %s", e, exc_info=True)
            return jsonify({"ok": False, "error": str(e)}), 500

    @app.route("/api/v1/config/reload", methods=["POST"])
    def config_reload():
        try:
            if on_config_reload:
                try:
                    ok = on_config_reload()
                    return jsonify({"ok": bool(ok)})
                except Exception as cb_e:
                    logger.error("on_config_reload: %s", cb_e, exc_info=True)
                    return (
                        jsonify({"ok": False, "error": str(cb_e)}),
                        500,
                    )
            from config import config as cfg

            return jsonify({"ok": cfg.reload()})
        except Exception as e:
            return jsonify({"ok": False, "error": str(e)}), 500

    return app


def start_bot_api_server(
    message_handler,
    on_config_reload: Optional[Callable[[], None]] = None,
) -> Optional[threading.Thread]:
    from config import config

    if not getattr(config, "bot_api", None) or not config.bot_api.enabled:
        logger.info("机器人 HTTP API 未启用，跳过监听")
        return None

    app = create_bot_app(message_handler, on_config_reload=on_config_reload)
    host = config.bot_api.host
    port = int(config.bot_api.port)

    def run():
        try:
            logger.info("机器人 HTTP API 监听 http://%s:%s", host, port)
            app.run(
                host=host,
                port=port,
                threaded=True,
                use_reloader=False,
            )
        except Exception as e:
            logger.error("机器人 HTTP API 启动失败: %s", e, exc_info=True)

    t = threading.Thread(target=run, daemon=True, name="BotHttpApi")
    t.start()
    return t


def _apply_reply_delay():
    """应用回复延迟"""
    from config import config

    min_delay = config.behavior.reply_delay.min_seconds
    max_delay = config.behavior.reply_delay.max_seconds
    if max_delay > 0:
        delay = random.uniform(min_delay, max_delay)
        logger.info(f"应用回复延迟: {delay:.2f}秒")
        time.sleep(delay)

