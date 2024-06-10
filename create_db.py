import argparse
from app import app, db
from db import User


def create_database(name, first_name, email):
    with app.app_context():
        db.create_all()
        add_first_admin(name, first_name, email)
        print("Database tables created successfully.")


def add_first_admin(name, first_name, email):
    admin_exists = db.session.query(User).filter_by(admin=True).first()
    if admin_exists is None:
        first_admin = User(first_name=first_name, name=name, email=email, admin=True)
        db.session.add(first_admin)
        db.session.commit()
        print(f"Admin account for {first_name} {name} created successfully.")
    else:
        print("Admin account already exists.")


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description="Create the database and add the first admin.")
    parser.add_argument('--name', required=True, help="Name of the admin.")
    parser.add_argument('--first_name', required=True, help="First name of the admin.")
    parser.add_argument('--email', required=True, help="Email of the admin.")

    args = parser.parse_args()
    create_database(args.name, args.first_name, args.email)
