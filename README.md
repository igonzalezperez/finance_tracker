# Expense Tracker App Backend

## Description

This project is the backend part of an expense tracking application, developed in Django. It's designed to manage and record financial transactions efficiently. The backend handles core functionalities such as data management and processing.

### Current Features
- **Transactions Model:** A robust model to store transaction data, with fields like date, item, category, and more. Each row in the database represents a single financial transaction.

### Future Enhancements
- **Frontend Development:** The frontend will be developed in a separate repository, focusing on user interaction and data presentation.
- **Analytics Features:** Future plans include implementing analytics for tracking expenses by category and visualizing financial data.

## Installation

This project uses PDM for dependency management.

1. **Clone the Repository:**
   ```bash
   git clone https://github.com/igonzalezperez/finance_tracker.git
   ```
2. **Install dependencies:**
   If pdm isn't installed, use `pip install pdm` first.
   ```bash
   pdm install
   ```
3. **Usage:**
   You'll need to have a secret key as an env variable, you can create one with:
   ```
   import secrets
   print(secrets.token_urlsafe(50))
   ```
   Then paste that into a .env file (follow the .env.example file)
   ```
   pdm run python manage.py migrate
   pdm run  python manage.py runserver
   ```
   The server will start on http://127.0.0.1:8000/. You can access the API endpoints from there.