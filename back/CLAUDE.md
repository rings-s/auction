# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

This is the **backend** of a real estate auction platform built with Django REST Framework. The application provides real-time bidding capabilities, comprehensive property management, user authentication, and analytics.

## Technology Stack

- **Framework**: Django 5.2 with Django REST Framework
- **Database**: SQLite (default) / PostgreSQL (optional via USE_POSTGRESQL=true)
- **Real-time**: Django Channels with WebSockets
- **Caching**: Redis or Database cache
- **Authentication**: JWT with SimpleJWT
- **Background Tasks**: Celery (configured but optional)
- **Analytics**: Plotly, Pandas, NumPy, Matplotlib
- **File Storage**: WhiteNoise for static files

## Development Commands

```bash
# Start development server
python manage.py runserver                    # Runs on http://localhost:8000

# Database operations
python manage.py makemigrations               # Create migrations
python manage.py migrate                      # Apply migrations
python manage.py createcachetable             # Create cache table (for DB cache)

# User management
python manage.py createsuperuser              # Create admin user
python manage.py shell                        # Django shell

# Static files
python manage.py collectstatic               # Collect static files

# Testing
python manage.py test                         # Run tests
python manage.py test accounts               # Test specific app

# Utilities
python manage.py check                        # Check for issues
python manage.py showmigrations               # Show migration status
```

## Project Architecture

### Django Apps Structure
```
accounts/                       # User management and authentication
├── models.py                   # CustomUser, UserProfile
├── views.py                    # Auth views (register, login, profile)
├── serializers.py              # User data serialization
├── urls.py                     # Auth endpoints
├── middleware.py               # Request logging, login tracking
└── permissions.py              # Custom permissions

base/                          # Core business logic
├── models.py                  # Auction, Property, Bid, Payment models
├── views.py                   # API views for all business objects
├── serializers.py             # API serialization
├── urls.py                    # Business logic endpoints
├── consumers.py               # WebSocket consumers for real-time
├── permissions.py             # Business logic permissions
├── filters.py                 # API filtering
└── tasks.py                   # Background tasks
```

### API Endpoints Structure
```
/api/accounts/
├── register/                   # User registration
├── login/                      # JWT authentication
├── profile/                    # User profile management
├── password/reset/             # Password reset flow
└── token/refresh/              # JWT token refresh

/api/
├── properties/                 # Property CRUD
├── auctions/                   # Auction management
├── bids/                       # Bidding system
├── messages/                   # Messaging system
├── dashboard/                  # Dashboard data
├── analytics/                  # Analytics data
├── bank-accounts/              # Payment account management
├── payments/                   # Payment processing
├── workers/                    # Maintenance worker management
├── rental-properties/          # Property management
├── tenants/                    # Tenant management
├── maintenance/                # Maintenance requests
└── expenses/                   # Expense tracking
```

### Model Relationships
```
CustomUser (accounts)
├── UserProfile (accounts)      # Extended user data
├── Property (base)             # User's properties
├── Auction (base)              # User's auctions
├── Bid (base)                  # User's bids
├── Message (base)              # User's messages
├── BankAccount (base)          # User's payment accounts
└── Payment (base)              # User's payments

Property (base)
├── Room (base)                 # Property rooms
├── Media (base)                # Property images/videos
├── Auction (base)              # Property auctions
└── RentalProperty (base)       # Rental property data

Auction (base)
├── Bid (base)                  # Auction bids
└── AuctionStatus updates       # Real-time status
```

## Real-time Features

### WebSocket Configuration
The application uses Django Channels for WebSocket connections:

```python
# Routing configuration
ASGI_APPLICATION = 'back.asgi.application'

# Channel layers (Redis for production, InMemory for development)
CHANNEL_LAYERS = {
    'default': {
        'BACKEND': 'channels_redis.core.RedisChannelLayer',  # or InMemoryChannelLayer
        'CONFIG': {"hosts": [REDIS_URL]},
    }
}
```

### WebSocket Consumers
Located in `base/consumers.py`:
- `AuctionConsumer`: Handles real-time auction updates, bidding, status changes
- Automatic user authentication via JWT tokens
- Broadcasting to auction-specific groups

