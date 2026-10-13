# Business Ledger App

A simple business ledger application split into a Django REST API backend and a React Native/Expo mobile client.

The repository is organized as a monorepo:

- `backend/` contains the Django project and API
- `mobile/` contains the Expo-based mobile app

## Project structure

```text
BusinessLedgerApp/
├── backend/
│   ├── accounts/           # Custom user/auth logic
│   ├── config/             # Django settings and URL configuration
│   ├── ledger/             # Ledger-related models, serializers, views, and logic
│   ├── .gitignore
│   ├── manage.py
│   └── requirements.txt
├── mobile/
│   ├── App.tsx             # App entry point
│   ├── app.json            # Expo app metadata
│   ├── package.json        # Mobile app dependencies and scripts
│   ├── index.ts            # App bootstrap
│   ├── tsconfig.json
│   ├── LICENSE
│   └── assets/
├── README.md
└── .gitignore
```

## Tech stack

### Backend
- Python 3
- Django 6.1.2
- Django REST Framework 3.18.3
- PostgreSQL support via `psycopg` / `psycopg2-binary`
- JWT authentication via `djangorestframework_simplejwt`
- Redis + Celery support for async/background work
- `python-decouple` for environment configuration

### Mobile app
- React Native 0.86.3
- Expo 57
- TypeScript
- React Navigation
- Expo Secure Store and local authentication support

## Features

- User authentication and account management
- Ledger/business transaction management
- REST API built with Django and DRF
- Mobile client for interacting with the backend
- JWT-based secure access

## Prerequisites

Before starting, make sure you have the following installed:

- Python 3.9+
- PostgreSQL (recommended for local development)
- Redis (if you want to run background workers)
- Node.js 18+
- npm or yarn

## Backend setup

1. Open a terminal and move into the backend folder:

```bash
cd backend
```

2. Create and activate a virtual environment:

```bash
python -m venv venv

# macOS/Linux
source venv/bin/activate

# Windows
venv\Scripts\activate
```

3. Install Python dependencies:

```bash
pip install -r requirements.txt
```

4. Create a `.env` file in `backend/` with the database and app settings:

```env
DEBUG=True
SECRET_KEY=your-secret-key
DB_NAME=businessledger
DB_USER=postgres
DB_PASSWORD=your-db-password
DB_HOST=localhost
DB_PORT=5432
```

5. Create the PostgreSQL database if needed:

```bash
psql -U postgres -c "CREATE DATABASE businessledger;"
```

6. Run database migrations:

```bash
python manage.py migrate
```

7. Start the Django development server:

```bash
python manage.py runserver
```

The API will be available at:

- `http://localhost:8000`

Optional: create a superuser for admin access:

```bash
python manage.py createsuperuser
```

## Mobile app setup

1. Move into the mobile folder:

```bash
cd mobile
```

2. Install dependencies:

```bash
npm install
```

3. Start the Expo app:

```bash
npm start
```

You can then launch the app in:

- an Android emulator
- an iOS simulator (macOS only)
- Expo Go on a physical device

Common scripts:

```bash
npm run android
npm run ios
npm run web
```

## Running the project together

- Start the backend API first.
- Then start the mobile app and ensure it points to the correct backend URL.
- If needed, update the API base URL in the mobile app configuration or environment-specific code.

## Development notes

- The backend uses Django's default project layout with `config/` as the settings package.
- The mobile app is a standalone Expo project under `mobile/`.
- The project is structured as a backend + mobile app monorepo instead of a single app.

## License

This project includes a license in the `mobile/` directory. Please refer to the repository files for licensing details.

## Contributing

1. Create a feature branch
2. Make your changes
3. Commit and push your branch
4. Open a pull request for review

## Support

If you run into setup issues, confirm that:

- PostgreSQL is running
- your `.env` values match local database credentials
- the backend server is started before the mobile app
- the mobile app is using the correct API host and port
