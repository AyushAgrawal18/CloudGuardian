
from sqlalchemy.orm import Session
from sqlalchemy import select

from backend.app.models.logs import LogEvent, LogTemplate
from backend.app.models.host import Host
from backend.app.services.log_parser import LogParser
import logging

logger = logging.getLogger(__name__)


class LogService:
    def __init__(self):
        self.parser = LogParser()

    def ingest_log(
        self,
        db: Session,
        host_id: str,
        timestamp,
        severity: str,
        message: str,
    ) -> LogEvent:
        # Verify that the host exists and is active.
        host = db.scalar(
            select(Host).where(Host.host_id == host_id)
        )

        if host is None:
            raise ValueError("Host not found")

        if host.status.value.lower() != "active":
            raise ValueError("Host is not active")

        # Update Drain3 in-memory state without persisting it yet.
        parsed = self.parser.parse(
            message,
            host_id=host_id,
        )

        try:
            # Find or create the corresponding template.
            template = db.scalar(
                select(LogTemplate).where(
                    LogTemplate.host_id == host_id,
                    LogTemplate.cluster_id == parsed["cluster_id"],
                )
            )

            if template is None:
                template = LogTemplate(
                    host_id=host_id,
                    cluster_id=parsed["cluster_id"],
                    template=parsed["template"],
                    cluster_size=parsed["cluster_size"],
                )
                db.add(template)
                db.flush()
            else:
                template.template = parsed["template"]
                template.cluster_size = parsed["cluster_size"]

            # Store the individual log event.
            event = LogEvent(
                host_id=host_id,
                template_id=template.id,
                timestamp=timestamp,
                severity=severity,
                message=parsed["message"],
            )

            db.add(event)
            db.flush()

            # Commit the database transaction first.
            db.commit()

        except Exception:
            db.rollback()

            # Discard uncommitted Drain3 changes.
            self.parser.discard_miner(host_id)
            raise

        # Persist Drain3 state only after database commit succeeds.
        try:
            self.parser.save_state(host_id)
        except Exception:
            logger.exception(
                "Log was committed, but Drain3 state persistence failed "
                "for host %s. The in-memory miner is retained for retry.",
                host_id,
            )

        return event
