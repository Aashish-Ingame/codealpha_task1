# StoreHub

A production-grade e-commerce web application built with Django and MySQL.

## Tech Stack
- Backend: Django 4.x (Python)
- Database: MySQL 8 (SQLite for local development)
- Frontend: HTML5, CSS3, Vanilla JavaScript
- Auth: Django built-in authentication

## Features
- Product browsing with search, filter, and sort
- Shopping cart with live quantity updates
- Checkout and order processing
- User registration, login, and profile management
- Django Admin for product and order management

## Setup Instructions
1. Clone the project and navigate to the folder
2. Create a virtual environment: python -m venv venv
3. Activate it: venv\Scripts\activate (Windows) or source venv/bin/activate (Mac/Linux)
4. Install dependencies: pip install -r requirements.txt
5. Copy .env.example to .env and fill in your values
6. Run migrations: python manage.py migrate
7. Create superuser: python manage.py createsuperuser
8. Seed products: python manage.py seed_products
9. Start server: python manage.py runserver

## Project Structure
- accounts/ — user auth, registration, login, profile
- products/ — product listing, detail, search, filter
- cart/ — shopping cart management
- orders/ — checkout, order history, order detail
- templates/ — shared base, home, landing page
- static/ — CSS, JS, images
- media/ — user-uploaded product images
