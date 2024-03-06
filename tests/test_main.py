import os

from browser.main import URL


def test_example_request() -> None:
    url = "http://example.org"

    response = URL(url).request()

    assert response.status == "200"
    assert "Example Domain" in response.body


def test_https() -> None:
    url = "https://browser.engineering/examples/example1-simple.html"

    response = URL(url).request()

    assert response.status == "200"

    assert "This is a simple" in response.body
    assert "web page with some" in response.body
    assert "text in it." in response.body


def test_local_files() -> None:
    project_directory = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    print(project_directory)
    url = f"file://{project_directory}/tests/test_files/hello.txt"

    response = URL(url).request()

    assert response.body == "hello world"


def test_data_scheme() -> None:
    url = "data:text/plain,hello world"

    response = URL(url).request()

    assert response.headers.get("Content-Type") == "text/plain"
    assert response.body == "hello world"
