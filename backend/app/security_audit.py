"""Auxiliary read/access records contain no narratives, query terms, cookies or file bytes."""
import hashlib
from sqlalchemy.exc import SQLAlchemyError
from .auth import COOKIE,token_hash
from .models import LoginSession,SecurityAudit


def record_access(app,request,status):
    path=request.url.path
    operations=[('/api/attachments/','EVIDENCE_ACCESS'),('/api/cases','CASE_ACCESS'),('/api/reports','REPORT_ACCESS'),
        ('/api/settings','TECHNICAL_ADMIN'),('/api/demo/','DEMO_CONTROL'),('/api/auth/','AUTHENTICATION'),
        ('/api/relationships','PAIR_REVIEW_ACCESS'),('/api/coordination','COORDINATION_ACCESS')]
    operation=next((kind for prefix,kind in operations if path.startswith(prefix)),None)
    if operation is None:return
    try:
        with app.state.sessions() as db:
            cookie=request.cookies.get(app.state.settings.cookie_name,'')
            session=db.get(LoginSession,token_hash(cookie)) if cookie else None
            db.add(SecurityAudit(user_id=session.user_id if session else None,operation=operation,
                resource_hash=hashlib.sha256(path.encode()).hexdigest(),method=request.method,status=status))
            db.commit()
    except SQLAlchemyError:
        # Business mutations have their own mandatory transactional audit. This auxiliary
        # access record is best effort during DB failure and cannot claim tamper-proofing.
        pass
