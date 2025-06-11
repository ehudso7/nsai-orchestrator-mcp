"""
Elite Security Implementation for NSAI Orchestrator MCP
Zero-Trust Architecture with Military-Grade Protection
"""

import asyncio
import hashlib
import hmac
import json
import secrets
import time
from base64 import b64encode, b64decode
from datetime import datetime, timedelta, timezone
from typing import Any, Dict, List, Optional, Set, Tuple
from dataclasses import dataclass, field
from enum import Enum
import re
from functools import wraps
import jwt
from cryptography.fernet import Fernet
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC
from cryptography.hazmat.primitives.ciphers.aead import AESGCM
import argon2
from argon2 import PasswordHasher
from argon2.exceptions import VerifyMismatchError, VerificationError, InvalidHash

# Advanced threat detection patterns
THREAT_PATTERNS = {
    "sql_injection": [
        r"(?i)(union|select|insert|update|delete|drop|create|alter|exec|execute|script|javascript|eval)\s*(all|distinct|from|where|join|into|values|set|declare|cast|convert|table|database|procedure|function)",
        r"(?i)(--|#|\/\*|\*\/|xp_|sp_|0x[0-9a-f]+)",
        r"(?i)(concat|substring|ascii|hex|char|ord)\s*\(",
        r"(?i)(benchmark|sleep|waitfor|delay|pg_sleep)\s*\(",
    ],
    "xss": [
        r"<script[^>]*>.*?</script>",
        r"(?i)(javascript|vbscript|onload|onerror|onmouseover|onclick|onfocus|onblur):",
        r"(?i)<(iframe|frame|embed|object|applet|meta|link|style|form|input)",
        r"(?i)(document\.|window\.|eval\(|setTimeout\(|setInterval\()",
    ],
    "path_traversal": [
        r"\.\.\/|\.\.\\",
        r"(?i)(etc\/passwd|boot\.ini|win\.ini|system32)",
        r"(?i)(\/proc\/|\/etc\/|\/var\/|c:\\|d:\\)",
    ],
    "command_injection": [
        r"[;&|`$]|\$\(|\|\||&&",
        r"(?i)(nc|netcat|wget|curl|ping|traceroute|nslookup|dig)\s+",
        r"(?i)(chmod|chown|sudo|su|passwd|shadow|sudoers)",
    ],
    "ldap_injection": [
        r"[()&|!*]|\*\)",
        r"(?i)(objectclass|cn|sn|uid|userpassword)=",
    ],
    "xxe": [
        r"<!ENTITY[^>]*>",
        r"SYSTEM\s+[\"'][^\"']*[\"']",
        r"<!DOCTYPE[^>]*>",
    ],
}

# Security event types
class SecurityEventType(Enum):
    AUTH_SUCCESS = "auth_success"
    AUTH_FAILURE = "auth_failure"
    SUSPICIOUS_ACTIVITY = "suspicious_activity"
    ATTACK_DETECTED = "attack_detected"
    RATE_LIMIT_EXCEEDED = "rate_limit_exceeded"
    PERMISSION_DENIED = "permission_denied"
    DATA_BREACH_ATTEMPT = "data_breach_attempt"
    API_KEY_COMPROMISED = "api_key_compromised"

@dataclass
class SecurityEvent:
    event_type: SecurityEventType
    user_id: Optional[str]
    ip_address: str
    user_agent: str
    timestamp: datetime = field(default_factory=lambda: datetime.now(timezone.utc))
    details: Dict[str, Any] = field(default_factory=dict)
    severity: str = "medium"
    
@dataclass
class SecurityContext:
    user_id: str
    roles: Set[str]
    permissions: Set[str]
    ip_address: str
    user_agent: str
    session_id: str
    authenticated_at: datetime
    mfa_verified: bool = False
    risk_score: float = 0.0
    
