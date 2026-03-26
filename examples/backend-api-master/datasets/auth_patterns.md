## JWT Authentication

JSON Web Tokens (JWT) are the recommended authentication method for API endpoints.

### Token Structure

JWT tokens consist of three parts separated by dots:

- Header: Contains the token type and signing algorithm
- Payload: Contains the claims (user data)
- Signature: Verifies the token hasn't been tampered with

### Implementation Pattern

```python
import jwt
from datetime import datetime, timedelta

def create_jwt_token(user_id: str, secret_key: str) -> str:
    """Create a JWT token for user authentication."""
    payload = {
        "user_id": user_id,
        "exp": datetime.utcnow() + timedelta(hours=24),
        "iat": datetime.utcnow()
    }
    return jwt.encode(payload, secret_key, algorithm="HS256")

def verify_jwt_token(token: str, secret_key: str) -> dict:
    """Verify and decode a JWT token."""
    try:
        payload = jwt.decode(token, secret_key, algorithms=["HS256"])
        return payload
    except jwt.ExpiredSignatureError:
        raise ValueError("Token has expired")
    except jwt.InvalidTokenError:
        raise ValueError("Invalid token")
```

### Usage in FastAPI

```python
from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials

security = HTTPBearer()

async def get_current_user(
    credentials: HTTPAuthorizationCredentials = Depends(security)
) -> dict:
    """Extract and verify the current user from JWT token."""
    token = credentials.credentials
    try:
        payload = verify_jwt_token(token, SECRET_KEY)
        return payload
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=str(e)
        )
```

## API Key Authentication

For service-to-service communication, API keys are preferred.

### Key Generation

```python
import secrets

def generate_api_key() -> str:
    """Generate a secure API key."""
    return secrets.token_urlsafe(32)
```

### Key Validation

```python
from fastapi import Header, HTTPException

async def verify_api_key(x_api_key: str = Header(...)) -> str:
    """Verify the API key from request headers."""
    if x_api_key not in VALID_API_KEYS:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Invalid API key"
        )
    return x_api_key
```

## OAuth 2.0 Integration

For third-party integrations, OAuth 2.0 with PKCE is recommended.

### Authorization Flow

1. Generate code verifier and challenge
2. Redirect user to authorization server
3. Exchange authorization code for tokens
4. Use refresh token for long-lived access

### Token Storage

Store tokens securely using environment variables or a secrets manager. Never commit tokens to version control.
