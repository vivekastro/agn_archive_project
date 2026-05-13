from sqlalchemy import text

from app.database import engine, Base
from app import models


def main() -> None:
    with engine.begin() as conn:
        conn.execute(text("CREATE SCHEMA IF NOT EXISTS agn"))

    Base.metadata.create_all(bind=engine)

    print("Tables created successfully.")


if __name__ == "__main__":
    main()
