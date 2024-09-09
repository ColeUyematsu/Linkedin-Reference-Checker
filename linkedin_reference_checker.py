import requests
import pandas as pd
import re
from datetime import datetime


# API Call to Fetch LinkedIn Profiles
def fetch_linkedin_profiles(linked_urls):
    """
    Fetch LinkedIn profiles using the RapidAPI LinkedIn Bulk Data Scraper.

    Parameters:
    - linked_urls: List of LinkedIn profile URLs.

    Returns:
    - A list of dictionaries containing LinkedIn profile data.
    """
    url = "https://linkedin-bulk-data-scraper.p.rapidapi.com/profiles"
    
    payload = {"links": linked_urls}
    headers = {
        "x-rapidapi-key": "6aa1f124cfmsh15b0cec6407acc6p13ba6cjsn98da755dc51e",
        "x-rapidapi-host": "linkedin-bulk-data-scraper.p.rapidapi.com",
        "Content-Type": "application/json",
        "x-rapidapi-user": "usama"
    }
    

    response = requests.post(url, json=payload, headers=headers)
    
    if response.status_code == 200:
        return response.json().get('data', [])
    else:
        print(f"Failed to fetch data: {response.status_code} - {response.text}")
        return []

def process_profile_data(profiles):
    """
    Process LinkedIn profile data to extract relevant information.

    Parameters:
    - profiles: A list of LinkedIn profiles as dictionaries.

    Returns:
    - A pandas DataFrame with the processed profile data.
    """
    employee_data = []

    for profile in profiles:
        full_name = profile['data'].get('fullName', profile['data'].get('firstName', '') + ' ' + profile['data'].get('lastName', ''))
        linkedin_url = profile.get('entry')

        experiences = profile['data'].get('experiences', [])
        experience_details = []

        for experience in experiences:
            if experience.get('breakdown', False):
                sub_experiences = experience.get('subComponents', [])
                for sub_exp in sub_experiences:
                    title = sub_exp.get('title', 'N/A')
                    company = experience.get('title', 'N/A')  
                    start_date = sub_exp.get('caption', 'N/A').split(' · ')[0]  
                    duration = sub_exp.get('caption', 'N/A')
                    experience_details.append(f"{title} at {company} ({start_date} - {duration})")
            else:
                title = experience.get('title', 'N/A')
                company = experience.get('subtitle', 'N/A')
                duration = experience.get('caption', 'N/A')
                experience_details.append(f"{title} at {company} ({duration})")

        experience_str = "; ".join(experience_details)

        employee_data.append({
            "Name": full_name,
            "Experience": experience_str,
            "LinkedIn URL": linkedin_url
        })

    return pd.DataFrame(employee_data)

# Fetch Single Employee Data
def fetch_employee_data(linkedin_url):
    profile_data = fetch_linkedin_profiles([linkedin_url])
    if profile_data:
        profile = profile_data[0]
        full_name = profile.get('fullName', 'Unknown')
        experiences = profile.get('experiences', [])
        parsed_experience = []

        for experience in experiences:
            title = clean_title(experience.get('title', 'N/A'))
            company = normalize_company_name(experience.get('subtitle', 'N/A'))
            start_date, end_date = parse_dates(experience.get('caption', 'N/A'))
            
            # Ensure both start_date and end_date are not None
            if start_date and end_date:
                parsed_experience.append({
                    'Title': title,
                    'Company': company,
                    'Start Date': start_date,
                    'End Date': end_date
                })
        
        # Check if any experiences were successfully parsed
        if not parsed_experience:
            print(f"No valid experiences found for LinkedIn profile: {linkedin_url}")
            return None

        return {
            "Name": full_name,
            "LinkedIn URL": linkedin_url,
            "Parsed Experience": parsed_experience
        }
    return None

# Normalize Company Names
def normalize_company_name(name):
    unwanted_phrases = [
        'full-time', 'part-time', 'contract', 'internship', 'seasonal', 
        'temporary', 'consultant', 'freelance', 'remote', 'volunteer', 
        'casual', 'apprentice', 'co-op', 'graduate', 'entry-level', 
        'per diem', 'project-based', 'shift', 'intern', 'associate', 
        'trainee'
    ]
    name = re.sub(r'\b(?:' + '|'.join(unwanted_phrases) + r')\b', '', name, flags=re.IGNORECASE)
    name = re.sub(r'[·.,]', '', name)
    name = re.sub(r'\s+', ' ', name.strip().lower())  # Normalize spaces and case
    return name

