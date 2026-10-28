from dataclasses import dataclass
from datetime import timedelta, timezone
import hashlib
import secrets
from argon2 import PasswordHasher
from argon2.exceptions import VerifyMismatchError, VerificationError
from fastapi import Depends, HTTPException, Request
from sqlalchemy import select
from sqlalchemy.orm import Session
from .models import LoginSession, Membership, User, now

hasher = PasswordHasher()
DUMMY_HASH=hasher.hash('Synthetic dummy verification; not an account password')
COOKIE = "samanvay_session"


def token_hash(value):
    return hashlib.sha256(value.encode()).hexdigest()


def utc(value):
    return value.replace(tzinfo=timezone.utc) if value.tzinfo is None else value


def get_db(request: Request):
    with request.app.state.sessions() as session:
        yield session


@dataclass
class Principal:
    user: User
    session: LoginSession
    memberships: list[Membership]


def principal(request: Request, db: Session = Depends(get_db)):
    token = request.cookies.get(request.app.state.settings.cookie_name, "")
    session = db.get(LoginSession, token_hash(token)) if token else None
    if not session or session.revoked or utc(session.expires_at) <= now():
        raise HTTPException(401, "Sign in to continue.")
    user = db.get(User, session.user_id)
    if not user or not user.active:
        raise HTTPException(401, "This session is no longer valid.")
    memberships = list(db.scalars(select(Membership).where(Membership.user_id == user.id)))
    return Principal(user, session, memberships)


def require_origin(request: Request):
    origin = request.headers.get("origin")
    if origin and origin not in request.app.state.settings.allowed_origins:
        raise HTTPException(403, "Request origin is not allowed.")
    if request.headers.get("sec-fetch-site") == "cross-site":
        raise HTTPException(403, "Cross-site requests are not allowed.")


def mutation(request: Request, actor: Principal = Depends(principal)):
    require_origin(request)
    token = request.headers.get("x-csrf-token", "")
    if not secrets.compare_digest(token, actor.session.csrf_token):
        raise HTTPException(403, "Session validation failed. Reload before trying again.")
    return actor


def session_view(actor: Principal):
    return {"user": {"id": actor.user.id, "username": actor.user.username, "display_name": actor.user.display_name,
                     "memberships": [{"role": m.role, "bureau": m.bureau_id, "region": m.region_id} for m in actor.memberships]},
            "csrf_token": actor.session.csrf_token, "expires_at": utc(actor.session.expires_at).isoformat(), "synthetic": True}


def password_matches(encoded, password):
    try:
        return hasher.verify(encoded, password)
    except (VerifyMismatchError, VerificationError):
        return False


def new_session(user, hours):
    token = secrets.token_urlsafe(40)
    session = LoginSession(token_hash=token_hash(token), user_id=user.id,
                           csrf_token=secrets.token_urlsafe(32), expires_at=now() + timedelta(hours=hours))
    return token, session
