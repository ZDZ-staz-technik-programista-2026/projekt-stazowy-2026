from app.database import SessionLocal
from app.models import Role, User

db = SessionLocal()


student_role = Role(
    name="Student"
)

supervisor_role = Role(
    name="Supervisor"
)

db.add(supervisor_role)
db.add(student_role)
db.commit()
db.refresh(supervisor_role)
db.refresh(student_role)

student = User(
    name="Test Student 1",
    daily_hour_limit=8,
    role_id=1
)
student2 = User(
    name="Test Student 2",
    daily_hour_limit=8,
    role_id=1
)

student3 = User(
    name="Test Student 3",
    daily_hour_limit=8,
    role_id=1
)

db.add(student)
db.add(student2)
db.add(student3)
db.commit()
db.refresh(student)
db.refresh(student2)
db.refresh(student3)


supervisor = User(
    name="Supervisor",
    role_id=2
)

db.add(supervisor)
db.commit()
db.refresh(supervisor)


print("Dodano:")
print(student.id, student.name, student.role_id)
print(student2.id, student2.name, student2.role_id)
print(student3.id, student3.name, student3.role_id)
print(supervisor.id, supervisor.name)

db.close()