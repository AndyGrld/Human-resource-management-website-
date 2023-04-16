# Human Management System

A website to keep track of employees and job openings.
The first account created becomes the admin/superuser.

## Getting started
1. Enter your gmail api key on line 1 of password.txt
2. Enter your email address on line 2 of password.txt(emails from site will be sent to this account)
3. pip install -r requirements.txt
4. set FLASK_APP = main.py
5. flask run

## Admin (Human Resource Manager)
1. Keeps track of employees progress by assessing their performance and skills.
2. Can add employees to the company, edit employee details and also remove employee details from the database.
3. Add and edit projects, jobs, user and clients in the database.
4. Assign projects and jobs to employees.
5. Can make an employee a manager to other employees.

## Clients
1. Clients request for a project to be made, this project is then added by the admin.
2. Clients can make requests via the contact us page, this sends an email the company.

## Employees
1. The employees are those that work for said company.
2. Employees can view their dashboard and those of other employees.
3. An employee can be a manager to other employees.
4. Projects are assinged to employee manually by the admin.

## Users
1. Those not working in the company but just visit the website.
2. They can subscribe to the site and gain notifications about new job opportunities in the company.
3. Users can view available jobs and apply for a job
4. Users include their details during application which is then reviewed by the admin.

## Projects
1. Projects are created when a client makes a request for one.
2. Progress of projects is checked by storing the date the project commenced and the date it was completed.

## Jobs
1. Jobs are the assigned the employee and are used to determine the kind of projects the can work on.
2. Available jobs are displayed to non-employee for application.
