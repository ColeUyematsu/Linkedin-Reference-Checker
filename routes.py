from flask import render_template, url_for, flash, redirect, request
from flask_login import login_user, current_user, logout_user, login_required
from models import db, User, Employee
from linkedin_reference_checker import fetch_employee_data, check_shared_experience, fetch_linkedin_profiles, parse_dates, normalize_company_name, process_profile_data
from werkzeug.security import generate_password_hash, check_password_hash
from flask import Blueprint
import pandas as pd
from datetime import datetime

main = Blueprint('main', __name__)

@main.route("/")
@main.route("/home")
def home():
    return redirect(url_for('main.login'))

@main.route("/register", methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        username = request.form['username']
        email = request.form['email']
        password = generate_password_hash(request.form['password'], method='pbkdf2:sha256')
        
        user = User(username=username, email=email, password=password)
        db.session.add(user)
        db.session.commit()
        flash('Your account has been created!', 'success')
        return redirect(url_for('main.login'))
    
    return render_template('register.html')

@main.route("/login", methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        return redirect(url_for('main.dashboard'))
    if request.method == 'POST':
        email = request.form['email']
        password = request.form['password']
        user = User.query.filter_by(email=email).first()
        if user and check_password_hash(user.password, password):
            login_user(user)
            return redirect(url_for('main.dashboard'))
        else:
            flash('Login Unsuccessful. Please check email and password', 'danger')
    return render_template('login.html')

@main.route("/dashboard")
@login_required
def dashboard():
    employees = Employee.query.filter_by(owner=current_user)
    return render_template('dashboard.html', employees=employees)

@main.route("/add_employee", methods=['POST'])
@login_required
def add_employee():
    if request.method == 'POST':
        linkedin_url = request.form['linkedin_url']
        employee_data = fetch_employee_data(linkedin_url)

        if employee_data:
            name = employee_data.get('Name', 'Unknown')
            experience = "\n".join([f"{exp['Title']} at {exp['Company']} ({exp['Start Date']} - {exp['End Date']})" 
                                    for exp in employee_data.get('Parsed Experience', [])])
            
            employee = Employee(name=name, linkedin_url=linkedin_url, experience=experience, owner=current_user)
            db.session.add(employee)
            db.session.commit()
            flash('Employee added successfully!', 'success')
        else:
            flash('Failed to fetch data from LinkedIn. Please check the URL and try again.', 'danger')

    return redirect(url_for('main.dashboard'))

@main.route("/check_reference", methods=['GET', 'POST'])
@login_required
def check_reference():
    if request.method == 'POST':
        linkedin_url = request.form['linkedin_url']
        profile_data = fetch_linkedin_profiles([linkedin_url])

        if profile_data:
            profile_df = process_profile_data(profile_data)

            if profile_df.empty:
                flash('Failed to parse experiences for the provided LinkedIn profile.', 'danger')
                return redirect(url_for('main.dashboard'))

            # Construct new_employee_data
            new_employee_data = {
                "Name": profile_df.iloc[0]["Name"],
                "LinkedIn URL": profile_df.iloc[0]["LinkedIn URL"],
                "Parsed Experience": []
            }

            # Extract new employee's experience data
            for experience in profile_df.iloc[0]["Experience"].split("; "):
                try:
                    parts = experience.split(" at ", 1)
                    if len(parts) == 2:
                        title, company_duration = parts
                    else:
                        title = parts[0]
                        company_duration = "N/A"

                    parts = company_duration.rsplit(" (", 1)
                    if len(parts) == 2:
                        company, date_range = parts
                    else:
                        company = parts[0]
                        date_range = "N/A"

                    start_date, end_date = parse_dates(date_range.rstrip(")"))
                except ValueError:
                    print(f"Error parsing experience: {experience}")
                    continue

                new_employee_data["Parsed Experience"].append({
                    'Title': title,
                    'Company': normalize_company_name(company),
                    'Start Date': start_date,
                    'End Date': end_date if end_date else 'Present'
                })

            # Fetch existing employees and parse their experiences
            employees_query = Employee.query.filter_by(owner=current_user).all()
            employee_dicts = []

            for employee in employees_query:
                experiences = employee.experience.split('; ')
                for exp in experiences:
                    try:
                        parts = exp.split(" at ", 1)
                        if len(parts) == 2:
                            title, company_duration = parts
                        else:
                            title = parts[0]
                            company_duration = "N/A"

                        parts = company_duration.rsplit(" (", 1)
                        if len(parts) == 2:
                            company, date_range = parts
                        else:
                            company = parts[0]
                            date_range = "N/A"

                        start_date, end_date = parse_dates(date_range)
                        employee_dicts.append({
                            'Name': employee.name,
                            'LinkedIn URL': employee.linkedin_url,
                            'Company': normalize_company_name(company),
                            'Start Date': start_date,
                            'End Date': end_date,
                            'Title': title  # Include the title in the dictionary
                        })
                    except ValueError as e:
                        print(f"Error parsing experience: {exp} - {str(e)}")

            # Check for shared experiences
            shared_experiences = check_shared_experience(new_employee_data, pd.DataFrame(employee_dicts))

            if shared_experiences:
                new_employee_title = new_employee_data['Parsed Experience'][0]['Title']  # Extract first title
                # Pass datetime to the template
                return render_template('shared_experience.html', 
                                       shared_experiences=shared_experiences, 
                                       new_employee_title=new_employee_title,
                                       datetime=datetime)  # Pass datetime here
            else:
                flash('No shared experience found.', 'info')
                return redirect(url_for('main.dashboard'))

        else:
            flash('Failed to fetch data for the new employee.', 'danger')
            return redirect(url_for('main.dashboard'))

    return render_template('check_reference.html')

@main.route("/add_multiple_employees", methods=['POST'])
@login_required
def add_multiple_employees():
    linkedin_urls = request.form.getlist('linkedin_urls')
    linkedin_urls = [url.strip() for url in linkedin_urls if url.strip()]  # Clean and filter out empty lines

    if len(linkedin_urls) > 25:
        flash('You can only submit up to 25 LinkedIn URLs at a time.', 'danger')
        return redirect(url_for('main.dashboard'))

    employee_profiles = fetch_linkedin_profiles(linkedin_urls)

    for profile in employee_profiles:
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
                    caption = sub_exp.get('caption', 'N/A').split(' · ')
                    start_date = caption[0] if len(caption) > 0 else 'N/A'
                    duration = caption[1] if len(caption) > 1 else 'N/A'
                    experience_details.append(f"{title} at {company} ({start_date} - {duration})")
            else:
                title = experience.get('title', 'N/A')
                company = experience.get('subtitle', 'N/A')
                caption = experience.get('caption', 'N/A').split(' · ')
                start_date = caption[0] if len(caption) > 0 else 'N/A'
                duration = caption[1] if len(caption) > 1 else 'N/A'

                # Ensure dates aren't duplicated
                experience_entry = f"{title} at {company} ({start_date}"
                if duration and duration != start_date:  # Only add duration if it's not the same as start_date
                    experience_entry += f" - {duration})"
                else:
                    experience_entry += ")"

                experience_details.append(experience_entry)

        # Join experience details into a string
        experience_str = "; ".join(experience_details)

        # Add LinkedIn URL as a hyperlink
        experience_str += f'<br>LinkedIn URL: <a href="{linkedin_url}" target="_blank">{linkedin_url}</a>'

        # Create and add the employee to the database
        employee = Employee(name=full_name, linkedin_url=linkedin_url, experience=experience_str, owner=current_user)
        db.session.add(employee)

    db.session.commit()
    flash(f'{len(employee_profiles)} employees added successfully!', 'success')
    
    return redirect(url_for('main.dashboard'))

@main.route("/delete_employee/<int:employee_id>", methods=['POST'])
@login_required
def delete_employee(employee_id):
    employee = Employee.query.get_or_404(employee_id)
    if employee.owner != current_user:
        flash('You do not have permission to delete this employee.', 'danger')
        return redirect(url_for('main.dashboard'))
    
    db.session.delete(employee)
    db.session.commit()
    flash('Employee deleted successfully!', 'success')
    return redirect(url_for('main.dashboard'))

@main.route("/logout")
@login_required
def logout():
    logout_user()
    return redirect(url_for('main.login'))