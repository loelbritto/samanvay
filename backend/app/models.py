from datetime import datetime, timezone
import uuid
from sqlalchemy import Boolean, CheckConstraint, DateTime, ForeignKey, Index, Integer, JSON, String, Text, UniqueConstraint, text
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column


def now():
    return datetime.now(timezone.utc)


def new_id():
    return str(uuid.uuid4())


class Base(DeclarativeBase):
    pass


class Region(Base):
    __tablename__ = "regions"
    id: Mapped[str] = mapped_column(String(50), primary_key=True)
    name: Mapped[str] = mapped_column(String(120))


class Bureau(Base):
    __tablename__ = "bureaus"
    id: Mapped[str] = mapped_column(String(30), primary_key=True)
    name: Mapped[str] = mapped_column(String(160))


class User(Base):
    __tablename__ = "users"
    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=new_id)
    username: Mapped[str] = mapped_column(String(120), unique=True)
    display_name: Mapped[str] = mapped_column(String(120))
    password_hash: Mapped[str] = mapped_column(Text)
    active: Mapped[bool] = mapped_column(Boolean, default=True)
    synthetic: Mapped[bool] = mapped_column(Boolean, default=True)


class Membership(Base):
    __tablename__ = "role_memberships"
    __table_args__ = (UniqueConstraint("user_id", "role", "bureau_id"),)
    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=new_id)
    user_id: Mapped[str] = mapped_column(ForeignKey("users.id"))
    role: Mapped[str] = mapped_column(String(40))
    bureau_id: Mapped[str | None] = mapped_column(ForeignKey("bureaus.id"), nullable=True)
    region_id: Mapped[str | None] = mapped_column(ForeignKey("regions.id"), nullable=True)


class Institution(Base):
    __tablename__ = "institutions"
    id: Mapped[str] = mapped_column(String(50), primary_key=True)
    name: Mapped[str] = mapped_column(String(180))
    city: Mapped[str] = mapped_column(String(80))
    region_id: Mapped[str] = mapped_column(ForeignKey("regions.id"))
    synthetic: Mapped[bool] = mapped_column(Boolean, default=True)
    version: Mapped[int] = mapped_column(Integer, default=1)


class InstitutionAlias(Base):
    __tablename__ = "institution_aliases"
    __table_args__ = (UniqueConstraint("institution_id", "alias"),)
    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=new_id)
    institution_id: Mapped[str] = mapped_column(ForeignKey("institutions.id"))
    alias: Mapped[str] = mapped_column(String(180))
    provenance: Mapped[str] = mapped_column(Text)
    confirmed_by: Mapped[str] = mapped_column(ForeignKey("users.id"))
    confirmed_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=now)
    version: Mapped[int] = mapped_column(Integer, default=1)


class CaseRecord(Base):
    __tablename__ = "cases"
    __table_args__ = (CheckConstraint("version >= 1"), CheckConstraint("lifecycle IN ('RECEIVED','ASSIGNED','UNDER_REVIEW','AWAITING_INFORMATION','DISPOSED')"))
    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=new_id)
    public_id: Mapped[str] = mapped_column(String(50), unique=True, index=True)
    institution_id: Mapped[str] = mapped_column(ForeignKey("institutions.id"), index=True)
    original_institution_text: Mapped[str] = mapped_column(Text)
    identity_status: Mapped[str] = mapped_column(String(30), default="CONFIRMED_SELECTION")
    received_at: Mapped[datetime] = mapped_column(DateTime(timezone=True))
    subject: Mapped[str] = mapped_column(String(200))
    description: Mapped[str] = mapped_column(Text)
    category: Mapped[str] = mapped_column(String(80))
    lifecycle: Mapped[str] = mapped_column(String(40), default="RECEIVED")
    current_owner_id: Mapped[str] = mapped_column(ForeignKey("users.id"), index=True)
    current_bureau_id: Mapped[str] = mapped_column(ForeignKey("bureaus.id"), index=True)
    last_action: Mapped[str] = mapped_column(String(120), default="Complaint received")
    last_action_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=now)
    next_action: Mapped[str] = mapped_column(String(500))
    due_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    due_version: Mapped[int] = mapped_column(Integer, default=1)
    escalation_level: Mapped[int] = mapped_column(Integer, default=0)
    version: Mapped[int] = mapped_column(Integer, default=1)
    synthetic: Mapped[bool] = mapped_column(Boolean, default=True)
    facts: Mapped[dict] = mapped_column(JSON, default=dict, server_default="{}")
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=now)


