import tkinter as tk
from tkinter import filedialog, messagebox
import csv
import configparser
from ldap3 import Server, Connection, ALL, SUBTREE

class LDAPSearcherApp:
    """
    A GUI-based application for performing LDAP searches and managing CSV data.

    Features:
    - Load search input from a CSV file.
    - Configure and connect to an LDAP server.
    - Perform searches based on user-provided parameters.
    - Display results in the GUI and export them to a CSV file.
    """

    def __init__(self, root):
        """
        Initialize the LDAP searcher application.

        Args:
            root: The main Tkinter window.
        """
        self.root = root
        self.ldap_server_properties = {}

        # Configure main window
        self.root.title("LDAP Searcher by igalvit (2024)")
        self.root.resizable(True, True)

        # Build UI
        self.create_search_frame()
        self.create_ldap_frame()
        self.create_data_frame()
        self.create_results_frame()

    def create_search_frame(self):
        """Create the frame for search parameter inputs."""
        self.search_frame = tk.LabelFrame(self.root, text="Search Parameters")
        self.search_frame.grid(row=0, column=0, padx=10, pady=10, sticky=tk.W)

        self.search_field = self.add_placeholder_entry(
            self.search_frame, "LDAP field to search", row=0, column=1, label="Search Field"
        )
        self.search_base = self.add_placeholder_entry(
            self.search_frame, "LDAP search base", row=1, column=1, label="Search Base"
        )
        self.search_attributes = self.add_placeholder_entry(
            self.search_frame,
            "LDAP attributes to search (separated by commas)",
            row=2,
            column=1,
            label="Search Attributes",
        )

    def create_ldap_frame(self):
        """Create the frame for LDAP server configuration."""
        self.ldap_frame = tk.Frame(self.root)
        self.ldap_frame.grid(row=0, column=1, padx=10, pady=10)

        tk.Button(self.ldap_frame, text="Select LDAP Server", command=self.select_ldap_server).grid(
            row=0, column=0, padx=10, pady=5, sticky=tk.W
        )
        self.ldap_search_button = tk.Button(
            self.ldap_frame, state="disabled", text="LDAP Search", command=self.perform_ldap_search
        )
        self.ldap_search_button.grid(row=0, column=1, padx=10, pady=10, sticky=tk.W)

    def create_data_frame(self):
        """Create the frame for search input data."""
        self.data_frame = tk.LabelFrame(self.root, text="Search Data")
        self.data_frame.grid(row=1, column=0, padx=10, pady=10, sticky=tk.W)

        self.left_textbox = tk.Text(self.data_frame, width=40, height=20)
        self.left_textbox.grid(row=0, column=0, padx=10, pady=10)
        tk.Button(self.data_frame, text="Load CSV", command=self.load_csv).grid(row=1, column=0, pady=10)

    def create_results_frame(self):
        """Create the frame for displaying search results."""
        self.results_frame = tk.LabelFrame(self.root, text="Results")
        self.results_frame.grid(row=1, column=1, padx=10, pady=10, sticky=tk.W)

        self.right_textbox = tk.Text(self.results_frame, width=40, height=20)
        self.right_textbox.grid(row=0, column=0, padx=10, pady=10)
        self.csv_export_button = tk.Button(
            self.results_frame, state="disabled", text="Export CSV", command=self.export_csv
        )
        self.csv_export_button.grid(row=1, column=0, pady=10)

    def add_placeholder_entry(self, parent, placeholder, row, column, label):
        """
        Add an Entry widget with placeholder behavior.

        Args:
            parent: Parent Tkinter widget.
            placeholder: Placeholder text to display.
            row: Row position in the grid.
            column: Column position in the grid.
            label: Label text for the Entry widget.

        Returns:
            The created Entry widget.
        """
        tk.Label(parent, text=label).grid(row=row, column=0, padx=5, pady=5, sticky=tk.W)
        entry = tk.Entry(parent, width=40)
        entry.insert(0, placeholder)

        # Bind placeholder logic
        entry.bind("<FocusIn>", lambda event: entry.delete(0, tk.END) if entry.get() == placeholder else None)
        entry.bind("<FocusOut>", lambda event: entry.insert(0, placeholder) if entry.get() == "" else None)

        entry.grid(row=row, column=column, padx=5, pady=5, sticky=tk.W)
        return entry

    @staticmethod
    def set_placeholder(widget, placeholder):
        """
        Configure a widget with placeholder behavior.

        Args:
            widget: Tkinter widget (e.g., Entry).
            placeholder: Placeholder text to display.
        """
        widget.insert(0, placeholder)
        widget.bind("<FocusIn>", lambda event: widget.delete(0, tk.END) if widget.get() == placeholder else None)
        widget.bind("<FocusOut>", lambda event: widget.insert(0, placeholder) if widget.get() == "" else None)

    def load_csv(self):
        """Load search input data from a CSV file into the left textbox."""
        csv_file = filedialog.askopenfilename(title="Select a CSV file", filetypes=[("CSV files", "*.csv")])
        if csv_file:
            try:
                with open(csv_file, "r", encoding="utf-8") as file:
                    self.left_textbox.delete("1.0", tk.END)
                    self.left_textbox.insert(tk.END, file.read().strip())
            except Exception as e:
                self.show_error("Error loading CSV", e)

    def export_csv(self):
        """Export search results from the right textbox to a CSV file."""
        csv_file = filedialog.asksaveasfilename(
            title="Save as", defaultextension=".csv", filetypes=[("CSV files", "*.csv")]
        )
        if csv_file:
            try:
                content = self.right_textbox.get("1.0", tk.END).strip()
                if content:
                    with open(csv_file, "w", newline="", encoding="utf-8") as file:
                        writer = csv.writer(file)
                        for line in content.splitlines():
                            writer.writerow([line])
                    messagebox.showinfo("Success", "The file was successfully saved.")
                else:
                    self.show_warning("Empty Content", "The results textbox is empty.")
            except Exception as e:
                self.show_error("Error exporting CSV", e)

    def select_ldap_server(self):
        """Load LDAP server properties from a configuration file."""
        file = filedialog.askopenfilename(
            title="Select the file with the LDAP server properties", filetypes=[("Properties files", "*.ini")]
        )
        if file:
            self.ldap_server_properties = self.read_properties_file(file)
            self.ldap_search_button["state"] = tk.ACTIVE

    @staticmethod
    def read_properties_file(file):
        """
        Read and parse a properties file for LDAP server configuration.

        Args:
            file: Path to the properties file.

        Returns:
            A dictionary containing the parsed properties.
        """
        config = configparser.ConfigParser()
        try:
            config.read(file)
            return {section: dict(config.items(section)) for section in config.sections()}
        except Exception as e:
            messagebox.showerror("Error", f"Failed to read properties file: {e}")
            return {}

    def perform_ldap_search(self):
        """Perform an LDAP search based on user-provided parameters."""
        # Check and validate search parameters
        search_params = self.validate_search_parameters()
        if not search_params:
            return

        # Perform LDAP search
        self.right_textbox.delete("1.0", tk.END)
        try:
            server_info = self.ldap_server_properties.get("server", {})
            credentials = self.ldap_server_properties.get("credentials", {})
            server = Server(server_info.get("server"), get_info=ALL)
            conn = Connection(server, user=credentials.get("username"), password=credentials.get("password"), auto_bind=True)

            attributes = search_params["attributes"]
            self.right_textbox.insert(tk.END, ";".join(attributes) + "\n")

            for entry in self.left_textbox.get("1.0", tk.END).strip().splitlines():
                search_filter = f"({search_params['field']}={entry})"
                conn.search(
                    search_base=search_params["base"], search_filter=search_filter, search_scope=SUBTREE, attributes=attributes
                )
                if conn.entries:
                    for result in conn.entries:
                        self.right_textbox.insert(
                            tk.END, ";".join(str(result[attr]) for attr in attributes) + "\n"
                        )
            conn.unbind()
            self.csv_export_button["state"] = tk.ACTIVE
        except Exception as e:
            self.show_error("LDAP Search Error", e)

    def validate_search_parameters(self):
        """
        Validate and retrieve search parameters from the user input.

        Returns:
            A dictionary containing the search parameters if valid, otherwise None.
        """
        field = self.search_field.get()
        base = self.search_base.get()
        attributes = self.search_attributes.get()

        if not field or field == "LDAP field to search":
            self.show_warning("Invalid Input", "Search field is required.")
            return None
        if not base or base == "LDAP search base":
            self.show_warning("Invalid Input", "Search base is required.")
            return None
        if not attributes or attributes == "LDAP attributes to search (separated by commas)":
            self.show_warning("Invalid Input", "At least one search attribute is required.")
            return None
        # This is strange but it's for user's convenience to show as the first
        # attribute the same used as search field.
        attributes = f"{field}," + attributes 
        return {"field": field, "base": base, "attributes": [attr.strip() for attr in attributes.split(",")]}  

    @staticmethod
    def show_warning(title, message):
        """Show a warning message box."""
        messagebox.showwarning(title, message)

    @staticmethod
    def show_error(title, exception):
        """Show an error message box."""
        messagebox.showerror(title, f"{exception.__class__.__name__}: {exception}")

if __name__ == "__main__":
    root = tk.Tk()
    app = LDAPSearcherApp(root)
    root.mainloop()
