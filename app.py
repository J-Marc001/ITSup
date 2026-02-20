import os
from datetime import datetime
from functools import wraps

from flask import Flask, flash, redirect, render_template, request, url_for
from flask_login import (
    LoginManager,
    UserMixin,
    current_user,
    login_required,
    login_user,
    logout_user,
)
from flask_sqlalchemy import SQLAlchemy
from werkzeug.security import check_password_hash, generate_password_hash

app = Flask(__name__)
app.config["SECRET_KEY"] = "ma_cle_secrete_super_securisee"

# Configuration XAMPP (MySQL)
# Format: mysql+pymysql://utilisateur:motdepasse@hote/nom_base
app.config["SQLALCHEMY_DATABASE_URI"] = "mysql+pymysql://root:@localhost/maintenance_db"
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False

db = SQLAlchemy(app)
login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = "login"

# --- MODÈLES ---


class User(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(50), unique=True, nullable=False)
    email = db.Column(db.String(100), unique=True, nullable=False)
    password = db.Column(db.String(255), nullable=False)
    role = db.Column(db.String(20), nullable=False)  # 'EMPLOYEE', 'TECHNICIAN', 'ADMIN'
    full_name = db.Column(db.String(100), nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)


class Category(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(50), nullable=False)
    description = db.Column(db.Text)


class Status(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(30), nullable=False)
    color = db.Column(db.String(20))


class Priority(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(30), nullable=False)
    level = db.Column(db.Integer)