class Complainant(Base):
    __tablename__ = "complainants"
    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=new_id)
    case_id: Mapped[str] = mapped_column(ForeignKey("cases.id"), unique=True)
    synthetic_token: Mapped[str] = mapped_column(String(80))
    contact: Mapped[str | None] = mapped_column(String(200), nullable=True)


class OriginalSubmission(Base):
    __tablename__ = "original_submissions"
    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=new_id)
    case_id: Mapped[str] = mapped_column(ForeignKey("cases.id"), unique=True)
    payload: Mapped[dict] = mapped_column(JSON)
    sha256: Mapped[str] = mapped_column(String(64))
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=now)


class Assignment(Base):
    __tablename__ = "assignment_history"
    __table_args__ = (Index('uq_current_assignment','case_id',unique=True,sqlite_where=text('effective_to IS NULL')),)
    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=new_id)
    case_id: Mapped[str] = mapped_column(ForeignKey("cases.id"), index=True)
    owner_id: Mapped[str] = mapped_column(ForeignKey("users.id"))
    bureau_id: Mapped[str] = mapped_column(ForeignKey("bureaus.id"))
    assigned_by: Mapped[str] = mapped_column(ForeignKey("users.id"))
    reason: Mapped[str] = mapped_column(Text)
    effective_from: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=now)
    effective_to: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)


class WorkflowEvent(Base):
    __tablename__ = "workflow_events"
    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=new_id)
    case_id: Mapped[str] = mapped_column(ForeignKey("cases.id"), index=True)
    event_type: Mapped[str] = mapped_column(String(80))
    actor_id: Mapped[str | None] = mapped_column(ForeignKey("users.id"), nullable=True)
    reason: Mapped[str] = mapped_column(Text)
    before_version: Mapped[int] = mapped_column(Integer)
    after_version: Mapped[int] = mapped_column(Integer)
    occurred_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=now)


class Attachment(Base):
    __tablename__ = "attachments"
    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=new_id)
    case_id: Mapped[str] = mapped_column(ForeignKey("cases.id"), index=True)
    storage_key: Mapped[str] = mapped_column(String(80), unique=True)
    original_filename: Mapped[str] = mapped_column(String(160))
    detected_type: Mapped[str] = mapped_column(String(80))
    size: Mapped[int] = mapped_column(Integer)
    sha256: Mapped[str] = mapped_column(String(64))
    created_by: Mapped[str] = mapped_column(ForeignKey("users.id"))
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=now)
    verified_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)


class AccessGrant(Base):
    __tablename__ = "access_grants"
    __table_args__ = (UniqueConstraint("user_id", "case_id", "data_class"),)
    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=new_id)
    user_id: Mapped[str] = mapped_column(ForeignKey("users.id"))
    case_id: Mapped[str] = mapped_column(ForeignKey("cases.id"))
    data_class: Mapped[str] = mapped_column(String(10))
    reason: Mapped[str] = mapped_column(Text)
    granted_by: Mapped[str] = mapped_column(ForeignKey("users.id"))
    expires_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)


