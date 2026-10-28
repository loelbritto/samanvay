from typing import Protocol
from ..domain.case_actions import ActionCommand, ActionDecision, CaseState, decide_action


class CaseActionRepository(Protocol):
    """An authorised case snapshot and one atomic, version-checked write."""
    def snapshot(self, command: ActionCommand) -> CaseState: ...
    def commit(self, command: ActionCommand, decision: ActionDecision) -> None: ...


def execute_case_action(repository: CaseActionRepository, command: ActionCommand) -> None:
    decision = decide_action(repository.snapshot(command), command)
    repository.commit(command, decision)
