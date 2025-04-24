#!/usr/bin/env python3
import os
import argparse
import subprocess
import time
from flask import render_template
from dotenv import load_dotenv
from app import create_app, db
from app.utils import utils

# Load environment variables from .env
load_dotenv()

# CLI commands using argparse
def main():
    parser = argparse.ArgumentParser(description="MISP Modules Website CLI")
    parser.add_argument("--dev", action="store_true", help="Run misp-modules and the website in debug mode")
    parser.add_argument("--db-init", action="store_true", help="Initialize the database")
    parser.add_argument("--db-migrate", action="store_true", help="Generate a new database migration")
    parser.add_argument("--db-upgrade", action="store_true", help="Apply database migrations")
    parser.add_argument("--db-downgrade", action="store_true", help="Revert the latest database migration")
    args = parser.parse_args()

    # Create the app only when needed
    app = create_app()

    # Import utils after app creation to avoid circular imports
    from app.utils.init_modules import create_modules_db
    from app.utils.utils import gen_admin_password

    # Register 404 error handler
    @app.errorhandler(404)
    def error_page_not_found(e):
        return render_template('404.html'), 404

    if args.dev:
        utils.IS_DEVELOPMENT = True
        print("Starting misp-modules...")
        misp_proc = subprocess.Popen(["poetry", "run", "misp-modules", "-l", "127.0.0.1"], cwd="..")
        time.sleep(2)  # Wait for misp-modules to initialize
        print("Starting website in debug mode...")
        app.run(host=app.config['FLASK_URL'], port=app.config['FLASK_PORT'], debug=True)
        try:
            misp_proc.wait()
        except KeyboardInterrupt:
            print("Stopping development environment...")
            misp_proc.terminate()
    elif args.db_init:
        with app.app_context():
            db.create_all()
            create_modules_db()
            gen_admin_password()
            print("Database initialized.")
    elif args.db_migrate:
        with app.app_context():
            subprocess.run(["flask", "db", "migrate"])
    elif args.db_upgrade:
        with app.app_context():
            subprocess.run(["flask", "db", "upgrade"])
    elif args.db_downgrade:
        with app.app_context():
            subprocess.run(["flask", "db", "downgrade"])
    else:
        parser.print_help()

if __name__ == "__main__":
    main()
