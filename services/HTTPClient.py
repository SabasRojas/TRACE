import gzip
from io import BytesIO

import requests
from typing import Any, Dict, Optional

# Update HttpResponse to include headers.
class HttpRequest:
    def __init__(self, method: str, url: str, headers: Dict[str, str], payload: Any):
        self.method = method
        self.url = url
        self.headers = headers
        self.payload = payload

class HttpResponse:
    def __init__(self, status_code: int, body: str, headers: Dict[str, str]):
        self.status_code = status_code
        self.body = body
        self.headers = headers

class RequestManager:
    def create_request(self, method: str, url: str, headers: Dict[str, str],
                       params: Dict[str, str], payload: Any) -> HttpRequest:
        # Here you could merge parameters into the payload if needed.
        # For GET requests, `params` can be used instead of payload.
        # For simplicity, we'll assume payload holds all necessary data.
        return HttpRequest(method, url, headers, payload)

class ProxyServer:
    def forward_request(self, request: HttpRequest) -> None:
        pass
        # print(f"[Proxy] Forwarding {request.method} request to {request.url}")

    def handle_forwarding_error(self, error: Exception) -> None:
        print(f"[Proxy] Error during request forwarding: {error}")

class HTTPClient:
    def __init__(self, request_manager: RequestManager, proxy_server: Optional[ProxyServer] = None):
        self.request_manager = request_manager
        self.proxy_server = proxy_server
        self.last_response: Optional[HttpResponse] = None

    def send_request(self, url: str, data: Any, req_type: str, headers: Dict[str, str]) -> None:
        request = self.request_manager.create_request(req_type, url, headers, params={}, payload=data)
        if self.proxy_server is not None:
            try:
                self.proxy_server.forward_request(request)
            except Exception as e:
                self.proxy_server.handle_forwarding_error(e)
                return
        self.last_response = self._send_http(request)

    def send_request_with_cookies(self, url: str, data: Any, req_type: str, headers: Dict[str, str], cookies: dict, hide_status_codes: Optional[list[int]] = None, show_only_status_codes: Optional[list[int]] = None) -> None:
        request = self.request_manager.create_request(req_type, url, headers, params={}, payload=data)
        if self.proxy_server:
            try:
                self.proxy_server.forward_request(request)
            except Exception as e:
                self.proxy_server.handle_forwarding_error(e)
                return
        try:
            response = requests.request(
                req_type,
                url,
                headers=headers,
                json=data,
                cookies=cookies,
            )
            status = response.status_code
            if hide_status_codes and status in hide_status_codes:
                # drop it
                self.last_response = None
                return
            if show_only_status_codes and status not in show_only_status_codes:
                # drop it
                self.last_response = None
                return
            # otherwise wrap and store
            self.last_response = HttpResponse(status, response.text, dict(response.headers))
        except Exception as e:
            raise RuntimeError(f"HTTP request with cookies failed: {e}")

    def send_request_from_model(self, request_model: 'RequestModel') -> None:
        request = self.request_manager.create_request(
            method=request_model.method,
            url=request_model.url,
            headers=request_model.headers,
            params=request_model.parameters,
            payload=request_model.payload
        )
        if self.proxy_server is not None:
            try:
                self.proxy_server.forward_request(request)
            except Exception as e:
                self.proxy_server.handle_forwarding_error(e)
                raise Exception("Proxy forwarding failed")
        self.last_response = self._send_http(request)

    def receive_response(self) -> Optional[HttpResponse]:
        return self.last_response

    def get_status_code(self) -> int:
        if self.last_response is not None:
            return self.last_response.status_code
        raise RuntimeError("No response available. Send a request first.")

    def get_response_body(self) -> str:
        if self.last_response is not None:
            return self.last_response.body
        raise RuntimeError("No response available. Send a request first.")

    def _send_http(self, request: HttpRequest) -> HttpResponse:
        try:
            if request.method.upper() == "GET":
                response = requests.get(request.url, headers=request.headers)
            else:
                response = requests.request(request.method, request.url, headers=request.headers, json=request.payload)

            content_encoding = response.headers.get("Content-Encoding", "").lower()

            raw_bytes = response.content

            # Check for gzip
            if content_encoding == "gzip" and raw_bytes[:2] == b'\x1f\x8b':
                buf = BytesIO(raw_bytes)
                with gzip.GzipFile(fileobj=buf) as gz:
                    body_text = gz.read().decode("utf-8", errors="replace")
            # Check for UTF-16 LE BOM
            elif raw_bytes[:2] == b'\xff\xfe':
                body_text = raw_bytes.decode("utf-16le", errors="replace")
            # Check for UTF-16 BE BOM
            elif raw_bytes[:2] == b'\xfe\xff':
                body_text = raw_bytes.decode("utf-16be", errors="replace")
            else:
                # Default to UTF-8
                if response.encoding is None:
                    response.encoding = 'utf-8'
                body_text = response.text
            return HttpResponse(response.status_code, body_text, dict(response.headers))

        except Exception as e:
            raise RuntimeError(f"HTTP request failed: {e}")



