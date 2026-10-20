import unittest
from agent import list_invoices, read_invoice, save_invoice, verify_invoice

class ToolsTest(unittest.TestCase):
    def test_list(self):
        self.assertGreaterEqual(len(list_invoices()), 3)
    def test_path_traversal(self):
        self.assertIn('error', read_invoice('../.env'))
    def test_invalid_data(self):
        result = save_invoice('INV-1002','ABC Technologies','2026-10-18','2026-11-18','-1','INR','INV-1002.txt')
        self.assertIn('error', result)
    def test_save_and_verify(self):
        result = save_invoice('INV-1002','ABC Technologies','2026-10-18','2026-11-18','18900','INR','INV-1002.txt')
        self.assertIn(result['status'], ('saved','already_exists'))
        self.assertTrue(verify_invoice('INV-1002')['verified'])

if __name__ == '__main__':
    unittest.main()
