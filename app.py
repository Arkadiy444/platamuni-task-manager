from functools import wraps
from datetime import datetime, date

from flask import (
    Flask,
    render_template,
    redirect,
    url_for,
    request,
    flash,
    session,
    abort,
)

from werkzeug.security import generate_password_hash, check_password_hash

from config import Config
from models import db, User, ProjectObject, ProjectSection, ProjectPart


def parse_date(value: str):
    """Преобразование строки YYYY-MM-DD в date, либо None."""
    if not value:
        return None
    try:
        return datetime.strptime(value, "%Y-%m-%d").date()
    except ValueError:
        return None


def create_app() -> Flask:
    app = Flask(__name__)
    app.config.from_object(Config)

    db.init_app(app)

    # ---- Первичное наполнение БД ----

    def seed_objects() -> None:
        if ProjectObject.query.count() > 0:
            return

        objects_data = [
            {"code": "PLGL1-GP.2-000-000-SIT", "short_name": "SIT", "full_name": "Ситуационный план"},
            {"code": "PLGL1-GP.2-000-H01-CEN", "short_name": "H01–H04", "full_name": "Hotel H01–H04"},
            {"code": "PLGL1-GP.2-000-H05-SOB", "short_name": "H05", "full_name": "Hotel H05"},
            {"code": "PLGL1-GP.2-000-H06-SOB", "short_name": "H06", "full_name": "Hotel H06"},
            {"code": "PLGL1-GP.2-000-H07-SOB", "short_name": "H07", "full_name": "Hotel H07"},
            {"code": "PLGL1-GP.2-000-H08-SOB", "short_name": "H08", "full_name": "Hotel H08"},
            {"code": "PLGL1-GP.2-000-H09-SOB", "short_name": "H09", "full_name": "Hotel H09"},
            {"code": "PLGL1-GP.2-000-H10-SOB", "short_name": "H10", "full_name": "Hotel H10"},
            {"code": "PLGL1-GP.2-000-H11-SOB", "short_name": "H11", "full_name": "Hotel H11"},
            {"code": "PLGL1-GP.2-000-H12-SOB", "short_name": "H12", "full_name": "Hotel H12"},
            {"code": "PLGL1-GP.2-000-B01-B03", "short_name": "B01–B03", "full_name": "BA Tip B3"},
            {"code": "PLGL1-GP.2-000-B02-B02", "short_name": "B02", "full_name": "BA Tip B2"},
            {"code": "PLGL1-GP.2-000-B03-B04", "short_name": "B03–B04", "full_name": "BA Tip B4"},
            {"code": "PLGL1-GP.2-000-B04-B01", "short_name": "B04–B01", "full_name": "BA Tip B1"},
            {"code": "PLGL1-GP.2-000-B05-B02", "short_name": "B05–B02", "full_name": "BA Tip B2"},
            {"code": "PLGL1-GP.2-000-B06-B1A", "short_name": "B06–B1A", "full_name": "BA Tip B1A"},
            {"code": "PLGL1-GP.2-000-B07-B3A", "short_name": "B07–B3A", "full_name": "BA Tip B3A"},
            {"code": "PLGL1-GP.2-000-B08-B2B", "short_name": "B08–B2B", "full_name": "BA Tip B2B"},
            {"code": "PLGL1-GP.2-000-B09-B2A", "short_name": "B09–B2A", "full_name": "BA Tip B2A"},
            {"code": "PLGL1-GP.2-000-B10-B3B", "short_name": "B10–B3B", "full_name": "BA Tip B3B"},
            {"code": "PLGL1-GP.2-000-M02-GAR", "short_name": "GAR", "full_name": "Гараж"},
        ]

        for item in objects_data:
            obj = ProjectObject(
                code=item["code"],
                short_name=item["short_name"],
                full_name=item["full_name"],
            )
            db.session.add(obj)

        db.session.commit()

    def seed_sections() -> None:
        if ProjectSection.query.count() > 0:
            return

        sections_template = [
            {"code": "000", "name": "Opšta dokumentacija (Описательная документация)"},
            {"code": "010", "name": "Arhitektonski projekat (Архитектурный проект)"},
            {"code": "020", "name": "Projekat konstrukcije (Конструктивные решения)"},
            {"code": "030", "name": "Projekat hidrotehničkih instalacija (Водоснабжение и канализация)"},
            {"code": "040", "name": "Projekat elektroenergetskih instalacija (Электроснабжение / ЭОМ)"},
            {"code": "050", "name": "Elektronska komunikaciona mreža (Слаботочные системы / ЭС)"},
            {"code": "060", "name": "Termotehničke instalacije (Отопление)"},
            {"code": "061", "name": "Sprinkler instalacije (АУПТ)"},
            {"code": "062", "name": "Ventilacija i klima (Вентиляция и кондиционирование)"},
            {"code": "080", "name": "Saobraćajna signalizacija (Проект дорожного движения)"},
            {"code": "090", "name": "Uređenje terena (Ландшафтный дизайн)"},
            {"code": "121", "name": "Zaštita od požara (Пожарная безопасность)"},
            {"code": "122", "name": "Energetska efikasnost (Энергоэффективность)"},
            {"code": "125", "name": "Konzervatorski projekat (Консерваторский проект)"},
        ]

        objects = ProjectObject.query.order_by(ProjectObject.id).all()
        if not objects:
            return

        for obj in objects:
            for index, section in enumerate(sections_template, start=1):
                sec = ProjectSection(
                    object_id=obj.id,
                    code=section["code"],
                    name=section["name"],
                    order_index=index,
                )
                db.session.add(sec)

        db.session.commit()

    def seed_parts() -> None:
        if ProjectPart.query.count() > 0:
            return

        parts_template = [
            "OPŠTA DOKUMENTACIJA (Общая документация)",
            "TEKSTUALNA DOKUMENTACIJA (Текстовая часть)",
            "Numerička dokumentacija (Расчёты и сметы)",
            "GRAFIČKA DOKUMENTACIJA (Графическая документация)",
            "Finalni album (Финальный альбом, собранный из частей)",
        ]

        sections = ProjectSection.query.order_by(ProjectSection.id).all()
        if not sections:
            return

        for sec in sections:
            for index, name in enumerate(parts_template, start=1):
                part = ProjectPart(
                    section_id=sec.id,
                    name=name,
                    order_index=index,
                )
                db.session.add(part)

        db.session.commit()

    with app.app_context():
        db.create_all()
        seed_objects()
        seed_sections()
        seed_parts()

    # ----- Декораторы доступа -----

    def login_required(view_function):
        @wraps(view_function)
        def wrapped_view(**kwargs):
            if "user_id" not in session:
                return redirect(url_for("login"))
            return view_function(**kwargs)

        return wrapped_view

    def admin_required(view_function):
        @wraps(view_function)
        def wrapped_view(**kwargs):
            user_id = session.get("user_id")
            if user_id is None:
                return redirect(url_for("login"))

            user = User.query.get(user_id)
            if user is None or not user.is_admin:
                return abort(403)

            return view_function(**kwargs)

        return wrapped_view

    # ----- Маршруты -----

    @app.route("/")
    def index():
        if "user_id" in session:
            return redirect(url_for("dashboard"))
        return redirect(url_for("login"))

    @app.route("/register", methods=["GET", "POST"])
    def register():
        if request.method == "POST":
            email = request.form.get("email", "").strip().lower()
            name = request.form.get("name", "").strip()
            password = request.form.get("password", "")
            password_confirm = request.form.get("password_confirm", "")

            if not email or not name or not password or not password_confirm:
                flash("Заполните все поля.", "error")
            elif password != password_confirm:
                flash("Пароли не совпадают.", "error")
            else:
                existing_user = User.query.filter_by(email=email).first()
                if existing_user is not None:
                    flash("Пользователь с таким email уже существует.", "error")
                else:
                    users_count = User.query.count()
                    is_admin = users_count == 0
                    is_approved = is_admin

                    new_user = User(
                        email=email,
                        name=name,
                        password_hash=generate_password_hash(password),
                        is_admin=is_admin,
                        is_approved=is_approved,
                    )
                    db.session.add(new_user)
                    db.session.commit()

                    if is_admin:
                        flash("Регистрация администратора прошла успешно. Теперь можно войти.", "success")
                    else:
                        flash("Регистрация отправлена. Ожидайте подтверждения аккаунта администратором.", "success")

                    return redirect(url_for("login"))

        return render_template("register.html")

    @app.route("/login", methods=["GET", "POST"])
    def login():
        if request.method == "POST":
            email = request.form.get("email", "").strip().lower()
            password = request.form.get("password", "")

            user = User.query.filter_by(email=email).first()
            if user is None:
                flash("Неверный email или пароль.", "error")
            else:
                if not check_password_hash(user.password_hash, password):
                    flash("Неверный email или пароль.", "error")
                else:
                    if not user.is_approved:
                        flash("Ваш аккаунт ещё не подтверждён администратором.", "error")
                    else:
                        session["user_id"] = user.id
                        session["user_name"] = user.name
                        session["is_admin"] = user.is_admin
                        return redirect(url_for("dashboard"))

        return render_template("login.html")

    @app.route("/logout")
    def logout():
        session.clear()
        return redirect(url_for("login"))

    @app.route("/dashboard")
    @login_required
    def dashboard():
        user_name = session.get("user_name", "Пользователь")
        is_admin = session.get("is_admin", False)
        objects = ProjectObject.query.order_by(ProjectObject.id).all()

        total_tasks = 0
        overdue_tasks = 0
        done_tasks = 0

        return render_template(
            "dashboard.html",
            user_name=user_name,
            is_admin=is_admin,
            objects=objects,
            total_tasks=total_tasks,
            overdue_tasks=overdue_tasks,
            done_tasks=done_tasks,
        )

    @app.route("/objects/<int:object_id>")
    @login_required
    def object_detail(object_id: int):
        obj = ProjectObject.query.get_or_404(object_id)
        sections = (
            ProjectSection.query
            .filter_by(object_id=object_id)
            .order_by(ProjectSection.order_index)
            .all()
        )
        return render_template("object_detail.html", obj=obj, sections=sections)

    @app.route("/sections/<int:section_id>", methods=["GET", "POST"])
    @login_required
    def section_detail(section_id: int):
        section = ProjectSection.query.get_or_404(section_id)
        obj = section.object

        if request.method == "POST":
            part_id = request.form.get("part_id")
            if part_id:
                part = ProjectPart.query.get_or_404(int(part_id))
                if part.section_id != section.id:
                    abort(400)

                if "start_date" in request.form:
                    part.start_date = parse_date(request.form.get("start_date"))

                if "end_date" in request.form:
                    part.end_date = parse_date(request.form.get("end_date"))

                if "assignee_name" in request.form:
                    part.assignee_name = request.form.get("assignee_name") or None

                if "album_link" in request.form:
                    part.album_link = request.form.get("album_link") or None

                status = request.form.get("status")
                allowed_statuses = {"pending", "in_progress", "done", "returned"}
                if status in allowed_statuses:
                    part.status = status

                db.session.commit()
                flash("Данные части обновлены.", "success")
                return redirect(url_for("section_detail", section_id=section.id))

        parts = (
            ProjectPart.query
            .filter_by(section_id=section.id)
            .order_by(ProjectPart.order_index)
            .all()
        )

        today = date.today()
        for p in parts:
            if p.end_date and p.end_date < today and p.status != "done":
                p.is_overdue = True
            else:
                p.is_overdue = False

        status_choices = [
            ("pending", "В ожидании"),
            ("in_progress", "В разработке"),
            ("done", "Выполнено"),
            ("returned", "Возвращено на доработку"),
        ]

        return render_template(
            "section_detail.html",
            section=section,
            obj=obj,
            parts=parts,
            status_choices=status_choices,
        )

    @app.route("/admin/users", methods=["GET", "POST"])
    @login_required
    @admin_required
    def admin_users():
        if request.method == "POST":
            user_id = request.form.get("user_id")
            action = request.form.get("action")

            if user_id and action:
                target = User.query.get(int(user_id))
                current_user_id = session.get("user_id")

                if target:
                    if action == "approve":
                        target.is_approved = True
                    elif action == "revoke":
                        target.is_approved = False
                    elif action == "make_admin":
                        target.is_admin = True
                    elif action == "remove_admin":
                        if target.id == current_user_id:
                            flash("Нельзя снять права администратора с самого себя.", "error")
                        else:
                            target.is_admin = False
                    elif action == "delete":
                        if target.id == current_user_id:
                            flash("Нельзя удалить собственный аккаунт.", "error")
                        else:
                            db.session.delete(target)
                            db.session.commit()
                            flash("Пользователь удалён.", "success")
                            return redirect(url_for("admin_users"))

                    db.session.commit()

            return redirect(url_for("admin_users"))

        users = User.query.order_by(User.id).all()
        return render_template("admin_users.html", users=users)

    return app


if __name__ == "__main__":
    application = create_app()
    application.run(debug=True)
