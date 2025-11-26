# WARP.md

This file provides guidance to WARP (warp.dev) when working with code in this repository.

## Project Overview

**Kinopolka** is a Django-based film club management application (Чайный киноклуб) for archiving watched films, managing watchlists, creating postcards/invitations, tracking a bar inventory, and generating statistics. The application uses Django REST Framework for the API, async views with ADRF, and integrates with the Kinopoisk API for movie metadata.

- **Production URLs**: https://kinopolka.com / https://kinopolka.рф
- **Language**: Russian (ru-ru)
- **Timezone**: Asia/Yekaterinburg
- **Database**: SQLite3
- **Package Manager**: `uv` (Python package manager)

## Common Development Commands

### Environment Setup
```bash
# Install dependencies and sync environment
uv sync

# Activate virtual environment (if needed manually)
source .venv/bin/activate
```

### Running the Application
```bash
# Start development server (uses uvicorn + ASGI)
sh start.sh

# Or run directly with uvicorn
uv run uvicorn filmoclub.asgi:application --host 0.0.0.0 --port 8000

# With auto-reload for development
uv run uvicorn filmoclub.asgi:application --host 0.0.0.0 --port 8000 --reload

# Run with Docker Compose
docker-compose up
```

### Database Management
```bash
# Create migrations
uv run manage.py makemigrations

# Apply migrations
uv run manage.py migrate

# Create superuser
uv run manage.py createsuperuser
```

### Static Files
```bash
# Collect static files (required before running)
uv run manage.py collectstatic --noinput
```

### Custom Management Commands
```bash
# Fix duplicate poster names in database
uv run manage.py fix_posters_names

# Download movie posters locally
uv run manage.py download_posters
```

### Testing
```bash
# Run all tests
uv run manage.py test

# Run tests for specific app
uv run manage.py test lists
uv run manage.py test bar
```

### Code Quality
```bash
# Run Ruff linter (check only)
uv run ruff check .

# Run Ruff with auto-fix
uv run ruff check --fix .

# Format code with Ruff
uv run ruff format .
```

### API Documentation
When the server is running:
- Swagger UI: http://localhost:8000/api/docs/
- ReDoc: http://localhost:8000/api/docs/redoc/
- Schema: http://localhost:8000/api/schema/

## Architecture Overview

### High-Level Structure

Kinopolka follows a **Handler Pattern** architecture where business logic is separated into handler classes in the `classes/` directory, keeping Django views thin. The application uses async views extensively with ADRF (Async Django REST Framework).

```
filmoclub/               # Main Django project
├── settings.py         # Environment-driven config (DEBUG, ALLOWED_HOSTS via env vars)
├── urls.py             # Root URL configuration
├── asgi.py             # ASGI application entry point
└── wsgi.py             # WSGI application entry point (not actively used)

classes/                # Business logic handlers (Handler Pattern)
├── movie.py            # MovieHandler, MoviesStructure
├── note.py             # NoteHandler
├── postcard.py         # PostcardHandler
├── user.py             # UserHandler
├── cocktail.py         # CocktailHandler
├── ingredient.py       # IngredientHandler
├── statistic.py        # Statistic
├── kp.py               # KP_Movie - Kinopoisk API client
├── invitation.py       # Invitation - email sending
├── tg.py               # Telegram - bot integration
├── tools.py            # Tools - utility functions
└── caching.py          # Caching - DiskCache wrapper

Django Apps:
lists/                  # Core movie management (Movie, Genre, Actor, Director, Note models)
postcard/               # Postcard/invitation management (Postcard model)
bar/                    # Bar inventory (Ingredient, Cocktail, CocktailIngredient models)
features/               # Frontend features (catalog, statistics, carousel, tarot, gym)
tools/                  # Admin tools (init project, import films, view users/notes)

mixins/                 # Shared mixins
└── global_data.py      # GlobalDataMixin - adds users & random images to context

utils/                  # Utility modules
├── exception_handler.py
├── response_handler.py
├── middleware.py
└── top_secret.py       # Called on startup

templates/              # Django templates
static/                 # Static assets
staticfiles/            # Collected static files (generated)
media/                  # User-uploaded media files
```

### Key Design Patterns

#### 1. Handler Classes (Service Layer)
All core business logic lives in `classes/` directory, not in views:
- **MovieHandler**: CRUD operations for movies, Kinopoisk API integration
- **NoteHandler**: User notes/ratings management
- **PostcardHandler**: Postcard generation and management
- **CocktailHandler**, **IngredientHandler**: Bar inventory logic
- **UserHandler**: User data management
- **Statistic**: Analytics and statistics generation

Views are thin and primarily orchestrate handler calls.

#### 2. Async-First Architecture
The application uses Django's ASGI with async views (ADRF):
- Most views inherit from `adrf.views.APIView` or use `@asapi_view` decorator
- Handler methods often have both sync and async versions (e.g., `a_download`)
- Uses `httpx` (async HTTP client) instead of `requests` where possible

#### 3. Caching Strategy
`Caching` class (in `classes/caching.py`) wraps `diskcache` for:
- API responses from Kinopoisk
- User data (via `GlobalDataMixin`)
- Cache directory: `app_cache/`
- Default timeout: configurable per use case (e.g., 2 min for KP API, 15 min for users)

