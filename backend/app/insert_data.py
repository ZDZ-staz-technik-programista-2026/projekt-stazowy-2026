from app.database import SessionLocal
from app.models import Role, User


def insert_data():
    """
    Inserts initial test data into the database.

    Creates required roles and test users if they do not already exist.
    The function is safe to run multiple times because existing records
    are checked before insertion.

    Created data:
        Roles:
            - Student
            - Supervisor

        Users:
            - Test Student 1
            - Test Student 2
            - Test Student 3
            - Test Supervisor

    The database session is always closed after execution.
    """
    db = SessionLocal()

    try:
        required_users = [
            "Test Student 1",
            "Test Student 2",
            "Test Student 3",
            "Test Supervisor",
        ]

        existing_users = (
            db.query(User.name)
            .filter(User.name.in_(required_users))
            .all()
        )

        existing_user_names = {
            user.name for user in existing_users
        }

        # Avoid inserting duplicate seed data when the script is executed again.
        if len(existing_user_names) == len(required_users):
            print("Test data already exists. Nothing to insert.")
            return


        # Create required roles if they do not already exist.
        student_role = (
            db.query(Role)
            .filter_by(name="Student")
            .first()
        )

        if student_role is None:
            student_role = Role(name="Student")
            db.add(student_role)


        supervisor_role = (
            db.query(Role)
            .filter_by(name="Supervisor")
            .first()
        )

        if supervisor_role is None:
            supervisor_role = Role(name="Supervisor")
            db.add(supervisor_role)


        db.commit()

        db.refresh(student_role)
        db.refresh(supervisor_role)


        # Create student test accounts.
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

            if exists is None:
                db.add(
                    User(
                        name=student_name,
                        daily_hours_limit=8,
                        role_id=student_role.id,
                    )
                )


        # Create supervisor test account.
        supervisor_name = "Test Supervisor"

        exists = (
            db.query(User)
            .filter_by(name=supervisor_name)
            .first()
        )

        if exists is None:
            db.add(
                User(
                    name=supervisor_name,
                    daily_hours_limit=8,
                    role_id=supervisor_role.id,
                )
            )


        db.commit()

        print("Test data inserted.")

    finally:
        db.close()