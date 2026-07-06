"""
Authentication service for user registration, login, and OAuth.
"""

from datetime import datetime
from typing import Optional

from sqlalchemy.orm import Session

from app.core.security import (
    create_access_token,
    create_refresh_token,
    get_password_hash,
    verify_password,
)
from app.models.user import User, UserProfile
from app.schemas.auth import LoginRequest, RegisterRequest, Token
from app.schemas.user import UserCreate


class AuthService:
    """Authentication business logic service."""
    
    @staticmethod
    def create_user(db: Session, user_data: RegisterRequest) -> User:
        """
        Create a new user with hashed password.
        
        Args:
            db: Database session
            user_data: Registration data
        
        Returns:
            Created user
        
        Raises:
            ValueError: If email already exists
        """
        # Check if user exists
        existing = db.query(User).filter(User.email == user_data.email).first()
        if existing:
            raise ValueError("Email already registered")
        
        # Create user
        user = User(
            email=user_data.email,
            hashed_password=get_password_hash(user_data.password),
            full_name=user_data.full_name,
            is_active=True,
            is_verified=False,
        )
        db.add(user)
        db.flush()  # Get user.id
        
        # Create user profile
        profile = UserProfile(user_id=user.id)
        db.add(profile)
        db.commit()
        db.refresh(user)
        
        return user
    
    @staticmethod
    def authenticate_user(
        db: Session,
        credentials: LoginRequest
    ) -> Optional[User]:
        """
        Authenticate user with email and password.
        
        Args:
            db: Database session
            credentials: Login credentials
        
        Returns:
            User if authentication successful, None otherwise
        """
        user = db.query(User).filter(User.email == credentials.email).first()
        
        if not user:
            return None
        
        if not user.hashed_password:
            # OAuth user without password
            return None
        
        if not verify_password(credentials.password, user.hashed_password):
            return None
        
        if not user.is_active:
            return None
        
        # Update last login
        user.last_login_at = datetime.utcnow()
        db.commit()
        
        return user
    
    @staticmethod
    def create_tokens_for_user(user: User) -> Token:
        """
        Create access and refresh tokens for user.
        
        Args:
            user: User object
        
        Returns:
            Token pair
        """
        token_data = {"sub": str(user.id), "email": user.email}
        
        access_token = create_access_token(token_data)
        refresh_token = create_refresh_token(token_data)
        
        return Token(
            access_token=access_token,
            refresh_token=refresh_token,
            token_type="bearer",
        )
    
    @staticmethod
    def get_or_create_oauth_user(
        db: Session,
        email: str,
        oauth_provider: str,
        oauth_id: str,
        full_name: Optional[str] = None,
        avatar_url: Optional[str] = None,
    ) -> User:
        """
        Get existing OAuth user or create new one.
        
        Args:
            db: Database session
            email: User email from OAuth provider
            oauth_provider: Provider name ("google", "github")
            oauth_id: Provider-specific user ID
            full_name: User's full name
            avatar_url: Profile picture URL
        
        Returns:
            User object
        """
        # Check if user exists with this OAuth ID
        user = db.query(User).filter(
            User.oauth_provider == oauth_provider,
            User.oauth_id == oauth_id
        ).first()
        
        if user:
            # Update last login
            user.last_login_at = datetime.utcnow()
            db.commit()
            return user
        
        # Check if user exists with this email (link accounts)
        user = db.query(User).filter(User.email == email).first()
        
        if user:
            # Link OAuth provider to existing account
            user.oauth_provider = oauth_provider
            user.oauth_id = oauth_id
            if avatar_url and not user.avatar_url:
                user.avatar_url = avatar_url
            user.last_login_at = datetime.utcnow()
            db.commit()
            return user
        
        # Create new OAuth user
        user = User(
            email=email,
            oauth_provider=oauth_provider,
            oauth_id=oauth_id,
            full_name=full_name,
            avatar_url=avatar_url,
            is_active=True,
            is_verified=True,  # OAuth users are pre-verified
            hashed_password=None,  # No password for OAuth users
        )
        db.add(user)
        db.flush()
        
        # Create profile
        profile = UserProfile(user_id=user.id)
        db.add(profile)
        db.commit()
        db.refresh(user)
        
        return user
