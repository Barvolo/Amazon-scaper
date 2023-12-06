Amazon Price Comparison Web Application

[![Video Title](https://img.youtube.com/vi/8TZqG4Co2gg/0.jpg)](https://www.youtube.com/watch?v=8TZqG4Co2gg)


This application allows users to search for products on Amazon and compare prices across different Amazon websites (Amazon.com, Amazon.co.uk, Amazon.de, Amazon.ca).
Getting Started

    download the source code.
    Install the required packages .
    Run the Flask app by executing flask run.
    Open your web browser and visit http://localhost:5000 to start using the application.

How to Use

    Enter a search query in the input field and click the "SEARCH" button.
    Browse the search results and click on a product to view its price comparison across different Amazon websites.
    To view your past searches, click the "My past searches" link.

Folder Structure

    app.py: The main Python file containing the Flask application logic.
    static/: Contains the static files for the application, such as JavaScript and CSS files.
        app.js: The JavaScript file handling frontend logic, including API calls and DOM manipulation.
        styles.css: The CSS file for styling the application.
    templates/: Contains the HTML template files.
        index.html: The main HTML file for the application.

Dependencies

    Flask: A lightweight web framework for Python.
    BeautifulSoup: A library for parsing HTML and XML documents.
    Requests: A library for making HTTP requests in Python.
    
Installation

Ensure you have Python 3 installed on your system.

    Create a virtual environment:

python -m venv venv

Activate the virtual environment:

    On Windows:

.\venv\Scripts\activate

On macOS/Linux:

bash

source venv/bin/activate

Running the Application

    Set the Flask environment variables:
        On Windows:

        arduino

set FLASK_APP=app.py
set FLASK_ENV=development

On macOS/Linux:

arduino

    export FLASK_APP=app.py
    export FLASK_ENV=development

Run the Flask app:

arduino

flask run

Open your web browser and visit http://localhost:5000 to start using the application.