class AdvancedEncryption:
    """Military-grade encryption with key rotation"""
    
    def __init__(self, master_key: Optional[bytes] = None):
        self.master_key = master_key or Fernet.generate_key()
        self._key_rotation_interval = timedelta(days=30)
        self._keys: Dict[str, Tuple[bytes, datetime]] = {}
        self._current_key_id = self._generate_key_id()
        self._keys[self._current_key_id] = (self.master_key, datetime.now(timezone.utc))
        
    def _generate_key_id(self) -> str:
        return secrets.token_urlsafe(16)
        
    def _derive_key(self, salt: bytes, key_id: str) -> bytes:
        """Derive an encryption key from master key"""
        kdf = PBKDF2HMAC(
            algorithm=hashes.SHA256(),
            length=32,
            salt=salt,
            iterations=100000,
        )
        key = kdf.derive(self._keys[key_id][0])
        return b64encode(key)
        
    async def encrypt(self, data: str, context: Optional[str] = None) -> str:
        """Encrypt data with automatic key rotation"""
        # Check if key rotation is needed
        current_key_age = datetime.now(timezone.utc) - self._keys[self._current_key_id][1]
        if current_key_age > self._key_rotation_interval:
            await self._rotate_key()
            
        # Generate salt
        salt = secrets.token_bytes(16)
        
        # Derive key with context
        context_bytes = (context or "").encode()
        key = self._derive_key(salt + context_bytes, self._current_key_id)
        
        # Encrypt
        f = Fernet(key)
        encrypted = f.encrypt(data.encode())
        
        # Package with metadata
        package = {
            "v": 1,  # Version
            "kid": self._current_key_id,  # Key ID
            "salt": b64encode(salt).decode(),
            "data": encrypted.decode(),
            "ts": int(time.time())
        }
        
        return b64encode(json.dumps(package).encode()).decode()
        
    async def decrypt(self, encrypted_data: str, context: Optional[str] = None) -> str:
        """Decrypt data with key version support"""
        try:
            # Unpack
            package = json.loads(b64decode(encrypted_data))
            
            # Verify timestamp (prevent replay attacks)
            if abs(time.time() - package["ts"]) > 3600:  # 1 hour window
                raise ValueError("Encrypted data expired")
                
            # Get key
            key_id = package["kid"]
            if key_id not in self._keys:
                raise ValueError("Unknown key ID")
                
            # Derive key
            salt = b64decode(package["salt"])
            context_bytes = (context or "").encode()
            key = self._derive_key(salt + context_bytes, key_id)
            
            # Decrypt
            f = Fernet(key)
            decrypted = f.decrypt(package["data"].encode())
            
            return decrypted.decode()
            
        except Exception as e:
            raise ValueError(f"Decryption failed: {str(e)}")
            
    async def _rotate_key(self) -> None:
        """Rotate encryption keys"""
        new_key = Fernet.generate_key()
        new_key_id = self._generate_key_id()
        self._keys[new_key_id] = (new_key, datetime.now(timezone.utc))
        self._current_key_id = new_key_id
        
        # Clean old keys (keep last 3)
        if len(self._keys) > 3:
            oldest_key = min(self._keys.items(), key=lambda x: x[1][1])
            del self._keys[oldest_key[0]]

