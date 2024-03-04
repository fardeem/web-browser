import socket
import ssl


def log(*args, **kwargs):
    print("\033[94m", *args, "\033[0m", **kwargs)


class URL:
    port: int | None

    def __init__(self, url: str):
        self.scheme, url = url.split("://", 1)
        assert self.scheme in ["http", "https"]

        if "/" not in url:
            url = url + "/"

        self.host, url = url.split("/", 1)
        self.path = "/" + url

        self.port = None

    def request(self) -> str:
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

        http_request = "GET {} HTTP/1.0\r\n".format(
            self.path
        ) + "Host: {}\r\n\r\n".format(self.host)

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

        return body


class Browser:
    def __init__(self) -> None:
        pass

    def load(self, url: str) -> None:
        parsed_url = URL(url)
        response = parsed_url.request()

        self.show(response)

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

browser.load("https://browser.engineering/http.html")
