import socket
import ssl
from typing import Optional


def log(*args: str) -> None:
    print("\033[94m", *args, "\033[0m")


class Response:
    def __init__(
        self,
        body: str,
        status: Optional[str] = None,
        headers: Optional[dict[str, str]] = None,
    ) -> None:
        self.status = status
        self.headers = headers if headers is not None else {}
        self.body = body


class URL:
    port: int | None

    def __init__(self, url: str):
        if url.startswith("data:"):
            self.scheme = "data"
            self.host = ""
            self.path = url.replace("data:", "")
            return

        self.scheme, url = url.split("://", 1)
        assert self.scheme in ["http", "https", "file"]

        if "/" not in url:
            url = url + "/"

        self.host, url = url.split("/", 1)
        self.path = "/" + url

        if ":" in self.host:
            self.host, port = self.host.split(":", 1)
            self.port = int(port)
        else:
            self.port = None

    def request(self) -> Response:
        if self.scheme == "file":
            return self._open_file()

        if self.scheme == "data":
            return self._data_scheme()

        s = socket.socket(
            family=socket.AF_INET,
            type=socket.SOCK_STREAM,
            proto=socket.IPPROTO_TCP,
        )

        port = self.port if self.port else 80 if self.scheme == "http" else 443

        s.connect((self.host, port))

        if self.scheme == "https":
            ctx = ssl.create_default_context()
            s = ctx.wrap_socket(s, server_hostname=self.host)

        request_headers = {
            "Host": self.host,
            "Connection": "close",
            "User-Agent": "fardeems-browser",
        }

        http_request = (
            "GET {} HTTP/1.0\r\n".format(self.path)
            + "\n".join([f"{key}: {value}" for key, value in request_headers.items()])
            + "\r\n\r\n"
        )

        log("Requesting to", self.host)
        # We need to be sending bytes so we encode it here
        s.send(http_request.encode("utf8"))

        response = s.makefile("r", encoding="utf8", newline="\r\n")

        statusline = response.readline()
        version, status, explanation = statusline.split(" ", 2)

        log("Response")
        log(f"Version: {version}, Status: {status}, Explanation: {explanation}")

        response_headers = {}
        while True:
            line = response.readline()
            if line == "\r\n":
                break
            header, value = line.split(":", 1)
            response_headers[header.casefold()] = value.strip()

        assert "transfer-encoding" not in response_headers
        assert "content-encoding" not in response_headers

        body = response.read()
        s.close()

        return Response(
            status=status,
            body=body,
            headers=response_headers,
        )

    # private class method open file
    def _open_file(self) -> Response:
        try:
            with open(self.path, "r") as f:
                body = f.read()

            return Response(
                body=body,
            )
        except:
            return Response(
                body="",
            )

    def _data_scheme(self) -> Response:
        content_type, body = self.path.split(",", 1)

        return Response(
            body=body,
            headers={"Content-Type": content_type},
        )


class Browser:
    def __init__(self) -> None:
        pass

    def load(self, url: str) -> None:
        parsed_url = URL(url)
        response = parsed_url.request()

        self.show(response.body)

    def show(self, body: str) -> None:
        in_tag = False
        for c in body:
            if c == "<":
                in_tag = True
            elif c == ">":
                in_tag = False
            elif not in_tag:
                print(c, end="")


browser = Browser()

# browser.load("https://browser.engineering/http.html")
browser.load("https://browser.engineering/examples/example1-simple.html")
# browser.load("http://localhost:8000/")