class Ticket(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(200), nullable=False)
    description = db.Column(db.Text, nullable=False)
    category_id = db.Column(db.Integer, db.ForeignKey("category.id"), nullable=False)
    priority_id = db.Column(db.Integer, db.ForeignKey("priority.id"), nullable=False)
    status_id = db.Column(db.Integer, db.ForeignKey("status.id"), default=1)
    requester_id = db.Column(db.Integer, db.ForeignKey("user.id"), nullable=False)
    assigned_to = db.Column(db.Integer, db.ForeignKey("user.id"), nullable=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    category = db.relationship("Category", backref="tickets")
    priority = db.relationship("Priority", backref="tickets")
    status = db.relationship("Status", backref="tickets")
    requester = db.relationship(
        "User", foreign_keys=[requester_id], backref="requested_tickets"
    )
    technician = db.relationship(
        "User", foreign_keys=[assigned_to], backref="assigned_tickets"
    )


class Comment(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    ticket_id = db.Column(db.Integer, db.ForeignKey("ticket.id"), nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey("user.id"), nullable=False)
    content = db.Column(db.Text, nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    user = db.relationship("User", backref="comments")
    ticket = db.relationship("Ticket", backref="comments")


# --- DÉCORATEUR ADMIN ---
def admin_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if not current_user.is_authenticated or current_user.role != "ADMIN":
            flash("Accès refusé : Vous n'êtes pas administrateur.", "danger")
            return redirect(url_for("dashboard"))
        return f(*args, **kwargs)

    return decorated_function


# --- SETUP LOGIN ---
@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))


# --- ROUTES GÉNÉRALES ---


@app.route("/")
def index():
    if current_user.is_authenticated:
        return redirect(url_for("dashboard"))
    return redirect(url_for("login"))


@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        username = request.form.get("username")
        password = request.form.get("password")
        user = User.query.filter_by(username=username).first()
        if user and check_password_hash(user.password, password):
            login_user(user)
            return redirect(url_for("dashboard"))
        flash("Identifiants invalides", "danger")
    return render_template("login.html")


@app.route("/register", methods=["GET", "POST"])
def register():
    if request.method == "POST":
        hashed_pw = generate_password_hash(
            request.form.get("password"), method="pbkdf2:sha256"
        )
        new_user = User(
            username=request.form.get("username"),
            email=request.form.get("email"),
            password=hashed_pw,
            role="EMPLOYEE",
            full_name=request.form.get("fullname"),
        )
        try:
            db.session.add(new_user)
            db.session.commit()
            flash("Compte créé ! Connectez-vous.", "success")
            return redirect(url_for("login"))
        except:
            flash("Erreur: Email ou Username déjà pris.", "danger")
    return render_template("register.html")


@app.route("/logout")
@login_required
def logout():
    logout_user()
    return redirect(url_for("login"))


@app.route("/dashboard")
@login_required
def dashboard():
    if current_user.role == "ADMIN":
        tickets = Ticket.query.all()
    elif current_user.role == "TECHNICIAN":
        tickets = Ticket.query.filter(
            (Ticket.assigned_to == current_user.id) | (Ticket.assigned_to == None)
        ).all()
    else:
        tickets = Ticket.query.filter_by(requester_id=current_user.id).all()
    return render_template("dashboard.html", tickets=tickets)


@app.route("/ticket/new", methods=["GET", "POST"])
@login_required
def create_ticket():
    if request.method == "POST":
        new_ticket = Ticket(
            title=request.form.get("title"),
            description=request.form.get("description"),
            category_id=request.form.get("category"),
            priority_id=request.form.get("priority"),
            requester_id=current_user.id,
        )
        db.session.add(new_ticket)
        db.session.commit()
        flash("Ticket créé avec succès", "success")
        return redirect(url_for("dashboard"))

    categories = Category.query.all()
    priorities = Priority.query.all()
    return render_template(
        "create_ticket.html", categories=categories, priorities=priorities
    )


@app.route("/ticket/<int:id>", methods=["GET", "POST"])
@login_required
def ticket_detail(id):
    ticket = Ticket.query.get_or_404(id)

    if request.method == "POST":
        if "content" in request.form:
            comment = Comment(
                ticket_id=ticket.id,
                user_id=current_user.id,
                content=request.form.get("content"),
            )
            db.session.add(comment)

        if current_user.role in ["ADMIN", "TECHNICIAN"]:
            if "status_id" in request.form:
                ticket.status_id = request.form.get("status_id")
            if "technician_id" in request.form and current_user.role == "ADMIN":
                ticket.assigned_to = request.form.get("technician_id")

        db.session.commit()
        return redirect(url_for("ticket_detail", id=ticket.id))

    statuses = Status.query.all()
    technicians = User.query.filter(User.role.in_(["TECHNICIAN", "ADMIN"])).all()
    return render_template(
        "ticket_detail.html", ticket=ticket, statuses=statuses, technicians=technicians
    )


# --- ROUTES ADMINISTRATION (DÉPLACÉES ICI AVANT LE MAIN) ---


@app.route("/admin/users")
@login_required
@admin_required
def manage_users():
    users = User.query.all()
    return render_template("admin_users.html", users=users)


@app.route("/admin/user/edit/<int:id>", methods=["GET", "POST"])
@login_required
@admin_required
def edit_user(id):
    user = User.query.get_or_404(id)

    if request.method == "POST":
        user.username = request.form.get("username")
        user.email = request.form.get("email")
        user.full_name = request.form.get("fullname")
        user.role = request.form.get("role")

        try:
            db.session.commit()
            flash(f"Utilisateur {user.username} mis à jour avec succès.", "success")
            return redirect(url_for("manage_users"))
        except:
            flash("Erreur lors de la mise à jour.", "danger")

    return render_template("edit_user.html", user=user)


@app.route("/admin/user/delete/<int:id>")
@login_required
@admin_required
def delete_user(id):
    if id == current_user.id:
        flash("Vous ne pouvez pas vous supprimer vous-même !", "danger")
        return redirect(url_for("manage_users"))

    user = User.query.get_or_404(id)
    db.session.delete(user)
    db.session.commit()
    flash("Utilisateur supprimé.", "warning")
    return redirect(url_for("manage_users"))


# --- LANCEMENT DE L'APPLICATION (TOUJOURS À LA FIN) ---

if __name__ == "__main__":
    # init_db() # Désactivé car DB gérée par XAMPP
    app.run(debug=True)
