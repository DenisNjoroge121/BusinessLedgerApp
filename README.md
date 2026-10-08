# Business Ledger App

A comprehensive business ledger application built with a Django REST backend and React Native frontend.

## Project Structure

```
BusinessLedgerApp/
├── backend/          # Django REST Framework backend
│   ├── config/       # Django configuration
│   ├── ledger/       # Ledger application
│   ├── manage.py     # Django management script
│   └── requirements.txt
└── frontend/         # React Native Expo app
    ├── App.tsx       # Main app component
    ├── package.json
    └── assets/       # App assets
```

## Technology Stack

### Backend
- **Python 3.x**
- **Django 6.1.2** - Web framework
- **Django REST Framework 3.18.3** - REST API
- **PostgreSQL** - Database (psycopg2-binary)
- **Celery 5.6.3** - Task queue
- **Redis 8.1.0** - Message broker & caching
- **JWT Authentication** - djangorestframework-simplejwt

### Frontend
- **React Native 0.86.3** - Mobile framework
- **Expo 57.0.27** - React Native development platform
- **TypeScript** - Type-safe JavaScript
- **React Navigation** - Navigation library
- **Axios** - HTTP client

## Prerequisites

Before you begin, ensure you have the following installed:

### For Backend Development
- Python 3.8 or higher
- PostgreSQL 12 or higher
- Redis Server
- pip (Python package manager)
- virtualenv (recommended)

### For Frontend Development
- Node.js 18.x or higher
- npm or yarn
- Expo CLI: `npm install -g expo-cli`

## Backend Installation

### 1. Clone the Repository
```bash
git clone https://github.com/DenisNjoroge121/BusinessLedgerApp.git
cd BusinessLedgerApp/backend
```

### 2. Create Virtual Environment
```bash
# On macOS/Linux
python3 -m venv venv
source venv/bin/activate

# On Windows
python -m venv venv
venv\Scripts\activate
```

### 3. Install Dependencies
```bash
pip install -r requirements.txt
```

### 4. Set Up Environment Variables
Create a `.env` file in the `backend/` directory with the following variables:
```env
DEBUG=True
SECRET_KEY=your-secret-key-here
ALLOWED_HOSTS=localhost,127.0.0.1

# Database
DB_ENGINE=django.db.backends.postgresql
DB_NAME=businessledger
DB_USER=postgres
DB_PASSWORD=your-db-password
DB_HOST=localhost
DB_PORT=5432

# Redis
REDIS_URL=redis://localhost:6379/0

# CORS
CORS_ALLOWED_ORIGINS=http://localhost:3000,http://localhost:19000
```

### 5. Configure PostgreSQL Database
```bash
# Create database (if not exists)
psql -U postgres -c "CREATE DATABASE businessledger;"

# Create user (if not exists)
psql -U postgres -c "CREATE USER ledger_user WITH PASSWORD 'your-password';"
```

### 6. Run Migrations
```bash
python manage.py migrate
```

### 7. Create Superuser (Admin)
```bash
python manage.py createsuperuser
```

### 8. Start Redis Server
```bash
# macOS (if installed via Homebrew)
redis-server

# Linux
redis-server

# Docker
docker run -d -p 6379:6379 redis:latest
```

### 9. Start Django Development Server
```bash
python manage.py runserver
```

The backend will be available at `http://localhost:8000`

### 10. Start Celery Worker (Optional, for background tasks)
```bash
celery -A config worker -l info
```

## Frontend Installation

### 1. Navigate to Frontend Directory
```bash
cd BusinessLedgerApp/frontend
```

### 2. Install Dependencies
```bash
npm install
# or
yarn install
```

### 3. Start the Expo Development Server
```bash
npm start
# or
yarn start
```

### 4. Run on Different Platforms

#### Run on Web
```bash
npm run web
```

#### Run on Android
```bash
npm run android
```
Requires Android SDK and Android emulator setup.

#### Run on iOS
```bash
npm run ios
```
Requires macOS and Xcode.

#### Using Expo Go App
1. Download Expo Go from your device's app store
2. Scan the QR code displayed in the terminal after running `npm start`
3. The app will load on your device

## Development Workflow

### Backend Development
1. Activate virtual environment: `source venv/bin/activate`
2. Make changes to backend code
3. Test with: `python manage.py test`
4. Run development server: `python manage.py runserver`

### Frontend Development
1. Ensure backend is running
2. Update API endpoints if needed in axios configuration
3. Run Expo: `npm start`
4. Test on emulator or device

## API Documentation

Once the backend is running, access:
- Admin Panel: `http://localhost:8000/admin/`
- API Root: `http://localhost:8000/api/`
- API Browsable Interface available at `/api/` endpoints

## Database Management

### Create Migrations
```bash
python manage.py makemigrations
```

### Apply Migrations
```bash
python manage.py migrate
```

### Reset Database
```bash
python manage.py flush
```

## Troubleshooting

### Backend Issues

**Port 8000 already in use:**
```bash
python manage.py runserver 8001
```

**PostgreSQL connection error:**
- Ensure PostgreSQL is running
- Check credentials in `.env` file
- Verify database name exists

**Redis connection error:**
- Ensure Redis server is running
- Check `REDIS_URL` in `.env` file

### Frontend Issues

**Expo port already in use:**
```bash
expo start -p 19001
```

**Module not found:**
```bash
rm -rf node_modules
npm install
```

**Clear cache:**
```bash
npm start --clear
```

## Additional Resources

- [Django Documentation](https://docs.djangoproject.com/)
- [Django REST Framework](https://www.django-rest-framework.org/)
- [React Native Documentation](https://reactnative.dev/)
- [Expo Documentation](https://docs.expo.dev/)
- [PostgreSQL Documentation](https://www.postgresql.org/docs/)

## Contributing

1. Create a feature branch: `git checkout -b feature/YourFeatureName`
2. Commit your changes: `git commit -m 'Add YourFeatureName'`
3. Push to the branch: `git push origin feature/YourFeatureName`
4. Submit a Pull Request

## License

This project is licensed under the MIT License - see the LICENSE file for details.

## Support

For issues or questions, please open an issue on GitHub or contact the project maintainer.
