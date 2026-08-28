import os
from pathlib import Path
import subprocess
import sys
from uuid import uuid4

import psycopg
from psycopg import sql
from sqlalchemy.engine import make_url

from app.core.config import get_settings


API_DIRECTORY = Path(__file__).resolve().parents[1]


def test_alembic_upgrade_against_clean_database() -> None:
    settings = get_settings()
    application_url = make_url(settings.database_url)
    schema_name = f"carboniq_migration_test_{uuid4().hex}"
    connection_url = application_url.set(drivername="postgresql").render_as_string(
        hide_password=False
    )
    test_url = application_url.update_query_dict(
        {"options": f"-csearch_path={schema_name}"}
    ).render_as_string(
        hide_password=False,
    )

    with psycopg.connect(connection_url, autocommit=True) as connection:
        connection.execute(
            sql.SQL("CREATE SCHEMA {}").format(sql.Identifier(schema_name))
        )

    try:
        environment = os.environ.copy()
        environment["DATABASE_URL"] = test_url
        subprocess.run(
            [sys.executable, "-m", "alembic", "upgrade", "head"],
            cwd=API_DIRECTORY,
            env=environment,
            check=True,
            capture_output=True,
            text=True,
        )

        with psycopg.connect(connection_url) as connection:
            revision = connection.execute(
                sql.SQL("SELECT version_num FROM {}.alembic_version").format(
                    sql.Identifier(schema_name)
                )
            ).fetchone()

        assert revision == ("5316ace179ad",)
    finally:
        with psycopg.connect(connection_url, autocommit=True) as connection:
            connection.execute(
                sql.SQL("DROP SCHEMA IF EXISTS {} CASCADE").format(
                    sql.Identifier(schema_name)
                )
            )
