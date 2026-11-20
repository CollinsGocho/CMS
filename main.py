"""
Classroom Management System (CMS)
Main entry point. Launches the graphical user interface (GUI) or
command-line interface (CLI) based on user arguments.

Usage:
    python main.py          # Launches Desktop GUI (Default)
    python main.py --cli    # Launches Interactive Terminal CLI
    python main.py --seed   # Initializes / Resets database with sample data
    python main.py --test   # Executes the unit & integration test suite
"""

import argparse
import sys


def main():
    parser = argparse.ArgumentParser(
        description="Classroom Management System (CMS) - Attendance & Academic Performance Tracker"
    )
    parser.add_argument("--cli", action="store_true", help="Launch interactive terminal CLI instead of GUI")
    parser.add_argument("--seed", action="store_true", help="Reset and re-populate database with seed data")
    parser.add_argument("--test", action="store_true", help="Run automated test suite")

    args = parser.parse_args()

    if args.seed:
        from database import db
        print("[CMS] Initializing database and applying seed dataset...")
        db.init_database(seed=True)
        print("[CMS] Database populated successfully. Database file: cms.db")
        return

    if args.test:
        import unittest
        print("[CMS] Running test suite...")
        suite = unittest.defaultTestLoader.discover(".", pattern="test_*.py")
        runner = unittest.TextTestRunner(verbosity=2)
        result = runner.run(suite)
        sys.exit(0 if result.wasSuccessful() else 1)

    if args.cli:
        from app_cli import ClassroomCLI
        cli = ClassroomCLI()
        cli.run()
    else:
        # Try GUI first, fall back to CLI if headless or display unavailable
        try:
            import tkinter as tk
            from app_gui import ClassroomGUI

            root = tk.Tk()
            app = ClassroomGUI(root)
            print("[CMS] Launching Classroom Management System Desktop GUI...")
            root.mainloop()
        except Exception as e:
            print(f"[CMS] GUI could not be opened ({e}). Falling back to CLI mode...")
            from app_cli import ClassroomCLI
            cli = ClassroomCLI()
            cli.run()


if __name__ == "__main__":
    main()
