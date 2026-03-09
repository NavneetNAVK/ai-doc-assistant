from playwright.sync_api import sync_playwright


def test_chat_page_loads():

    with sync_playwright() as p:

        browser = p.chromium.launch(headless=False)
        page = browser.new_page()

        page.goto("http://127.0.0.1:8000")

        assert "Nexus" in page.content()

        browser.close()

def test_sidebar_toggle():

    with sync_playwright() as p:

        browser = p.chromium.launch(headless=False)
        page = browser.new_page()

        page.goto("http://127.0.0.1:8000")

        page.click(".menu-btn")

        assert page.locator(".sidebar").is_visible()

        browser.close()

def test_send_message():

    with sync_playwright() as p:

        browser = p.chromium.launch(headless=False)
        page = browser.new_page()

        page.goto("http://127.0.0.1:8000")

        page.fill('input[name="query"]', "hello, Generate summary of the document")

        page.click(".send-btn")

        assert "hello" in page.content()

        browser.close()
      
def test_pdf_modal():

    with sync_playwright() as p:

        browser = p.chromium.launch(headless=False)
        page = browser.new_page()

        page.goto("http://127.0.0.1:8000/chat/55/")

        if page.locator(".pdf-card").count() > 0:
            page.click(".pdf-card")
            assert page.locator("#pdfModal").is_visible()

        browser.close()