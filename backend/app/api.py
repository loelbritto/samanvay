from datetime import datetime, time, timedelta, timezone
import hashlib
import json
import secrets
from zoneinfo import ZoneInfo
from fastapi import Depends, FastAPI, File, Form, Header, HTTPException, Request, Response, UploadFile
from fastapi.exceptions import RequestValidationError
from fastapi.responses import FileResponse, JSONResponse
from pydantic import ValidationError
from sqlalchemy import and_, func, or_, select, update
from sqlalchemy.exc import IntegrityError, SQLAlchemyError
from sqlalchemy.orm import Session
from .auth import COOKIE, DUMMY_HASH, Principal, get_db, hasher, mutation, new_session, password_matches, principal, require_origin, session_view, token_hash, utc
from .config import Settings
from .database import make_database
from .models import AccessGrant, Assignment, Attachment, Bureau, CaseRecord, Complainant, Institution, InstitutionAlias, IntakeRequest, LoginAttempt, Membership, OriginalSubmission, OutboxJob, User, WorkflowEvent, now, new_id
from .policies import can_assign, can_read, grants, intake_membership, load_case, visible_cases
from .schemas import AssignmentInput, CaseInput, LoginInput
from .storage import prepare_files, private_path, store
from .reporting import Filters, case_query
from .scheduling import context_now

INDIA = ZoneInfo("Asia/Kolkata")


from .case_views import serialize_case


