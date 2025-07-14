# Developer Guide for Pesticide and Insecticide Dose Calculator

## Overview

This document provides technical details about the Pesticide and Insecticide Dose Calculator web application, designed to assist developers in understanding, modifying, and maintaining the codebase.

## Architecture

The application follows a simple client-server architecture using the Flask web framework for the backend and standard web technologies (HTML, CSS, JavaScript) for the frontend.

-   **Frontend:** Located in the `templates/` (HTML) and `static/` (CSS, JavaScript) directories. Handles the user interface, language switching, and communication with the backend via asynchronous JavaScript calls (Fetch API).
-   **Backend:** A Flask application (`app.py`) that handles HTTP requests, interacts with the SQLite database, performs dose calculations and unit conversions, and provides data to the frontend.
-   **Database:** An SQLite database (`pesticide_recommendations.db`) is used to store crop information, pest/disease data, chemical details, and recommendation records.

## Database Schema

The SQLite database has the following tables:

-   **`Crops`**: Stores information about different crop types.
    -   `crop_id` (INTEGER PRIMARY KEY AUTOINCREMENT): Unique identifier.
    -   `crop_name_en` (TEXT UNIQUE NOT NULL): Crop name in English.
    -   `crop_name_hi` (TEXT UNIQUE NOT NULL): Crop name in Hindi.

-   **`PestsDiseases`**: Stores information about different pests and diseases.
    -   `pest_disease_id` (INTEGER PRIMARY KEY AUTOINCREMENT): Unique identifier.
    -   `pest_disease_name_en` (TEXT UNIQUE NOT NULL): Name in English.
    -   `pest_disease_name_hi` (TEXT UNIQUE NOT NULL): Name in Hindi.

-   **`Chemicals`**: Stores information about recommended chemicals.
    -   `chemical_id` (INTEGER PRIMARY KEY AUTOINCREMENT): Unique identifier.
    -   `chemical_name_en` (TEXT UNIQUE NOT NULL): Chemical name in English.
    -   `chemical_name_hi` (TEXT UNIQUE NOT NULL): Chemical name in Hindi.

-   **`Recommendations`**: Links crops, pests/diseases, and chemicals, storing dose information and sources.
    -   `recommendation_id` (INTEGER PRIMARY KEY AUTOINCREMENT): Unique identifier.
    -   `crop_id` (INTEGER): Foreign key referencing `Crops.crop_id`.
    -   `pest_disease_id` (INTEGER): Foreign key referencing `PestsDiseases.pest_disease_id`.
    -   `chemical_id` (INTEGER): Foreign key referencing `Chemicals.chemical_id`.
    -   `recommended_dose` (REAL NOT NULL): Numerical value of the dose.
    -   `unit` (TEXT NOT NULL): Unit of the recommended dose (e.g., g/acre, ml/liter).
    -   `source` (TEXT): Source of the recommendation (e.g., URL, publication details).

## Backend Logic (`app.py`)

-   **Database Connection:** The `get_db()` function establishes a connection to the SQLite database, and `close_db()` closes it. `db.row_factory = sqlite3.Row` is used to access columns by name.
-   **Table Creation and Data Insertion:** `create_tables()` sets up the database schema. `insert_example_data()` populates the tables with sample data (this should be replaced with a proper data loading mechanism for production).
-   **Routes:**
    -   `/`: Renders the `index.html` template.
    -   `/get_crops` (GET): Returns a JSON list of crops (English and Hindi names).
    -   `/get_pests_diseases` (GET): Takes `crop_en` as a query parameter and returns a JSON list of pests/diseases relevant to that crop.
    -   `/calculate` (POST): Receives user input (crop, pest/disease, area, units, language) as JSON. Queries the database for the recommendation, performs dose calculation using `calculate_dose()`, and returns the result or an error as JSON.
-   **`get_recommendation(crop_name_en, pest_disease_name_en)`:** Queries the `Recommendations` table, joining with `Crops`, `PestsDiseases`, and `Chemicals` to find a recommendation based on English crop and pest/disease names.
-   **`calculate_dose(recommended_dose, recommended_unit, area, area_unit, desired_output_unit)`:** This function handles dose calculations and unit conversions.
    -   It first converts the input `area` to acres if it's in hectares.
    -   It then attempts to convert the `recommended_dose` to a common base unit (currently supports g/acre, kg/acre, ml/acre, liter/acre conversions to grams/acre or ml/acre).
    -   The total dose for the given area is calculated.
    -   Finally, it converts the total dose to the `desired_output_unit` if a supported conversion path exists.
    -   **Note:** Conversions involving units like ppm, ppb, or percentage solutions, or conversions between weight (grams/kg) and volume (ml/liter) require chemical density information, which is not currently stored in the database. This function needs to be extended with more conversion factors and potentially density data for comprehensive unit handling.