class LoginSession(Base):
    __tablename__ = "login_sessions"
    token_hash: Mapped[str] = mapped_column(String(64), primary_key=True)
    user_id: Mapped[str] = mapped_column(ForeignKey("users.id"))
    csrf_token: Mapped[str] = mapped_column(String(80))
    expires_at: Mapped[datetime] = mapped_column(DateTime(timezone=True))
    revoked: Mapped[bool] = mapped_column(Boolean, default=False)


class LoginAttempt(Base):
    __tablename__ = "login_attempts"
    key: Mapped[str] = mapped_column(String(64), primary_key=True)
    count: Mapped[int] = mapped_column(Integer, default=0)
    window_start: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=now)


class IntakeRequest(Base):
    __tablename__ = "intake_requests"
    __table_args__ = (UniqueConstraint("user_id", "request_key"),)
    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=new_id)
    user_id: Mapped[str] = mapped_column(ForeignKey("users.id"))
    request_key: Mapped[str] = mapped_column(String(80))
    fingerprint: Mapped[str] = mapped_column(String(64))
    case_id: Mapped[str] = mapped_column(ForeignKey("cases.id"))


class OutboxJob(Base):
    __tablename__ = "outbox_jobs"
    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=new_id)
    case_id: Mapped[str] = mapped_column(ForeignKey("cases.id"))
    kind: Mapped[str] = mapped_column(String(80), default="EVIDENCE_INTEGRITY")
    dedup_key: Mapped[str] = mapped_column(String(100), unique=True)
    status: Mapped[str] = mapped_column(String(30), default="PENDING")
    attempts: Mapped[int] = mapped_column(Integer, default=0)
    lease_until: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    available_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=now)
    completed_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    error_code: Mapped[str | None] = mapped_column(String(80), nullable=True)


class CapabilityGrant(Base):
    __tablename__ = "capability_grants"
    __table_args__ = (UniqueConstraint("user_id", "capability", "scope_type", "scope_id"),)
    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=new_id)
    user_id: Mapped[str] = mapped_column(ForeignKey("users.id"))
    capability: Mapped[str] = mapped_column(String(40))
    scope_type: Mapped[str] = mapped_column(String(30))
    scope_id: Mapped[str] = mapped_column(String(50))
    reason: Mapped[str] = mapped_column(Text)


class Transfer(Base):
    __tablename__ = "transfers"
    __table_args__ = (CheckConstraint("status IN ('PENDING','ACCEPTED','REJECTED','CANCELLED','EXPIRED')"),
        Index('uq_pending_transfer','case_id',unique=True,sqlite_where=text("status = 'PENDING'")))
    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=new_id)
    case_id: Mapped[str] = mapped_column(ForeignKey("cases.id"), index=True)
    source_owner_id: Mapped[str] = mapped_column(ForeignKey("users.id"))
    source_bureau_id: Mapped[str] = mapped_column(ForeignKey("bureaus.id"))
    requester_id: Mapped[str] = mapped_column(ForeignKey("users.id"))
    target_owner_id: Mapped[str] = mapped_column(ForeignKey("users.id"))
    target_bureau_id: Mapped[str] = mapped_column(ForeignKey("bureaus.id"))
    status: Mapped[str] = mapped_column(String(20), default="PENDING")
    reason: Mapped[str] = mapped_column(Text)
    response_reason: Mapped[str | None] = mapped_column(Text, nullable=True)
    expires_at: Mapped[datetime] = mapped_column(DateTime(timezone=True))
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=now)
    responded_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    version: Mapped[int] = mapped_column(Integer, default=1)


class CaseAction(Base):
    __tablename__ = "case_actions"
    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=new_id)
    case_id: Mapped[str] = mapped_column(ForeignKey("cases.id"), index=True)
    kind: Mapped[str] = mapped_column(String(40))
    payload: Mapped[dict] = mapped_column(JSON)
    actor_id: Mapped[str] = mapped_column(ForeignKey("users.id"))
    case_version: Mapped[int] = mapped_column(Integer)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=now)