def create_app(settings=None):
    app = FastAPI(title="Samanvay synthetic local prototype", version="0.2.0")
    app.state.settings = settings or Settings.from_env()
    app.state.engine, app.state.sessions = make_database(app.state.settings)
    from .request_limits import BodyLimitMiddleware
    app.add_middleware(BodyLimitMiddleware)

    @app.middleware("http")
    async def response_policy(request, call_next):
        try:
            if int(request.headers.get("content-length", "0")) > 16 * 1024 * 1024:
                return JSONResponse({"detail": "Request exceeds the 16 MiB local-demo limit."}, status_code=413)
        except ValueError:
            return JSONResponse({"detail": "Invalid request length."}, status_code=400)
        response = await call_next(request)
        response.headers["Cache-Control"] = "no-store"
        response.headers["X-Content-Type-Options"] = "nosniff"
        response.headers['Referrer-Policy']='no-referrer'
        response.headers['X-Frame-Options']='DENY'
        from .security_audit import record_access
        record_access(app,request,response.status_code)
        return response

    @app.exception_handler(RequestValidationError)
    async def safe_validation(_, exc):
        return JSONResponse({"detail": [{"loc": list(e["loc"]), "msg": e["msg"], "type": e["type"]} for e in exc.errors()]}, status_code=422)

    @app.exception_handler(SQLAlchemyError)
    async def database_error(_, exc):
        return JSONResponse({"detail": "Database operation could not be completed. No success is confirmed; retry with the same request key."}, status_code=503)

    @app.get("/api/health")
    def health(db: Session = Depends(get_db)):
        db.execute(select(1))
        return {"status": "ok", "synthetic": True, "database": "persistent SQLite", "integrations": "none"}

    @app.post("/api/auth/login")
    def login(data: LoginInput, request: Request, response: Response, db: Session = Depends(get_db)):
        require_origin(request)
        username = data.username.strip().lower()
        key = token_hash(username)
        attempt = db.get(LoginAttempt, key)
        if attempt and utc(attempt.window_start) > now() - timedelta(minutes=5) and attempt.count >= 10:
            raise HTTPException(429, "Too many sign-in attempts. Try again after five minutes.")
        user = db.scalar(select(User).where(User.username == username, User.active.is_(True)))
        matched=password_matches(user.password_hash if user else DUMMY_HASH,data.password)
        if not user or not matched:
            if not attempt:
                attempt = LoginAttempt(key=key, count=0, window_start=now())
                db.add(attempt)
            if utc(attempt.window_start) <= now() - timedelta(minutes=5):
                attempt.count, attempt.window_start = 0, now()
            attempt.count += 1
            db.commit()
            raise HTTPException(401, "Invalid synthetic account credentials.")
        if attempt:
            attempt.count = 0
        token, session = new_session(user, app.state.settings.session_hours)
        db.add(session)
        db.commit()
        response.set_cookie(app.state.settings.cookie_name, token, httponly=True, secure=app.state.settings.secure_cookie,
                            samesite="strict", max_age=app.state.settings.session_hours * 3600, path="/")
        actor = Principal(user, session, list(db.scalars(select(Membership).where(Membership.user_id == user.id))))
        return session_view(actor)

    @app.get("/api/auth/session")
    def session(actor: Principal = Depends(principal)):
        return session_view(actor)

    @app.post("/api/auth/logout", status_code=204)
    def logout(response: Response, actor: Principal = Depends(mutation), db: Session = Depends(get_db)):
        actor.session.revoked = True
        db.commit()
        response.delete_cookie(app.state.settings.cookie_name, path="/")

    @app.get("/api/institutions")
    def institutions(actor: Principal = Depends(principal), db: Session = Depends(get_db)):
        return [{"id": i.id, "name": i.name, "city": i.city, "region": i.region_id, "version": i.version,
                 "synthetic": i.synthetic, "aliases": [{"alias": a.alias, "provenance": a.provenance} for a in db.scalars(select(InstitutionAlias).where(InstitutionAlias.institution_id == i.id))]}
                for i in db.scalars(select(Institution).order_by(Institution.city))]

    @app.get("/api/overview")
    def overview(actor: Principal = Depends(principal), db: Session = Depends(get_db)):
        population = list(db.scalars(select(CaseRecord).where(visible_cases(actor)).order_by(CaseRecord.created_at.desc())))
        return {"total": len(population), "pending": sum(c.lifecycle != "DISPOSED" for c in population),
                "under_review": sum(c.lifecycle == "UNDER_REVIEW" for c in population),
                "institutions": len({c.institution_id for c in population}), "as_of": context_now(db).isoformat(), "synthetic": True,
                "cases": [serialize_case(db, actor, c) for c in population[:20]]}

    @app.get("/api/cases")
    def case_list(filters: Filters = Depends(), offset: int = 0, limit: int = 200,
                  actor: Principal = Depends(principal), db: Session = Depends(get_db)):
        if offset < 0 or limit < 1 or limit > 200:
            raise HTTPException(422, "Use a nonnegative offset and limit from 1 to 200.")
        query=case_query(actor,filters)
        total=db.scalar(select(func.count()).select_from(query.subquery()))
        records=db.scalars(query.order_by(CaseRecord.created_at.desc(),CaseRecord.id).offset(offset).limit(limit))
        return {"total":total,"items":[serialize_case(db,actor,c) for c in records],"limit":limit,"offset":offset,"synthetic":True}

    @app.get("/api/search/suggestions")
    def search_suggestions(q: str = "", actor: Principal = Depends(principal), db: Session = Depends(get_db)):
        records=db.scalars(case_query(actor,Filters(q=q[:200])).order_by(CaseRecord.public_id).limit(10))
        return [{"case_id":c.public_id,"institution_id":c.institution_id} for c in records]

    @app.get("/api/cases/{public_id}")
    def detail(public_id: str, actor: Principal = Depends(principal), db: Session = Depends(get_db)):
        return serialize_case(db, actor, load_case(db, actor, public_id), detail=True)

    @app.post("/api/cases", status_code=201)
    async def create_case(payload: str = Form(...), files: list[UploadFile] = File(default=[]),
                          request_key: str = Header(..., alias="Idempotency-Key"),
                          actor: Principal = Depends(mutation), db: Session = Depends(get_db)):
        if not (8 <= len(request_key) <= 80):
            raise HTTPException(422, "A valid intake request key is required.")
        try:
            original = json.loads(payload)
            data = CaseInput.model_validate(original)
        except (ValueError, ValidationError):
            raise HTTPException(422, "Check all required complaint fields, lengths, dates and the DEMO- token.")
        if not data.synthetic:
            raise HTTPException(422, "This prototype accepts synthetic records only.")
        if data.expected_disposal_date and data.expected_disposal_date < data.received_date:
            raise HTTPException(422, "Expected disposal date cannot precede the received date.")
        membership = intake_membership(actor)
        institution = db.get(Institution, data.institution_id)
        if not institution or not institution.synthetic:
            raise HTTPException(422, "Select a fictional institution by its exact identifier.")
        if membership.region_id and membership.region_id != institution.region_id:
            raise HTTPException(403, "Institution is outside this regional intake scope.")
        prepared = await prepare_files(files)
        fingerprint = hashlib.sha256(json.dumps({"payload": original, "evidence": [{"name": e.filename, "sha256": e.sha256} for e in prepared]}, sort_keys=True, ensure_ascii=False).encode()).hexdigest()
        prior = db.scalar(select(IntakeRequest).where(IntakeRequest.user_id == actor.user.id, IntakeRequest.request_key == request_key))
        if prior:
            if prior.fingerprint != fingerprint:
                raise HTTPException(409, "This request key already belongs to different complaint content.")
            case = db.get(CaseRecord, prior.case_id)
            return serialize_case(db, actor, load_case(db, actor, case.public_id), detail=True)
        case = CaseRecord(id=new_id(), public_id="DEMO-" + secrets.token_hex(6).upper(), institution_id=institution.id,
            original_institution_text=original["original_institution_text"], received_at=datetime.combine(data.received_date, time(), INDIA).astimezone(timezone.utc),
            subject=data.subject, description=original["description"], category=data.category, facts=data.facts.model_dump(mode='json'),
            current_owner_id=actor.user.id, current_bureau_id=membership.bureau_id, next_action=data.next_action,
            due_at=datetime.combine(data.expected_disposal_date + timedelta(days=1), time(), INDIA).astimezone(timezone.utc) if data.expected_disposal_date else None)
        written = []
        try:
            db.add(case)
            db.flush()
            original_json = json.dumps(original, sort_keys=True, ensure_ascii=False).encode()
            db.add_all([OriginalSubmission(case_id=case.id, payload=original, sha256=hashlib.sha256(original_json).hexdigest()),
                Complainant(case_id=case.id, synthetic_token=data.complainant_token),
                Assignment(case_id=case.id, owner_id=actor.user.id, bureau_id=membership.bureau_id, assigned_by=actor.user.id, reason="Initial accountable intake owner"),
                WorkflowEvent(case_id=case.id, event_type="RECEIVED", actor_id=actor.user.id, reason="Original synthetic complaint and evidence recorded", before_version=0, after_version=1),
                WorkflowEvent(case_id=case.id, event_type="OWNER_ASSIGNED", actor_id=actor.user.id, reason="Intake officer remains accountable", before_version=1, after_version=1),
                IntakeRequest(user_id=actor.user.id, request_key=request_key, fingerprint=fingerprint, case_id=case.id),
                OutboxJob(case_id=case.id, dedup_key="evidence:" + case.id)])
            db.add(OutboxJob(case_id=case.id,kind='DOMAIN_CHANGED',dedup_key='domain:'+case.id+':1'))
            for evidence in prepared:
                storage_key, path = store(app.state.settings, evidence)
                written.append(path)
                db.add(Attachment(case_id=case.id, storage_key=storage_key, original_filename=evidence.filename,
                    detected_type=evidence.detected_type, size=len(evidence.content), sha256=evidence.sha256, created_by=actor.user.id))
            db.commit()
        except BaseException:
            db.rollback()
            for path in written:
                path.unlink(missing_ok=True)
            raise
        return serialize_case(db, actor, case, detail=True)

    @app.get("/api/officers")
    def officers(actor: Principal = Depends(principal), db: Session = Depends(get_db)):
        bureaus = [m.bureau_id for m in actor.memberships if m.role == "BUREAU_SUPERVISOR"]
        query = select(User, Membership).join(Membership, Membership.user_id == User.id).where(User.active.is_(True),
            Membership.role.in_(["RB_OFFICER", "PGRC_OFFICER", "REGIONAL_OFFICER"]), Membership.bureau_id.in_(bureaus))
        return [{"id": u.id, "name": u.display_name, "bureau": m.bureau_id} for u, m in db.execute(query)]

    @app.post("/api/cases/{public_id}/assignment")
    def assign(public_id: str, data: AssignmentInput, actor: Principal = Depends(mutation), db: Session = Depends(get_db)):
        case = load_case(db, actor, public_id)
        if not can_assign(actor, case):
            raise HTTPException(403, "Only the authorized bureau supervisor can reassign this case.")
        if case.version != data.expected_version:
            raise HTTPException(409, "The case changed. Reload the current record before assigning again.")
        target = db.get(User, data.owner_id)
        institution = db.get(Institution, case.institution_id)
        membership = db.scalar(select(Membership).where(Membership.user_id == data.owner_id,
            Membership.bureau_id == case.current_bureau_id,
            or_(Membership.region_id.is_(None), Membership.region_id == institution.region_id),
            Membership.role.in_(["RB_OFFICER", "PGRC_OFFICER", "REGIONAL_OFFICER"])))
        from .models import Transfer
        if db.scalar(select(Transfer.id).where(Transfer.case_id == case.id, Transfer.status == "PENDING")):
            raise HTTPException(409, "Cancel or resolve the pending transfer before reassignment.")
        if not target or not target.active or not membership or case.lifecycle == "DISPOSED":
            raise HTTPException(422, "Choose an active eligible officer in the current bureau and an active case.")
        if case.current_owner_id == target.id:
            raise HTTPException(422, "This officer already owns the case.")
        changed = db.execute(update(CaseRecord).where(CaseRecord.id == case.id, CaseRecord.version == data.expected_version).values(
            current_owner_id=target.id, lifecycle="ASSIGNED", version=data.expected_version + 1, last_action="Owner reassigned", last_action_at=now()).execution_options(synchronize_session=False))
        if changed.rowcount != 1:
            db.rollback()
            raise HTTPException(409, "The case changed. Reload the current record before assigning again.")
        when = now()
        db.execute(update(Assignment).where(Assignment.case_id == case.id, Assignment.effective_to.is_(None)).values(effective_to=when))
        db.add_all([Assignment(case_id=case.id, owner_id=target.id, bureau_id=case.current_bureau_id,
            assigned_by=actor.user.id, reason=data.reason, effective_from=when),
            WorkflowEvent(case_id=case.id, event_type="OWNER_REASSIGNED", actor_id=actor.user.id, reason=data.reason,
                before_version=data.expected_version, after_version=data.expected_version + 1, occurred_at=when)])
        db.commit()
        db.expire_all()
        return serialize_case(db, actor, load_case(db, actor, public_id), detail=True)

    @app.get("/api/attachments/{attachment_id}")
    def attachment(attachment_id: str, actor: Principal = Depends(principal), db: Session = Depends(get_db)):
        item = db.get(Attachment, attachment_id)
        case = db.get(CaseRecord, item.case_id) if item else None
        if not item or not case or not can_read(db, actor, case, "M") or not can_read(db, actor, case, "A"):
            raise HTTPException(404, "Evidence not found or not available in your scope.")
        path = private_path(app.state.settings, item.storage_key)
        if not path.is_file():
            raise HTTPException(503, "Stored evidence is unavailable. The original record has been retained.")
        return FileResponse(path, media_type=item.detected_type, filename=item.original_filename, content_disposition_type="attachment")

    from .workflows import register_workflows
    register_workflows(app, serialize_case)
    from .coordination import register_coordination
    register_coordination(app, serialize_case)
    from .matching import register_matching
    register_matching(app)
    from .scheduling import register_scheduling
    register_scheduling(app)
    from .reporting import register_reporting
    register_reporting(app)
    from .demo import register_demo
    register_demo(app)
    from .workspace import register_workspace
    register_workspace(app, serialize_case)
    return app
