from app.database import SessionLocal
from app.models import Role, User


def insert_data():
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

        if len(existing_user_names) == len(required_users):
            print("Test data already exists. Nothing to insert.")
            return


        # Roles
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


        # Students
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


        # Supervisor
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