## Database Configuration

### SQLite (Default)
```python
# Automatic configuration - no setup required
DATABASES = {'default': {'ENGINE': 'django.db.backends.sqlite3'}}
```

### PostgreSQL (Optional)
```bash
# Set environment variable
export USE_POSTGRESQL=true

# Or in .env file
USE_POSTGRESQL=true
DB_NAME=auction
DB_USER=postgres
DB_PASSWORD=your_password
```

### Cache Configuration
```bash
# Use Redis cache (requires Redis running)
USE_REDIS_CACHE=true

# Use database cache (SQLite compatible)
USE_REDIS_CACHE=false
python manage.py createcachetable  # One-time setup
```

## Authentication System

### Custom User Model
```python
# accounts/models.py
class CustomUser(AbstractUser):
    email = EmailField(unique=True)     # Email as username
    role = CharField(max_length=50)     # USER, PREMIUM_USER, ADMIN, etc.
    is_email_verified = BooleanField(default=False)
    
class UserProfile(models.Model):
    user = OneToOneField(CustomUser)
    # Extended profile fields
```

### JWT Configuration
```python
SIMPLE_JWT = {
    'ACCESS_TOKEN_LIFETIME': timedelta(minutes=60),
    'REFRESH_TOKEN_LIFETIME': timedelta(days=7),
    'ROTATE_REFRESH_TOKENS': True,
}
```

## Development Workflow

### Starting Development
1. Install dependencies: `pip install -r requirements.txt`
2. Apply migrations: `python manage.py migrate`
3. Create superuser: `python manage.py createsuperuser`
4. Start server: `python manage.py runserver`
5. Access admin: http://localhost:8000/admin/

### Environment Configuration
Key environment variables (see `settings.py` for full list):
```bash
DEBUG=true                      # Development mode
SECRET_KEY=your-secret-key      # Django secret key
USE_POSTGRESQL=true             # Enable PostgreSQL
USE_REDIS_CACHE=true            # Enable Redis caching
EMAIL_HOST_USER=your@email.com  # SMTP configuration
FRONTEND_URL=http://localhost:5173  # Frontend URL for CORS
```

### API Development Patterns
- Use ViewSets for CRUD operations
- Implement custom permissions in `permissions.py`
- Add filtering in `filters.py` for list views
- Use serializers for data validation and transformation
- Add proper error handling and logging

### Adding New Models
1. Define model in appropriate app's `models.py`
2. Create migrations: `python manage.py makemigrations`
3. Apply migrations: `python manage.py migrate`
4. Create serializer in `serializers.py`
5. Create viewset in `views.py`
6. Add URL patterns in `urls.py`

## Security Configuration

### Production Settings
```python
# Automatically enabled when DEBUG=False
SECURE_SSL_REDIRECT = True
SESSION_COOKIE_SECURE = True
CSRF_COOKIE_SECURE = True
SECURE_HSTS_SECONDS = 31536000
```

### CORS Configuration
```python
# Development
CORS_ALLOWED_ORIGINS = [
    "http://localhost:5173",    # SvelteKit dev server
    "http://localhost:7500",    # Docker frontend
]

# Authentication required for API access
CORS_ALLOW_CREDENTIALS = True
```

## Docker Development

### Using Docker Compose
```bash
# From project root directory
docker-compose up                           # Start all services
docker-compose up backend                   # Start backend only
docker-compose logs backend                 # View backend logs
docker-compose exec backend python manage.py shell  # Access Django shell
```

### Docker Configuration
- Backend runs on port 8451 (mapped from container 8000)
- PostgreSQL on port 5433
- Redis on port 6380
- Environment variables configured via docker-compose.yml

## Property Management Features

### Core Property Management Models
```python
# Property rental management
RentalProperty, Tenant, Lease
MaintenanceRequest, MaintenanceCategory
Expense, ExpenseCategory
Worker, WorkerCategory
PropertyManagementCompany
```

### Analytics and Reporting
- Property performance analytics
- Maintenance cost tracking
- Rental income reporting
- Worker performance metrics
- Expense categorization and analysis

