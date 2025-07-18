# L7Nutri - AI Agent Instructions

## Project Overview
L7Nutri is a **nutrition tracking and AI-powered advisory Flask application** designed for multi-deployment environments. The project supports both SQLite (local) and PostgreSQL (Render) databases with Google Gemini AI integration for intelligent nutrition insights.

## Architecture Patterns

### Multi-Environment Configuration
- **Local Development**: SQLite database (`nutricao.db`)
- **Render Deployment**: PostgreSQL with environment-based configuration
- **Database Detection**: Uses `DATABASE_URL` environment variable for PostgreSQL, falls back to SQLite
- **AI Integration**: Google Gemini AI (optional) via `GEMINI_API_KEY` environment variable

### Core Models Structure
```python
# Key relationships in app.py:
Usuario -> RegistroAlimentar -> Alimento/Receita
Usuario -> AlergiaUsuario -> Alergia
Usuario -> PreferenciaUsuario -> Preferencia
Usuario -> PlanoSugestao -> Receita (multiple foreign keys)
```

### Deploy Structure
- **Root**: Main development files (`app.py`, `main.py`)
- **deploy_render/**: Render-specific simplified deployment files
- **deploy_hostinger/**: Hostinger-specific MySQL deployment
- **migrations/**: Flask-Migrate database versioning

## Development Workflows

### Database Management
```bash
# Database migrations (Flask-Migrate)
flask db init
flask db migrate -m "description"
flask db upgrade

# Production initialization
python init_producao.py
```

### Deployment Commands
```bash
# Render deployment (use deploy_render/ files)
web: gunicorn main:app  # Procfile command

# Local development
python app.py  # Full-featured version
python main.py  # Simplified version
```

### Environment Variables
```env
# Required for production
DATABASE_URL=postgresql://...
SECRET_KEY=your-secret-key
JWT_SECRET_KEY=your-jwt-key

# Optional AI features
GEMINI_API_KEY=your-gemini-key
```

## Project-Specific Conventions

### API Route Patterns
- Public APIs: `/api/diagnostico-publico` (no auth required)
- Authenticated APIs: `/api/usuarios/*` (JWT required)  
- Debug routes: `/api/debug/*` (development only)
- Nutrition AI: `/api/nutri/*` (Gemini AI integration)

### Database Model Naming
- Snake_case table names: `__tablename__ = 'table_name'`
- Relationship backrefs use singular/plural appropriately
- Foreign key patterns: `{table}_id` format

### File Organization
- `app.py`: Full-featured main application
- `main.py`: Simplified deployment version
- `templates/`: Jinja2 HTML templates
- `migrations/`: Database version control
- `deploy_*/`: Environment-specific configurations

## Critical Integration Points

### Google Gemini AI
```python
# Safe AI initialization pattern used throughout
if gemini_api_key and gemini_api_key != 'SUA_CHAVE_AQUI':
    genai.configure(api_key=gemini_api_key)
    modelo_ia = genai.GenerativeModel('gemini-1.5-flash')
else:
    modelo_ia = None
```

### Database Environment Detection
```python
# Multi-database support pattern
DATABASE_URL = os.getenv('DATABASE_URL')
if DATABASE_URL:
    if DATABASE_URL.startswith('postgres://'):
        DATABASE_URL = DATABASE_URL.replace('postgres://', 'postgresql://', 1)
    app.config['SQLALCHEMY_DATABASE_URI'] = DATABASE_URL
else:
    app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///nutricao.db'
```

### Authentication Flow
- JWT tokens with 365-day expiration for extended sessions
- Bcrypt password hashing throughout
- Session-based authentication for web routes

## Key Files to Reference
- `app.py`: Complete application with all models and routes
- `deploy_render/main.py`: Simplified deployment version
- `requirements.txt`: Full dependency list vs `deploy_render/requirements.txt` (minimal)
- `migrations/`: Database schema evolution
- `templates/`: Frontend interface patterns

## Common Debugging Patterns
- Use `debug_main.py` for deployment troubleshooting
- Database connection testing via `with app.app_context():`
- Logging patterns: Import logging, configure handlers, use throughout
- Error handling: JSON responses with appropriate HTTP status codes
