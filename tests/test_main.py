from browser.main import URL


def test_example_request():
    url = "http://example.org"

    response = URL(url).request()

    assert response.status == "200"
    assert "Example Domain" in response.body


def test_https():
    url = "https://browser.engineering/examples/example1-simple.html"

    response = URL(url).request()

    assert response.status == "200"

    assert "This is a simple" in response.body
    assert "web page with some" in response.body
    assert "text in it." in response.body