## Background Tasks

### Celery Configuration (Optional)
```python
# Configured in settings.py but not required for basic functionality
# Use for: email sending, report generation, maintenance scheduling
```

## Logging Configuration

### Log Files
```
logs/
├── django.log          # General application logs
└── error.log           # Error-specific logs
```

### Custom Middleware
- `RequestLogMiddleware`: Logs all API requests with timing
- `LoginTrackingMiddleware`: Tracks user login attempts and security
- `SuperuserOnlyAdminMiddleware`: Restricts admin access

## API Documentation

### REST Framework Features
- Browsable API at `/api/` endpoints
- Automatic API documentation
- Filtering, search, and ordering on list views
- Pagination (10 items per page)
- Rate limiting (100/hour anonymous, 1000/hour authenticated)

### WebSocket API
```javascript
// Frontend connection
const ws = new WebSocket('ws://localhost:8000/ws/auction/{auction_id}/');

// Message types
{
    "type": "place_bid",
    "auction_id": 123,
    "bid_amount": 1000
}
```

## Testing Strategy

### Running Tests
```bash
python manage.py test                       # All tests
python manage.py test accounts              # App-specific tests
python manage.py test base.tests.test_auctions  # Specific test file
```

### Test Structure
- Unit tests for models, serializers, views
- Integration tests for API endpoints
- WebSocket consumer tests for real-time features

## Architecture Notes

### Real-time Auction System
- WebSocket connections maintain bidding state
- Optimistic locking prevents bid conflicts
- Automatic auction status updates (active, ended, cancelled)
- Real-time notifications for bid updates

### Multi-language Support
- Django internationalization ready
- Arabic slug support for URLs
- RTL layout considerations in frontend integration

### Performance Considerations
- Database query optimization with select_related/prefetch_related
- Redis caching for frequently accessed data
- Connection pooling for database access
- Static file serving optimized with WhiteNoise

### Extensibility
The architecture supports easy extension for:
- Additional property types
- Enhanced auction formats
- More payment methods
- Advanced analytics and reporting
- Third-party integrations (payment gateways, mapping services)

## Development Principles & Best Practices

### SOLID Principles Implementation

**Single Responsibility Principle**:
- Each model represents one business concept
- ViewSets handle single resource operations
- Serializers focus on data transformation only
- Custom permissions handle specific authorization logic

**Open/Closed Principle**:
```python
# Extend functionality without modifying existing code
class PropertyViewSet(BasePropertyViewSet):
    def get_queryset(self):
        return super().get_queryset().filter(is_active=True)
```

**Liskov Substitution Principle**:
- Custom user model extends AbstractUser properly
- Serializer inheritance maintains interface contracts
- ViewSet inheritance preserves expected behavior

**Interface Segregation Principle**:
- Separate serializers for different use cases (list, detail, create)
- Focused permission classes for specific operations
- Modular API endpoints with clear responsibilities

**Dependency Inversion Principle**:
- Use Django's dependency injection for settings and services
- Abstract database operations through Django ORM
- Configuration-driven feature toggles

### Code Quality Standards

**Model Design Principles**:
```python
class Auction(models.Model):
    # Clear, descriptive field names
    title = models.CharField(max_length=200, help_text="Auction title")
    
    # Proper relationships with related_name
    property = models.ForeignKey('Property', on_delete=models.CASCADE, 
                                related_name='auctions')
    
    # Database constraints for data integrity
    starting_price = models.DecimalField(max_digits=12, decimal_places=2,
                                       validators=[MinValueValidator(0)])
    
    # Audit fields for tracking
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['status', 'end_time']),
        ]
```

**API Design Patterns**:
- RESTful URL patterns with consistent naming
- Proper HTTP status codes for all responses
- Comprehensive error handling with meaningful messages
- Pagination for list endpoints (10 items per page)
- Filtering and search capabilities where appropriate

