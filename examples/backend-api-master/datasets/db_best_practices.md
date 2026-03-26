## Database Connection Management

### Connection Pooling

Always use connection pooling for database connections to improve performance and resource utilization.

```python
from sqlalchemy import create_engine
from sqlalchemy.pool import QueuePool

engine = create_engine(
    "postgresql://user:password@localhost/dbname",
    poolclass=QueuePool,
    pool_size=5,
    max_overflow=10,
    pool_timeout=30,
    pool_recycle=1800
)
```

### Async Database Operations

For async applications, use async database drivers and connection pools.

```python
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.orm import sessionmaker

async_engine = create_async_engine(
    "postgresql+asyncpg://user:password@localhost/dbname",
    pool_size=5,
    max_overflow=10
)

async_session = sessionmaker(
    async_engine,
    class_=AsyncSession,
    expire_on_commit=False
)
```

## Query Optimization

### Indexing Strategy

Create indexes for frequently queried columns:

```sql
-- Create index on foreign keys
CREATE INDEX idx_user_id ON orders(user_id);

-- Create composite index for common query patterns
CREATE INDEX idx_status_created ON orders(status, created_at);

-- Create partial index for filtered queries
CREATE INDEX idx_active_users ON users(email) WHERE status = 'active';
```

### Query Patterns

Use efficient query patterns to minimize database load:

```python
# Bad: N+1 query problem
users = session.query(User).all()
for user in users:
    orders = session.query(Order).filter_by(user_id=user.id).all()

# Good: Use joined loading
from sqlalchemy.orm import joinedload

users = session.query(User).options(joinedload(User.orders)).all()
```

## Data Validation

### Input Validation

Always validate input data before database operations:

```python
from pydantic import BaseModel, validator

class UserCreate(BaseModel):
    email: str
    password: str

    @validator('email')
    def validate_email(cls, v):
        if '@' not in v:
            raise ValueError('Invalid email format')
        return v

    @validator('password')
    def validate_password(cls, v):
        if len(v) < 8:
            raise ValueError('Password must be at least 8 characters')
        return v
```

### SQL Injection Prevention

Use parameterized queries to prevent SQL injection:

```python
# Bad: String concatenation (vulnerable to SQL injection)
query = f"SELECT * FROM users WHERE email = '{email}'"

# Good: Parameterized query
query = "SELECT * FROM users WHERE email = :email"
result = session.execute(query, {"email": email})
```

## Transaction Management

### Atomic Operations

Use transactions for operations that must succeed or fail together:

```python
from sqlalchemy.orm import Session

def transfer_funds(session: Session, from_id: int, to_id: int, amount: float):
    """Transfer funds between accounts atomically."""
    try:
        from_account = session.query(Account).with_for_update().get(from_id)
        to_account = session.query(Account).with_for_update().get(to_id)

        if from_account.balance < amount:
            raise ValueError("Insufficient funds")

        from_account.balance -= amount
        to_account.balance += amount

        session.commit()
    except Exception:
        session.rollback()
        raise
```

## Error Handling

### Database Error Handling

Handle database errors gracefully:

```python
from sqlalchemy.exc import IntegrityError, OperationalError

def create_user(session: Session, user_data: dict):
    """Create a user with proper error handling."""
    try:
        user = User(**user_data)
        session.add(user)
        session.commit()
        return user
    except IntegrityError as e:
        session.rollback()
        if "unique constraint" in str(e):
            raise ValueError("User with this email already exists")
        raise
    except OperationalError as e:
        session.rollback()
        raise RuntimeError(f"Database error: {e}")
```

## Migration Best Practices

### Schema Changes

Use migration tools for schema changes:

```bash
# Generate migration
alembic revision --autogenerate -m "Add user table"

# Apply migration
alembic upgrade head

# Rollback migration
alembic downgrade -1
```

### Data Migrations

For data migrations, use separate migration scripts:

```python
# migrations/versions/002_migrate_user_data.py
def upgrade():
    # Migrate data from old schema to new schema
    op.execute("""
        UPDATE users 
        SET full_name = CONCAT(first_name, ' ', last_name)
        WHERE full_name IS NULL
    """)

def downgrade():
    # Reverse the migration if needed
    pass
```