class Resolution(Base):
    __tablename__ = "resolutions"
    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=new_id)
    case_id: Mapped[str] = mapped_column(ForeignKey("cases.id"), index=True)
    resolution: Mapped[str] = mapped_column(Text)
    evidence_ids: Mapped[list] = mapped_column(JSON)
    actor_id: Mapped[str] = mapped_column(ForeignKey("users.id"))
    disposed_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=now)
    case_version: Mapped[int] = mapped_column(Integer)


class IdentityDecision(Base):
    __tablename__ = "identity_decisions"
    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=new_id)
    case_id: Mapped[str] = mapped_column(ForeignKey("cases.id"), index=True)
    previous_institution_id: Mapped[str] = mapped_column(ForeignKey("institutions.id"))
    institution_id: Mapped[str] = mapped_column(ForeignKey("institutions.id"))
    original_text: Mapped[str] = mapped_column(Text)
    reason: Mapped[str] = mapped_column(Text)
    provenance: Mapped[str] = mapped_column(Text)
    actor_id: Mapped[str] = mapped_column(ForeignKey("users.id"))
    case_version: Mapped[int] = mapped_column(Integer)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=now)


class CoordinationGroup(Base):
    __tablename__ = "coordination_groups"
    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=new_id)
    institution_id: Mapped[str] = mapped_column(ForeignKey("institutions.id"), unique=True)
    condition_active: Mapped[bool] = mapped_column(Boolean, default=True)
    state: Mapped[str] = mapped_column(String(30), default="REVIEW_REQUIRED")
    lead_id: Mapped[str | None] = mapped_column(ForeignKey("users.id"), nullable=True)
    lead_bureau_id: Mapped[str | None] = mapped_column(ForeignKey("bureaus.id"), nullable=True)
    next_action: Mapped[str] = mapped_column(String(500), default="Authorised coordinator to review concurrent bureau activity")
    due_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    version: Mapped[int] = mapped_column(Integer, default=1)
    source_fingerprint: Mapped[str] = mapped_column(String(64), default="")
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=now)


class GroupParticipant(Base):
    __tablename__ = "coordination_participants"
    __table_args__ = (UniqueConstraint("group_id", "case_id"),)
    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=new_id)
    group_id: Mapped[str] = mapped_column(ForeignKey("coordination_groups.id"))
    case_id: Mapped[str] = mapped_column(ForeignKey("cases.id"))
    joined_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=now)


class GroupReview(Base):
    __tablename__ = "coordination_reviews"
    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=new_id)
    group_id: Mapped[str] = mapped_column(ForeignKey("coordination_groups.id"), index=True)
    actor_id: Mapped[str | None] = mapped_column(ForeignKey("users.id"), nullable=True)
    action: Mapped[str] = mapped_column(String(40))
    reason: Mapped[str] = mapped_column(Text)
    payload: Mapped[dict] = mapped_column(JSON)
    version: Mapped[int] = mapped_column(Integer)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=now)


class RelationshipSuggestion(Base):
    __tablename__ = "relationship_suggestions"
    __table_args__ = (UniqueConstraint("left_id", "right_id", "fingerprint", "method"),)
    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=new_id)
    left_id: Mapped[str] = mapped_column(ForeignKey("cases.id"), index=True)
    right_id: Mapped[str] = mapped_column(ForeignKey("cases.id"), index=True)
    left_version: Mapped[int] = mapped_column(Integer)
    right_version: Mapped[int] = mapped_column(Integer)
    fingerprint: Mapped[str] = mapped_column(String(64))
    method: Mapped[str] = mapped_column(String(100))
    proposed_label: Mapped[str] = mapped_column(String(20), default="UNKNOWN")
    evidence: Mapped[dict] = mapped_column(JSON)
    previous_id: Mapped[str | None] = mapped_column(ForeignKey("relationship_suggestions.id"), nullable=True)
    version: Mapped[int] = mapped_column(Integer, default=1)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=now)


