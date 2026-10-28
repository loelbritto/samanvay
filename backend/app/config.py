from dataclasses import dataclass
import os
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]


@dataclass(frozen=True)
class Settings:
    data_dir: Path
    environment: str = "demo"
    allowed_origins: tuple[str, ...] = ("http://127.0.0.1:5173", "http://localhost:5173", "http://127.0.0.1:5174", "http://localhost:5174", "http://127.0.0.1:8000", "http://127.0.0.1:8001")
    secure_cookie: bool = False
    session_hours: int = 8
    demo_controls: bool = False
    context_id: str = "local-synthetic"

    @property
    def cookie_name(self):
        import hashlib
        return 'samanvay_session' if self.context_id=='local-synthetic' else 'samanvay_demo_'+hashlib.sha256(self.context_id.encode()).hexdigest()[:20]

    @property
    def database_url(self):
        return "sqlite:///" + (self.data_dir / "samanvay.sqlite3").as_posix()

    @property
    def attachments_dir(self):
        return self.data_dir / "private-evidence"

    @classmethod
    def from_env(cls):
        env = os.getenv("SAMANVAY_ENV", "demo")
        if env not in {"demo", "test"}:
            raise RuntimeError("This local prototype supports only explicit synthetic demo/test environments.")
        return cls(Path(os.getenv("SAMANVAY_DATA_DIR", str(ROOT / ".local-data"))).resolve(), env,
            demo_controls=os.getenv('SAMANVAY_ENABLE_DEMO_CONTROLS')=='1',context_id=os.getenv('SAMANVAY_CONTEXT_ID','local-synthetic'))