**Security Implementation**:
```python
# Permission-based access control
class IsOwnerOrReadOnly(permissions.BasePermission):
    def has_object_permission(self, request, view, obj):
        return (request.method in permissions.SAFE_METHODS or 
                obj.owner == request.user)

# Input validation and sanitization
class PropertySerializer(serializers.ModelSerializer):
    def validate_price(self, value):
        if value < 0:
            raise serializers.ValidationError("Price cannot be negative")
        return value
```

### Database Design Principles

**Normalization Standards**:
- 3NF (Third Normal Form) for all business entities
- Proper foreign key relationships with cascade rules
- Avoid data duplication through normalized design
- Use database constraints for data integrity

**Query Optimization**:
```python
# Efficient querysets with select_related/prefetch_related
def get_queryset(self):
    return Auction.objects.select_related('property', 'owner')\
                         .prefetch_related('bids__bidder')\
                         .filter(is_active=True)

# Database indexes for performance
class Meta:
    indexes = [
        models.Index(fields=['status', 'end_time']),
        models.Index(fields=['property', 'created_at']),
    ]
```

**Data Migration Strategy**:
- Version-controlled database schema changes
- Backwards-compatible migrations when possible
- Data migration scripts for complex transformations
- Testing migrations on production-like datasets

### Error Handling & Logging

**Exception Handling Patterns**:
```python
# Custom exception classes
class AuctionError(Exception):
    pass

class BiddingClosedError(AuctionError):
    pass

# Proper error handling in views
def place_bid(self, request, *args, **kwargs):
    try:
        # Bid logic here
        pass
    except BiddingClosedError:
        return Response(
            {'error': 'Bidding has closed for this auction'},
            status=status.HTTP_400_BAD_REQUEST
        )
```

**Logging Strategy**:
- Structured logging with consistent formats
- Separate log levels for different environments
- Security event logging for audit trails
- Performance logging for optimization insights

### Testing Principles

**Test Coverage Requirements**:
- Unit tests for all models, serializers, and utility functions
- Integration tests for API endpoints
- WebSocket consumer tests for real-time functionality
- Minimum 80% code coverage

**Test Organization**:
```python
# Test structure
tests/
├── test_models.py      # Model unit tests
├── test_views.py       # API endpoint tests
├── test_serializers.py # Serializer validation tests
├── test_permissions.py # Permission logic tests
└── test_consumers.py   # WebSocket tests
```

**Test Data Management**:
- Use fixtures for consistent test data
- Factory pattern for complex object creation
- Isolated test databases for each test run
- Clean teardown after each test

### Performance & Scalability

**Caching Strategy**:
```python
# View-level caching for expensive operations
@cache_page(60 * 15)  # 15 minutes
def analytics_data(request):
    # Expensive analytics computation
    pass

# Model-level caching for frequently accessed data
@cached_property
def total_bids(self):
    return self.bids.count()
```

**Database Optimization**:
- Connection pooling for high-traffic endpoints
- Read replicas for analytics queries
- Periodic VACUUM and ANALYZE for PostgreSQL
- Monitor slow queries and optimize indexes

**Background Task Management**:
```python
# Celery tasks for time-consuming operations
@shared_task
def send_auction_reminder_emails(auction_id):
    # Email sending logic
    pass

@shared_task
def generate_analytics_report(user_id, date_range):
    # Report generation logic
    pass
```

### Security Best Practices

**Authentication & Authorization**:
- JWT token-based authentication with refresh tokens
- Role-based access control (USER, PREMIUM_USER, ADMIN)
- API rate limiting (100/hour anonymous, 1000/hour authenticated)
- CORS configuration for frontend security

**Data Protection**:
```python
# Sensitive data handling
class UserProfile(models.Model):
    # Never store passwords in plain text
    # Use Django's built-in password hashing
    
    # Encrypt sensitive fields if needed
    bank_account = EncryptedCharField(max_length=50, null=True, blank=True)
    
    # Audit trail for sensitive operations
    last_payment_at = models.DateTimeField(null=True, blank=True)
```

**Input Validation**:
- Server-side validation for all user inputs
- SQL injection prevention through ORM usage
- XSS protection with proper output encoding
- File upload validation and virus scanning

### Deployment & DevOps Principles

