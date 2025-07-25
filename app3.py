import os
import datetime
from flask import Flask, render_template_string, request, redirect, url_for, jsonify, flash, Response
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import func, extract
from werkzeug.security import generate_password_hash, check_password_hash
from flask_login import LoginManager, UserMixin, login_user, logout_user, login_required, current_user
from functools import wraps
import json
from collections import defaultdict

# WeasyPrint kitabxanasını PDF üçün import edirik
try:
    from weasyprint import HTML, CSS
except ImportError:
    print("XƏBƏRDARLIQ: WeasyPrint kitabxanası tapılmadı. PDF generasiyası işləməyəcək.")
    print("Quraşdırmaq üçün: pip install WeasyPrint")
    HTML = None

# -----------------------------------------------------------------------------
# TƏTBİQİN VƏ VERİLƏNLƏR BAZASININ KONFİQURASİYASI
# -----------------------------------------------------------------------------
basedir = os.path.abspath(os.path.dirname(__file__))

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///' + os.path.join(basedir, 'erp_database.db')
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['SECRET_KEY'] = 'bu-cox-gizli-bir-acardir-ve-deyisdirilmelidir'

db = SQLAlchemy(app)
login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'login'
login_manager.login_message = "Bu səhifəyə daxil olmaq üçün giriş etməlisiniz."
login_manager.login_message_category = "info"

# -----------------------------------------------------------------------------
# VERİLƏNLƏR BAZASI MODELLƏRİ (DATABASE MODELS)
# -----------------------------------------------------------------------------

# İstifadəçi Modeli
class User(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    password_hash = db.Column(db.String(200), nullable=False)
    role = db.Column(db.String(20), nullable=False, default='user') # Məs: 'admin', 'user'

    def set_password(self, password):
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password_hash, password)

