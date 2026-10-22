import uuid
from datetime import datetime
from enum import Enum, StrEnum
from typing import Any

from sqlalchemy import DateTime, func
from sqlalchemy import Enum as SqlEnum
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.orm import Mapped, mapped_column

from ml.serving.feature_store.models import Base


class JobKind(StrEnum):
    REORDER = "reorder"
    SPLIT = "split"
    RECOMMEND = "recommend"


class JobStatus(StrEnum):
    QUEUED = "queued"
    RUNNING = "running"
    SUCCEEDED = "succeeded"
    FAILED = "failed"


class JobPhase(StrEnum):
    RESOLVING = "resolving"
    COMPUTING = "computing"


def _enum_values(enum_class: type[Enum]) -> list[str]:
    return [str(member.value) for member in enum_class]


class Job(Base):
    __tablename__ = "jobs"

    id: Mapped[uuid.UUID] = mapped_column(primary_key=True, default=uuid.uuid4)
    user_id: Mapped[str] = mapped_column(index=True)
    kind: Mapped[JobKind] = mapped_column(
        SqlEnum(JobKind, native_enum=False, length=16, values_callable=_enum_values)
    )
    payload: Mapped[dict[str, Any]] = mapped_column(JSONB)
    status: Mapped[JobStatus] = mapped_column(
        SqlEnum(JobStatus, native_enum=False, length=16, values_callable=_enum_values),
        default=JobStatus.QUEUED,
    )
    phase: Mapped[JobPhase | None] = mapped_column(
        SqlEnum(JobPhase, native_enum=False, length=16, values_callable=_enum_values)
    )
    total: Mapped[int] = mapped_column(default=0)
    done: Mapped[int] = mapped_column(default=0)
    result: Mapped[dict[str, Any] | None] = mapped_column(JSONB(none_as_null=True))
    error: Mapped[str | None]
    attempts: Mapped[int] = mapped_column(default=0)
    locked_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), onupdate=func.now()
    )
