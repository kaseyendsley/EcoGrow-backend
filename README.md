# EcoGrow 🌱 (Backend)

EcoGrow helps users build climate-conscious habits through sustainability quests. Users can create and undertake challenges across categories like food, transportation, and energy, share their progress with photos and reflections, and connect with users who share their values. Whether it’s reducing waste, trying eco-friendly swaps, or learning new green habits, EcoGrow makes sustainable living approachable and fun. 

The EcoGrow Backend is a Python/Django REST Framework API that powers user authentication, quest management, and habit tracking. It provides secure, scalable RESTful endpoints designed for seamless frontend integration and future growth.  

The frontend for EcoGrow, built with Next.js and TailwindCSS, can be found here: [EcoGrow Frontend Repository](https://github.com/kaseyendsley/EcoGrow-frontend)

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

## License
This template is free to use and modify for any personal or professional projects.
