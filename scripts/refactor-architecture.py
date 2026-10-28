"""One-time, explicit source migration for the 2026-10-28 architecture pass."""
from pathlib import Path

root = Path(__file__).resolve().parents[1]
path = root / 'backend/app/workflows.py'
source = path.read_text(encoding='utf-8')
start = source.index('        values = {}\n', source.index('    def action('))
end = source.index('        return serialize(', start)
source = source[:start] + '''        from .application.case_actions import execute_case_action
        from .domain.case_actions import ActionCommand, RuleViolation
        from .infrastructure.case_actions import SqlCaseActionRepository
        command = ActionCommand(**{**data.model_dump(),
            'evidence_ids': tuple(data.evidence_ids),
            'facts': data.facts.model_dump(mode='json') if data.facts is not None else None})
        try:
            execute_case_action(SqlCaseActionRepository(db, actor, case), command)
        except RuleViolation as error:
            raise HTTPException(422, str(error)) from error
''' + source[end:]
source = source.replace('        active = case.lifecycle != "DISPOSED"\n', '')
path.write_text(source, encoding='utf-8')

path = root / 'backend/app/api.py'
source = path.read_text(encoding='utf-8')
start, end = source.index('def serialize_case('), source.index('def create_app(')
serializer = '''"""Role-aware case response projection shared by HTTP adapters."""
from datetime import timedelta
from zoneinfo import ZoneInfo
from sqlalchemy import select
from .auth import utc
from .models import Institution, User, OriginalSubmission, Complainant, Attachment, WorkflowEvent, Assignment
from .policies import can_read, can_assign

INDIA = ZoneInfo('Asia/Kolkata')


''' + source[start:end]
(root / 'backend/app/case_views.py').write_text(serializer, encoding='utf-8')
source = source[:start] + 'from .case_views import serialize_case\n\n\n' + source[end:]
source = source.replace('    return app\n', '    from .workspace import register_workspace\n    register_workspace(app, serialize_case)\n    return app\n')
path.write_text(source, encoding='utf-8')
print('Extracted case transition rules, transactional action use case, response projection; registered scoped queue.')
