# LDAP Searcher Application

This is an LDAP search application built using Python and Tkinter. It allows users to connect to an LDAP server, perform searches based on user-defined parameters, and export results to CSV files.

## Features

- **CSV Import/Export:**
  - Load search data from a CSV file.
  - Export search results to a CSV file.

- **LDAP Search:**
  - Configure LDAP server details via properties file.
  - Perform searches using specified filters, base, and attributes.
  - Display results in a user-friendly interface.

- **Placeholder Support:**
  - User-friendly placeholders in input fields.

## Requirements

Ensure the following Python packages are installed:

```bash
pip install -r requirements.txt
```

### Dependencies:
- `tkinter`
- `ldap3`
- `unittest`
- `configparser`

## Usage

### Running the Application

Run the `ldap_searcher.py` file to start the application:

```bash
python ldap_searcher.py
```

### Testing

Run the unit tests using the `unittest` module:

```bash
python -m unittest discover
```

## File Structure

```
.
├── ldap_searcher.py       # Main application
├── test_ldap_searcher.py     # Unit tests
├── requirements.txt          # Project dependencies
├── .gitignore                # Git ignore rules
├── README.md                 # Documentation
```

## Contributing

Contributions are welcome! If you encounter any issues or have feature requests, please submit a pull request or open an issue.

## License

This project is licensed under the MIT License. See the `LICENSE` file for details.
