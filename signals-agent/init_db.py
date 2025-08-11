#!/usr/bin/env python3
"""Database initialization CLI script."""

import sys
import logging
from database import init_db

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


def main():
    """Main function to initialize the database."""
    try:
        logger.info("Starting database initialization...")
        init_db()
        logger.info("Database initialization completed successfully!")
        return 0
    except Exception as e:
        logger.error(f"Database initialization failed: {e}")
        return 1


if __name__ == "__main__":
    sys.exit(main())
