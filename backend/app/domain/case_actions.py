"""Decide a case transition. Identity, relationships and coordination are not case state."""
from dataclasses import dataclass
from datetime import datetime
from typing import Any


class RuleViolation(ValueError):
    pass


@dataclass(frozen=True)
class CaseState:
    lifecycle: str
    received_at: datetime
    due_version: int
    escalation_level: int
    information_received: bool = False
    pending_transfer: bool = False
    evidence_authorised: bool = True


@dataclass(frozen=True)
class ActionCommand:
    action: str
    expected_version: int
    reason: str
    text: str = ''
    next_action: str = ''
    due_at: datetime | None = None
    evidence_ids: tuple[str, ...] = ()
    facts: dict[str, Any] | None = None


@dataclass(frozen=True)
class ActionDecision:
    changes: dict[str, Any]
    record_resolution: bool = False


def decide_action(state: CaseState, command: ActionCommand) -> ActionDecision:
    a, active = command.action, state.lifecycle != 'DISPOSED'
    changes: dict[str, Any] = {}
    if a == 'REVIEW':
        if state.lifecycle not in {'RECEIVED', 'ASSIGNED', 'AWAITING_INFORMATION'}:
            raise RuleViolation('Review cannot start from this state.')
        if state.lifecycle == 'AWAITING_INFORMATION' and not state.information_received:
            raise RuleViolation('Record the latest requested information before resuming review.')
        changes['lifecycle'] = 'UNDER_REVIEW'
    elif a == 'REQUEST_INFORMATION':
        if state.lifecycle != 'UNDER_REVIEW' or len(command.text) < 5 or not command.next_action:
            raise RuleViolation('Review state, information needed and next action are required.')
        changes.update(lifecycle='AWAITING_INFORMATION', next_action=command.next_action)
    elif a in {'INFORMATION', 'AMEND'}:
        if len(command.text) < 10:
            raise RuleViolation('Record at least ten characters of information; originals remain preserved.')
        if a == 'INFORMATION' and state.lifecycle != 'AWAITING_INFORMATION':
            raise RuleViolation('There is no pending information request.')
        if a == 'AMEND':
            changes['description'] = command.text
            if command.facts is not None:
                changes['facts'] = command.facts
    elif a == 'NEXT_ACTION':
        if not active or len(command.next_action) < 3:
            raise RuleViolation('An active case and next action are required.')
        changes['next_action'] = command.next_action
    elif a == 'DEADLINE':
        if not active or (command.due_at and (command.due_at.tzinfo is None or command.due_at < state.received_at)):
            raise RuleViolation('Use an explicit UTC-offset deadline after receipt, or clear the deadline.')
        changes.update(due_at=command.due_at, due_version=state.due_version + 1)
    elif a == 'ESCALATE':
        if not active:
            raise RuleViolation('Disposed cases cannot be escalated.')
        changes['escalation_level'] = state.escalation_level + 1
    elif a == 'DISPOSE':
        if not active or len(command.text) < 10 or state.pending_transfer:
            raise RuleViolation('Disposal needs a resolution and no pending transfer.')
        if not state.evidence_authorised:
            raise RuleViolation('Resolution evidence must be authorised and belong to this case.')
        changes['lifecycle'] = 'DISPOSED'
    elif a == 'REOPEN':
        if active or len(command.next_action) < 3:
            raise RuleViolation('Reopening requires a disposed case and next action.')
        changes.update(lifecycle='UNDER_REVIEW', next_action=command.next_action)
    else:
        raise RuleViolation('Unknown case action.')
    return ActionDecision(changes, record_resolution=a == 'DISPOSE')
