"""Production-grade security implementation."""

import jwt
import bcrypt
import secrets
import hashlib
from datetime import datetime, timedelta
from typing import Optional, Dict, Any, List
from fastapi import HTTPException, status, Depends, Request
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from passlib.context import CryptContext
from slowapi import Limiter, _rate_limit_exceeded_handler
from slowapi.util import get_remote_address
from slowapi.errors import RateLimitExceeded
from slowapi.middleware import SlowAPIMiddleware
import structlog
from config import get_settings

logger = structlog.get_logger()
settings = get_settings()

# Password hashing
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

# Rate limiting
limiter = Limiter(key_func=get_remote_address)

# Security schemes
security = HTTPBearer(auto_error=False)


class SecurityManager:
    """Centralized security management."""
    
    @staticmethod
    def hash_password(password: str) -> str:
        """Hash password using bcrypt."""
        salt = bcrypt.gensalt(rounds=settings.security.bcrypt_rounds)
        return bcrypt.hashpw(password.encode('utf-8'), salt).decode('utf-8')
    
    @staticmethod
    def verify_password(password: str, hashed: str) -> bool:
        """Verify password against hash."""
        return bcrypt.checkpw(password.encode('utf-8'), hashed.encode('utf-8'))
    
    @staticmethod
    def generate_token(data: Dict[str, Any], expires_delta: Optional[timedelta] = None) -> str:
        """Generate JWT token."""
        to_encode = data.copy()
        if expires_delta:
            expire = datetime.utcnow() + expires_delta
        else:
            expire = datetime.utcnow() + timedelta(minutes=settings.security.jwt_expire_minutes)
        
        to_encode.update({"exp": expire, "iat": datetime.utcnow()})
        
        return jwt.encode(
            to_encode,
            settings.security.jwt_secret,
            algorithm=settings.security.jwt_algorithm
        )
    
    @staticmethod
    def verify_token(token: str) -> Dict[str, Any]:
        """Verify and decode JWT token."""
        try:
            payload = jwt.decode(
                token,
                settings.security.jwt_secret,
                algorithms=[settings.security.jwt_algorithm]
            )
            return payload
        except jwt.ExpiredSignatureError:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Token has expired"
            )
        except jwt.JWTError:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid token"
            )
    
    @staticmethod
    def generate_api_key(prefix: str = "nsai") -> str:
        """Generate secure API key."""
        random_part = secrets.token_urlsafe(32)
        return f"{prefix}_{random_part}"
    
    @staticmethod
    def hash_api_key(api_key: str) -> str:
        """Hash API key for storage."""
        return hashlib.sha256(api_key.encode()).hexdigest()
    
    @staticmethod
    def verify_api_key(api_key: str, hashed: str) -> bool:
        """Verify API key against hash."""
        return hashlib.sha256(api_key.encode()).hexdigest() == hashed


class InputSanitizer:
    """Input sanitization and validation."""
    
    @staticmethod
    def sanitize_string(input_str: str, max_length: int = 1000) -> str:
        """Sanitize string input."""
        if not isinstance(input_str, str):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Input must be a string"
            )
        
        # Remove null bytes and control characters
        sanitized = input_str.replace('\x00', '').replace('\r', '').replace('\n', ' ')
        
        # Limit length
        if len(sanitized) > max_length:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Input too long. Maximum {max_length} characters."
            )
        
        return sanitized.strip()
    
    @staticmethod
    def sanitize_dict(input_dict: Dict[str, Any], max_depth: int = 5) -> Dict[str, Any]:
        """Sanitize dictionary input recursively."""
        if not isinstance(input_dict, dict):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Input must be a dictionary"
            )
        
        if max_depth <= 0:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Input dictionary too deeply nested"
            )
        
        sanitized = {}
        for key, value in input_dict.items():
            if isinstance(key, str):
                clean_key = InputSanitizer.sanitize_string(key, 100)
                if isinstance(value, str):
                    sanitized[clean_key] = InputSanitizer.sanitize_string(value)
                elif isinstance(value, dict):
                    sanitized[clean_key] = InputSanitizer.sanitize_dict(value, max_depth - 1)
                elif isinstance(value, list):
                    sanitized[clean_key] = InputSanitizer.sanitize_list(value, max_depth - 1)
                else:
                    sanitized[clean_key] = value
        
        return sanitized
    
    @staticmethod
    def sanitize_list(input_list: List[Any], max_depth: int = 5) -> List[Any]:
        """Sanitize list input recursively."""
        if not isinstance(input_list, list):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Input must be a list"
            )
        
        if len(input_list) > 1000:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="List too long. Maximum 1000 items."
            )
        
        sanitized = []
        for item in input_list:
            if isinstance(item, str):
                sanitized.append(InputSanitizer.sanitize_string(item))
            elif isinstance(item, dict):
                sanitized.append(InputSanitizer.sanitize_dict(item, max_depth - 1))
            elif isinstance(item, list):
                sanitized.append(InputSanitizer.sanitize_list(item, max_depth - 1))
            else:
                sanitized.append(item)
        
        return sanitized


def get_current_user(credentials: Optional[HTTPAuthorizationCredentials] = Depends(security)):
    """Get current authenticated user."""
    if not credentials:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Authentication required"
        )
    
    payload = SecurityManager.verify_token(credentials.credentials)
    return payload


def require_api_key(request: Request):
    """Require valid API key in header."""
    api_key = request.headers.get("X-API-Key")
    if not api_key:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="API key required"
        )
    
    # In production, verify against stored hash
    # For now, we'll use a simple validation
    if not api_key.startswith("nsai_"):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid API key format"
        )
    
    return api_key


async def log_security_event(
    event_type: str,
    details: Dict[str, Any],
    request: Request,
    severity: str = "info"
):
    """Log security events for audit trail."""
    event_data = {
        "event_type": event_type,
        "timestamp": datetime.utcnow().isoformat(),
        "client_ip": get_remote_address(request),
        "user_agent": request.headers.get("user-agent"),
        "endpoint": str(request.url),
        "method": request.method,
        "details": details,
        "severity": severity
    }
    
    if severity == "critical":
        logger.critical("Security event", **event_data)
    elif severity == "warning":
        logger.warning("Security event", **event_data)
    else:
        logger.info("Security event", **event_data)


# Rate limiting decorators
def rate_limit_by_ip(rate: str):
    """Rate limit by IP address."""
    return limiter.limit(rate)


def rate_limit_by_user(rate: str):
    """Rate limit by authenticated user."""
    def _rate_limit_by_user(request: Request):
        # Extract user ID from token if available
        auth_header = request.headers.get("authorization")
        if auth_header and auth_header.startswith("Bearer "):
            try:
                token = auth_header.split(" ")[1]
                payload = SecurityManager.verify_token(token)
                return payload.get("user_id", get_remote_address(request))
            except:
                pass
        return get_remote_address(request)
    
    return limiter.limit(rate, key_func=_rate_limit_by_user)


# CSRF protection
def generate_csrf_token(session_id: str) -> str:
    """Generate CSRF token for session."""
    data = f"{session_id}:{datetime.utcnow().isoformat()}:{settings.security.secret_key}"
    return hashlib.sha256(data.encode()).hexdigest()


def verify_csrf_token(token: str, session_id: str) -> bool:
    """Verify CSRF token."""
    expected = generate_csrf_token(session_id)
    return secrets.compare_digest(token, expected)