#### 4. Global Context Mixin
`GlobalDataMixin` (in `mixins/global_data.py`) automatically injects:
- List of all users
- Random theme images based on query params
Used by all template-rendering views to ensure consistent context.

#### 5. Kinopoisk API Integration
`KP_Movie` class in `classes/kp.py`:
- Fetches movie metadata from https://api.kinopoisk.dev
- Requires `KP_API_TOKEN` environment variable
- Includes automatic caching and error handling
- Returns `None` on errors with `self.error` set

#### 6. Environment-Based Configuration
All sensitive/environment-specific config via environment variables in `start.sh`:
- `DEBUG`, `ALLOWED_HOSTS`, `SECRET_KEY`
- `ENVIRONMENT` (dev/prod) - controls CORS, logging, SSL redirect
- `KP_API_TOKEN`, `TELEGRAM_BOT_TOKEN`, `TELEGRAM_GROUP_ID`
- `EMAIL_HOST_USER`, `EMAIL_HOST_PASSWORD`
- `LOKI_URL` (for Grafana Loki logging in production)

### Data Models

#### Core Models (lists app)
- **Movie**: Main entity with Kinopoisk ID, metadata, ratings, watch status
  - ManyToMany: Genre, Actor, Director, Writer
  - `is_archive`: watched vs. to-watch distinction
  - `watch_date`: when the movie was watched
- **Note**: User ratings/reviews for movies (unique constraint on user+movie)
- **User**: Extended Django User with avatar URL
- **Genre/Actor/Director/Writer**: Related entities with Kinopoisk IDs

#### Postcard Models (postcard app)
- **Postcard**: Event invitations with meeting date, title, related movies, screenshot
  - `is_active`: toggleable for display purposes
  - Ordered by `-meeting_date`

#### Bar Models (bar app)
- **Ingredient**: Bar ingredients with availability status and images
- **Cocktail**: Recipes with instructions and images
- **CocktailIngredient**: Through model with amount and unit (ml/g/pcs)
- Cocktail availability computed based on ingredient availability

### URL Structure
- `/admin/` - Django admin
- `/movies/` - Movie CRUD, notes, filtering (lists app)
- `/` - Postcard views (postcard app - root URL)
- `/tools/` - Admin utilities (tools app)
- `/features/` - Catalog, statistics, carousel, tarot, gym (features app)
- `/bar/` - Bar inventory management (bar app)
- `/api/docs/` - Swagger UI
- `/api/docs/redoc/` - ReDoc
- `/api/schema/` - OpenAPI schema

### Logging
- Custom logger: `kinopolka` (use `logging.getLogger("kinopolka")`)
- In production (`ENVIRONMENT=prod`), logs go to both console and Grafana Loki
- LogFilter adds `function`, `line`, `file`, `message` tags to all log records
- Django logs set to WARNING level to reduce noise

### Static Files
- Uses WhiteNoise for serving static files
- `STATICFILES_STORAGE`: CompressedManifestStaticFilesStorage
- `WHITENOISE_USE_ASYNC`: True
- Run `collectstatic` before deployment

## Important Notes

### Environment Variables Required
Create `start.sh` with these variables (see example_start.sh):
- `ENVIRONMENT` (dev/prod)
- `DEBUG` (0/1)
- `ALLOWED_HOSTS` (semicolon-separated)
- `SECRET_KEY`
- `KP_API_TOKEN` (Kinopoisk API key)
- `TELEGRAM_BOT_TOKEN`, `TELEGRAM_GROUP_ID`
- `EMAIL_HOST_USER`, `EMAIL_HOST_PASSWORD`
- `LOKI_URL` (for logging)

### CSRF Protection
CSRF middleware is **disabled** in settings (`django.middleware.csrf.CsrfViewMiddleware` is commented out). Be aware of security implications.

### CORS
- **Development**: `CORS_ALLOW_ALL_ORIGINS = True`
- **Production**: Limited to `kinopolka.com` and `kinopolka.рф`

### Handler Usage Pattern
When adding new features:
1. Create a handler class in `classes/`
2. Export it in `classes/__init__.py`
3. Implement business logic in the handler
4. Keep views thin - just call handler methods and return responses
5. Add async versions of methods (prefix with `a_`) when possible

Example:
```python
# In classes/myhandler.py
class MyHandler:
    @staticmethod
    async def a_process_data():
        # async logic
        pass

# In views.py
from classes import MyHandler

@asapi_view(["GET"])
async def my_view(request):
    result = await MyHandler.a_process_data()
    return Response(result)
```

### Testing Approach
- Use Django's `TestCase`
- Tests are minimal currently (mostly placeholder files)
- Test files exist in each app's `tests.py`
- Run with `uv run manage.py test`

### Code Style (Ruff Configuration)
- Line length: 120 characters
- Target Python: 3.10
- Enabled rules: E, W, F, I, B, C, A, UP, YTT, RUF, DJ, ANN, PIE, SIM, C901, ASYNC
- Migrations and `__pycache__` excluded
- Django-specific rules enforced (e.g., `on_delete` required)
- Max complexity: 10
