from app.database import SessionLocal
from app.models import Role, User


def insert_data() -> None:
    """Seed the database with initial roles and test users.

    Ensures idempotency by checking for the existence of required roles and 
    user accounts before performing insert operations to avoid duplicate records.

    Logic Flow:
        1. Query existing target test users to determine if seeding is required.
        2. Ensure base system roles ("Student", "Supervisor") exist in DB.
        3. Create and commit missing role entities to generate valid foreign keys.
        4. Instantiate missing Student user records with default daily hour limits.
        5. Instantiate missing Supervisor user record.
        6. Commit transaction and close the database session.
    """
    db = SessionLocal()

    try:
        # Define the set of required initial test users
        required_users = [
            "Test Student 1",
            "Test Student 2",
            "Test Student 3",
            "Test Supervisor",
        ]

        # Check existing users in the database to prevent duplicate seeding runs
        existing_users = (
            db.query(User.name)
            .filter(User.name.in_(required_users))
            .all()
        )

        existing_user_names = {
            user.name for user in existing_users
        }

        # Early return if all required seed users already exist
        if len(existing_user_names) == len(required_users):
            print("Test data already exists. Nothing to insert.")
            return

        # -------------------------------------------------------------------
        # Role Seeding & Instantiation
        # -------------------------------------------------------------------
        
        # Ensure "Student" role exists
        student_role = (
            db.query(Role)
            .filter_by(name="Student")
            .first()
        )

        if student_role is None:
            student_role = Role(name="Student")
            db.add(student_role)

        # Ensure "Supervisor" role exists
        supervisor_role = (
            db.query(Role)
            .filter_by(name="Supervisor")
            .first()
        )

        if supervisor_role is None:
            supervisor_role = Role(name="Supervisor")
            db.add(supervisor_role)

        # Commit newly added roles to flush and assign primary key IDs
        db.commit()

        # Refresh role model instances to fetch DB-assigned primary keys
        db.refresh(student_role)
        db.refresh(supervisor_role)

        # -------------------------------------------------------------------
        # Student Users Seeding
        # -------------------------------------------------------------------
        students = [
            "Test Student 1",
            "Test Student 2",
            "Test Student 3",
        ]

        for student_name in students:
            exists = (
                db.query(User)
                .filter_by(name=student_name)
                .first()
            )

            # Only add student user if not previously seeded
            if exists is None:
                db.add(
                    User(
                        name=student_name,
                        daily_hours_limit=8,
                        role_id=student_role.id,
                    )
                )

        # -------------------------------------------------------------------
        # Supervisor User Seeding
        # -------------------------------------------------------------------
        supervisor_name = "Test Supervisor"

        exists = (
            db.query(User)
            .filter_by(name=supervisor_name)
            .first()
        )

        # Only add supervisor user if not previously seeded
        if exists is None:
            db.add(
                User(
                    name=supervisor_name,
                    daily_hours_limit=8,
                    role_id=supervisor_role.id,
                )
            )

        # Persist all newly created user records
        db.commit()

        print("Test data inserted.")

    finally:
        # Guarantee session closure regardless of success or runtime exceptions
        db.close()