**Environment Configuration**:
- 12-factor app methodology
- Environment-specific settings via environment variables
- Secrets management for production credentials
- Health check endpoints for monitoring

**Monitoring & Observability**:
```python
# Custom middleware for request tracking
class RequestLogMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        start_time = time.time()
        response = self.get_response(request)
        
        logger.info(f"Request {request.method} {request.path} "
                   f"took {time.time() - start_time:.2f}s")
        return response
```

**Production Readiness**:
- Docker containerization for consistent deployments
- Database migration automation
- Static file serving with CDN integration
- Load balancer configuration for high availability

## Project Management Guidelines

### Development Workflow Standards

**Feature Development Process**:
1. **Requirements Analysis**: Clear specification of business logic and API contracts
2. **Database Design**: Schema design with proper relationships and constraints
3. **API Design**: RESTful endpoint design with proper status codes
4. **Implementation**: Follow Django best practices and coding standards
5. **Testing**: Comprehensive test coverage including edge cases
6. **Documentation**: API documentation and code comments
7. **Code Review**: Peer review focusing on security, performance, and maintainability

**Code Review Checklist**:
- [ ] Database queries optimized with select_related/prefetch_related
- [ ] Proper error handling and meaningful error messages
- [ ] Security considerations (authentication, authorization, input validation)
- [ ] Test coverage for new functionality
- [ ] Documentation updated for API changes
- [ ] Migration files reviewed for production safety
- [ ] Performance impact assessed for high-traffic endpoints

**Quality Assurance Process**:
```bash
# Pre-commit validation
python manage.py check                    # Django system checks
python manage.py test                     # Run test suite
python manage.py makemigrations --dry-run # Check for model changes
flake8 .                                 # Code style checking
```

### API Development Standards

**RESTful Design Principles**:
- Use appropriate HTTP methods (GET, POST, PUT, PATCH, DELETE)
- Consistent URL patterns following REST conventions
- Proper use of HTTP status codes
- Stateless request design
- Resource-oriented URL structure

**Response Format Standards**:
```python
# Success response format
{
    "data": { ... },
    "meta": {
        "count": 25,
        "next": "http://api.example.com/auctions/?page=3",
        "previous": "http://api.example.com/auctions/?page=1"
    }
}

# Error response format
{
    "error": {
        "code": "VALIDATION_ERROR",
        "message": "Invalid auction data provided",
        "details": {
            "starting_price": ["This field cannot be negative"]
        }
    }
}
```

### Performance Monitoring

**Key Performance Indicators**:
- API response time: < 200ms for most endpoints
- Database query time: < 50ms for simple queries
- WebSocket connection establishment: < 1s
- Memory usage: < 512MB per worker process

**Performance Testing**:
- Load testing for high-traffic endpoints
- Database performance testing with realistic data volumes
- WebSocket stress testing for concurrent connections
- Memory profiling for memory leak detection

### Security Guidelines

**Security Checklist**:
- [ ] All API endpoints properly authenticated/authorized
- [ ] Input validation on all user-provided data
- [ ] SQL injection prevention through ORM usage
- [ ] XSS protection with proper output encoding
- [ ] CSRF protection enabled for state-changing operations
- [ ] Rate limiting configured for all endpoints
- [ ] Security headers configured (HSTS, CSP, etc.)
- [ ] Sensitive data encrypted at rest and in transit

**Vulnerability Management**:
- Regular dependency security audits
- Automated security scanning in CI/CD pipeline
- Security incident response procedures
- Regular penetration testing for critical systems

### Deployment & Operations

**Production Deployment Checklist**:
- [ ] Environment variables configured correctly
- [ ] Database migrations tested and applied
- [ ] Static files collected and served via CDN
- [ ] SSL certificates configured and valid
- [ ] Monitoring and alerting configured
- [ ] Backup procedures tested and documented
- [ ] Performance baselines established
- [ ] Security configurations validated

**Monitoring & Alerting**:
- Application performance monitoring (APM)
- Database performance monitoring
- Security event monitoring
- Business metrics tracking (auctions, bids, revenue)
- Infrastructure monitoring (CPU, memory, disk, network)