## Frontend Structure (`templates/index.html`, `static/style.css`, `static/script.js`)

-   **`index.html`:** Defines the HTML structure of the single-page application. Includes input forms, output display areas, and language toggle buttons. Links to `style.css` and `script.js`.
-   **`style.css`:** Provides basic styling for the layout and form elements.
-   **`script.js`:** Handles client-side interactions:
    -   Event listeners for language buttons to switch `currentLang` and update UI text using the `textElements` dictionary.
    -   Fetches crop data on page load and populates the crop dropdown.
    -   Event listener on the crop dropdown to fetch and populate the pest/disease dropdown based on the selected crop.
    -   Event listener on the "Calculate" button to gather input, make a POST request to `/calculate`, and display the results or errors.
    -   Includes placeholder functions (`updateAreaUnitOptions`, `updateOutputUnitOptions`) for handling unit label translation if needed in the future.

## Deployment

The application is designed to be deployed on platforms that support Python/Flask applications.

1.  **Prerequisites:** Ensure you have Python, Flask, and Gunicorn installed (or rely on the hosting platform's environment).
2.  **Files:** The necessary files for deployment are `app.py`, `templates/` directory, `static/` directory, `requirements.txt`, and `Procfile`.
3.  **`requirements.txt`:** Lists Python dependencies (`Flask`, `gunicorn`).
4.  **`Procfile`:** Specifies how the application should be run in a production environment (e.g., `web: gunicorn app:app`).
5.  **Database:** For production, consider migrating from SQLite to a more robust database like PostgreSQL or MySQL, especially if concurrent access is expected. Update the database connection logic in `get_db()` accordingly, potentially using environment variables for credentials.
6.  **Initialization:** Ensure the `init_db()` function (or equivalent database migration/setup script) is run *once* on the hosting environment to create tables and populate initial data. How this is done is platform-dependent (e.g., a custom management command, a separate script run via the platform's console).
7.  **Platform-Specific Steps:** Follow the deployment instructions for your chosen hosting platform (e.g., Git push to Heroku, deploying via AWS Elastic Beanstalk console, etc.).

## Maintenance and Updates

Ongoing maintenance and updates are crucial for the application's accuracy and usability.

### 1. Data Updates

-   **Source Monitoring:** Regularly monitor authentic government sources (e.g., ICAR, state agricultural department websites, Krishi Vigyan Kendras) for updated recommendations on pesticides, insecticides, doses, and new information on diseases and pests.
-   **Data Extraction:** Develop or use tools/scripts to extract updated data efficiently. This might involve web scraping (ensure compliance with website terms of service) or processing official publications.
-   **Database Schema Review:** If new types of information become available (e.g., specific application methods, safety intervals), review and update the database schema as needed.
-   **Data Loading:** Implement a robust process for loading updated data into the database. This should handle adding new records, updating existing ones, and potentially archiving outdated information. Consider using a data migration script or an administrative interface.

### 2. Unit Conversion Formulas

-   **Verification:** Periodically review the unit conversion formulas in the `calculate_dose()` function. Ensure they are accurate and cover all necessary conversions.
-   **Expansion:** If recommendations are found in new units (e.g., per square meter, per plant) or if conversions requiring density become necessary, update the `calculate_dose()` function and potentially the database schema (to store density information for chemicals).
-   **Testing:** Thoroughly test any changes to unit conversion logic with a range of input values and units.

### 3. Bug Fixing and Performance

-   **Monitoring:** Implement logging and error tracking to identify bugs in the backend. Monitor frontend errors through browser developer consoles or dedicated error monitoring services.
-   **Testing:** Maintain a suite of test cases (unit tests for backend functions, integration tests, end-to-end tests for the web interface) to catch regressions when making changes.
-   **Performance Optimization:** Monitor application performance (response times, database query performance). Optimize database queries, backend logic, or frontend rendering if performance bottlenecks are identified.

### 4. Feature Enhancements

-   **User Feedback:** Gather feedback from users (farmers and students) to understand their needs and identify potential new features (e.g., support for more crops/pests, adding information on organic alternatives, visual guides for diseases/pests).
-   **Language Support:** If expanding to other regional languages is desired, extend the database schema and frontend language handling logic.
-   **Accessibility:** Continuously work on improving the application's accessibility for users with disabilities.

### 5. Technical Stack Updates

-   **Dependency Management:** Regularly update Flask, Gunicorn, and other Python dependencies to benefit from bug fixes and security patches. Use `pip freeze > requirements.txt` or a dependency management tool to manage versions.
-   **Frontend Libraries:** If any JavaScript libraries are used (currently none, but could be added for UI improvements), keep them updated.
-   **Security:** Stay informed about common web security vulnerabilities (e.g., SQL injection, XSS) and ensure the application code follows secure coding practices.

By following this maintenance plan, the Pesticide and Insecticide Dose Calculator can remain a valuable and reliable resource for its users.
