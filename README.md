# Food Bridge

Food Bridge is a full-stack web application built with Django that connects food donors (restaurants, grocery stores, event organizers, individuals) with verified community recipients (shelters, NGOs, community kitchens) to reduce food waste and fight hunger.

## Features

- Real-time logistical matching engine pairing donation listings with nearby/eligible verified recipients
- Donor and recipient verification/approval pipeline (admin-reviewed)
- RESTful API layer feeding live admin dashboards with resource availability data
- Optimized PostgreSQL queries/indices for fast retrieval during high-demand allocation periods
- Notification system for match requests, approvals, and pickup/delivery status
- Role-based dashboards (Donor, Recipient, Admin)

## Tech Stack

- **Backend:** Python, Django (Django REST Framework for API endpoints)
- **Database:** PostgreSQL (with optimized indexing for high-traffic queries)
- **Frontend:** Django Templates + Bootstrap 5 (responsive, mobile-first)
- **Auth:** Django's built-in auth system extended with role-based access (Donor / Recipient / Admin)

## Getting Started

### Prerequisites

- Python 3.8+
- PostgreSQL
- pip

### Installation

1. Clone the repository:
   ```
   git clone https://github.com/your-username/food-bridge.git
   cd food-bridge
   ```

2. Create a virtual environment:
   ```
   python -m venv venv
   source venv/bin/activate   # On Windows: venv\Scripts\activate
   ```

3. Install dependencies:
   ```
   pip install -r requirements.txt
   ```

4. Set up the database:
   - Create a PostgreSQL database named `food_bridge`
   - Update the database credentials in `food_bridge/settings.py` if necessary
   - Run migrations:
     ```
     python manage.py migrate
     ```

5. Create a superuser:
   ```
   python manage.py createsuperuser
   ```

6. Run the development server:
   ```
   python manage.py runserver
   ```

7. Visit `http://127.0.0.1:8000` in your browser.

## Usage

- Donors can sign up and create donation listings with details about the food surplus.
- Recipients can sign up, get verified by admins, and browse available donations.
- Adkins can manage verification requests, monitor donations, and oversee the platform.

## Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## Acknowledgments

- Inspired by the need to reduce food waste and support community food security.
- Built with Django and Bootstrap.
```