# Clean Job Titles
def clean_title(title):
    unwanted_phrases = [
        'temporary', 'consultant', 'freelance', 'remote', 'volunteer', 
        'casual', 'apprentice', 'co-op', 'graduate', 'entry-level', 
        'per diem', 'project-based', 'shift', 'trainee'
    ]
    title = re.sub(r'\b(?:' + '|'.join(unwanted_phrases) + r')\b', '', title, flags=re.IGNORECASE)
    title = re.sub(r'[·.,]', '', title)
    title = re.sub(r'\s+', ' ', title.strip())
    return title

# Parse Date Ranges
import re
from datetime import datetime

import re
from datetime import datetime

def parse_dates(date_range):
    """
    Parse date ranges that may include:
    - "Start Date - End Date"
    - "Start Date - Present"
    - "Start Date" (only one date)
    - Formats with additional text (e.g., "- 5 yrs 1 mo")

    Returns:
    - start_date (str) in 'YYYY-MM-DD' format or None
    - end_date (str) in 'YYYY-MM-DD' format, 'Present', or None
    """
    # Normalize the date range by stripping any extra text after the first two components
    parts = date_range.split(' - ')

    # Handle cases with exactly two parts
    if len(parts) >= 2:
        start_date_str = parts[0].strip()
        end_date_str = parts[1].strip()

        try:
            start_date = datetime.strptime(start_date_str, '%b %Y').strftime('%Y-%m-%d')
        except ValueError:
            start_date = None
        
        if end_date_str.lower() == 'present':
            end_date = 'Present'
        else:
            try:
                end_date = datetime.strptime(end_date_str, '%b %Y').strftime('%Y-%m-%d')
            except ValueError:
                end_date = None

        return start_date, end_date

    # Handle cases with only one date (likely just a start date)
    elif len(parts) == 1:
        try:
            start_date = datetime.strptime(parts[0].strip(), '%b %Y').strftime('%Y-%m-%d')
        except ValueError:
            start_date = None
        return start_date, None
    
    return None, None



def check_shared_experience(new_employee_data, existing_employees_df):
    shared_experiences = []
    
    for new_experience in new_employee_data.get('Parsed Experience', []):
        normalized_new_company = normalize_company_name(new_experience['Company'])
        new_start_date = datetime.strptime(new_experience['Start Date'], '%Y-%m-%d')
        new_end_date = (
            datetime.strptime(new_experience['End Date'], '%Y-%m-%d')
            if new_experience['End Date'] and new_experience['End Date'] != 'Present'
            else datetime.now()
        )
        
        # To avoid duplicates, keep track of matched existing employees and experiences
        matched_experiences = set()

        for _, existing_employee in existing_employees_df.iterrows():
            normalized_existing_company = normalize_company_name(existing_employee['Company'])
            if existing_employee['Start Date']:
                existing_start_date = datetime.strptime(existing_employee['Start Date'], '%Y-%m-%d')
            else:
                # Skip this employee or handle as needed, setting a default or continue
                existing_start_date = None
                continue 
            existing_end_date = (
                datetime.strptime(existing_employee['End Date'], '%Y-%m-%d')
                if existing_employee['End Date'] and existing_employee['End Date'] != 'Present'
                else datetime.now()
            )

            # Avoid redundant matches by checking if this experience has already been matched
            experience_key = (existing_employee['Name'], existing_employee['Company'], existing_employee['Start Date'], existing_employee['End Date'])
            if experience_key in matched_experiences:
                continue  # Skip if already matched

            # Match company and date ranges
            if normalized_new_company == normalized_existing_company and (new_start_date <= existing_end_date) and (existing_start_date <= new_end_date):
                # Once matched, mark this combination as processed
                matched_experiences.add(experience_key)
                
                shared_experiences.append({
                    'Employee Name': existing_employee.get('Name', 'N/A'),
                    'LinkedIn URL': existing_employee.get('LinkedIn URL', 'N/A'),
                    'Company': new_experience['Company'],
                    'Shared Job Title': existing_employee.get('Title', 'N/A'),
                    'Shared Start Date': max(existing_start_date, new_start_date).strftime('%Y-%m-%d'),
                    'Shared End Date': min(existing_end_date, new_end_date).strftime('%Y-%m-%d') if new_end_date <= existing_end_date else 'Present'
                })
                
    return shared_experiences

def format_shared_experiences(shared_experiences, new_employee_title):
    formatted_output = f"New Employee's Job Title: {new_employee_title}\n\n"
    formatted_output += "Shared Experiences:\n"
    for experience in shared_experiences:
        formatted_output += (
            f"{experience['Employee Name']} ({experience['LinkedIn URL']}) - "
            f"{experience['Company']} ({experience['Shared Start Date']} - {experience['Shared End Date']})\n"
            f"Existing Employee's Job Title: {experience['Shared Job Title']}\n\n"
        )
    return formatted_output