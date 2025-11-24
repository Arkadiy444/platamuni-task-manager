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

    # Связанные разделы (000,010,020,030,040...)
    sections = db.relationship("ProjectSection", back_populates="object", lazy=True)


class ProjectSection(db.Model):
    """
    Раздел проекта внутри конкретного объекта:
    000 Opšta dokumentacija,
    010 Arhitektonski projekat,
    020 Projekat konstrukcije,
    ...
    """

    __tablename__ = "project_sections"

    id = db.Column(db.Integer, primary_key=True)

    # Привязка к объекту (Hotel H06, SIT, GAR и т.д.)
    object_id = db.Column(db.Integer, db.ForeignKey("project_objects.id"), nullable=False)

    # Код раздела: 000, 010, 020, 030, 040, 050, 060, 061, 062, 080, 090, 121, 122, 125
    code = db.Column(db.String(8), nullable=False)

    # Имя раздела (билингвально, чтобы было понятно всем):
    # например: "Opšta dokumentacija (Описательная документация)"
    name = db.Column(db.String(255), nullable=False)

    # Порядок сортировки, чтобы не путать 000/010/020...
    order_index = db.Column(db.Integer, nullable=False)

    created_at = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)

    # Обратная связь на объект
    object = db.relationship("ProjectObject", back_populates="sections")
