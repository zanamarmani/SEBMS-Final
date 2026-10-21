"""JSON renderer wrapping every success payload in a consistent envelope.

Success:  {"success": true,  "data": ..., "error": null}
Errors:   produced by core.exceptions.api_exception_handler (already enveloped).
"""
from rest_framework.renderers import JSONRenderer


class EnvelopeRenderer(JSONRenderer):
    def render(self, data, accepted_media_type=None, renderer_context=None):
        if data is None:
            payload = None
        elif isinstance(data, dict) and "success" in data:
            payload = data
        else:
            payload = {"success": True, "data": data, "error": None}
        return super().render(payload, accepted_media_type, renderer_context)