class ZeroTrustAuthenticator:
    """Zero-trust authentication with continuous verification"""
    
    def __init__(self, secret_key: str, redis_client):
        self.secret_key = secret_key
        self.redis = redis_client
        self.password_hasher = PasswordHasher(
            time_cost=2,
            memory_cost=65536,
            parallelism=1,
            hash_len=32,
            salt_len=16
        )
        self.jwt_algorithm = "HS256"
        self.session_timeout = 3600  # 1 hour
        self.mfa_timeout = 300  # 5 minutes
        
    async def create_user(self, username: str, password: str, roles: List[str]) -> Dict[str, Any]:
        """Create user with secure password storage"""
        # Validate password strength
        if not self._validate_password_strength(password):
            raise ValueError("Password does not meet security requirements")
            
        # Hash password
        password_hash = self.password_hasher.hash(password)
        
        # Generate user ID
        user_id = f"user_{secrets.token_urlsafe(16)}"
        
        # Store user
        user_data = {
            "id": user_id,
            "username": username,
            "password_hash": password_hash,
            "roles": roles,
            "created_at": datetime.now(timezone.utc).isoformat(),
            "mfa_secret": secrets.token_urlsafe(32),
            "failed_attempts": 0,
            "locked_until": None
        }
        
        await self.redis.hset(f"users:{username}", mapping=user_data)
        
        return {"user_id": user_id, "username": username, "roles": roles}
        
    async def authenticate(
        self,
        username: str,
        password: str,
        ip_address: str,
        user_agent: str
    ) -> Tuple[bool, Optional[str], Optional[SecurityContext]]:
        """Authenticate with anti-brute-force protection"""
        # Get user
        user_data = await self.redis.hgetall(f"users:{username}")
        if not user_data:
            # Prevent timing attacks
            self.password_hasher.hash(password)
            return False, "Invalid credentials", None
            
        # Check if account is locked
        if user_data.get(b"locked_until"):
            locked_until = datetime.fromisoformat(user_data[b"locked_until"].decode())
            if datetime.now(timezone.utc) < locked_until:
                return False, "Account temporarily locked", None
            else:
                # Unlock account
                await self.redis.hdel(f"users:{username}", "locked_until")
                await self.redis.hset(f"users:{username}", "failed_attempts", 0)
                
        # Verify password
        try:
            self.password_hasher.verify(user_data[b"password_hash"].decode(), password)
            
            # Check if rehashing is needed
            if self.password_hasher.check_needs_rehash(user_data[b"password_hash"].decode()):
                new_hash = self.password_hasher.hash(password)
                await self.redis.hset(f"users:{username}", "password_hash", new_hash)
                
        except (VerifyMismatchError, VerificationError, InvalidHash):
            # Increment failed attempts
            failed_attempts = int(user_data.get(b"failed_attempts", 0)) + 1
            await self.redis.hset(f"users:{username}", "failed_attempts", failed_attempts)
            
            # Lock account after 5 failed attempts
            if failed_attempts >= 5:
                locked_until = datetime.now(timezone.utc) + timedelta(minutes=15)
                await self.redis.hset(f"users:{username}", "locked_until", locked_until.isoformat())
                return False, "Account locked due to multiple failed attempts", None
                
            return False, "Invalid credentials", None
            
        # Reset failed attempts on successful auth
        await self.redis.hset(f"users:{username}", "failed_attempts", 0)
        
        # Create session
        session_id = secrets.token_urlsafe(32)
        
        # Create security context
        context = SecurityContext(
            user_id=user_data[b"id"].decode(),
            roles=set(json.loads(user_data[b"roles"].decode())),
            permissions=await self._get_permissions_for_roles(json.loads(user_data[b"roles"].decode())),
            ip_address=ip_address,
            user_agent=user_agent,
            session_id=session_id,
            authenticated_at=datetime.now(timezone.utc),
            risk_score=await self._calculate_risk_score(username, ip_address, user_agent)
        )
        
        # Store session
        session_data = {
            "user_id": context.user_id,
            "username": username,
            "roles": json.dumps(list(context.roles)),
            "permissions": json.dumps(list(context.permissions)),
            "ip_address": ip_address,
            "user_agent": user_agent,
            "authenticated_at": context.authenticated_at.isoformat(),
            "last_activity": datetime.now(timezone.utc).isoformat(),
            "risk_score": context.risk_score
        }
        
        await self.redis.hset(f"sessions:{session_id}", mapping=session_data)
        await self.redis.expire(f"sessions:{session_id}", self.session_timeout)
        
        # Generate JWT token
        token_data = {
            "sub": context.user_id,
            "username": username,
            "roles": list(context.roles),
            "session_id": session_id,
            "iat": datetime.now(timezone.utc),
            "exp": datetime.now(timezone.utc) + timedelta(seconds=self.session_timeout)
        }
        
        token = jwt.encode(token_data, self.secret_key, algorithm=self.jwt_algorithm)
        
        return True, token, context
        
    async def verify_token(self, token: str, ip_address: str, user_agent: str) -> Optional[SecurityContext]:
        """Verify JWT token with continuous validation"""
        try:
            # Decode token
            payload = jwt.decode(token, self.secret_key, algorithms=[self.jwt_algorithm])
            
            # Get session
            session_id = payload["session_id"]
            session_data = await self.redis.hgetall(f"sessions:{session_id}")
            
            if not session_data:
                return None
                
            # Verify IP and user agent (zero-trust)
            if (session_data[b"ip_address"].decode() != ip_address or
                session_data[b"user_agent"].decode() != user_agent):
                # Session hijacking attempt detected
                await self._log_security_event(
                    SecurityEventType.SUSPICIOUS_ACTIVITY,
                    payload["sub"],
                    ip_address,
                    user_agent,
                    {"reason": "Session hijacking attempt"}
                )
                await self.redis.delete(f"sessions:{session_id}")
                return None
                
            # Update last activity
            await self.redis.hset(f"sessions:{session_id}", "last_activity", 
                                datetime.now(timezone.utc).isoformat())
            await self.redis.expire(f"sessions:{session_id}", self.session_timeout)
            
            # Recreate security context
            context = SecurityContext(
                user_id=payload["sub"],
                roles=set(payload["roles"]),
                permissions=set(json.loads(session_data[b"permissions"].decode())),
                ip_address=ip_address,
                user_agent=user_agent,
                session_id=session_id,
                authenticated_at=datetime.fromisoformat(session_data[b"authenticated_at"].decode()),
                risk_score=float(session_data[b"risk_score"])
            )
            
            return context
            
        except jwt.ExpiredSignatureError:
            return None
        except jwt.InvalidTokenError:
            # Log potential attack
            await self._log_security_event(
                SecurityEventType.SUSPICIOUS_ACTIVITY,
                None,
                ip_address,
                user_agent,
                {"reason": "Invalid token"}
            )
            return None
            
    def _validate_password_strength(self, password: str) -> bool:
        """Validate password meets security requirements"""
        if len(password) < 12:
            return False
        if not re.search(r"[A-Z]", password):
            return False
        if not re.search(r"[a-z]", password):
            return False
        if not re.search(r"\d", password):
            return False
        if not re.search(r"[!@#$%^&*(),.?\":{}|<>]", password):
            return False
        return True
        
    async def _get_permissions_for_roles(self, roles: List[str]) -> Set[str]:
        """Get permissions for roles with inheritance"""
        permissions = set()
        
        for role in roles:
            role_perms = await self.redis.smembers(f"role_permissions:{role}")
            permissions.update(p.decode() for p in role_perms)
            
        return permissions
        
    async def _calculate_risk_score(self, username: str, ip_address: str, user_agent: str) -> float:
        """Calculate authentication risk score"""
        risk_score = 0.0
        
        # Check IP reputation
        ip_reputation = await self._check_ip_reputation(ip_address)
        if ip_reputation == "malicious":
            risk_score += 0.8
        elif ip_reputation == "suspicious":
            risk_score += 0.4
            
        # Check login history
        recent_ips = await self.redis.lrange(f"login_history:{username}:ips", 0, 9)
        if ip_address.encode() not in recent_ips:
            risk_score += 0.2  # New IP
            
        # Check user agent
        recent_agents = await self.redis.lrange(f"login_history:{username}:agents", 0, 9)
        if user_agent.encode() not in recent_agents:
            risk_score += 0.1  # New device
            
        # Check time of day
        current_hour = datetime.now(timezone.utc).hour
        if current_hour < 6 or current_hour > 22:
            risk_score += 0.1  # Unusual hours
            
        # Update history
        await self.redis.lpush(f"login_history:{username}:ips", ip_address)
        await self.redis.ltrim(f"login_history:{username}:ips", 0, 49)
        await self.redis.lpush(f"login_history:{username}:agents", user_agent)
        await self.redis.ltrim(f"login_history:{username}:agents", 0, 49)
        
        return min(risk_score, 1.0)
        
    async def _check_ip_reputation(self, ip_address: str) -> str:
        """Check IP reputation against threat intelligence"""
        # Check local blacklist
        if await self.redis.sismember("ip_blacklist", ip_address):
            return "malicious"
            
        # Check rate limits
        recent_requests = await self.redis.incr(f"ip_requests:{ip_address}")
        await self.redis.expire(f"ip_requests:{ip_address}", 3600)
        
        if recent_requests > 1000:
            return "suspicious"
            
        return "clean"
        
    async def _log_security_event(
        self,
        event_type: SecurityEventType,
        user_id: Optional[str],
        ip_address: str,
        user_agent: str,
        details: Dict[str, Any]
    ) -> None:
        """Log security event for audit and threat detection"""
        event = SecurityEvent(
            event_type=event_type,
            user_id=user_id,
            ip_address=ip_address,
            user_agent=user_agent,
            details=details
        )
        
        # Store in Redis stream for real-time processing
        await self.redis.xadd(
            "security_events",
            {
                "type": event.event_type.value,
                "user_id": event.user_id or "",
                "ip_address": event.ip_address,
                "user_agent": event.user_agent,
                "timestamp": event.timestamp.isoformat(),
                "details": json.dumps(event.details),
                "severity": event.severity
            }
        )

