# LinkedIn Reference Checker

## Overview
The **LinkedIn Reference Checker** is a web-based application designed to help employers or teams compare the work experiences of different employees based on their LinkedIn profiles. This project automates the process of fetching employee profiles, identifying shared work experiences, and displaying commonalities between employees. It aims to streamline HR processes or background checks by leveraging LinkedIn data in a simple, organized way.

## Features
- **Fetch LinkedIn Profiles**: Automatically retrieve detailed work experience data from LinkedIn profiles using an API.
- **Check for Shared Experiences**: Compare employees' work experiences and identify any overlap in companies or roles.
- **View Results**: Display shared job roles, companies, and timeframes directly in the app.
- **Manage Employees**: Add, delete, or view employee profiles in the application.
- **Multiple LinkedIn Profiles**: Add multiple LinkedIn profiles at once for batch processing.
  
## Purpose
The goal of this project is to allow organizations to quickly analyze and compare employee profiles to see if any employees share common job roles or employers, which can be useful for building teams, checking references, or streamlining the recruitment process.

## How It Works
1. **User Authentication**: Users can create an account and log in to manage their employee data.
2. **Input LinkedIn URLs**: Users can input LinkedIn profile URLs for employees they want to analyze.
3. **API Integration**: The application integrates with a LinkedIn data scraper API to fetch profile details.
4. **Shared Experience Detection**: The system compares work experiences and identifies any overlap in job roles or companies.
5. **View Results**: Users can view the shared work experiences in an organized format within the app.

## Technologies Used
- **Backend**: Python (Flask Framework)
- **Frontend**: HTML, CSS, JavaScript
- **Database**: SQLAlchemy for data management
- **API Integration**: RapidAPI for LinkedIn profile data scraping
- **Authentication**: Flask-Login for user authentication

## Setup Instructions
1. Clone the repository:
    ```bash
    git clone https://github.com/yourusername/linkedin-reference-checker.git
    cd linkedin-reference-checker
    ```

2. Install the required dependencies:
    ```bash
    pip install -r requirements.txt
    ```

3. Set up environment variables for the LinkedIn API keys and other configuration details:
    ```bash
    export RAPIDAPI_KEY=<your-rapidapi-key>
    export RAPIDAPI_HOST=<your-rapidapi-host>
    ```

4. Initialize the database:
    ```bash
    flask db init
    flask db migrate
    flask db upgrade
    ```

5. Run the Flask application:
    ```bash
    flask run
    ```

6. Access the app via `http://127.0.0.1:5000/`.

## Future Enhancements
- **Data Analytics**: Add features to analyze work history trends between employees.
- **Reporting**: Generate downloadable reports of shared experiences for HR teams.
- **Improved Error Handling**: Implement better error reporting for failed LinkedIn profile fetches.
  

