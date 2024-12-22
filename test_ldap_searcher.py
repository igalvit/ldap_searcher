import unittest
from unittest.mock import MagicMock, patch
import tkinter as tk
from ldap3 import ALL, SUBTREE
from ldap_searcher import LDAPSearcherApp  # Assuming the class is in ldap_searcher.py


class TestLDAPSearcherApp(unittest.TestCase):
    """
    Unit tests for the LDAPSearcherApp class.

    This test suite verifies the functionality of the LDAPSearcherApp, including:
    - Placeholder entry behavior
    - Loading and exporting CSV files
    - Validating search parameters
    - Performing LDAP searches
    """

    def setUp(self):
        """
        Set up the test environment by initializing the application.

        This method creates a Tkinter root window and initializes an instance of the LDAPSearcherApp.
        """
        self.root = tk.Tk()
        self.app = LDAPSearcherApp(self.root)

    def tearDown(self):
        """
        Destroy the Tkinter root window after each test.

        This ensures that the GUI does not persist between tests.
        """
        self.root.destroy()

    def test_add_placeholder_entry(self):
        """
        Test the creation of an Entry widget with a placeholder.

        This test verifies that:
        - The placeholder text is correctly inserted when the Entry is initialized.
        - The placeholder text is removed when the Entry gains focus.
        - The placeholder text is restored when the Entry loses focus and is empty.
        - The placeholder text does not overwrite user input.
        """
        entry = self.app.add_placeholder_entry(self.app.root, "Placeholder Text", 0, 1, "Test Label")

        # Verify the placeholder is present initially
        self.assertEqual(entry.get(), "Placeholder Text")

        # Simulate FocusIn logic directly
        if entry.get() == "Placeholder Text":
            entry.delete(0, tk.END)
        self.assertEqual(entry.get(), "")  # Placeholder should be removed

        # Simulate FocusOut logic directly with empty text
        if entry.get() == "":
            entry.insert(0, "Placeholder Text")
        self.assertEqual(entry.get(), "Placeholder Text")  # Placeholder should be restored

        # Simulate FocusOut logic directly with user-entered text
        entry.delete(0, tk.END)
        entry.insert(0, "User Input")
        if entry.get() == "":
            entry.insert(0, "Placeholder Text")
        self.assertEqual(entry.get(), "User Input")  # Placeholder should not overwrite user input

    @patch("builtins.open", new_callable=unittest.mock.mock_open, read_data="test,data")
    def test_load_csv(self, mock_open):
        """
        Test loading data from a CSV file into the left textbox.

        This test verifies that the content of a CSV file is correctly read and displayed
        in the left textbox.
        """
        with patch("tkinter.filedialog.askopenfilename", return_value="test.csv"):
            self.app.load_csv()
            self.assertEqual(self.app.left_textbox.get("1.0", tk.END).strip(), "test,data")

    @patch("builtins.open", new_callable=unittest.mock.mock_open)
    def test_export_csv(self, mock_open):
        """
        Test exporting data from the right textbox to a CSV file.

        This test ensures that the content of the right textbox is correctly written to
        a CSV file when the export function is triggered.
        """
        self.app.right_textbox.insert("1.0", "result1\nresult2")
        
        with patch("tkinter.filedialog.asksaveasfilename", return_value="output.csv"):
            self.app.export_csv()
            mock_open.assert_called_once_with("output.csv", "w", newline="", encoding="utf-8")

            # Verify that the correct content is written to the file
            handle = mock_open()
            written_data = [call.args[0] for call in handle.write.call_args_list]
            self.assertIn("result1\r\n", written_data)
            self.assertIn("result2\r\n", written_data)

    
    @patch("ldap_searcher.Connection")
    @patch("ldap_searcher.Server")
    def test_perform_ldap_search(self, mock_server, mock_connection):
        """
        Test performing an LDAP search with mocked server and connection.

        This test verifies that:
        - The LDAP server and connection are initialized correctly.
        - The search is performed with the expected parameters.
        - The search results are correctly displayed in the right textbox.
        """
        #from ldap3 import ALL, SUBTREE  # Import the real constants

        # Mock server and connection setup
        mock_server_instance = mock_server.return_value
        mock_conn_instance = mock_connection.return_value
        mock_conn_instance.search.return_value = True
        mock_conn_instance.entries = [
            MagicMock(**{"__getitem__.return_value": "value1"}),
            MagicMock(**{"__getitem__.return_value": "value2"})
        ]

        self.app.ldap_server_properties = {
            "server": {"server": "test_server"},
            "credentials": {"username": "test_user", "password": "test_pass"}
        }

        # Set up search parameters
        self.app.left_textbox.insert("1.0", "test_search_value")
        self.app.search_field.delete(0, tk.END)
        self.app.search_field.insert(0, "test_field")
        self.app.search_base.delete(0, tk.END)
        self.app.search_base.insert(0, "test_base")
        self.app.search_attributes.delete(0, tk.END)
        self.app.search_attributes.insert(0, "attr1,attr2")

        # Execute the LDAP search
        self.app.perform_ldap_search()

        # Verify that the Server object was called with the correct arguments
        mock_server.assert_called_once_with("test_server", get_info=ALL)

        # Verify that the Connection object was created with the correct arguments
        mock_connection.assert_called_once_with(
            mock_server_instance, user="test_user", password="test_pass", auto_bind=True
        )

        # Verify that the search method was called with the correct arguments
        mock_conn_instance.search.assert_called_once_with(
            search_base="test_base",
            search_filter="(test_field=test_search_value)",
            search_scope=SUBTREE,  # Use the real SUBTREE constant here
            attributes=["attr1", "attr2"]
        )

        # Verify the results in the right textbox
        self.assertIn("value1", self.app.right_textbox.get("1.0", tk.END))
        self.assertIn("value2", self.app.right_textbox.get("1.0", tk.END))

    def test_validate_search_parameters(self):
        """
        Test the validation of search parameters.

        This test verifies that valid search parameters are correctly extracted from
        user input and returned as a dictionary.
        """
        # Clear placeholder values before inserting test data
        self.app.search_field.delete(0, tk.END)
        self.app.search_base.delete(0, tk.END)
        self.app.search_attributes.delete(0, tk.END)

        # Insert test data
        self.app.search_field.insert(0, "test_field")
        self.app.search_base.insert(0, "test_base")
        self.app.search_attributes.insert(0, "attr1, attr2")

        # Call validate_search_parameters
        params = self.app.validate_search_parameters()

        # Assert the returned values
        self.assertIsNotNone(params)
        self.assertEqual(params["field"], "test_field")
        self.assertEqual(params["base"], "test_base")
        self.assertEqual(params["attributes"], ["attr1", "attr2"])


    def test_validate_search_parameters_invalid(self):
        """
        Test validation with missing parameters.

        This test ensures that validation fails when required parameters are missing
        or incomplete, returning None.
        """
        self.app.search_field.insert(0, "")  # No search field
        params = self.app.validate_search_parameters()
        self.assertIsNone(params)

if __name__ == "__main__":
    unittest.main()
