"""SDO-only broker/worker probe; never expose credentials or provider errors."""
import logging

from rest_framework.response import Response
from rest_framework.views import APIView

from core.permissions import IsSDO
from SEBMS.celery import app

logger = logging.getLogger(__name__)


class WorkerHealthView(APIView):
    permission_classes = [IsSDO]

    def get(self, request):
        try:
            with app.connection_for_write(
                connect_timeout=5,
                transport_options={
                    "socket_connect_timeout": 5,
                    "socket_timeout": 5,
                    "retry_on_timeout": False,
                },
            ) as connection:
                connection.ensure_connection(max_retries=0)
                replies = app.control.ping(timeout=3, connection=connection)
            workers = sum(
                1 for reply in replies or []
                for result in reply.values()
                if isinstance(result, dict) and result.get("ok") == "pong"
            )
            return Response(
                {"status": "ok" if workers else "worker_unavailable", "workers": workers},
                status=200 if workers else 503,
            )
        except Exception as exc:
            logger.warning("Worker probe failed (%s)", type(exc).__name__)
            return Response({"status": "broker_unavailable", "workers": 0}, status=503)