class RelationshipDecision(Base):
    __tablename__ = "relationship_decisions"
    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=new_id)
    suggestion_id: Mapped[str] = mapped_column(ForeignKey("relationship_suggestions.id"), index=True)
    action: Mapped[str] = mapped_column(String(20))
    label: Mapped[str | None] = mapped_column(String(20), nullable=True)
    reason: Mapped[str] = mapped_column(Text)
    actor_id: Mapped[str] = mapped_column(ForeignKey("users.id"))
    suggestion_version: Mapped[int] = mapped_column(Integer)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=now)


class EmbeddingCache(Base):
    __tablename__ = "local_vector_cache"
    key: Mapped[str] = mapped_column(String(64), primary_key=True)
    model: Mapped[str] = mapped_column(String(100))
    vector: Mapped[list] = mapped_column(JSON)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=now)


class DemoContext(Base):
    __tablename__ = "demo_context"
    id: Mapped[str] = mapped_column(String(80), primary_key=True)
    synthetic: Mapped[bool] = mapped_column(Boolean, default=True)
    clock_offset_seconds: Mapped[int] = mapped_column(Integer, default=0)
    clock_version: Mapped[int] = mapped_column(Integer, default=1)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=now)


class AdministrativePolicy(Base):
    __tablename__ = "administrative_policies"
    id: Mapped[str] = mapped_column(String(40), primary_key=True)
    version: Mapped[int] = mapped_column(Integer, default=1)
    approaching_hours: Mapped[int] = mapped_column(Integer, default=48)
    escalation_hours: Mapped[int] = mapped_column(Integer, default=24)
    auto_escalate: Mapped[bool] = mapped_column(Boolean, default=True)
    label: Mapped[str] = mapped_column(String(200), default="Illustrative synthetic policy; not official AICTE deadlines")


class AdministrativeEvent(Base):
    __tablename__ = "administrative_events"
    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=new_id)
    actor_id: Mapped[str | None] = mapped_column(ForeignKey("users.id"), nullable=True)
    kind: Mapped[str] = mapped_column(String(40))
    reason: Mapped[str] = mapped_column(Text)
    payload: Mapped[dict] = mapped_column(JSON)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=now)


class SchedulerEffect(Base):
    __tablename__ = "scheduler_effects"
    key: Mapped[str] = mapped_column(String(200), primary_key=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=now)


class Notification(Base):
    __tablename__ = "notifications"
    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=new_id)
    user_id: Mapped[str] = mapped_column(ForeignKey("users.id"), index=True)
    case_id: Mapped[str | None] = mapped_column(ForeignKey("cases.id"), nullable=True)
    group_id: Mapped[str | None] = mapped_column(ForeignKey("coordination_groups.id"), nullable=True)
    suggestion_id: Mapped[str | None] = mapped_column(ForeignKey("relationship_suggestions.id"), nullable=True)
    transfer_id: Mapped[str | None] = mapped_column(ForeignKey("transfers.id"), nullable=True)
    kind: Mapped[str] = mapped_column(String(40))
    title: Mapped[str] = mapped_column(String(200))
    dedup_key: Mapped[str] = mapped_column(String(250), unique=True)
    policy_version: Mapped[int] = mapped_column(Integer)
    state: Mapped[str] = mapped_column(String(30), default="PENDING")
    attempts: Mapped[int] = mapped_column(Integer, default=0)
    available_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=now)
    lease_until: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    delivered_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    acknowledged_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=now)


class SecurityAudit(Base):
    __tablename__ = "security_audit"
    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=new_id)
    user_id: Mapped[str | None] = mapped_column(ForeignKey("users.id"), nullable=True)
    operation: Mapped[str] = mapped_column(String(60))
    resource_hash: Mapped[str] = mapped_column(String(64))
    method: Mapped[str] = mapped_column(String(10))
    status: Mapped[int] = mapped_column(Integer)
    occurred_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=now)
