from flask_sqlalchemy import SQLAlchemy
from datetime import datetime

db = SQLAlchemy()


class User(db.Model):
    __tablename__ = "users"

    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(255), unique=True, nullable=False)
    name = db.Column(db.String(255), nullable=False)
    password_hash = db.Column(db.String(255), nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)

    # Является ли пользователь администратором
    is_admin = db.Column(db.Boolean, default=False, nullable=False)

    # Подтверждён ли аккаунт администратором
    is_approved = db.Column(db.Boolean, default=False, nullable=False)


class ProjectObject(db.Model):
    """
    Объект фазы 2 (здание / блок / ситуационный план / гараж).
    """

    __tablename__ = "project_objects"

    id = db.Column(db.Integer, primary_key=True)

    # Полный шифр, как в ТЗ, например: "PLGL1-GP.2-000-H06-SOB"
    code = db.Column(db.String(255), unique=True, nullable=False)

    # Короткое имя для отображения, например: "H06", "H01–H04", "B01–B03", "GAR", "SIT"
    short_name = db.Column(db.String(64), nullable=False)

    # Читабельное имя: "Hotel H06", "BA Tip B3", "Гараж", "Ситуационный план"
    full_name = db.Column(db.String(255), nullable=False)

    created_at = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)