class ThreatDetector:
    """Advanced threat detection with ML-ready features"""
    
    def __init__(self, redis_client):
        self.redis = redis_client
        self.threat_patterns = THREAT_PATTERNS
        
    async def scan_input(self, data: Any, context: str = "general") -> Tuple[bool, List[str]]:
        """Scan input for threats with pattern matching"""
        threats_found = []
        
        # Convert to string for analysis
        if isinstance(data, dict):
            data_str = json.dumps(data)
        elif isinstance(data, list):
            data_str = " ".join(str(item) for item in data)
        else:
            data_str = str(data)
            
        # Check against threat patterns
        for threat_type, patterns in self.threat_patterns.items():
            for pattern in patterns:
                if re.search(pattern, data_str, re.IGNORECASE | re.DOTALL):
                    threats_found.append(threat_type)
                    break
                    
        # Check for encoded payloads
        if self._check_encoded_threats(data_str):
            threats_found.append("encoded_payload")
            
        # Context-specific checks
        if context == "filename":
            if self._check_file_threats(data_str):
                threats_found.append("malicious_filename")
        elif context == "email":
            if not self._validate_email(data_str):
                threats_found.append("invalid_email")
                
        # Log threat detection
        if threats_found:
            await self.redis.xadd(
                "threat_detections",
                {
                    "timestamp": datetime.now(timezone.utc).isoformat(),
                    "threats": json.dumps(threats_found),
                    "context": context,
                    "data_hash": hashlib.sha256(data_str.encode()).hexdigest()
                }
            )
            
        return len(threats_found) == 0, threats_found
        
    def _check_encoded_threats(self, data: str) -> bool:
        """Check for base64/hex encoded threats"""
        # Check for base64 encoded patterns
        try:
            decoded = b64decode(data)
            if len(decoded) > 20:  # Reasonable threshold
                decoded_str = decoded.decode('utf-8', errors='ignore')
                for patterns in self.threat_patterns.values():
                    for pattern in patterns:
                        if re.search(pattern, decoded_str, re.IGNORECASE):
                            return True
        except:
            pass
            
        # Check for hex encoded patterns
        hex_pattern = r"(?:0x)?([0-9a-fA-F]{20,})"
        hex_matches = re.findall(hex_pattern, data)
        for hex_str in hex_matches:
            try:
                decoded = bytes.fromhex(hex_str).decode('utf-8', errors='ignore')
                for patterns in self.threat_patterns.values():
                    for pattern in patterns:
                        if re.search(pattern, decoded, re.IGNORECASE):
                            return True
            except:
                pass
                
        return False
        
    def _check_file_threats(self, filename: str) -> bool:
        """Check for malicious filenames"""
        dangerous_extensions = {
            '.exe', '.bat', '.cmd', '.com', '.scr', '.vbs', '.vbe',
            '.js', '.jse', '.wsf', '.wsh', '.ps1', '.psm1', '.psd1',
            '.msi', '.jar', '.app', '.deb', '.rpm'
        }
        
        # Check double extensions
        if filename.count('.') > 1:
            parts = filename.split('.')
            if any(f".{ext}" in dangerous_extensions for ext in parts[1:]):
                return True
                
        # Check direct dangerous extensions
        return any(filename.lower().endswith(ext) for ext in dangerous_extensions)
        
    def _validate_email(self, email: str) -> bool:
        """Validate email format"""
        email_pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
        return bool(re.match(email_pattern, email))

