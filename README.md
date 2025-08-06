# Next.js + Django Fullstack Template (Backend)

This is the **Django + Django REST Framework** backend template for full-stack projects.  
It is designed to be used with a [Next.js + TypeScript frontend template](https://github.com/kaseyendsley/nextjs-django-template-frontend).

---

## Features
- Python dependency management with **Poetry**
- Django 5 + Django REST Framework pre-installed
- Basic `/health` endpoint for quick API checks
- Ready to extend with additional apps and APIs

---

## Requirements
- Python 3.11+ (recommended)
- [Poetry](https://python-poetry.org/docs/#installation)

---

## Getting Started

1. **Clone the Repo**
   ```
   git clone <this-repo-url>
   cd nextjs-django-template-backend
   ```

2. **Install Dependencies**
   ```
   poetry install
   ```

3. **Activate Virtual Environment**
   ```
   poetry env activate
   source $(poetry env info --path)/bin/activate
   ```

4. **Apply Migrations**
   ```
   python manage.py migrate
   ```

5. **Run Development Server**
   ```
   python manage.py runserver
   ```
   Visit [http://127.0.0.1:8000/health/](http://127.0.0.1:8000/health/) to verify everything is working.

---

## Project Structure
```
backend/        # Project settings
core/           # Core app with health endpoint
manage.py       # Django project manager
pyproject.toml  # Poetry dependencies
```

---

## Next Steps
- Add more apps for project-specific features
- Connect to PostgreSQL (for production)
- Add authentication or other common middleware

---

## License
This template is free to use and modify for any personal or professional projects.
