'''
PHASE 1 — UNIT TESTS (FAST, REQUIRED)
🎯 Goal
Test core business logic in isolation without relying on templates, HTTP, or the browser.
These tests run very fast and catch most backend bugs early.
Run them frequently during development.
'''

'import'
from django.test import TestCase
from chat.models import ChatSession, ChatMessage
from django.core.files.uploadedfile import SimpleUploadedFile
from unittest.mock import patch
from chat.services import search_document
from django.urls import reverse
from django.test import TestCase

'''
Test1: Chat Session Creation
What this ensures:
✔ session saves correctly
✔ database works
✔ model fields behave correctly
'''
class ChatSessionTests(TestCase):

    def test_create_chat_session(self):
        session = ChatSession.objects.create(title="Test Chat")

        self.assertEqual(session.title, "Test Chat")
        self.assertIsNotNone(session.id)

'''
Test2: Message Saving
This catches:
✔ model errors
✔ foreign key issues
✔ role/content mistakes
'''        
class MessageTests(TestCase):

    def test_message_creation(self):
        session = ChatSession.objects.create(title="Chat")

        msg = ChatMessage.objects.create(
            session=session,
            role="user",
            content="Hello"
        )

        self.assertEqual(msg.content, "Hello")
        self.assertEqual(msg.role, "user")
        self.assertEqual(msg.session, session)
'''
Test3: PDF Upload Validation
This verifies:
✔ uploads work
✔ form accepts PDFs
✔ server doesn't crash
'''

class FileUploadTest(TestCase):

    def test_rejects_non_pdf(self):
        fake_file = SimpleUploadedFile(
            "test.txt",
            b"hello",
            content_type="text/plain"
        )

        response = self.client.post("/chat/", {
            "document": fake_file
        })

        self.assertNotEqual(response.status_code, 200)
'''
Test4: RAG / Service Logic
This ensures:
✔ RAG pipeline works
✔ AI response returns usable text
✔ no crashes during processing
'''     
class RagTests(TestCase):

    @patch("chat.services.requests.post")
    def test_search_document_returns_text(self, mock_post):

        # Fake Gemini API response
        mock_post.return_value.status_code = 200
        mock_post.return_value.json.return_value = {
            "candidates": [{
                "content": {
                    "parts": [{
                        "text": "<p>Mock AI response</p>"
                    }]
                }
            }]
        }

        # Call service
        response = search_document("What is AI?")

        # Assertions
        self.assertIsInstance(response, str)
        self.assertTrue(len(response) > 0)

'''
PHASE 2 — Integration Tests (Views + Templates)

These tests check that Django views, templates, and context work together.

They do NOT test AI logic — only your web app behavior.

We verify:

Chat page loads

Sidebar sessions render

Messages render

CSRF token exists

Chat session URL works
'''



class ChatViewTests(TestCase):

    def setUp(self):
        # Create a chat session
        self.session = ChatSession.objects.create(title="Integration Test Chat")

        # Create messages
        ChatMessage.objects.create(
            session=self.session,
            role="user",
            content="Hello AI"
        )

        ChatMessage.objects.create(
            session=self.session,
            role="ai",
            content="Hello human"
        )


    def test_chat_page_loads(self):
        """Chat page should return 200"""
        url = reverse("chat_session", args=[self.session.id])
        response = self.client.get(url)

        self.assertEqual(response.status_code, 200)


    def test_sidebar_sessions_render(self):
        """Sidebar should show existing sessions"""
        url = reverse("chat_session", args=[self.session.id])
        response = self.client.get(url)

        self.assertContains(response, "Integration Test Chat")


    def test_messages_render(self):
        """Messages should appear in template"""
        url = reverse("chat_session", args=[self.session.id])
        response = self.client.get(url)

        self.assertContains(response, "Hello AI")
        self.assertContains(response, "Hello human")


    def test_csrf_token_present(self):
        """Forms should include CSRF token"""
        url = reverse("chat_session", args=[self.session.id])
        response = self.client.get(url)

        self.assertContains(response, "csrfmiddlewaretoken")