# Müştərilər Cədvəli
class Customer(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    full_name = db.Column(db.String(100), nullable=False)
    company_name = db.Column(db.String(100))
    email = db.Column(db.String(100), unique=True)
    phone = db.Column(db.String(30))
    address = db.Column(db.String(200))
    contact_person = db.Column(db.String(100))
    billing_address = db.Column(db.String(200))
    website = db.Column(db.String(100))
    invoices = db.relationship('Invoice', backref='customer', lazy=True, cascade="all, delete-orphan")
    proposals = db.relationship('Proposal', backref='customer', lazy=True, cascade="all, delete-orphan")
    sales_orders = db.relationship('SalesOrder', backref='customer', lazy=True, cascade="all, delete-orphan")

# Təchizatçılar Cədvəli
class Vendor(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    full_name = db.Column(db.String(100), nullable=False)
    company_name = db.Column(db.String(100))
    email = db.Column(db.String(100), unique=True)
    phone = db.Column(db.String(30))
    address = db.Column(db.String(200))
    contact_person = db.Column(db.String(100))
    billing_address = db.Column(db.String(200))
    website = db.Column(db.String(100))
    purchase_orders = db.relationship('PurchaseOrder', backref='vendor', lazy=True, cascade="all, delete-orphan")

# Məhsullar və Xidmətlər Cədvəli
class Item(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    unit_type = db.Column(db.String(30))
    item_type = db.Column(db.String(20), default='Goods')
    category = db.Column(db.String(50))
    description = db.Column(db.Text)
    warranty_time = db.Column(db.String(50))
    purchase_price = db.Column(db.Float, default=0.0)
    purchase_tax = db.Column(db.Float, default=18.0)
    sale_price = db.Column(db.Float, default=0.0)
    sale_tax = db.Column(db.Float, default=18.0)

# Ödəniş Tapşırıqları (Invoices) Cədvəli
class Invoice(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    invoice_number = db.Column(db.String(50), unique=True, nullable=False)
    customer_id = db.Column(db.Integer, db.ForeignKey('customer.id'), nullable=False)
    invoice_date = db.Column(db.Date, default=datetime.date.today)
    due_date = db.Column(db.Date)
    total_amount = db.Column(db.Float, default=0.0)
    status = db.Column(db.String(20), default='Unpaid')
    notes = db.Column(db.Text)
    items = db.relationship('InvoiceItem', backref='invoice', lazy=True, cascade="all, delete-orphan")

class InvoiceItem(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    invoice_id = db.Column(db.Integer, db.ForeignKey('invoice.id'), nullable=False)
    item_id = db.Column(db.Integer, db.ForeignKey('item.id'), nullable=False)
    quantity = db.Column(db.Integer, default=1)
    price = db.Column(db.Float)
    tax = db.Column(db.Float)
    item = db.relationship('Item')

# Təkliflər (Proposals) Cədvəli
class Proposal(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    proposal_number = db.Column(db.String(50), unique=True, nullable=False)
    customer_id = db.Column(db.Integer, db.ForeignKey('customer.id'), nullable=False)
    proposal_date = db.Column(db.Date, default=datetime.date.today)
    expire_date = db.Column(db.Date)
    total_amount = db.Column(db.Float, default=0.0)
    status = db.Column(db.String(20), default='Pending') # Pending, Confirmed, Declined
    notes = db.Column(db.Text)
    items = db.relationship('ProposalItem', backref='proposal', lazy=True, cascade="all, delete-orphan")

class ProposalItem(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    proposal_id = db.Column(db.Integer, db.ForeignKey('proposal.id'), nullable=False)
    item_id = db.Column(db.Integer, db.ForeignKey('item.id'), nullable=False)
    quantity = db.Column(db.Integer, default=1)
    price = db.Column(db.Float)
    tax = db.Column(db.Float)
    item = db.relationship('Item')

# Satış Sifarişləri (Sales Orders)
class SalesOrder(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    order_number = db.Column(db.String(50), unique=True, nullable=False)
    customer_id = db.Column(db.Integer, db.ForeignKey('customer.id'), nullable=False)
    order_date = db.Column(db.Date, default=datetime.date.today)
    delivery_date = db.Column(db.Date)
    total_amount = db.Column(db.Float, default=0.0)
    status = db.Column(db.String(30), default='Pending') # Pending, Confirmed, Shipped
    notes = db.Column(db.Text)
    items = db.relationship('SalesOrderItem', backref='sales_order', lazy=True, cascade="all, delete-orphan")

class SalesOrderItem(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    sales_order_id = db.Column(db.Integer, db.ForeignKey('sales_order.id'), nullable=False)
    item_id = db.Column(db.Integer, db.ForeignKey('item.id'), nullable=False)
    quantity = db.Column(db.Integer, default=1)
    price = db.Column(db.Float)
    tax = db.Column(db.Float)
    item = db.relationship('Item')

# Alış Sifarişləri (Purchase Orders)
class PurchaseOrder(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    order_number = db.Column(db.String(50), unique=True, nullable=False)
    vendor_id = db.Column(db.Integer, db.ForeignKey('vendor.id'), nullable=False)
    order_date = db.Column(db.Date, default=datetime.date.today)
    expected_delivery_date = db.Column(db.Date)
    total_amount = db.Column(db.Float, default=0.0)
    status = db.Column(db.String(30), default='Ordered') # Ordered, Received, Canceled
    notes = db.Column(db.Text)
    items = db.relationship('PurchaseOrderItem', backref='purchase_order', lazy=True, cascade="all, delete-orphan")

class PurchaseOrderItem(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    purchase_order_id = db.Column(db.Integer, db.ForeignKey('purchase_order.id'), nullable=False)
    item_id = db.Column(db.Integer, db.ForeignKey('item.id'), nullable=False)
    quantity = db.Column(db.Integer, default=1)
    price = db.Column(db.Float) # Here we will use purchase_price from Item
    tax = db.Column(db.Float)
    item = db.relationship('Item')

# -----------------------------------------------------------------------------
# AUTHENTICATION & AUTHORIZATION
# -----------------------------------------------------------------------------
@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

def roles_required(*roles):
    def wrapper(f):
        @wraps(f)
        def wrapped(*args, **kwargs):
            if not current_user.is_authenticated or current_user.role not in roles:
                flash("Bu əməliyyatı icra etmək üçün səlahiyyətiniz yoxdur.", "danger")
                return redirect(request.referrer or url_for('dashboard'))
            return f(*args, **kwargs)
        return wrapped
    return wrapper

# -----------------------------------------------------------------------------
# HTML ŞABLONLARI (PYTHON STRING OLARAQ)
# -----------------------------------------------------------------------------

# Bütün səhifələr üçün əsas baza şablonu
BASE_TEMPLATE = """
<!doctype html>
<html lang="az">
<head>
    <meta charset="utf-8">
    <meta name="viewport" content="width=device-width, initial-scale=1">
    <title>{{ title }} - ERP Sistemi</title>
    <link href="https://cdn.jsdelivr.net/npm/bootstrap@5.3.3/dist/css/bootstrap.min.css" rel="stylesheet">
    <link rel="stylesheet" href="https://cdn.jsdelivr.net/npm/bootstrap-icons@1.11.3/font/bootstrap-icons.min.css">
    <style>
        body { background-color: #f8f9fa; }
        .sidebar {
            position: fixed; top: 0; left: 0; bottom: 0;
            width: 250px; padding: 20px; background-color: #343a40; color: white;
            display: flex; flex-direction: column;
        }
        .sidebar a {
            color: #adb5bd; text-decoration: none; display: block;
            padding: 10px 15px; border-radius: 5px;
        }
        .sidebar a:hover, .sidebar a.active { background-color: #495057; color: white; }
        .sidebar .nav-link i { margin-right: 10px; }
        .sidebar-footer { margin-top: auto; }
        .main-content { margin-left: 260px; padding: 20px; }
        .card { border: none; box-shadow: 0 0 15px rgba(0,0,0,0.1); }
        .stat-card { transition: transform 0.2s; }
        .stat-card:hover { transform: translateY(-5px); }
        @media print {
            .sidebar, .no-print { display: none !important; }
            .main-content { margin-left: 0; }
            body { background-color: white; }
        }
    </style>
</head>
<body>
    <div class="sidebar">
        <div>
            <h3 class="mb-4"><i class="bi bi-gear-wide-connected"></i> ERP Proqramı</h3>
            <ul class="nav flex-column">
                <li class="nav-item"><a class="nav-link {% if request.path == url_for('dashboard') %}active{% endif %}" href="{{ url_for('dashboard') }}"><i class="bi bi-speedometer2"></i> İdarə Paneli</a></li>
                <li class="nav-item"><a class="nav-link {% if request.path == url_for('reports') %}active{% endif %}" href="{{ url_for('reports') }}"><i class="bi bi-bar-chart-line"></i> Hesabatlar</a></li>
                <li class="nav-item mt-2"><hr class="text-secondary"></li>
                <li class="nav-item"><a class="nav-link {% if 'customer' in request.path %}active{% endif %}" href="{{ url_for('list_customers') }}"><i class="bi bi-people"></i> Müştərilər</a></li>
                <li class="nav-item"><a class="nav-link {% if 'vendor' in request.path %}active{% endif %}" href="{{ url_for('list_vendors') }}"><i class="bi bi-truck"></i> Təchizatçılar</a></li>
                <li class="nav-item"><a class="nav-link {% if 'item' in request.path %}active{% endif %}" href="{{ url_for('list_items') }}"><i class="bi bi-box-seam"></i> Məhsullar</a></li>
                <li class="nav-item mt-2"><hr class="text-secondary"></li>
                <li class="nav-item"><a class="nav-link {% if 'proposal' in request.path %}active{% endif %}" href="{{ url_for('list_proposals') }}"><i class="bi bi-file-earmark-text"></i> Təkliflər</a></li>
                <li class="nav-item"><a class="nav-link {% if 'sales_order' in request.path %}active{% endif %}" href="{{ url_for('list_sales_orders') }}"><i class="bi bi-cart"></i> Satış Sifarişləri</a></li>
                <li class="nav-item"><a class="nav-link {% if 'purchase_order' in request.path %}active{% endif %}" href="{{ url_for('list_purchase_orders') }}"><i class="bi bi-cart-plus"></i> Alış Sifarişləri</a></li>
                <li class="nav-item"><a class="nav-link {% if 'invoice' in request.path %}active{% endif %}" href="{{ url_for('list_invoices') }}"><i class="bi bi-receipt"></i> Fakturalar</a></li>
            </ul>
        </div>
        <div class="sidebar-footer">
            <hr class="text-secondary">
            <div class="text-white small">
                <i class="bi bi-person-circle"></i> {{ current_user.username }} ({{ current_user.role }})
            </div>
            <a class="nav-link" href="{{ url_for('logout') }}"><i class="bi bi-box-arrow-right"></i> Çıxış</a>
        </div>
    </div>

    <main class="main-content">
        {% with messages = get_flashed_messages(with_categories=true) %}
            {% if messages %}
                {% for category, message in messages %}
                <div class="alert alert-{{ category }} alert-dismissible fade show" role="alert">
                    {{ message }}
                    <button type="button" class="btn-close" data-bs-dismiss="alert" aria-label="Close"></button>
                </div>
                {% endfor %}
            {% endif %}
        {% endwith %}
        {{ content | safe }}
    </main>
    
    <script src="https://cdn.jsdelivr.net/npm/bootstrap@5.3.3/dist/js/bootstrap.bundle.min.js"></script>
    <script src="https://cdn.jsdelivr.net/npm/chart.js"></script>
    {% if extra_js %}
        {{ extra_js | safe }}
    {% endif %}
</body>
</html>
"""

LOGIN_TEMPLATE = """
<!doctype html>
<html lang="az">
<head>
    <meta charset="utf-8">
    <meta name="viewport" content="width=device-width, initial-scale=1">
    <title>Giriş - ERP Sistemi</title>
    <link href="https://cdn.jsdelivr.net/npm/bootstrap@5.3.3/dist/css/bootstrap.min.css" rel="stylesheet">
    <style>
        body { display: flex; align-items: center; justify-content: center; height: 100vh; background-color: #f0f2f5; }
        .login-card { width: 100%; max-width: 400px; padding: 40px; }
    </style>
</head>
<body>
    <div class="card login-card">
        <div class="card-body">
            <h2 class="text-center mb-4">ERP Sistemə Giriş</h2>
            {% with messages = get_flashed_messages(with_categories=true) %}
                {% if messages %}
                    {% for category, message in messages %}
                    <div class="alert alert-{{ category }}">{{ message }}</div>
                    {% endfor %}
                {% endif %}
            {% endwith %}
            <form method="post">
                <div class="mb-3">
                    <label for="username" class="form-label">İstifadəçi adı</label>
                    <input type="text" class="form-control" id="username" name="username" required>
                </div>
                <div class="mb-3">
                    <label for="password" class="form-label">Şifrə</label>
                    <input type="password" class="form-control" id="password" name="password" required>
                </div>
                <button type="submit" class="btn btn-primary w-100">Daxil Ol</button>
            </form>
            <p class="text-center mt-3">Hesabınız yoxdur? <a href="{{ url_for('register') }}">Qeydiyyatdan keçin</a></p>
        </div>
    </div>
</body>
</html>
"""

# Ana səhifə / İdarə Paneli üçün HTML
DASHBOARD_HTML = """
<div class="container-fluid">
    <h1 class="h2 mb-4">İdarə Paneli</h1>
    <!-- Simple Stats Row -->
    <div class="row">
        <div class="col-lg-3 col-md-6 mb-4">
            <div class="card text-white bg-primary h-100 stat-card">
                <div class="card-body d-flex justify-content-between align-items-center">
                    <div>
                        <h5 class="card-title"><i class="bi bi-people"></i> Cəmi Müştərilər</h5>
                        <p class="card-text fs-2 fw-bold">{{ stats.total_customers }}</p>
                    </div>
                </div>
            </div>
        </div>
        <div class="col-lg-3 col-md-6 mb-4">
            <div class="card text-white bg-success h-100 stat-card">
                <div class="card-body d-flex justify-content-between align-items-center">
                    <div>
                        <h5 class="card-title"><i class="bi bi-receipt"></i> Cəmi Fakturalar</h5>
                        <p class="card-text fs-2 fw-bold">{{ stats.total_invoices }}</p>
                    </div>
                </div>
            </div>
        </div>
        <div class="col-lg-3 col-md-6 mb-4">
            <div class="card text-white bg-warning h-100 stat-card">
                <div class="card-body d-flex justify-content-between align-items-center">
                    <div>
                        <h5 class="card-title"><i class="bi bi-currency-dollar"></i> Ödənilməmiş Məbləğ</h5>
                        <p class="card-text fs-2 fw-bold">{{ "%.2f"|format(stats.unpaid_amount or 0) }} AZN</p>
                    </div>
                </div>
            </div>
        </div>
        <div class="col-lg-3 col-md-6 mb-4">
            <div class="card text-white bg-info h-100 stat-card">
                <div class="card-body d-flex justify-content-between align-items-center">
                    <div>
                        <h5 class="card-title"><i class="bi bi-box-seam"></i> Cəmi Məhsullar</h5>
                        <p class="card-text fs-2 fw-bold">{{ stats.total_items }}</p>
                    </div>
                </div>
            </div>
        </div>
    </div>
    <!-- Detailed Stats Row -->
    <div class="row">
        <div class="col-lg-3 col-md-6 mb-4">
            <div class="card text-white bg-dark h-100 stat-card">
                <div class="card-body">
                    <div class="d-flex justify-content-between align-items-center">
                        <div>
                            <h5 class="card-title">Ümumi Gəlir</h5>
                            <p class="card-text fs-4">{{ "%.2f"|format(stats.total_revenue or 0) }} AZN</p>
                        </div>
                        <i class="bi bi-cash-coin fs-1 text-white-50"></i>
                    </div>
                </div>
            </div>
        </div>
        <div class="col-lg-3 col-md-6 mb-4">
            <div class="card text-white bg-secondary h-100 stat-card">
                <div class="card-body">
                     <div class="d-flex justify-content-between align-items-center">
                        <div>
                            <h5 class="card-title">Gözləyən Təkliflər</h5>
                            <p class="card-text fs-4">{{ stats.pending_proposals }}</p>
                        </div>
                        <i class="bi bi-file-earmark-text fs-1 text-white-50"></i>
                    </div>
                </div>
            </div>
        </div>
        <div class="col-lg-3 col-md-6 mb-4">
            <div class="card text-white bg-danger h-100 stat-card">
                <div class="card-body">
                    <div class="d-flex justify-content-between align-items-center">
                        <div>
                            <h5 class="card-title">Açıq Sifarişlər</h5>
                            <p class="card-text fs-4">{{ stats.open_sales_orders }}</p>
                        </div>
                        <i class="bi bi-cart-check fs-1 text-white-50"></i>
                    </div>
                </div>
            </div>
        </div>
        <div class="col-lg-3 col-md-6 mb-4">
            <div class="card text-white" style="background-color: #6f42c1;" h-100 stat-card">
                <div class="card-body">
                    <div class="d-flex justify-content-between align-items-center">
                        <div>
                            <h5 class="card-title">Cəmi Təchizatçılar</h5>
                            <p class="card-text fs-4">{{ stats.total_vendors }}</p>
                        </div>
                        <i class="bi bi-truck fs-1 text-white-50"></i>
                    </div>
                </div>
            </div>
        </div>
    </div>
    <!-- Recent Invoices Table -->
    <div class="card mt-4">
        <div class="card-header">
            Son Ödəniş Tapşırıqları (Fakturalar)
        </div>
        <div class="card-body">
            <table class="table table-hover">
                <thead>
                    <tr><th>Faktura #</th><th>Müştəri</th><th>Tarix</th><th>Məbləğ</th><th>Status</th></tr>
                </thead>
                <tbody>
                {% for invoice in recent_invoices %}
                    <tr>
                        <td><a href="{{ url_for('view_invoice', id=invoice.id) }}">{{ invoice.invoice_number }}</a></td>
                        <td>{{ invoice.customer.company_name or invoice.customer.full_name }}</td>
                        <td>{{ invoice.invoice_date.strftime('%d-%m-%Y') }}</td>
                        <td>{{ "%.2f"|format(invoice.total_amount) }} AZN</td>
                        <td>
                            {% if invoice.status == 'Paid' %}
                                <span class="badge bg-success">Ödənilib</span>
                            {% elif invoice.status == 'Unpaid' %}
                                <span class="badge bg-warning">Ödənilməyib</span>
                            {% else %}
                                <span class="badge bg-danger">{{ invoice.status }}</span>
                            {% endif %}
                        </td>
                    </tr>
                {% else %}
                <tr><td colspan="5" class="text-center">Heç bir faktura tapılmadı.</td></tr>
                {% endfor %}
                </tbody>
            </table>
        </div>
    </div>
</div>
"""

REPORTS_PAGE_HTML = """
<div class="container-fluid">
    <h1 class="h2 mb-4">Hesabatlar</h1>
    <div class="card">
        <div class="card-header">
            <h3>Mənfəət və Zərər Hesabatı</h3>
        </div>
        <div class="card-body">
            <table class="table table-bordered">
                <tbody>
                    <tr>
                        <td>Ümumi Gəlir (Ödənilmiş Fakturalar)</td>
                        <td class="text-end fs-5 text-success"><strong>{{ "%.2f"|format(report.total_revenue or 0) }} AZN</strong></td>
                    </tr>
                    <tr>
                        <td>Satılan Malların Dəyəri (COGS)</td>
                        <td class="text-end fs-5 text-danger"><strong>- {{ "%.2f"|format(report.cogs or 0) }} AZN</strong></td>
                    </tr>
                    <tr class="table-primary">
                        <td class="fw-bold">Ümumi Mənfəət</td>
                        <td class="text-end fs-4 fw-bold">{{ "%.2f"|format(report.gross_profit or 0) }} AZN</td>
                    </tr>
                </tbody>
            </table>
        </div>
        <div class="card-footer text-muted">
            Bu hesabat yalnız statusu "Paid" olan fakturalar və onlara bağlı məhsulların alış qiymətləri əsasında hesablanmışdır.
        </div>
    </div>
</div>
"""

# Ümumi siyahı və forma səhifələri üçün şablonlar
LIST_PAGE_HTML = """
<div class="d-flex justify-content-between align-items-center mb-4">
    <h1 class="h2">{{ title }}</h1>
    <a href="{{ add_url }}" class="btn btn-primary"><i class="bi bi-plus-circle"></i> Yeni Əlavə Et</a>
</div>
<div class="card">
    <div class="card-body">
        <div class="table-responsive">
            <table class="table table-hover">
                <thead>
                    <tr>
                        {% for header in headers %}
                            <th>{{ header }}</th>
                        {% endfor %}
                        <th>Əməliyyatlar</th>
                    </tr>
                </thead>
                <tbody>
                    {% for row in rows %}
                    <tr>
                        {% for cell in row.cells %}
                            <td>{{ cell | safe }}</td>
                        {% endfor %}
                        <td>
                            {% if row.view_url %}
                                <a href="{{ row.view_url }}" class="btn btn-sm btn-info" title="Bax"><i class="bi bi-eye"></i></a>
                            {% endif %}
                            <a href="{{ row.edit_url }}" class="btn btn-sm btn-warning" title="Redaktə et"><i class="bi bi-pencil-square"></i></a>
                            {% if current_user.role == 'admin' %}
                            <a href="{{ row.delete_url }}" class="btn btn-sm btn-danger" onclick="return confirm('Silmək istədiyinizə əminsiniz?');" title="Sil"><i class="bi bi-trash"></i></a>
                            {% endif %}
                        </td>
                    </tr>
                    {% else %}
                    <tr>
                        <td colspan="{{ headers|length + 1 }}" class="text-center">Məlumat tapılmadı.</td>
                    </tr>
                    {% endfor %}
                </tbody>
            </table>
        </div>
    </div>
</div>
"""

FORM_PAGE_HTML = """
<h1 class="h2 mb-4">{{ title }}</h1>
<div class="card">
    <div class="card-body">
        <form method="POST" action="">
            {{ form_fields | safe }}
            <button type="submit" class="btn btn-success"><i class="bi bi-check-circle"></i> Yadda Saxla</button>
            <a href="{{ back_url }}" class="btn btn-secondary"><i class="bi bi-x-circle"></i> Ləğv Et</a>
        </form>
    </div>
</div>
{{ extra_js | safe if extra_js }}
"""


# PDF üçün xüsusi şablon (çap versiyası)
PDF_TEMPLATE_BASE = """
<!doctype html>
<html>
<head>
    <meta charset="utf-8">
    <title>{{ title }}</title>
    <style>
        @import url('https://fonts.googleapis.com/css2?family=DejaVu+Sans&display=swap');
        body { font-family: 'DejaVu Sans', sans-serif; font-size: 12px; color: #333; }
        .container { padding: 20px; }
        h1 { font-size: 24px; text-align: center; margin-bottom: 20px; color: #000; }
        table { width: 100%; border-collapse: collapse; margin-top: 20px; }
        th, td { border: 1px solid #ccc; padding: 8px; text-align: left; }
        th { background-color: #f2f2f2; }
        .header-info { display: flex; justify-content: space-between; margin-bottom: 40px; }
        .header-info div { width: 48%; }
        .text-end { text-align: right; }
        tfoot strong { font-size: 14px; }
    </style>
</head>
<body>
    <div class="container">
        <h1>{{ doc_type }} #{{ doc_number }}</h1>
        <div class="header-info">
            <div>
                <h4>{{ 'Kimdən' if doc_type != 'Alış Sifarişi' else 'Kimə' }}:</h4>
                <p><strong>Sizin Şirkət</strong><br>Bakı, Azərbaycan<br>info@sirket.az</p>
            </div>
            <div class="text-end">
                <h4>{{ 'Kimə' if doc_type != 'Alış Sifarişi' else 'Kimdən' }}:</h4>
                <p><strong>{{ partner.company_name or partner.full_name }}</strong><br>{{ partner.address or '' }}<br>{{ partner.email or '' }}</p>
            </div>
        </div>
        <div class="header-info">
            <div>
                <p><strong>{{ doc_date_label }}:</strong> {{ main_date.strftime('%d-%m-%Y') }}</p>
                <p><strong>{{ sub_date_label }}:</strong> {{ sub_date.strftime('%d-%m-%Y') if sub_date }}</p>
            </div>
             <div class="text-end">
                <p><strong>Status:</strong> {{ status }}</p>
            </div>
        </div>
        <table>
            <thead>
                <tr>
                    <th>Məhsul/Xidmət</th>
                    <th class="text-end">Miqdar</th>
                    <th class="text-end">Qiymət</th>
                    <th class="text-end">Vergi (%)</th>
                    <th class="text-end">Cəm</th>
                </tr>
            </thead>
            <tbody>
                {% for item in items %}
                    {% set line_total = item.quantity * item.price %}
                    {% set tax_amount = line_total * (item.tax / 100) %}
                    {% set total_with_tax = line_total + tax_amount %}
                    <tr>
                        <td>{{ item.item.name }}</td>
                        <td class="text-end">{{ item.quantity }}</td>
                        <td class="text-end">{{ "%.2f"|format(item.price) }} AZN</td>
                        <td class="text-end">{{ "%.2f"|format(item.tax) }}%</td>
                        <td class="text-end">{{ "%.2f"|format(total_with_tax) }} AZN</td>
                    </tr>
                {% endfor %}
            </tbody>
            <tfoot>
                <tr>
                    <td colspan="4" class="text-end"><strong>Yekun Məbləğ:</strong></td>
                    <td class="text-end"><strong>{{ "%.2f"|format(total_amount) }} AZN</strong></td>
                </tr>
            </tfoot>
        </table>
        {% if notes %}
        <div style="margin-top: 20px;">
            <strong>Qeydlər:</strong>
            <p>{{ notes }}</p>
        </div>
        {% endif %}
    </div>
</body>
</html>
"""

# Sənədlərə baxış üçün ümumi şablon
VIEW_DOC_HTML = """
<div class="d-flex justify-content-between align-items-center mb-4 no-print">
    <h1 class="h2">{{ doc_type }} #{{ doc.order_number or doc.invoice_number or doc.proposal_number }}</h1>
    <div>
        <a href="{{ pdf_url }}" class="btn btn-danger"><i class="bi bi-file-earmark-pdf"></i> PDF Yüklə</a>
        <a href="#" class="btn btn-secondary" onclick="window.print();"><i class="bi bi-printer"></i> Çap Et</a>
        {% if doc_type == 'Faktura' and doc.status == 'Unpaid' %}
        <a href="{{ url_for('mark_invoice_paid', id=doc.id) }}" class="btn btn-success"><i class="bi bi-check-all"></i> Ödənildi kimi qeyd et</a>
        {% endif %}
    </div>
</div>
<div class="card p-4">
    <div class="row mb-4">
        <div class="col-md-6">
            <h4>{{ 'Kimdən' if doc_type != 'Alış Sifarişi' else 'Kimə' }}:</h4>
            <p class="mb-0"><strong>Sizin Şirkət</strong></p>
            <p class="mb-0">Bakı, Azərbaycan</p>
            <p class="mb-0">info@sirket.az</p>
        </div>
        <div class="col-md-6 text-md-end">
            <h4>{{ 'Kimə' if doc_type != 'Alış Sifarişi' else 'Kimdən' }}:</h4>
            <p class="mb-0"><strong>{{ partner.company_name or partner.full_name }}</strong></p>
            <p class="mb-0">{{ partner.address or '' }}</p>
            <p class="mb-0">{{ partner.email or '' }}</p>
        </div>
    </div>
    <div class="row mb-4">
        <div class="col-md-6">
            <p class="mb-0"><strong>{{ doc_date_label }}:</strong> {{ main_date.strftime('%d-%m-%Y') }}</p>
            <p class="mb-0"><strong>{{ sub_date_label }}:</strong> {{ sub_date.strftime('%d-%m-%Y') if sub_date }}</p>
        </div>
        <div class="col-md-6 text-md-end">
            <p class="mb-0"><strong>Status:</strong> {{ status_badge | safe }}</p>
        </div>
    </div>
    <table class="table table-bordered">
        <thead class="table-dark">
            <tr><th>Məhsul/Xidmət</th><th class="text-end">Miqdar</th><th class="text-end">Qiymət</th><th class="text-end">Vergi (%)</th><th class="text-end">Cəm</th></tr>
        </thead>
        <tbody>
            {% for item in doc.items %}
                {% set line_total = item.quantity * item.price %}{% set tax_amount = line_total * (item.tax / 100) %}{% set total_with_tax = line_total + tax_amount %}
                <tr>
                    <td>{{ item.item.name }}</td>
                    <td class="text-end">{{ item.quantity }}</td>
                    <td class="text-end">{{ "%.2f"|format(item.price) }} AZN</td>
                    <td class="text-end">{{ "%.2f"|format(item.tax) }}%</td>
                    <td class="text-end">{{ "%.2f"|format(total_with_tax) }} AZN</td>
                </tr>
            {% endfor %}
        </tbody>
        <tfoot>
            <tr><td colspan="4" class="text-end"><strong>Yekun Məbləğ:</strong></td><td class="text-end"><strong>{{ "%.2f"|format(doc.total_amount) }} AZN</strong></td></tr>
        </tfoot>
    </table>
    {% if doc.notes %}<div class="mt-4"><strong>Qeydlər:</strong><p>{{ doc.notes }}</p></div>{% endif %}
</div>
"""

# -----------------------------------------------------------------------------
# KÖMƏKÇİ FUNKSİYALAR
# -----------------------------------------------------------------------------
def generate_form_fields(fields, item=None):
    html = ""
    for field in fields:
        field_type = field.get('type', 'text')
        name = field['name']
        label = field['label']
        value = getattr(item, name, '') if item else field.get('default', '')
        if isinstance(value, datetime.date): value = value.strftime('%Y-%m-%d')
        options = field.get('options', [])
        html += f'<div class="mb-3"><label for="{name}" class="form-label">{label}</label>'
        if field_type == 'textarea':
            html += f'<textarea class="form-control" id="{name}" name="{name}">{value}</textarea>'
        elif field_type == 'select':
            html += f'<select class="form-select" id="{name}" name="{name}">'
            for opt_val, opt_label in options:
                selected = 'selected' if str(opt_val) == str(value) else ''
                html += f'<option value="{opt_val}" {selected}>{opt_label}</option>'
            html += '</select>'
        else:
            html += f'<input type="{field_type}" class="form-control" id="{name}" name="{name}" value="{value}">'
        html += '</div>'
    return html

def render_page(template_html, title, **context):
    content = render_template_string(template_html, **context)
    return render_template_string(BASE_TEMPLATE, title=title, content=content, request=request, **context)

# -----------------------------------------------------------------------------
# ROUTES (SƏHİFƏLƏR)
# -----------------------------------------------------------------------------

# --- Authentication Routes ---
@app.route('/login', methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        return redirect(url_for('dashboard'))
    if request.method == 'POST':
        user = User.query.filter_by(username=request.form['username']).first()
        if user and user.check_password(request.form['password']):
            login_user(user)
            return redirect(url_for('dashboard'))
        else:
            flash('İstifadəçi adı və ya şifrə yanlışdır.', 'danger')
    return render_template_string(LOGIN_TEMPLATE)

@app.route('/register', methods=['GET', 'POST'])
def register():
    if current_user.is_authenticated:
        return redirect(url_for('dashboard'))
    if request.method == 'POST':
        if User.query.filter_by(username=request.form['username']).first():
            flash('Bu istifadəçi adı artıq mövcuddur.', 'warning')
            return redirect(url_for('register'))
        
        new_user = User(username=request.form['username'])
        new_user.set_password(request.form['password'])
        if User.query.count() == 0:
            new_user.role = 'admin'
        else:
            new_user.role = 'user'
        
        db.session.add(new_user)
        db.session.commit()
        flash('Qeydiyyat uğurla tamamlandı! İndi daxil ola bilərsiniz.', 'success')
        return redirect(url_for('login'))
    return render_template_string(LOGIN_TEMPLATE.replace("Giriş", "Qeydiyyat").replace("Daxil Ol", "Qeydiyyatdan Keç").replace("qeydiyyatdan keçin", "daxil olun").replace(url_for('register'), url_for('login')))


@app.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect(url_for('login'))

# --- Main Routes ---
@app.route('/')
@login_required
def dashboard():
    stats = {
        # Row 1 (from image)
        'total_customers': db.session.query(func.count(Customer.id)).scalar() or 0,
        'total_invoices': db.session.query(func.count(Invoice.id)).scalar() or 0,
        'unpaid_amount': db.session.query(func.sum(Invoice.total_amount)).filter(Invoice.status == 'Unpaid').scalar() or 0.0,
        'total_items': db.session.query(func.count(Item.id)).scalar() or 0,
        # Row 2 (detailed)
        'total_revenue': db.session.query(func.sum(Invoice.total_amount)).filter(Invoice.status == 'Paid').scalar() or 0.0,
        'pending_proposals': Proposal.query.filter_by(status='Pending').count(),
        'open_sales_orders': SalesOrder.query.filter(SalesOrder.status.in_(['Pending', 'Confirmed'])).count(),
        'total_vendors': db.session.query(func.count(Vendor.id)).scalar() or 0,
    }
    
    recent_invoices = Invoice.query.order_by(Invoice.invoice_date.desc()).limit(5).all()

    return render_page(DASHBOARD_HTML, title="İdarə Paneli", stats=stats, recent_invoices=recent_invoices)

@app.route('/reports')
@login_required
def reports():
    # Mənfəət və Zərər Hesabatı
    total_revenue = db.session.query(func.sum(Invoice.total_amount)).filter(Invoice.status == 'Paid').scalar() or 0.0
    
    # Satılan Malların Dəyərinin Hesablanması (COGS)
    paid_invoice_items = db.session.query(InvoiceItem).join(Invoice).filter(Invoice.status == 'Paid').all()
    cogs = 0.0
    for inv_item in paid_invoice_items:
        # Hər satılan məhsulun alış qiymətini tapırıq
        item_cost = inv_item.item.purchase_price
        cogs += item_cost * inv_item.quantity
        
    gross_profit = total_revenue - cogs
    
    report_data = {
        'total_revenue': total_revenue,
        'cogs': cogs,
        'gross_profit': gross_profit
    }
    
    return render_page(REPORTS_PAGE_HTML, title="Hesabatlar", report=report_data)


# --- Customers Routes ---
@app.route('/customers')
@login_required
def list_customers():
    customers = Customer.query.all()
    rows = [
        {'cells': [c.full_name, c.company_name, c.email, c.phone], 'edit_url': url_for('edit_customer', id=c.id), 'delete_url': url_for('delete_customer', id=c.id)} 
        for c in customers
    ]
    return render_page(LIST_PAGE_HTML, title="Müştərilər", headers=["Ad Soyad", "Şirkət", "Email", "Telefon"], rows=rows, add_url=url_for('add_customer'))

@app.route('/customers/add', methods=['GET', 'POST'])
@login_required
def add_customer():
    if request.method == 'POST':
        new_customer = Customer(**request.form)
        db.session.add(new_customer)
        db.session.commit()
        flash("Yeni müştəri uğurla əlavə edildi.", "success")
        return redirect(url_for('list_customers'))
    fields = [
        {'name': 'full_name', 'label': 'Ad Soyad'}, {'name': 'company_name', 'label': 'Şirkət Adı'},
        {'name': 'email', 'label': 'Email', 'type': 'email'}, {'name': 'phone', 'label': 'Telefon'},
        {'name': 'address', 'label': 'Ünvan', 'type': 'textarea'}, {'name': 'contact_person', 'label': 'Əlaqədar Şəxs'},
        {'name': 'billing_address', 'label': 'Hüquqi Ünvan', 'type': 'textarea'}, {'name': 'website', 'label': 'Vebsayt'},
    ]
    return render_page(FORM_PAGE_HTML, title="Yeni Müştəri", form_fields=generate_form_fields(fields), back_url=url_for('list_customers'))

@app.route('/customers/edit/<int:id>', methods=['GET', 'POST'])
@login_required
def edit_customer(id):
    customer = Customer.query.get_or_404(id)
    if request.method == 'POST':
        for key, value in request.form.items():
            setattr(customer, key, value)
        db.session.commit()
        flash("Müştəri məlumatları yeniləndi.", "success")
        return redirect(url_for('list_customers'))
    fields = [
        {'name': 'full_name', 'label': 'Ad Soyad'}, {'name': 'company_name', 'label': 'Şirkət Adı'},
        {'name': 'email', 'label': 'Email', 'type': 'email'}, {'name': 'phone', 'label': 'Telefon'},
        {'name': 'address', 'label': 'Ünvan', 'type': 'textarea'}, {'name': 'contact_person', 'label': 'Əlaqədar Şəxs'},
        {'name': 'billing_address', 'label': 'Hüquqi Ünvan', 'type': 'textarea'}, {'name': 'website', 'label': 'Vebsayt'},
    ]
    return render_page(FORM_PAGE_HTML, title="Müştərini Redaktə Et", form_fields=generate_form_fields(fields, customer), back_url=url_for('list_customers'))

@app.route('/customers/delete/<int:id>')
@login_required
@roles_required('admin')
def delete_customer(id):
    customer = Customer.query.get_or_404(id)
    db.session.delete(customer)
    db.session.commit()
    flash(f"'{customer.full_name}' adlı müştəri silindi.", "success")
    return redirect(url_for('list_customers'))

# --- Vendors Routes ---
@app.route('/vendors')
@login_required
def list_vendors():
    vendors = Vendor.query.all()
    rows = [
        {'cells': [v.full_name, v.company_name, v.email, v.phone], 'edit_url': url_for('edit_vendor', id=v.id), 'delete_url': url_for('delete_vendor', id=v.id)}
        for v in vendors
    ]
    return render_page(LIST_PAGE_HTML, title="Təchizatçılar", headers=["Ad Soyad", "Şirkət", "Email", "Telefon"], rows=rows, add_url=url_for('add_vendor'))

@app.route('/vendors/add', methods=['GET', 'POST'])
@login_required
def add_vendor():
    if request.method == 'POST':
        new_vendor = Vendor(**request.form)
        db.session.add(new_vendor)
        db.session.commit()
        flash("Yeni təchizatçı uğurla əlavə edildi.", "success")
        return redirect(url_for('list_vendors'))
    fields = [
        {'name': 'full_name', 'label': 'Ad Soyad'}, {'name': 'company_name', 'label': 'Şirkət Adı'},
        {'name': 'email', 'label': 'Email', 'type': 'email'}, {'name': 'phone', 'label': 'Telefon'},
        {'name': 'address', 'label': 'Ünvan', 'type': 'textarea'}, {'name': 'contact_person', 'label': 'Əlaqədar Şəxs'},
    ]
    return render_page(FORM_PAGE_HTML, title="Yeni Təchizatçı", form_fields=generate_form_fields(fields), back_url=url_for('list_vendors'))

@app.route('/vendors/edit/<int:id>', methods=['GET', 'POST'])
@login_required
def edit_vendor(id):
    vendor = Vendor.query.get_or_404(id)
    if request.method == 'POST':
        for key, value in request.form.items():
            setattr(vendor, key, value)
        db.session.commit()
        flash("Təchizatçı məlumatları yeniləndi.", "success")
        return redirect(url_for('list_vendors'))
    fields = [
        {'name': 'full_name', 'label': 'Ad Soyad'}, {'name': 'company_name', 'label': 'Şirkət Adı'},
        {'name': 'email', 'label': 'Email', 'type': 'email'}, {'name': 'phone', 'label': 'Telefon'},
        {'name': 'address', 'label': 'Ünvan', 'type': 'textarea'}, {'name': 'contact_person', 'label': 'Əlaqədar Şəxs'},
    ]
    return render_page(FORM_PAGE_HTML, title="Təchizatçını Redaktə Et", form_fields=generate_form_fields(fields, vendor), back_url=url_for('list_vendors'))

@app.route('/vendors/delete/<int:id>')
@login_required
@roles_required('admin')
def delete_vendor(id):
    vendor = Vendor.query.get_or_404(id)
    db.session.delete(vendor)
    db.session.commit()
    flash(f"'{vendor.full_name}' adlı təchizatçı silindi.", "success")
    return redirect(url_for('list_vendors'))

# --- Items Routes ---
@app.route('/items')
@login_required
def list_items():
    items = Item.query.all()
    rows = [
        {'cells': [i.name, i.item_type, i.category, f"{i.sale_price:.2f} AZN", f"{i.purchase_price:.2f} AZN"], 'edit_url': url_for('edit_item', id=i.id), 'delete_url': url_for('delete_item', id=i.id)}
        for i in items
    ]
    return render_page(LIST_PAGE_HTML, title="Məhsullar və Xidmətlər", headers=["Ad", "Növ", "Kateqoriya", "Satış Qiyməti", "Alış Qiyməti"], rows=rows, add_url=url_for('add_item'))

@app.route('/items/add', methods=['GET', 'POST'])
@login_required
def add_item():
    if request.method == 'POST':
        new_item = Item(**request.form)
        db.session.add(new_item)
        db.session.commit()
        flash("Yeni məhsul/xidmət uğurla əlavə edildi.", "success")
        return redirect(url_for('list_items'))
    fields = [
        {'name': 'name', 'label': 'Məhsul/Xidmət Adı'}, {'name': 'item_type', 'label': 'Növ', 'type': 'select', 'options': [('Goods', 'Məhsul'), ('Service', 'Xidmət')]},
        {'name': 'unit_type', 'label': 'Ölçü Vahidi (ədəd, kq, metr)'}, {'name': 'category', 'label': 'Kateqoriya (IT, Qida, İnşaat)'},
        {'name': 'sale_price', 'label': 'Satış Qiyməti (AZN)', 'type': 'number', 'default': '0.00'}, {'name': 'sale_tax', 'label': 'Satış Vergisi (%)', 'type': 'number', 'default': '18.0'},
        {'name': 'purchase_price', 'label': 'Alış Qiyməti (AZN)', 'type': 'number', 'default': '0.00'}, {'name': 'purchase_tax', 'label': 'Alış Vergisi (%)', 'type': 'number', 'default': '18.0'},
        {'name': 'warranty_time', 'label': 'Zəmanət Müddəti'}, {'name': 'description', 'label': 'Təsvir', 'type': 'textarea'},
    ]
    return render_page(FORM_PAGE_HTML, title="Yeni Məhsul/Xidmət", form_fields=generate_form_fields(fields), back_url=url_for('list_items'))

@app.route('/items/edit/<int:id>', methods=['GET', 'POST'])
@login_required
def edit_item(id):
    item = Item.query.get_or_404(id)
    if request.method == 'POST':
        for key, value in request.form.items():
            setattr(item, key, value)
        db.session.commit()
        flash("Məhsul/xidmət məlumatları yeniləndi.", "success")
        return redirect(url_for('list_items'))
    fields = [
        {'name': 'name', 'label': 'Məhsul/Xidmət Adı'}, {'name': 'item_type', 'label': 'Növ', 'type': 'select', 'options': [('Goods', 'Məhsul'), ('Service', 'Xidmət')]},
        {'name': 'unit_type', 'label': 'Ölçü Vahidi (ədəd, kq, metr)'}, {'name': 'category', 'label': 'Kateqoriya (IT, Qida, İnşaat)'},
        {'name': 'sale_price', 'label': 'Satış Qiyməti (AZN)', 'type': 'number'}, {'name': 'sale_tax', 'label': 'Satış Vergisi (%)', 'type': 'number'},
        {'name': 'purchase_price', 'label': 'Alış Qiyməti (AZN)', 'type': 'number'}, {'name': 'purchase_tax', 'label': 'Alış Vergisi (%)', 'type': 'number'},
        {'name': 'warranty_time', 'label': 'Zəmanət Müddəti'}, {'name': 'description', 'label': 'Təsvir', 'type': 'textarea'},
    ]
    return render_page(FORM_PAGE_HTML, title="Məhsulu Redaktə Et", form_fields=generate_form_fields(fields, item), back_url=url_for('list_items'))

@app.route('/items/delete/<int:id>')
@login_required
@roles_required('admin')
def delete_item(id):
    item = Item.query.get_or_404(id)
    db.session.delete(item)
    db.session.commit()
    flash(f"'{item.name}' adlı məhsul/xidmət silindi.", "success")
    return redirect(url_for('list_items'))

# --- Invoices Routes ---
@app.route('/invoices')
@login_required
def list_invoices():
    invoices = Invoice.query.order_by(Invoice.invoice_date.desc()).all()
    rows = []
    for i in invoices:
        status_badge = {'Paid': '<span class="badge bg-success">Ödənilib</span>', 'Unpaid': '<span class="badge bg-warning">Ödənilməyib</span>', 'Overdue': '<span class="badge bg-danger">Gecikdirilib</span>'}.get(i.status, f'<span class="badge bg-secondary">{i.status}</span>')
        rows.append({'cells': [i.invoice_number, i.customer.company_name or i.customer.full_name, i.invoice_date.strftime('%d-%m-%Y'), f"{i.total_amount:.2f} AZN", status_badge], 'view_url': url_for('view_invoice', id=i.id), 'edit_url': url_for('edit_invoice', id=i.id), 'delete_url': url_for('delete_invoice', id=i.id)})
    return render_page(LIST_PAGE_HTML, title="Fakturalar", headers=["#", "Müştəri", "Tarix", "Məbləğ", "Status"], rows=rows, add_url=url_for('add_invoice'))

@app.route('/invoices/add', methods=['GET', 'POST'])
@login_required
def add_invoice():
    if request.method == 'POST':
        form = request.form
        due_date = datetime.datetime.strptime(form['due_date'], '%Y-%m-%d').date() if form['due_date'] else None
        last_invoice = Invoice.query.order_by(Invoice.id.desc()).first()
        new_invoice_num = f"INV-{(last_invoice.id if last_invoice else 0) + 1:05d}"
        new_invoice = Invoice(invoice_number=new_invoice_num, customer_id=form['customer_id'], invoice_date=datetime.datetime.strptime(form['invoice_date'], '%Y-%m-%d').date(), due_date=due_date, status='Unpaid', notes=form['notes'])
        total_amount = 0
        for i in range(len(form.getlist('item_id[]'))):
            item_id, quantity = form.getlist('item_id[]')[i], int(form.getlist('quantity[]')[i])
            item = Item.query.get(item_id)
            price, tax = item.sale_price, item.sale_tax
            total_amount += (price * quantity) * (1 + tax / 100)
            invoice_item = InvoiceItem(invoice=new_invoice, item_id=item_id, quantity=quantity, price=price, tax=tax)
            db.session.add(invoice_item)
        new_invoice.total_amount = total_amount
        db.session.add(new_invoice)
        db.session.commit()
        flash("Yeni faktura uğurla yaradıldı.", "success")
        return redirect(url_for('list_invoices'))
    
    customers = [(c.id, c.company_name or c.full_name) for c in Customer.query.all()]
    items = Item.query.all()
    form_html = f"""
        <div class="row">
            <div class="col-md-6">{generate_form_fields([{'name': 'customer_id', 'label': 'Müştəri Seçin', 'type': 'select', 'options': customers}])}</div>
            <div class="col-md-3">{generate_form_fields([{'name': 'invoice_date', 'label': 'Faktura Tarixi', 'type': 'date', 'default': datetime.date.today().strftime('%Y-%m-%d')}])}</div>
            <div class="col-md-3">{generate_form_fields([{'name': 'due_date', 'label': 'Son Ödəniş Tarixi', 'type': 'date'}])}</div>
        </div><hr><h4>Məhsullar</h4><div id="items-container"></div>
        <button type="button" class="btn btn-secondary btn-sm" id="add-item-btn"><i class="bi bi-plus"></i> Məhsul Əlavə Et</button><hr>
        {generate_form_fields([{'name': 'notes', 'label': 'Qeydlər', 'type': 'textarea'}])}
    """
    js_script = f"""
    <script>
        const itemsOptions = `{''.join([f'<option value="{i.id}">{i.name}</option>' for i in items])}`;
        document.getElementById('add-item-btn').addEventListener('click', function() {{
            const itemRow = document.createElement('div');
            itemRow.className = 'row mb-2 align-items-center item-row';
            itemRow.innerHTML = `
                <div class="col-md-7"><select class="form-select" name="item_id[]" required>${{itemsOptions}}</select></div>
                <div class="col-md-3"><input type="number" class="form-control" name="quantity[]" value="1" min="1" required></div>
                <div class="col-md-2"><button type="button" class="btn btn-danger btn-sm remove-item-btn w-100"><i class="bi bi-trash"></i> Sil</button></div>
            `;
            document.getElementById('items-container').appendChild(itemRow);
        }});
        document.getElementById('items-container').addEventListener('click', e => {{
            if (e.target.closest('.remove-item-btn')) e.target.closest('.item-row').remove();
        }});
    </script>
    """
    return render_page(FORM_PAGE_HTML, title="Yeni Faktura", form_fields=form_html, back_url=url_for('list_invoices'), extra_js=js_script)

@app.route('/invoices/edit/<int:id>')
@login_required
def edit_invoice(id):
    flash("Redaktə funksiyası hazırlanır.", "info")
    return redirect(url_for('list_invoices'))

@app.route('/invoices/delete/<int:id>')
@login_required
@roles_required('admin')
def delete_invoice(id):
    invoice = Invoice.query.get_or_404(id)
    db.session.delete(invoice)
    db.session.commit()
    flash("Faktura silindi.", "success")
    return redirect(url_for('list_invoices'))

@app.route('/invoices/view/<int:id>')
@login_required
def view_invoice(id):
    invoice = Invoice.query.get_or_404(id)
    status_badge = {'Paid': '<span class="badge bg-success fs-6">Ödənilib</span>', 'Unpaid': '<span class="badge bg-warning fs-6">Ödənilməyib</span>'}.get(invoice.status, f'<span class="badge bg-danger fs-6">{invoice.status}</span>')
    return render_page(VIEW_DOC_HTML, title=f"Faktura #{invoice.invoice_number}", doc=invoice, doc_type="Faktura", partner=invoice.customer,
                       main_date=invoice.invoice_date, sub_date=invoice.due_date, doc_date_label="Faktura Tarixi", sub_date_label="Son Ödəniş Tarixi",
                       status_badge=status_badge, pdf_url=url_for('download_invoice_pdf', id=id))

@app.route('/invoices/mark_paid/<int:id>')
@login_required
def mark_invoice_paid(id):
    invoice = Invoice.query.get_or_404(id)
    invoice.status = 'Paid'
    db.session.commit()
    flash(f"Faktura #{invoice.invoice_number} 'Ödənildi' olaraq qeyd edildi.", "success")
    return redirect(url_for('view_invoice', id=id))

# --- Proposals Routes ---
@app.route('/proposals')
@login_required
def list_proposals():
    proposals = Proposal.query.order_by(Proposal.proposal_date.desc()).all()
    rows = []
    for p in proposals:
        status_map = {'Confirmed': '<span class="badge bg-success">Təsdiqlənib</span>', 'Pending': '<span class="badge bg-warning">Gözləmədə</span>', 'Declined': '<span class="badge bg-danger">Ləğv Edilib</span>'}
        status_badge = status_map.get(p.status, f'<span class="badge bg-secondary">{p.status}</span>')
        rows.append({'cells': [p.proposal_number, p.customer.company_name or p.customer.full_name, p.proposal_date.strftime('%d-%m-%Y'), f"{p.total_amount:.2f} AZN", status_badge], 'view_url': url_for('view_proposal', id=p.id), 'edit_url': url_for('edit_proposal', id=p.id), 'delete_url': url_for('delete_proposal', id=p.id)})
    return render_page(LIST_PAGE_HTML, title="Təkliflər", headers=["#", "Müştəri", "Tarix", "Məbləğ", "Status"], rows=rows, add_url=url_for('add_proposal'))

@app.route('/proposals/add', methods=['GET', 'POST'])
@login_required
def add_proposal():
    if request.method == 'POST':
        form = request.form
        expire_date = datetime.datetime.strptime(form['expire_date'], '%Y-%m-%d').date() if form['expire_date'] else None
        last_prop = Proposal.query.order_by(Proposal.id.desc()).first()
        new_prop_num = f"PRO-{(last_prop.id if last_prop else 0) + 1:05d}"
        new_proposal = Proposal(proposal_number=new_prop_num, customer_id=form['customer_id'], proposal_date=datetime.datetime.strptime(form['proposal_date'], '%Y-%m-%d').date(), expire_date=expire_date, status=form['status'], notes=form['notes'])
        total_amount = 0
        for i in range(len(form.getlist('item_id[]'))):
            item_id, quantity = form.getlist('item_id[]')[i], int(form.getlist('quantity[]')[i])
            item = Item.query.get(item_id)
            price, tax = item.sale_price, item.sale_tax
            total_amount += (price * quantity) * (1 + tax / 100)
            prop_item = ProposalItem(proposal=new_proposal, item_id=item_id, quantity=quantity, price=price, tax=tax)
            db.session.add(prop_item)
        new_proposal.total_amount = total_amount
        db.session.add(new_proposal)
        db.session.commit()
        flash("Yeni təklif uğurla yaradıldı.", "success")
        return redirect(url_for('list_proposals'))

    customers = [(c.id, c.company_name or c.full_name) for c in Customer.query.all()]
    items = Item.query.all()
    form_html = f"""
        <div class="row">
            <div class="col-md-4">{generate_form_fields([{'name': 'customer_id', 'label': 'Müştəri Seçin', 'type': 'select', 'options': customers}])}</div>
            <div class="col-md-4">{generate_form_fields([{'name': 'status', 'label': 'Status', 'type': 'select', 'options': [('Pending', 'Gözləmədə'), ('Confirmed', 'Təsdiqlənib'), ('Declined', 'Ləğv Edilib')]}])}</div>
            <div class="col-md-2">{generate_form_fields([{'name': 'proposal_date', 'label': 'Təklif Tarixi', 'type': 'date', 'default': datetime.date.today().strftime('%Y-%m-%d')}])}</div>
            <div class="col-md-2">{generate_form_fields([{'name': 'expire_date', 'label': 'Etibarlılıq Tarixi', 'type': 'date'}])}</div>
        </div><hr><h4>Məhsullar</h4><div id="items-container"></div>
        <button type="button" class="btn btn-secondary btn-sm" id="add-item-btn"><i class="bi bi-plus"></i> Məhsul Əlavə Et</button><hr>
        {generate_form_fields([{'name': 'notes', 'label': 'Qeydlər', 'type': 'textarea'}])}
    """
    js_script = f"""
    <script>
        const itemsOptions = `{''.join([f'<option value="{i.id}">{i.name}</option>' for i in items])}`;
        document.getElementById('add-item-btn').addEventListener('click', function() {{
            const itemRow = document.createElement('div');
            itemRow.className = 'row mb-2 align-items-center item-row';
            itemRow.innerHTML = `
                <div class="col-md-7"><select class="form-select" name="item_id[]" required>${{itemsOptions}}</select></div>
                <div class="col-md-3"><input type="number" class="form-control" name="quantity[]" value="1" min="1" required></div>
                <div class="col-md-2"><button type="button" class="btn btn-danger btn-sm remove-item-btn w-100"><i class="bi bi-trash"></i> Sil</button></div>
            `;
            document.getElementById('items-container').appendChild(itemRow);
        }});
        document.getElementById('items-container').addEventListener('click', e => {{
            if (e.target.closest('.remove-item-btn')) e.target.closest('.item-row').remove();
        }});
    </script>
    """
    return render_page(FORM_PAGE_HTML, title="Yeni Təklif", form_fields=form_html, back_url=url_for('list_proposals'), extra_js=js_script)

@app.route('/proposals/edit/<int:id>')
@login_required
def edit_proposal(id):
    flash("Redaktə funksiyası hazırlanır.", "info")
    return redirect(url_for('list_proposals'))

@app.route('/proposals/delete/<int:id>')
@login_required
@roles_required('admin')
def delete_proposal(id):
    proposal = Proposal.query.get_or_404(id)
    db.session.delete(proposal)
    db.session.commit()
    flash("Təklif silindi.", "success")
    return redirect(url_for('list_proposals'))


@app.route('/proposals/view/<int:id>')
@login_required
def view_proposal(id):
    proposal = Proposal.query.get_or_404(id)
    status_map = {'Confirmed': '<span class="badge bg-success fs-6">Təsdiqlənib</span>', 'Pending': '<span class="badge bg-warning fs-6">Gözləmədə</span>', 'Declined': '<span class="badge bg-danger fs-6">Ləğv Edilib</span>'}
    status_badge = status_map.get(proposal.status, f'<span class="badge bg-secondary fs-6">{proposal.status}</span>')
    return render_page(VIEW_DOC_HTML, title=f"Təklif #{proposal.proposal_number}", doc=proposal, doc_type="Təklif", partner=proposal.customer,
                       main_date=proposal.proposal_date, sub_date=proposal.expire_date, doc_date_label="Təklif Tarixi", sub_date_label="Etibarlılıq Tarixi",
                       status_badge=status_badge, pdf_url=url_for('download_proposal_pdf', id=id))

# --- Sales Orders Routes ---
@app.route('/sales_orders')
@login_required
def list_sales_orders():
    orders = SalesOrder.query.order_by(SalesOrder.order_date.desc()).all()
    rows = []
    for o in orders:
        status_map = {'Pending': '<span class="badge bg-warning">Gözləmədə</span>', 'Confirmed': '<span class="badge bg-info">Təsdiqlənib</span>', 'Shipped': '<span class="badge bg-success">Göndərilib</span>'}
        status_badge = status_map.get(o.status, f'<span class="badge bg-secondary">{o.status}</span>')
        rows.append({'cells': [o.order_number, o.customer.company_name or o.customer.full_name, o.order_date.strftime('%d-%m-%Y'), f"{o.total_amount:.2f} AZN", status_badge], 'view_url': url_for('view_sales_order', id=o.id), 'edit_url': url_for('edit_sales_order', id=o.id), 'delete_url': url_for('delete_sales_order', id=o.id)})
    return render_page(LIST_PAGE_HTML, title="Satış Sifarişləri", headers=["#", "Müştəri", "Tarix", "Məbləğ", "Status"], rows=rows, add_url=url_for('add_sales_order'))

@app.route('/sales_orders/add', methods=['GET', 'POST'])
@login_required
def add_sales_order():
    if request.method == 'POST':
        form = request.form
        delivery_date = datetime.datetime.strptime(form['delivery_date'], '%Y-%m-%d').date() if form['delivery_date'] else None
        last_order = SalesOrder.query.order_by(SalesOrder.id.desc()).first()
        new_order_num = f"SO-{(last_order.id if last_order else 0) + 1:05d}"
        new_order = SalesOrder(order_number=new_order_num, customer_id=form['customer_id'], order_date=datetime.datetime.strptime(form['order_date'], '%Y-%m-%d').date(), delivery_date=delivery_date, status=form['status'], notes=form['notes'])
        total_amount = 0
        for i in range(len(form.getlist('item_id[]'))):
            item_id, quantity = form.getlist('item_id[]')[i], int(form.getlist('quantity[]')[i])
            item = Item.query.get(item_id)
            price, tax = item.sale_price, item.sale_tax
            total_amount += (price * quantity) * (1 + tax / 100)
            order_item = SalesOrderItem(sales_order=new_order, item_id=item_id, quantity=quantity, price=price, tax=tax)
            db.session.add(order_item)
        new_order.total_amount = total_amount
        db.session.add(new_order)
        db.session.commit()
        flash("Yeni satış sifarişi uğurla yaradıldı.", "success")
        return redirect(url_for('list_sales_orders'))

    customers = [(c.id, c.company_name or c.full_name) for c in Customer.query.all()]
    items = Item.query.all()
    form_html = f"""
        <div class="row">
            <div class="col-md-4">{generate_form_fields([{'name': 'customer_id', 'label': 'Müştəri Seçin', 'type': 'select', 'options': customers}])}</div>
            <div class="col-md-4">{generate_form_fields([{'name': 'status', 'label': 'Status', 'type': 'select', 'options': [('Pending', 'Gözləmədə'), ('Confirmed', 'Təsdiqlənib'), ('Shipped', 'Göndərilib')]}])}</div>
            <div class="col-md-2">{generate_form_fields([{'name': 'order_date', 'label': 'Sifariş Tarixi', 'type': 'date', 'default': datetime.date.today().strftime('%Y-%m-%d')}])}</div>
            <div class="col-md-2">{generate_form_fields([{'name': 'delivery_date', 'label': 'Çatdırılma Tarixi', 'type': 'date'}])}</div>
        </div><hr><h4>Məhsullar</h4><div id="items-container"></div>
        <button type="button" class="btn btn-secondary btn-sm" id="add-item-btn"><i class="bi bi-plus"></i> Məhsul Əlavə Et</button><hr>
        {generate_form_fields([{'name': 'notes', 'label': 'Qeydlər', 'type': 'textarea'}])}
    """
    js_script = f"""
    <script>
        const itemsOptions = `{''.join([f'<option value="{i.id}">{i.name}</option>' for i in items])}`;
        document.getElementById('add-item-btn').addEventListener('click', function() {{
            const itemRow = document.createElement('div');
            itemRow.className = 'row mb-2 align-items-center item-row';
            itemRow.innerHTML = `
                <div class="col-md-7"><select class="form-select" name="item_id[]" required>${{itemsOptions}}</select></div>
                <div class="col-md-3"><input type="number" class="form-control" name="quantity[]" value="1" min="1" required></div>
                <div class="col-md-2"><button type="button" class="btn btn-danger btn-sm remove-item-btn w-100"><i class="bi bi-trash"></i> Sil</button></div>
            `;
            document.getElementById('items-container').appendChild(itemRow);
        }});
        document.getElementById('items-container').addEventListener('click', e => {{
            if (e.target.closest('.remove-item-btn')) e.target.closest('.item-row').remove();
        }});
    </script>
    """
    return render_page(FORM_PAGE_HTML, title="Yeni Satış Sifarişi", form_fields=form_html, back_url=url_for('list_sales_orders'), extra_js=js_script)

@app.route('/sales_orders/edit/<int:id>')
@login_required
def edit_sales_order(id):
    flash("Redaktə funksiyası hazırlanır.", "info")
    return redirect(url_for('list_sales_orders'))

@app.route('/sales_orders/delete/<int:id>')
@login_required
@roles_required('admin')
def delete_sales_order(id):
    order = SalesOrder.query.get_or_404(id)
    db.session.delete(order)
    db.session.commit()
    flash("Satış sifarişi silindi.", "success")
    return redirect(url_for('list_sales_orders'))

@app.route('/sales_orders/view/<int:id>')
@login_required
def view_sales_order(id):
    order = SalesOrder.query.get_or_404(id)
    status_map = {'Pending': '<span class="badge bg-warning fs-6">Gözləmədə</span>', 'Confirmed': '<span class="badge bg-info fs-6">Təsdiqlənib</span>', 'Shipped': '<span class="badge bg-success fs-6">Göndərilib</span>'}
    status_badge = status_map.get(order.status, f'<span class="badge bg-secondary fs-6">{order.status}</span>')
    return render_page(VIEW_DOC_HTML, title=f"Satış Sifarişi #{order.order_number}", doc=order, doc_type="Satış Sifarişi", partner=order.customer,
                       main_date=order.order_date, sub_date=order.delivery_date, doc_date_label="Sifariş Tarixi", sub_date_label="Çatdırılma Tarixi",
                       status_badge=status_badge, pdf_url=url_for('download_sales_order_pdf', id=id))

# --- Purchase Orders Routes ---
@app.route('/purchase_orders')
@login_required
def list_purchase_orders():
    orders = PurchaseOrder.query.order_by(PurchaseOrder.order_date.desc()).all()
    rows = []
    for o in orders:
        status_map = {'Ordered': '<span class="badge bg-warning">Sifariş Edilib</span>', 'Received': '<span class="badge bg-success">Qəbul Edilib</span>', 'Canceled': '<span class="badge bg-danger">Ləğv Edilib</span>'}
        status_badge = status_map.get(o.status, f'<span class="badge bg-secondary">{o.status}</span>')
        rows.append({'cells': [o.order_number, o.vendor.company_name or o.vendor.full_name, o.order_date.strftime('%d-%m-%Y'), f"{o.total_amount:.2f} AZN", status_badge], 'view_url': url_for('view_purchase_order', id=o.id), 'edit_url': url_for('edit_purchase_order', id=o.id), 'delete_url': url_for('delete_purchase_order', id=o.id)})
    return render_page(LIST_PAGE_HTML, title="Alış Sifarişləri", headers=["#", "Təchizatçı", "Tarix", "Məbləğ", "Status"], rows=rows, add_url=url_for('add_purchase_order'))

@app.route('/purchase_orders/add', methods=['GET', 'POST'])
@login_required
def add_purchase_order():
    if request.method == 'POST':
        form = request.form
        delivery_date = datetime.datetime.strptime(form['expected_delivery_date'], '%Y-%m-%d').date() if form['expected_delivery_date'] else None
        last_order = PurchaseOrder.query.order_by(PurchaseOrder.id.desc()).first()
        new_order_num = f"PO-{(last_order.id if last_order else 0) + 1:05d}"
        new_order = PurchaseOrder(order_number=new_order_num, vendor_id=form['vendor_id'], order_date=datetime.datetime.strptime(form['order_date'], '%Y-%m-%d').date(), expected_delivery_date=delivery_date, status=form['status'], notes=form['notes'])
        total_amount = 0
        for i in range(len(form.getlist('item_id[]'))):
            item_id, quantity = form.getlist('item_id[]')[i], int(form.getlist('quantity[]')[i])
            item = Item.query.get(item_id)
            price, tax = item.purchase_price, item.purchase_tax # Alış qiyməti istifadə olunur
            total_amount += (price * quantity) * (1 + tax / 100)
            order_item = PurchaseOrderItem(purchase_order=new_order, item_id=item_id, quantity=quantity, price=price, tax=tax)
            db.session.add(order_item)
        new_order.total_amount = total_amount
        db.session.add(new_order)
        db.session.commit()
        flash("Yeni alış sifarişi uğurla yaradıldı.", "success")
        return redirect(url_for('list_purchase_orders'))

    vendors = [(v.id, v.company_name or v.full_name) for v in Vendor.query.all()]
    items = Item.query.all()
    form_html = f"""
        <div class="row">
            <div class="col-md-4">{generate_form_fields([{'name': 'vendor_id', 'label': 'Təchizatçı Seçin', 'type': 'select', 'options': vendors}])}</div>
            <div class="col-md-4">{generate_form_fields([{'name': 'status', 'label': 'Status', 'type': 'select', 'options': [('Ordered', 'Sifariş Edilib'), ('Received', 'Qəbul Edilib'), ('Canceled', 'Ləğv Edilib')]}])}</div>
            <div class="col-md-2">{generate_form_fields([{'name': 'order_date', 'label': 'Sifariş Tarixi', 'type': 'date', 'default': datetime.date.today().strftime('%Y-%m-%d')}])}</div>
            <div class="col-md-2">{generate_form_fields([{'name': 'expected_delivery_date', 'label': 'Gözlənilən Tarix', 'type': 'date'}])}</div>
        </div><hr><h4>Məhsullar</h4><div id="items-container"></div>
        <button type="button" class="btn btn-secondary btn-sm" id="add-item-btn"><i class="bi bi-plus"></i> Məhsul Əlavə Et</button><hr>
        {generate_form_fields([{'name': 'notes', 'label': 'Qeydlər', 'type': 'textarea'}])}
    """
    js_script = f"""
    <script>
        const itemsOptions = `{''.join([f'<option value="{i.id}">{i.name}</option>' for i in items])}`;
        document.getElementById('add-item-btn').addEventListener('click', function() {{
            const itemRow = document.createElement('div');
            itemRow.className = 'row mb-2 align-items-center item-row';
            itemRow.innerHTML = `
                <div class="col-md-7"><select class="form-select" name="item_id[]" required>${{itemsOptions}}</select></div>
                <div class="col-md-3"><input type="number" class="form-control" name="quantity[]" value="1" min="1" required></div>
                <div class="col-md-2"><button type="button" class="btn btn-danger btn-sm remove-item-btn w-100"><i class="bi bi-trash"></i> Sil</button></div>
            `;
            document.getElementById('items-container').appendChild(itemRow);
        }});
        document.getElementById('items-container').addEventListener('click', e => {{
            if (e.target.closest('.remove-item-btn')) e.target.closest('.item-row').remove();
        }});
    </script>
    """
    return render_page(FORM_PAGE_HTML, title="Yeni Alış Sifarişi", form_fields=form_html, back_url=url_for('list_purchase_orders'), extra_js=js_script)

@app.route('/purchase_orders/edit/<int:id>')
@login_required
def edit_purchase_order(id):
    flash("Redaktə funksiyası hazırlanır.", "info")
    return redirect(url_for('list_purchase_orders'))

@app.route('/purchase_orders/delete/<int:id>')
@login_required
@roles_required('admin')
def delete_purchase_order(id):
    order = PurchaseOrder.query.get_or_404(id)
    db.session.delete(order)
    db.session.commit()
    flash("Alış sifarişi silindi.", "success")
    return redirect(url_for('list_purchase_orders'))

@app.route('/purchase_orders/view/<int:id>')
@login_required
def view_purchase_order(id):
    order = PurchaseOrder.query.get_or_404(id)
    status_map = {'Ordered': '<span class="badge bg-warning fs-6">Sifariş Edilib</span>', 'Received': '<span class="badge bg-success fs-6">Qəbul Edilib</span>', 'Canceled': '<span class="badge bg-danger fs-6">Ləğv Edilib</span>'}
    status_badge = status_map.get(order.status, f'<span class="badge bg-secondary fs-6">{order.status}</span>')
    return render_page(VIEW_DOC_HTML, title=f"Alış Sifarişi #{order.order_number}", doc=order, doc_type="Alış Sifarişi", partner=order.vendor,
                       main_date=order.order_date, sub_date=order.expected_delivery_date, doc_date_label="Sifariş Tarixi", sub_date_label="Gözlənilən Tarix",
                       status_badge=status_badge, pdf_url=url_for('download_purchase_order_pdf', id=id))


# --- PDF Generation Routes ---
@app.route('/invoices/<int:id>/pdf')
@login_required
def download_invoice_pdf(id):
    if not HTML:
        flash("PDF generasiyası üçün WeasyPrint kitabxanası quraşdırılmayıb.", "danger")
        return redirect(url_for('view_invoice', id=id))
    invoice = Invoice.query.get_or_404(id)
    rendered_html = render_template_string(PDF_TEMPLATE_BASE, title=f"Faktura {invoice.invoice_number}", doc_type="Faktura", doc_number=invoice.invoice_number, partner=invoice.customer, main_date=invoice.invoice_date, sub_date=invoice.due_date, doc_date_label="Faktura Tarixi", sub_date_label="Son Ödəniş Tarixi", status=invoice.status, items=invoice.items, total_amount=invoice.total_amount, notes=invoice.notes)
    pdf = HTML(string=rendered_html).write_pdf()
    return Response(pdf, mimetype='application/pdf', headers={'Content-Disposition': f'attachment;filename=Faktura-{invoice.invoice_number}.pdf'})

@app.route('/proposals/<int:id>/pdf')
@login_required
def download_proposal_pdf(id):
    if not HTML:
        flash("PDF generasiyası üçün WeasyPrint kitabxanası quraşdırılmayıb.", "danger")
        return redirect(url_for('view_proposal', id=id))
    proposal = Proposal.query.get_or_404(id)
    rendered_html = render_template_string(PDF_TEMPLATE_BASE, title=f"Təklif {proposal.proposal_number}", doc_type="Təklif", doc_number=proposal.proposal_number, partner=proposal.customer, main_date=proposal.proposal_date, sub_date=proposal.expire_date, doc_date_label="Təklif Tarixi", sub_date_label="Etibarlılıq Tarixi", status=proposal.status, items=proposal.items, total_amount=proposal.total_amount, notes=proposal.notes)
    pdf = HTML(string=rendered_html).write_pdf()
    return Response(pdf, mimetype='application/pdf', headers={'Content-Disposition': f'attachment;filename=Teklif-{proposal.proposal_number}.pdf'})

@app.route('/sales_orders/<int:id>/pdf')
@login_required
def download_sales_order_pdf(id):
    if not HTML:
        flash("PDF generasiyası üçün WeasyPrint kitabxanası quraşdırılmayıb.", "danger")
        return redirect(url_for('view_sales_order', id=id))
    order = SalesOrder.query.get_or_404(id)
    rendered_html = render_template_string(PDF_TEMPLATE_BASE, title=f"Satış Sifarişi {order.order_number}", doc_type="Satış Sifarişi", doc_number=order.order_number, partner=order.customer, main_date=order.order_date, sub_date=order.delivery_date, doc_date_label="Sifariş Tarixi", sub_date_label="Çatdırılma Tarixi", status=order.status, items=order.items, total_amount=order.total_amount, notes=order.notes)
    pdf = HTML(string=rendered_html).write_pdf()
    return Response(pdf, mimetype='application/pdf', headers={'Content-Disposition': f'attachment;filename=Satis-Sifarisi-{order.order_number}.pdf'})

@app.route('/purchase_orders/<int:id>/pdf')
@login_required
def download_purchase_order_pdf(id):
    if not HTML:
        flash("PDF generasiyası üçün WeasyPrint kitabxanası quraşdırılmayıb.", "danger")
        return redirect(url_for('view_purchase_order', id=id))
    order = PurchaseOrder.query.get_or_404(id)
    rendered_html = render_template_string(PDF_TEMPLATE_BASE, title=f"Alış Sifarişi {order.order_number}", doc_type="Alış Sifarişi", doc_number=order.order_number, partner=order.vendor, main_date=order.order_date, sub_date=order.expected_delivery_date, doc_date_label="Sifariş Tarixi", sub_date_label="Gözlənilən Tarix", status=order.status, items=order.items, total_amount=order.total_amount, notes=order.notes)
    pdf = HTML(string=rendered_html).write_pdf()
    return Response(pdf, mimetype='application/pdf', headers={'Content-Disposition': f'attachment;filename=Alis-Sifarisi-{order.order_number}.pdf'})


# -----------------------------------------------------------------------------
# TƏTBİQİ İŞƏ SALMA
# -----------------------------------------------------------------------------
if __name__ == '__main__':
    with app.app_context():
        db.create_all()
        if not User.query.filter_by(username='admin').first():
            print("İlk admin istifadəçisi yaradılır...")
            admin_user = User(username='admin', role='admin')
            admin_user.set_password('admin')
            db.session.add(admin_user)
            db.session.commit()
            print("İstifadəçi adı: admin, Şifrə: admin")
    app.run(debug=True)
