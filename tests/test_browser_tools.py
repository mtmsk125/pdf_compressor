"""Smoke tests for browser-based tool pages and the PDF tools interface."""

import unittest

from app import app


class BrowserToolsSmokeTests(unittest.TestCase):
    def setUp(self):
        app.config.update(TESTING=True)
        self.client = app.test_client()

    def test_pdf_tools_page_is_available_and_describes_local_processing(self):
        response = self.client.get("/tools")

        self.assertEqual(response.status_code, 200)
        html = response.get_data(as_text=True)
        self.assertIn("أدوات PDF تعمل في متصفحك", html)
        self.assertIn("دون رفعها إلى خادم الموقع", html)

    def test_pdf_tools_page_exposes_the_initial_week_one_operations(self):
        response = self.client.get("/tools")
        html = response.get_data(as_text=True)

        self.assertEqual(response.status_code, 200)
        for tool_value in ("merge", "extract", "rotate"):
            with self.subTest(tool=tool_value):
                self.assertIn(f'value="{tool_value}"', html)

        # Guard that document operations continue to use the browser-side PDF library.
        self.assertIn("PDFDocument.create()", html)
        self.assertIn("PDFDocument.load", html)
        self.assertIn("savePdf(output, filename)", html)

    def test_pdf_tools_page_exposes_the_extended_week_two_operations(self):
        response = self.client.get("/tools")
        html = response.get_data(as_text=True)

        self.assertEqual(response.status_code, 200)
        for tool_value in (
            "reorder",
            "remove",
            "duplicate",
            "pageNumbers",
            "watermark",
            "blankPages",
            "info",
        ):
            with self.subTest(tool=tool_value):
                self.assertIn(f'value="{tool_value}"', html)

        self.assertIn("ترتيب الصفحات الجديد", html)
        self.assertIn("العلامة المائية", html)
        self.assertIn("عدد الصفحات الفارغة", html)

    def test_image_and_text_tool_pages_are_available(self):
        for path in ("/image_tools", "/text_tools"):
            with self.subTest(path=path):
                response = self.client.get(path)
                self.assertEqual(response.status_code, 200)


if __name__ == "__main__":
    unittest.main()
