"""Authorised work-queue read model; selection precedes display pagination."""
from typing import Literal
from fastapi import Depends
from sqlalchemy import func, select
from sqlalchemy.orm import Session
from .auth import Principal, get_db, principal, utc
from .models import CaseRecord
from .policies import visible_cases
from .scheduling import context_now


def register_workspace(app, serialize):
    @app.get('/api/workspace')
    def workspace(queue: Literal['open', 'overdue', 'mine'] = 'open',
                  actor: Principal = Depends(principal), db: Session = Depends(get_db)):
        at = context_now(db)
        scope = visible_cases(actor)
        active = CaseRecord.lifecycle != 'DISPOSED'
        overdue = CaseRecord.due_at < at
        mine = CaseRecord.current_owner_id == actor.user.id
        def count(*conditions):
            return db.scalar(select(func.count()).select_from(CaseRecord).where(scope, *conditions))
        selection = [scope, active]
        if queue == 'overdue':
            selection.append(overdue)
        if queue == 'mine':
            selection.append(mine)
        rows = db.scalars(select(CaseRecord).where(*selection).order_by(
            CaseRecord.due_at.is_(None), CaseRecord.due_at, CaseRecord.received_at, CaseRecord.id).limit(12)).all()
        return {'as_of': utc(at).isoformat(), 'queue': queue,
                'counts': {'open': count(active), 'overdue': count(active, overdue),
                           'mine': count(active, mine), 'total': count()},
                'matching': count(*selection[1:]), 'limit': 12,
                'items': [serialize(db, actor, case) for case in rows]}