class PermissionManager:
    """Fine-grained permission management with inheritance"""
    
    def __init__(self, redis_client):
        self.redis = redis_client
        
    async def check_permission(
        self,
        context: SecurityContext,
        resource: str,
        action: str
    ) -> bool:
        """Check if user has permission for action on resource"""
        # Check direct permissions
        permission = f"{resource}:{action}"
        if permission in context.permissions:
            return True
            
        # Check wildcard permissions
        if f"{resource}:*" in context.permissions:
            return True
        if f"*:{action}" in context.permissions:
            return True
        if "*:*" in context.permissions:  # Super admin
            return True
            
        # Check resource hierarchy
        resource_parts = resource.split(".")
        for i in range(len(resource_parts)):
            parent_resource = ".".join(resource_parts[:i+1])
            if f"{parent_resource}.*:{action}" in context.permissions:
                return True
                
        return False
        
    async def grant_permission(
        self,
        role: str,
        resource: str,
        action: str
    ) -> None:
        """Grant permission to role"""
        permission = f"{resource}:{action}"
        await self.redis.sadd(f"role_permissions:{role}", permission)
        
    async def revoke_permission(
        self,
        role: str,
        resource: str,
        action: str
    ) -> None:
        """Revoke permission from role"""
        permission = f"{resource}:{action}"
        await self.redis.srem(f"role_permissions:{role}", permission)
        
    async def create_role_hierarchy(
        self,
        parent_role: str,
        child_role: str
    ) -> None:
        """Create role inheritance"""
        await self.redis.sadd(f"role_children:{parent_role}", child_role)
        
        # Copy parent permissions to child
        parent_perms = await self.redis.smembers(f"role_permissions:{parent_role}")
        if parent_perms:
            await self.redis.sadd(f"role_permissions:{child_role}", *parent_perms)

# Authorization decorator
def require_permission(resource: str, action: str):
    """Decorator to check permissions"""
    def decorator(func):
        @wraps(func)
        async def wrapper(self, context: SecurityContext, *args, **kwargs):
            permission_manager = self.container.resolve(PermissionManager)
            
            if not await permission_manager.check_permission(context, resource, action):
                await self._log_security_event(
                    SecurityEventType.PERMISSION_DENIED,
                    context.user_id,
                    context.ip_address,
                    context.user_agent,
                    {"resource": resource, "action": action}
                )
                raise PermissionError(f"Permission denied for {resource}:{action}")
                
            return await func(self, context, *args, **kwargs)
        return wrapper
    return decorator

# Export security components
__all__ = [
    'SecurityContext',
    'SecurityEventType',
    'AdvancedEncryption',
    'ZeroTrustAuthenticator',
    'ThreatDetector',
    'PermissionManager',
    'require_permission'
]