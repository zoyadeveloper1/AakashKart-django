# 🛒 GreatKart – Django E-Commerce Website

GreatKart is a Django-based e-commerce web application developed using Python and Django. The project provides a foundation for building an online shopping platform with a structured Django backend and database integration.



![alt text](image-2.png)


![alt text](image.png)

## 📌 Project Overview

GreatKart is designed as an online shopping application where users can browse products and interact with the shopping platform.

The project is built with **Python and Django** and follows Django's standard project structure.

## 🚀 Features

* User-friendly e-commerce interface
* Product browsing
* Product management
* User authentication
* Shopping cart functionality
* Order management
* Database integration
* Admin management through Django Admin
* Responsive web interface
* Static and media file support
* Production deployment support with Gunicorn and WhiteNoise

> Note: The exact features available depend on the current implementation of the project.
 🛠️ Technologies Used

### Backend

* Python
* Django 5.2.6

### Database

* SQLite / relational database

### Frontend

* HTML5
* CSS3
* JavaScript
* Django Templates

### Other Technologies

* Cloudinary
* Pillow
* Django Widget Tweaks
* Django Extensions
* ReportLab
* xhtml2pdf
* Gunicorn
* WhiteNoise
* python-dotenv

## 📂 Project Structure

```text
GreatKart/
│
├── manage.py
├── requirements.txt
├── README.md
├── .gitignore
│
├── greatkart/
│   ├── settings.py
│   ├── urls.py
│   ├── wsgi.py
│   └── ...
│
├── templates/
├── static/
├── media/
│
└── <Django applications>/
```

## ⚙️ Installation

### 1. Clone the Repository

```bash
git clone <YOUR-GITHUB-REPOSITORY-URL>
```

### 2. Navigate to the Project

```bash
cd GreatKart
```

### 3. Create a Virtual Environment

```bash
python -m venv venv
```

### 4. Activate the Virtual Environment

#### Windows

```bash
venv\Scripts\activate
```

#### macOS / Linux

```bash
source venv/bin/activate
```

### 5. Install Dependencies

```bash
pip install -r requirements.txt
```

The project includes a `requirements.txt` containing Django and the supporting packages used by the application.

## 🗄️ Database Setup

Run Django migrations:


python manage.py makemigrations
python manage.py migrate

## 👤 Create Admin User

Create a Django superuser:


python manage.py createsuperuser


Follow the terminal instructions to create the admin account.

## ▶️ Run the Development Server

Start the Django development server:

python manage.py runserver


Then open:


http://127.0.0.1:8000/


## 🔐 Environment Variables

For production or third-party services, sensitive configuration should be stored in environment variables rather than directly inside the source code.

Example:


SECRET_KEY=your-secret-key
DEBUG=False
CLOUDINARY_CLOUD_NAME=your-cloud-name
CLOUDINARY_API_KEY=your-api-key
CLOUDINARY_API_SECRET=your-api-secret


Do not commit `.env` files or secret credentials to GitHub.

## ☁️ Deployment

The project includes packages such as **Gunicorn** and **WhiteNoise**, which can be used for production deployment.
Before deployment:


python manage.py collectstatic
python manage.py migrate


A production deployment should also use:

* `DEBUG=False`
* Secure environment variables
* Proper `ALLOWED_HOSTS`
* Production database configuration
* Static/media file configuration

## 📦 Main Dependencies

The project currently includes:

* Django 5.2.6
* Cloudinary
* django-cloudinary-storage
* django-widget-tweaks
* Pillow
* Gunicorn
* WhiteNoise
* ReportLab
* xhtml2pdf
* python-dotenv
* Requests

The uploaded requirements file contains the complete pinned dependency set.

## 🔒 Security

For production use:

* Keep `SECRET_KEY` private
* Set `DEBUG=False`
* Configure `ALLOWED_HOSTS`
* Store API credentials in environment variables
* Never commit passwords, API keys, or `.env` files
* Use HTTPS in production

## 🔮 Future Enhancements

Possible future improvements include:

* Online payment gateway integration
* Advanced product filtering
* Wishlist functionality
* Product search
* Email notifications
* Order tracking
* Customer dashboard
* Improved API integration
* Cloud deployment
* Automated testing

## 👩‍💻 Author

**R. Durga Devi**

Python Full Stack Developer

### Technologies

`Python` · `Django` · `HTML` · `CSS` · `JavaScript` · `MySQL/SQLite` · `Git` · `GitHub`

---

