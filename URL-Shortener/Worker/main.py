import asyncio
import uuid
from datetime import datetime
from threading import Thread
from typing import Optional

from celery import Celery
from celery.signals import worker_process_init, worker_process_shutdown
from sqlalchemy import Column, DateTime, ForeignKey, Integer
from sqlalchemy.dialects.postgresql import TEXT, UUID
from sqlalchemy.ext.asyncio import AsyncEngine, AsyncSession, create_async_engine
from sqlmodel import Field, SQLModel, String, text

# --- Globals for the Worker Process ---
engine: Optional[AsyncEngine] = None
loop: Optional[asyncio.AbstractEventLoop] = None
loop_thread: Optional[Thread] = None


def start_event_loop(loop_to_run: asyncio.AbstractEventLoop):
    """Function to run the event loop in a separate thread."""
    asyncio.set_event_loop(loop_to_run)
    loop_to_run.run_forever()


@worker_process_init.connect
def init_worker(**kwargs):
    """
    Called when a worker process starts.
    - Creates a new event loop.
    - Starts the loop in a dedicated background thread.
    - Creates the async database engine for this process.
    """
    global engine, loop, loop_thread
    print("Initializing worker process...")

    loop = asyncio.new_event_loop()
    loop_thread = Thread(target=start_event_loop, args=(loop,), daemon=True)
    loop_thread.start()

    engine = create_async_engine(
        url="postgresql+asyncpg://postgres:postgres@postgres:5432/mydb",
        echo=True,
        pool_size=10,
        max_overflow=20,
        pool_timeout=30,
        pool_recycle=1800,
        pool_pre_ping=True,
    )
    print("Worker process initialized.")


@worker_process_shutdown.connect
def shutdown_worker(**kwargs):
    """
    Called when a worker process shuts down.
    - Stops the event loop.
    - Joins the thread.
    - Disposes of the database engine's connection pool.
    """
    global engine, loop, loop_thread
    if loop and loop_thread and engine:
        print("Shutting down worker process...")
        loop.call_soon_threadsafe(loop.stop)
        loop_thread.join()

        async def dispose_engine():
            await engine.dispose()

        loop.run_until_complete(dispose_engine())
        loop.close()
        print("Worker process shut down.")

# --- SQL Models (Unchanged) ---
class ShortURL(SQLModel, table=True):
    # ... model definition remains the same
    id: uuid.UUID = Field(
        sa_column=Column(
            UUID(as_uuid=True),
            server_default=text("uuidv7()"),
            primary_key=True,
            nullable=False,
            index=True,
        )
    )

    original_url: str = Field(
        sa_column=Column(
            TEXT,
            nullable=False,
            comment="Original URL to redirect to",
        )
    )

    short_code: str = Field(
        sa_column=Column(
            String(12),
            nullable=False,
            unique=True,
            index=True,
            comment="Generated slug (e.g. aB78xZ)",
        ),
    )

    user_id: Optional[uuid.UUID] = Field(
        default=None,
        sa_column=Column(
            UUID(as_uuid=True),
            ForeignKey("user.id"),
            nullable=True,
            index=True,
            comment="FK to User.id, nullable for anonymous links",
        ),
    )

    visit_count: int = Field(
        default=0,
        sa_column=Column(
            Integer,
            nullable=False,
            server_default=text("0"),
            comment="Number of times the short URL was visited",
        ),
    )

    created_at: datetime = Field(
        sa_column=Column(
            DateTime(timezone=True),
            nullable=False,
            server_default=text("CURRENT_TIMESTAMP"),
            comment="Record creation timestamp",
        )
    )

    expires_at: Optional[datetime] = Field(
        default=None,
        sa_column=Column(
            DateTime(timezone=True),
            nullable=True,
            comment="Optional expiration timestamp",
        ),
    )


class Visit(SQLModel, table=True):
    # ... model definition remains the same
    id: uuid.UUID = Field(
        sa_column=Column(
            UUID(as_uuid=True),
            server_default=text("uuidv7()"),
            primary_key=True,
            nullable=False,
            index=True,
        )
    )

    short_url_id: uuid.UUID = Field(
        sa_column=Column(
            UUID(as_uuid=True),
            ForeignKey("shorturl.id"),
            nullable=False,
            index=True,
            comment="FK to ShortURL.id",
        )
    )

    visited_at: datetime = Field(
        sa_column=Column(
            DateTime(timezone=True),
            nullable=False,
            server_default=text("CURRENT_TIMESTAMP"),
            comment="Timestamp of the visit",
        )
    )

    ip_address: str = Field(
        sa_column=Column(
            String(45),
            nullable=False,
            comment="Visitor IP address (v4 or v6)",
        )
    )

    user_agent: str = Field(
        sa_column=Column(
            String(512),
            nullable=False,
            comment="User-Agent header text",
        )
    )


# --- Celery App and Task ---
app = Celery(
    "tasks", broker="redis://dragonfly:6379/0", backend="redis://dragonfly:6379/0"
)
app.conf.broker_connection_retry_on_startup = True
app.conf.task_serializer = "json"
app.conf.result_serializer = "json"
app.conf.accept_content = ["json"]
app.conf.enable_utc = True


async def process_visit(load: dict):
    """The actual async logic for processing the visit."""
    if engine is None:
        raise RuntimeError("Database engine not initialized in this worker process.")

    async with AsyncSession(engine) as session:
        visit = Visit(
            short_url_id=load.get("short_url_id"),
            ip_address=load.get("ip_address"),
            user_agent=load.get("user_agent"),
        )
        session.add(visit)
        await session.commit()
        
        # *** THE FIX IS HERE ***
        # Eagerly load the database-generated values before the session closes.
        await session.refresh(visit)
        
    # Now that the session is closed, accessing visit.short_url_id is safe
    # because the data was pre-loaded by session.refresh().
    print(f"Successfully processed visit for short_url_id: {visit.short_url_id}")


@app.task(name="test")
def prepare_report(load: dict) -> dict:
    """
    Synchronous entrypoint that submits the async work to the
    worker's persistent event loop.
    """
    if loop is None:
        raise RuntimeError("Event loop not available in this worker process.")

    future = asyncio.run_coroutine_threadsafe(process_visit(load), loop)
    future.result()  # Wait for the async function to complete and raise any exceptions
    return load