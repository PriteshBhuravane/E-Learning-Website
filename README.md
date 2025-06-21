## Live Demo: https://e-learning-5uto.onrender.com/
# E-Learning Project

This is a Django-based E-Learning platform.  
Follow the steps below to set up and run the project on your local machine.

---

## 1. Clone the Repository

```bash
git clone <your-repo-url>
cd E-Learning_Project-master/Elearning
```

---

## 2. Create a Virtual Environment

```bash
python3 -m venv venv
source venv/bin/activate
```

---

## 3. Install Required Packages

```bash
pip install -r requirements.txt
```
> If `requirements.txt` is missing, install Django and other packages manually:
> ```bash
> pip install django crispy-bootstrap5 python-dotenv razorpay
> ```

---

## 4. Environment Variables

Create a `.env` file in the `Elearning/Elearning/` directory with the following content:

```
DJANGO_SECRET_KEY=your-django-secret-key
EMAIL_HOST_USER=your-email@example.com
EMAIL_HOST_PASSWORD=your-email-password
KEY_ID=your-razorpay-key-id
KEY_SECRET=your-razorpay-key-secret
```

**Never commit your `.env` file!**

---

## 5. Apply Migrations

```bash
python manage.py migrate
```

---

## 6. Create a Superuser (Admin)

```bash
python manage.py createsuperuser
```
Follow the prompts to set username, email, and password.

---

## 7. Run the Development Server

```bash
python manage.py runserver
```
Visit [http://127.0.0.1:8000/](http://127.0.0.1:8000/) in your browser.

---

## 8. Access the Admin Panel

Go to [http://127.0.0.1:8000/admin/](http://127.0.0.1:8000/admin/) and log in with your superuser credentials.

---

## 9. Notes

- To install new packages, use `pip install <package>` and update `requirements.txt` with `pip freeze > requirements.txt`.
- Static files are in the `static/` directory.
- Media uploads are in the `media/` directory.
- Sensitive settings are loaded from `.env` (see `settings.py` for details).

---

## 10. Troubleshooting

- If you get errors about missing packages, ensure your virtual environment is activated.
- For any database issues, try deleting `db.sqlite3` and rerunning migrations.

---

## 11. Useful Commands

- **Deactivate virtual environment:**  
  `deactivate`
- **Collect static files (for production):**  
  `python manage.py collectstatic`
- **Reset admin password:**  
  `python manage.py changepassword <username>`

---

## 12. Contributing

Feel free to fork the repo and submit pull requests!

---
