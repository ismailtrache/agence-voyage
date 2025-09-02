from flask import Flask, render_template, request, redirect, url_for, flash, session
import os
from werkzeug.utils import secure_filename
import json
from functools import wraps
from flask_mail import Mail, Message
from dotenv import load_dotenv

load_dotenv()

app = Flask(__name__)
app.secret_key = 'votre_cle_secrete_ici_pour_les_sessions'

# --- CONFIGURATION POUR L'ENVOI D'EMAILS ---
app.config['MAIL_SERVER'] = 'smtp.gmail.com'
app.config['MAIL_PORT'] = 465
app.config['MAIL_USERNAME'] = os.environ.get('MAIL_USERNAME')
app.config['MAIL_PASSWORD'] = os.environ.get('MAIL_PASSWORD')
app.config['MAIL_USE_TLS'] = False
app.config['MAIL_USE_SSL'] = True
mail = Mail(app)

# --- DÉTAILS DE CONNEXION ADMIN ---
ADMIN_USERNAME = 'admin'
ADMIN_PASSWORD = 'password123'

# Configuration des fichiers
UPLOAD_FOLDER = 'static/uploads'
ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif'}
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
os.makedirs(os.path.join(UPLOAD_FOLDER, 'destinations'), exist_ok=True)
DATA_FILE = 'data.json'

# --- FONCTIONS DE GESTION DES DONNÉES ---
def load_data():
    if not os.path.exists(DATA_FILE):
        initial_data = {
            'company_name': 'TRACHE TRAVEL & SERVICES',
            'logo': 'uploads/logo.jpg',
            'services': [
                {'nom': 'Réservation de Vols', 'description': 'Billets d\'avion au meilleur prix pour toutes les destinations mondiales.', 'icon': 'fa-plane-departure'},
                {'nom': 'Hôtels de Prestige', 'description': 'Sélection d\'hôtels de luxe et économiques dans le monde entier.', 'icon': 'fa-hotel'},
                {'nom': 'Circuits Sur Mesure', 'description': 'Voyages organisés et circuits personnalisés selon vos envies.', 'icon': 'fa-map-signs'},
                {'nom': 'Location de Voitures', 'description': 'Véhicules de location modernes pour tous vos déplacements.', 'icon': 'fa-car'},
                {'nom': 'Visa & Documentation', 'description': 'Assistance complète pour vos formalités administratives de voyage.', 'icon': 'fa-file-alt'},
                {'nom': 'Assurance Voyage', 'description': 'Protection complète pour voyager en toute sérénité et sécurité.', 'icon': 'fa-shield-alt'}
            ],
            'destinations': [
                {'nom': 'Paris, France', 'description': 'La ville lumière et ses monuments emblématiques.', 'prix': '€599', 'image': 'static/uploads/destinantions/paris.png'},
                {'nom': 'Dubaï, EAU', 'description': 'Luxe et modernité au cœur du désert.', 'prix': '€899', 'image': 'static/uploads/destinantions/dubai.png'},
                {'nom': 'Tokyo, Japon', 'description': 'Tradition et technologie dans la capitale nippone.', 'prix': '€1299', 'image': 'https://images.unsplash.com/photo-1542051841857-5f90071e7989?auto=format&fit=crop&w=800&q=60'},
                {'nom': 'New York, USA', 'description': 'La ville qui ne dort jamais et ses gratte-ciels.', 'prix': '€799', 'image': 'https://images.unsplash.com/photo-1496442226666-8d4d0e62e6e9?auto=format&fit=crop&w=800&q=60'},
                {'nom': 'Santorin, Grèce', 'description': 'Couchers de soleil magiques et villages blancs.', 'prix': '€750', 'image': 'static/uploads/destinantions/santorini.jpg'},
                {'nom': 'Bali, Indonésie', 'description': 'L\'île des dieux, entre plages et rizières verdoyantes.', 'prix': '€1100', 'image': 'https://images.unsplash.com/photo-1537996194471-e657df975ab4?auto=format&fit=crop&w=800&q=60'},
                {'nom': 'Rome, Italie', 'description': 'Un voyage à travers l\'histoire antique et la dolce vita.', 'prix': '€450', 'image': 'https://images.unsplash.com/photo-1552832230-c0197dd311b5?auto=format&fit=crop&w=800&q=60'},
                {'nom': 'Kyoto, Japon', 'description': 'L\'ancienne capitale impériale, ses temples et ses jardins zen.', 'prix': '€1350', 'image': 'https://images.unsplash.com/photo-1524413840807-0c3cb6fa808d?auto=format&fit=crop&w=800&q=60'},
                {'nom': 'Rio de Janeiro, Brésil', 'description': 'Entre plages iconiques, samba et paysages à couper le souffle.', 'prix': '€950', 'image': 'https://images.unsplash.com/photo-1483729558449-99ef09a8c325?auto=format&fit=crop&w=800&q=60'},
                {'nom': 'Le Caire, Égypte', 'description': 'Aux portes des pyramides, un plongeon dans l\'histoire des pharaons.', 'prix': '€680', 'image': 'static/uploads/destinantions/caire.jpg'},
                {'nom': 'Istanbul, Turquie', 'description': 'Un pont entre l\'Europe et l\'Asie, riche d\'histoire et de saveurs.', 'prix': '€480', 'image': 'https://images.unsplash.com/photo-1527838832700-5059252407fa?auto=format&fit=crop&w=800&q=60'},
                {'nom': 'Sharm El Sheikh, Égypte', 'description': 'Plongée de classe mondiale dans les eaux cristallines de la mer Rouge.', 'prix': '€550', 'image': 'static/uploads/destinantions/SharmElSheikh.jpg'},
                {'nom': 'Sousse, Tunisie', 'description': 'Combine des plages dorées avec une médina historique classée à l\'UNESCO.', 'prix': '€390', 'image': 'static/uploads/destinantions/sousse.jpg'},
                {'nom': 'Guangzhou, Chine', 'description': 'Mégapole moderne et dynamique, cœur du commerce et de la gastronomie cantonaise.', 'prix': '€850', 'image': 'static/uploads/destinantions/guangzhou.jpg'},
                {'nom': 'Toronto, Canada', 'description': 'La métropole cosmopolite du Canada, avec sa skyline iconique et sa scène culturelle vibrante.', 'prix': '€720', 'image': 'static/uploads/destinantions/toronto.jpg'}
            ],
            'contact_info': {
                'telephone': '+213 662 90 10 49 / +213 540 62 24 64',
                'email': 'trachetravelservice@gmail.com',
                'adresse': 'n°8 Rue Adda Ouled Derrer, Lot n°3 Hai Makkari, Oran, Algeria',
                'horaires': 'Dim-Jeu: 9h-18h, Sam: 9h-13h'
            },
            'why_us': [
                {'title': 'Meilleurs Prix Garantis', 'description': 'Nous négocions les meilleurs tarifs pour vous.', 'icon': 'fa-tags'},
                {'title': 'Support Client 24/7', 'description': 'Notre équipe est disponible à tout moment.', 'icon': 'fa-headset'},
                {'title': 'Destinations Mondiales', 'description': 'Explorez le monde avec nos offres exclusives.', 'icon': 'fa-globe-americas'}
            ]
        }
        with open(DATA_FILE, 'w', encoding='utf-8') as f:
            json.dump(initial_data, f, indent=4, ensure_ascii=False)
    with open(DATA_FILE, 'r', encoding='utf-8') as f:
        return json.load(f)

def save_data(data):
    with open(DATA_FILE, 'w', encoding='utf-8') as f:
        json.dump(data, f, indent=4, ensure_ascii=False)

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

def login_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'logged_in' not in session:
            return redirect(url_for('login'))
        return f(*args, **kwargs)
    return decorated_function

# --- ROUTES PUBLIQUES ---
@app.route('/')
def index():
    return render_template('index.html', data=load_data())

@app.route('/services')
def services():
    return render_template('services.html', data=load_data())

@app.route('/destinations')
def destinations():
    site_data = load_data()
    return render_template('destinations.html', data=site_data, destinations=site_data['destinations'])

@app.route('/contact')
def contact():
    return render_template('contact.html', data=load_data())

@app.route('/contact_form', methods=['POST'])
def contact_form():
    nom = request.form.get('nom')
    email = request.form.get('email')
    telephone = request.form.get('telephone')
    message = request.form.get('message')
    try:
        sujet = f"Nouveau message de {nom} pour Trache Travel"
        msg = Message(sujet, sender=app.config['MAIL_USERNAME'], recipients=[app.config['MAIL_USERNAME']])
        msg.body = f"Nom: {nom}\nEmail: {email}\nTéléphone: {telephone}\n\nMessage:\n{message}"
        mail.send(msg)
        flash(f'Merci {nom}, votre message a bien été envoyé !', 'success')
    except Exception as e:
        flash('Une erreur est survenue lors de l\'envoi du message. Veuillez vérifier les configurations.', 'danger')
        print(f"Erreur d'envoi d'email : {e}")
    return redirect(url_for('contact'))

# --- ROUTES DE CONNEXION ---
@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        if request.form['username'] == ADMIN_USERNAME and request.form['password'] == ADMIN_PASSWORD:
            session['logged_in'] = True
            return redirect(url_for('admin'))
        else:
            flash('Identifiants incorrects.', 'danger')
    return render_template('login.html')

@app.route('/logout')
def logout():
    session.pop('logged_in', None)
    return redirect(url_for('index'))

# --- ROUTES ADMIN ---
@app.route('/admin')
@login_required
def admin():
    return render_template('admin.html', data=load_data())

@app.route('/upload_logo', methods=['POST'])
@login_required
def upload_logo():
    site_data = load_data()
    if 'logo' in request.files and request.files['logo'].filename != '':
        file = request.files['logo']
        if allowed_file(file.filename):
            filename = secure_filename(file.filename)
            file.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))
            site_data['logo'] = f'uploads/{filename}'
            save_data(site_data)
            flash('Logo mis à jour !')
    return redirect(url_for('admin'))

@app.route('/admin/destination/add', methods=['POST'])
@login_required
def add_destination():
    site_data = load_data()
    new_dest = { "nom": request.form['nom'], "description": request.form['description'], "prix": request.form['prix'], "image": "" }
    if 'image' in request.files and request.files['image'].filename != '':
        file = request.files['image']
        if allowed_file(file.filename):
            filename = secure_filename(file.filename)
            dest_folder = os.path.join(app.config['UPLOAD_FOLDER'], 'destinations')
            file.save(os.path.join(dest_folder, filename))
            new_dest['image'] = f'uploads/destinations/{filename}'
    site_data['destinations'].append(new_dest)
    save_data(site_data)
    flash('Destination ajoutée !')
    return redirect(url_for('admin'))

@app.route('/admin/destination/edit/<int:index>', methods=['GET', 'POST'])
@login_required
def edit_destination(index):
    site_data = load_data()
    destination = site_data['destinations'][index]
    if request.method == 'POST':
        destination['nom'] = request.form['nom']
        destination['description'] = request.form['description']
        destination['prix'] = request.form['prix']
        if 'image' in request.files and request.files['image'].filename != '':
            file = request.files['image']
            if allowed_file(file.filename):
                filename = secure_filename(file.filename)
                dest_folder = os.path.join(app.config['UPLOAD_FOLDER'], 'destinations')
                file.save(os.path.join(dest_folder, filename))
                destination['image'] = f'uploads/destinations/{filename}'
        save_data(site_data)
        flash('Destination modifiée !')
        return redirect(url_for('admin'))
    return render_template('edit_destination.html', data=site_data, destination=destination, index=index)

@app.route('/admin/destination/delete/<int:index>')
@login_required
def delete_destination(index):
    site_data = load_data()
    if 0 <= index < len(site_data['destinations']):
        site_data['destinations'].pop(index)
        save_data(site_data)
        flash('Destination supprimée !')
    return redirect(url_for('admin'))

# NOUVELLES ROUTES POUR LE CLASSEMENT
@app.route('/admin/destination/move_up/<int:index>')
@login_required
def move_destination_up(index):
    site_data = load_data()
    if 0 < index < len(site_data['destinations']):
        site_data['destinations'][index], site_data['destinations'][index - 1] = site_data['destinations'][index - 1], site_data['destinations'][index]
        save_data(site_data)
        flash('Ordre des destinations mis à jour.')
    return redirect(url_for('admin'))

@app.route('/admin/destination/move_down/<int:index>')
@login_required
def move_destination_down(index):
    site_data = load_data()
    if 0 <= index < len(site_data['destinations']) - 1:
        site_data['destinations'][index], site_data['destinations'][index + 1] = site_data['destinations'][index + 1], site_data['destinations'][index]
        save_data(site_data)
        flash('Ordre des destinations mis à jour.')
    return redirect(url_for('admin'))

@app.route('/service/<service_name>')
def service_detail(service_name):
    site_data = load_data()
    service = next((s for s in site_data['services'] if s['nom'] == service_name), None)
    if not service:
        flash("Service introuvable.", "danger")
        return redirect(url_for('services'))
    
    # Routage conditionnel selon le service
    if service_name == "Visa & Documentation":
        return render_template('visa_service.html', data=site_data, service=service)
    elif service_name == "Assurance Voyage":
        return render_template('assurance_service.html', data=site_data, service=service)
    elif service_name == "Hôtels de Prestige":
        return render_template('hotels_service.html', data=site_data, service=service)
    else:
        return render_template('service_detail.html', data=site_data, service=service)


@app.route('/destinations')
def destinations_page():  # autre nom de fonction
    site_data = load_data()
    return render_template('destinations.html', data=site_data)


# ==============================================
# TEMPLATES HTML
# ==============================================
templates_dir = 'templates'
os.makedirs(templates_dir, exist_ok=True)

base_template = '''
<!DOCTYPE html>
<html lang="fr">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>{% block title %}{{ data.company_name }}{% endblock %}</title>
    <link href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.5.0/css/all.min.css" rel="stylesheet">
    <link href="https://fonts.googleapis.com/css2?family=Poppins:wght@300;400;500;600;700;800&display=swap" rel="stylesheet">
    <style>
        :root { --primary: #2C5B61; --secondary: #3A7C89; --accent: #EAB308; --light: #F8F9FA; --dark: #1B262C; --text-primary: #333; --text-secondary: #666; --shadow: 0 10px 30px rgba(0, 0, 0, 0.1); --border-radius: 12px; }
        * { margin: 0; padding: 0; box-sizing: border-box; }
        body { font-family: 'Poppins', sans-serif; color: var(--text-primary); background-color: #FFFFFF; overflow-x: hidden; }
        .container { max-width: 1200px; margin: 0 auto; padding: 0 1rem; }
        header { background: white; padding: 1rem 0; position: sticky; width: 100%; top: 0; z-index: 1000; box-shadow: 0 2px 15px rgba(0,0,0,0.05); }
        nav { display: flex; justify-content: space-between; align-items: center; }
        .logo-container { display: flex; align-items: center; gap: 15px; }
        .logo { width: 60px; height: 60px; border-radius: 50%; object-fit: cover; }
        .company-name { font-size: 1.5rem; font-weight: 700; color: var(--primary); }
        .nav-links { display: flex; list-style: none; gap: 1rem; align-items: center; }
        .nav-links a { color: var(--primary); text-decoration: none; font-weight: 500; padding: 0.5rem 1rem; border-radius: 25px; transition: all 0.3s ease; }
        .nav-links a:hover, .nav-links a.active { background-color: var(--primary); color: white; }
        .hamburger { display: none; font-size: 1.5rem; background: none; border: none; cursor: pointer; color: var(--primary); }
        main { min-height: 70vh; }
        .page-header { background: linear-gradient(rgba(0,0,0,0.5), rgba(0,0,0,0.5)), url('https://images.unsplash.com/photo-1501785888041-af3ef285b470?auto=format&fit=crop&w=1600&q=80') no-repeat center center/cover; padding: 4rem 0; text-align: center; color: white; }
        .page-header h1 { font-size: 2.5rem; font-weight: 700; }
        .section { padding: 4rem 0; }
        .section-light { background-color: var(--light); }
        .section-title { text-align: center; font-size: 2.2rem; font-weight: 700; color: var(--primary); margin-bottom: 3rem; position: relative; }
        .section-title::after { content: ''; position: absolute; bottom: -10px; left: 50%; transform: translateX(-50%); width: 60px; height: 4px; background-color: var(--accent); border-radius: 2px; }
        .section-subtitle { text-align: center; color: var(--text-secondary); max-width: 600px; margin: 0 auto 3rem auto; }
        footer { background-color: var(--primary); color: white; padding: 3rem 1rem; }
        .footer-content { display: grid; grid-template-columns: repeat(auto-fit, minmax(250px, 1fr)); gap: 2rem; max-width: 1200px; margin: 0 auto; }
        .footer-section h3 { color: var(--accent); margin-bottom: 1rem; }
        .footer-section p, .footer-section a { display: block; color: rgba(255,255,255,0.8); text-decoration: none; margin-bottom: 0.5rem; transition: color 0.3s; }
        .footer-section a:hover { color: var(--accent); }
        .footer-bottom { text-align: center; margin-top: 2rem; padding-top: 2rem; border-top: 1px solid var(--secondary); }
        .toast { position: fixed; bottom: -100px; left: 50%; transform: translateX(-50%); background-color: var(--primary); color: white; padding: 1rem 2rem; border-radius: 50px; box-shadow: 0 5px 15px rgba(0,0,0,0.2); z-index: 2000; transition: bottom 0.5s ease-in-out; }
        .toast.show { bottom: 30px; }
        @media (max-width: 768px) {
            .company-name { font-size: 1.2rem; }
            .hamburger { display: block; z-index: 1001; }
            .nav-links { position: fixed; top: 0; right: -100%; width: 70%; height: 100vh; background-color: white; box-shadow: -5px 0 15px rgba(0,0,0,0.1); flex-direction: column; align-items: flex-start; justify-content: flex-start; padding: 6rem 2rem 2rem; gap: 2rem; transition: right 0.4s ease-in-out; }
            .nav-links.active { right: 0; }
            .nav-links a { font-size: 1.2rem; width: 100%; }
        }
    </style>
</head>
<body>
    <header>
        <nav class="container">
            <a href="{{ url_for('index') }}" style="text-decoration: none;">
                <div class="logo-container">
                    {% if data.logo %}<img src="{{ url_for('static', filename=data.logo) }}" alt="Logo" class="logo">{% endif %}
                    <div class="company-name">{{ data.company_name }}</div>
                </div>
            </a>
            <ul class="nav-links" id="nav-links">
                <li><a href="{{ url_for('index') }}">Accueil</a></li>
                <li><a href="{{ url_for('services') }}">Services</a></li>
                <li><a href="{{ url_for('destinations') }}">Destinations</a></li>
                <li><a href="{{ url_for('contact') }}">Contact</a></li>
                <li><a href="{{ url_for('admin') }}">Admin</a></li>
            </ul>
            <button class="hamburger" id="hamburger-button"><i class="fas fa-bars"></i></button>
        </nav>
    </header>
    <main>
        {% with messages = get_flashed_messages(with_categories=true) %}
            {% if messages %}
                <div style="padding-top: 1rem; text-align: center;">
                {% for category, message in messages %}
                    <div class="alert-{{ category }}" style="background-color: #d4edda; color: #155724; padding: 1rem; border-radius: 8px; max-width: 800px; margin: 0 auto;">{{ message }}</div>
                {% endfor %}
                </div>
            {% endif %}
        {% endwith %}
        {% block content %}{% endblock %}
    </main>
    <footer>
        <div class="footer-content">
            <div class="footer-section"><h3>{{ data.company_name }}</h3><p>Votre partenaire pour des voyages inoubliables.</p></div>
            <div class="footer-section"><h3>Contact</h3><p><i class="fas fa-phone"></i> {{ data.contact_info.telephone }}</p><p><i class="fas fa-envelope"></i> {{ data.contact_info.email }}</p></div>
            <div class="footer-section"><h3>Liens Rapides</h3><a href="{{ url_for('services') }}">Services</a><a href="{{ url_for('destinations') }}">Destinations</a><a href="{{ url_for('contact') }}">Contact</a></div>
        </div>
        <div class="footer-bottom"><p>&copy; 2024 {{ data.company_name }}. Tous droits réservés.</p></div>
    </footer>
    <script>
        const hamburgerButton = document.getElementById('hamburger-button');
        const navLinks = document.getElementById('nav-links');
        const icon = hamburgerButton.querySelector('i');
        hamburgerButton.addEventListener('click', () => {
            navLinks.classList.toggle('active');
            if (navLinks.classList.contains('active')) {
                icon.classList.remove('fa-bars');
                icon.classList.add('fa-times');
            } else {
                icon.classList.remove('fa-times');
                icon.classList.add('fa-bars');
            }
        });
        document.addEventListener('DOMContentLoaded', () => {
            const quoteLinks = document.querySelectorAll('.quote-link');
            quoteLinks.forEach(link => {
                link.addEventListener('click', function(event) {
                    event.preventDefault();
                    const href = this.href;
                    let toast = document.querySelector('.toast');
                    if (!toast) {
                        toast = document.createElement('div');
                        toast.className = 'toast';
                        document.body.appendChild(toast);
                    }
                    toast.innerText = 'Pour un devis, veuillez nous contacter.';
                    setTimeout(() => { toast.classList.add('show'); }, 100);
                    setTimeout(() => {
                        toast.classList.remove('show');
                        setTimeout(() => { window.location.href = href; }, 500);
                    }, 2000);
                });
            });
        });
    </script>
</body>
</html>
'''

index_template = '''
{% extends "base.html" %}
{% block content %}
<style>
    .hero { height: 90vh; color: white; display: flex; align-items: center; justify-content: center; text-align: center; position: relative; background: linear-gradient(rgba(0,0,0,0.5), rgba(0,0,0,0.5)), url("{% if 'http' in data.destinations[8].image %}{{ data.destinations[8].image }}{% else %}{{ url_for('static', filename=data.destinations[8].image) }}{% endif %}") no-repeat center center/cover; }
    .hero-content { z-index: 2; padding: 0 1rem; }
    .hero h1 { font-size: 2.5rem; font-weight: 800; margin-bottom: 1rem; }
    .hero p { font-size: 1.1rem; margin-bottom: 2rem; }
    .search-bar { background: rgba(255, 255, 255, 0.9); backdrop-filter: blur(10px); padding: 1rem; border-radius: 50px; display: flex; align-items: center; gap: 0.5rem; box-shadow: 0 10px 40px rgba(0,0,0,0.2); max-width: 100%; margin: 2rem auto 0 auto; }
    .search-input { flex-grow: 1; border: none; background: transparent; font-size: 1rem; color: #333; padding-left: 0.5rem; }
    .search-btn { background: var(--primary); color: white; padding: 0.8rem 1.5rem; border-radius: 50px; text-decoration: none; font-weight: 600; border: none; cursor: pointer; transition: all 0.3s; }
    .services-grid, .destinations-grid, .why-us-grid { display: grid; gap: 1.5rem; grid-template-columns: 1fr; }
    @media (min-width: 576px) {
        .services-grid { grid-template-columns: repeat(auto-fit, minmax(300px, 1fr)); }
        .destinations-grid { grid-template-columns: repeat(auto-fit, minmax(280px, 1fr)); }
        .why-us-grid { grid-template-columns: repeat(auto-fit, minmax(300px, 1fr)); }
        .hero h1 { font-size: 3.5rem; }
        .hero p { font-size: 1.3rem; }
    }
    .destination-card { background: white; border-radius: var(--border-radius); overflow: hidden; box-shadow: var(--shadow); transition: all 0.3s ease; position: relative; }
    .destination-card:hover { transform: translateY(-10px); }
    .destination-card img { width: 100%; height: 350px; object-fit: cover; }
    .dest-overlay { position: absolute; top: 0; left: 0; width: 100%; height: 100%; background: linear-gradient(to top, rgba(0,0,0,0.8) 0%, transparent 100%); }
    .dest-content { position: absolute; bottom: 0; left: 0; padding: 1.5rem; color: white; width: 100%; }
    .dest-content h3 { font-size: 1.5rem; margin-bottom: 0.5rem; }
    .dest-price { position: absolute; top: 1rem; right: 1rem; background: var(--accent); color: var(--dark); padding: 0.5rem 1rem; border-radius: 50px; font-weight: 700; }
    .service-card { background: white; padding: 2rem; border-radius: var(--border-radius); text-align: center; box-shadow: var(--shadow); transition: all 0.3s ease; }
    .service-card:hover { transform: translateY(-10px); }
    .service-icon { font-size: 3rem; color: var(--primary); margin-bottom: 1rem; }
    .service-card h3 { color: var(--primary); margin-bottom: 1rem; }
    .why-us-icon { font-size: 2.5rem; color: var(--accent); margin-bottom: 1rem; }
    .services-grid {
        display: flex;
        justify-content: center; /* centre le bloc */
        gap: 20px; /* espace entre les cartes */
        flex-wrap: nowrap; /* empêche de passer à la ligne */
    }
    .services-grid .service-card {
        flex: 0 0 22%; /* chaque carte prend ±25% de largeur */
        box-sizing: border-box;
    }
    
    </style>
    

</style>

<section class="hero">
    <div class="hero-content"><h1>Le Voyage de Vos Rêves Commence Ici</h1><p>Découvrez des destinations incroyables et créez des souvenirs inoubliables.</p>
        <form action="{{ url_for('destinations') }}" method="get"><div class="search-bar"><i class="fas fa-search" style="color: #999; padding-left: 0.5rem;"></i><input type="text" name="query" placeholder="Essayez 'Paris', 'plage'..." class="search-input"><button type="submit" class="search-btn">Rechercher</button></div></form>
    </div>
</section>
<section class="section"><div class="container"><h2 class="section-title">Nos Services Exclusifs</h2><p class="section-subtitle">Nous nous occupons de tout pour que votre seule préoccupation soit de profiter.</p><div class="services-grid">{% for service in data.services if service.nom in ['Réservation de Vols','Hôtels de Prestige','Visa & Documentation','Assurance Voyage'] %}<a href="{% if service.nom == 'Réservation de Vols' %}{{ url_for('destinations') }}{% else %}{{ url_for('service_detail', service_name=service.nom) }}{% endif %}" style="text-decoration: none; color: inherit;"><div class="service-card"><div class="service-icon"><i class="fas {{ service.icon }}"></i></div><h3>{{ service.nom }}</h3><p>{{ service.description }}</p></div></a>{% endfor %}</div>
<section class="section section-light"><div class="container"><h2 class="section-title">Destinations Populaires</h2><p class="section-subtitle">Laissez-vous inspirer par notre sélection des destinations les plus prisées du moment.</p><div class="destinations-grid">{% for destination in data.destinations[:3] %}<a href="{{ url_for('contact') }}" class="destination-card quote-link" style="text-decoration: none; color: inherit;"><img src="{% if 'http' in destination.image %}{{ destination.image }}{% else %}{{ url_for('static', filename=destination.image) }}{% endif %}" alt="{{ destination.nom }}"><div class="dest-overlay"></div><div class="dest-price">{{ destination.prix }}</div><div class="dest-content"><h3>{{ destination.nom }}</h3><p>{{ destination.description }}</p></div></a>{% endfor %}</div></div></section>
<section class="section"><div class="container"><h2 class="section-title">Pourquoi Nous Choisir ?</h2><div class="why-us-grid">{% for item in data.why_us %}<div class="why-us-card"><div class="why-us-icon"><i class="fas {{ item.icon }}"></i></div><h3>{{ item.title }}</h3><p>{{ item.description }}</p></div>{% endfor %}</div></div></section>
{% endblock %}
'''


services_template = '''
{% extends "base.html" %}
{% block title %}{{ super() }} - Nos Services{% endblock %}
{% block content %}
<style>
    .service-card { background: white; padding: 2rem; border-radius: var(--border-radius); text-align: center; box-shadow: var(--shadow); transition: all 0.3s ease; }
    .service-card:hover { transform: translateY(-10px); }
    .service-icon { font-size: 3rem; color: var(--primary); margin-bottom: 1rem; }
    .service-card h3 { color: var(--primary); margin-bottom: 1rem; }
</style>
<div class="page-header">
    <h1>Nos Services</h1>
</div>
<section class="section">
    <div class="container">
        <h2 class="section-title">Une Gamme Complète Pour Votre Confort</h2>
        <p class="section-subtitle">De la planification à la réalisation de votre voyage, nous couvrons tous les aspects pour vous garantir une expérience exceptionnelle et sans souci.</p>
        <div style="display: grid; grid-template-columns: repeat(auto-fit, minmax(300px, 1fr)); gap: 2rem;">
            {% for service in data.services %}
            <a href="{{ url_for('contact') }}" class="quote-link" style="text-decoration: none; color: inherit;">
                <div class="service-card">
                    <div class="service-icon"><i class="fas {{ service.icon }}"></i></div>
                    <h3>{{ service.nom }}</h3>
                    <p style="color: var(--text-secondary);">{{ service.description }}</p>
                </div>
            </a>
            {% endfor %}
        </div>
    </div>
</section>
{% endblock %}
'''

destinations_template = '''
{% extends "base.html" %}
{% block content %}
<style>
    .destinations-grid { display: grid; grid-template-columns: 1fr; gap: 1.5rem; }
    @media (min-width: 576px) { .destinations-grid { grid-template-columns: repeat(auto-fit, minmax(320px, 1fr)); gap: 2.5rem; } }
    .destination-card { background: white; border-radius: var(--border-radius); overflow: hidden; box-shadow: var(--shadow); transition: all 0.3s ease; position: relative; }
    .destination-card img { width: 100%; height: 350px; object-fit: cover; }
    .dest-overlay { position: absolute; top: 0; left: 0; width: 100%; height: 100%; background: linear-gradient(to top, rgba(0,0,0,0.8) 0%, transparent 100%); }
    .dest-content { position: absolute; bottom: 0; left: 0; padding: 1.5rem; color: white; width: 100%; }
    .dest-price { position: absolute; top: 1rem; right: 1rem; background: var(--accent); color: var(--dark); padding: 0.5rem 1rem; border-radius: 50px; font-weight: 700; }
</style>
<div class="page-header"><h1>Explorez le Monde</h1></div>
<section class="section">
    <div class="container">
        <h2 class="section-title">Toutes Nos Destinations</h2>
        <p class="section-subtitle">
            {% if request.args.get('query') %}
                Résultats de la recherche pour : <strong>{{ request.args.get('query') }}</strong>
            {% else %}
                Des métropoles vibrantes aux plages paradisiaques, trouvez l'inspiration.
            {% endif %}
        </p>
        <div class="destinations-grid">
            {% for destination in destinations %}
            <a href="{{ url_for('contact') }}" class="destination-card quote-link" style="text-decoration: none; display: block;">
                <img src="{% if 'http' in destination.image %}{{ destination.image }}{% else %}{{ url_for('static', filename=destination.image) }}{% endif %}" alt="{{ destination.nom }}">
                <div class="dest-overlay"></div><div class="dest-price">{{ destination.prix }}</div>
                <div class="dest-content"><h3>{{ destination.nom }}</h3><p>{{ destination.description }}</p></div>
            </a>
            {% else %}
            <p>Aucune destination trouvée pour votre recherche.</p>
            {% endfor %}
        </div>
    </div>
</section>
{% endblock %}
'''

contact_template = '''
{% extends "base.html" %}
{% block content %}
<style>
    .contact-grid { display: grid; grid-template-columns: 1fr; gap: 2rem; }
    @media (min-width: 768px) { .contact-grid { grid-template-columns: 1fr 1fr; gap: 4rem; } }
    .contact-info p { display: flex; align-items: center; gap: 1rem; margin-bottom: 1.5rem; font-size: 1.1rem; }
    .contact-info i { font-size: 1.5rem; color: var(--primary); width: 30px; }
    .contact-form .form-group { margin-bottom: 1.5rem; }
    .contact-form label { display: block; margin-bottom: 0.5rem; font-weight: 500; }
    .contact-form input, .contact-form textarea { width: 100%; padding: 1rem; border: 1px solid #ccc; border-radius: var(--border-radius); font-family: 'Poppins', sans-serif; font-size: 1rem; }
    .btn-submit { background: var(--primary); color: white; padding: 1rem 2.5rem; border-radius: 50px; border: none; cursor: pointer; font-size: 1rem; font-weight: 600; transition: all 0.3s; }
</style>
<div class="page-header"><h1>Contactez-Nous</h1></div>
<section class="section">
    <div class="container">
        <h2 class="section-title">Prenons Contact</h2>
        <p class="section-subtitle">Une question ? Une demande de devis ? Notre équipe est à votre écoute.</p>
        <div class="contact-grid">
            <div class="contact-info">
                <h3>Informations de Contact</h3>
                <p><i class="fas fa-map-marker-alt"></i>{{ data.contact_info.adresse }}</p>
                <p><i class="fas fa-phone"></i>{{ data.contact_info.telephone }}</p>
                <p><i class="fas fa-envelope"></i>{{ data.contact_info.email }}</p>
                <p><i class="fas fa-clock"></i>{{ data.contact_info.horaires }}</p>
            </div>
            <div class="contact-form">
                <h3>Envoyez-nous un message</h3>
                <form action="{{ url_for('contact_form') }}" method="post">
                    <div class="form-group"><label for="nom">Nom Complet</label><input type="text" id="nom" name="nom" required></div>
                    <div class="form-group"><label for="email">Email</label><input type="email" id="email" name="email" required></div>
                    <div class="form-group"><label for="telephone">Numéro de téléphone (Optionnel)</label><input type="tel" id="telephone" name="telephone"></div>
                    <div class="form-group"><label for="message">Message</label><textarea id="message" name="message" rows="5" required></textarea></div>
                    <button type="submit" class="btn-submit">Envoyer</button>
                </form>
            </div>
        </div>
    </div>
</section>
{% endblock %}
'''

admin_template = '''
{% extends "base.html" %}
{% block content %}
<style>
    .admin-container { padding: 2rem 1rem; max-width: 900px; margin: 2rem auto; background: #f8f9fa; border-radius: 15px; box-shadow: var(--shadow); }
    .admin-section { margin-bottom: 3rem; }
    .admin-section h2 { font-size: 1.8rem; color: var(--primary); border-bottom: 3px solid var(--accent); padding-bottom: 0.5rem; margin-bottom: 1.5rem; }
    .form-group { margin-bottom: 1rem; }
    label { font-weight: 600; display: block; margin-bottom: 0.5rem; }
    input, textarea, select { width: 100%; padding: 0.8rem; border-radius: 8px; border: 1px solid #ccc; font-size: 1rem; font-family: 'Poppins', sans-serif; }
    .btn-submit { background: var(--primary); color: white; padding: 0.8rem 2rem; border-radius: 50px; border: none; cursor: pointer; font-size: 1rem; font-weight: 600; transition: all 0.3s; display: inline-block; margin-top: 1rem; }
    .dest-list { list-style: none; padding: 0; }
    .dest-item { display: flex; flex-wrap: wrap; justify-content: space-between; align-items: center; padding: 1rem; border-bottom: 1px solid #eee; }
    .dest-actions a { margin-left: 1rem; text-decoration: none; color: var(--primary); }
    .dest-actions a.delete { color: #e74c3c; }
    .order-arrows a { font-size: 1.2rem; margin-left: 1rem; }
</style>
<div class="page-header"><h1>Panneau de Contrôle</h1></div>
<div class="admin-container">
    <div class="admin-section">
        <h2>Ajouter une Destination</h2>
        <form action="{{ url_for('add_destination') }}" method="post" enctype="multipart/form-data">
            <div class="form-group"><label for="nom">Nom</label><input type="text" id="nom" name="nom" required></div>
            <div class="form-group"><label for="description">Description</label><textarea id="description" name="description" rows="3" required></textarea></div>
            <div class="form-group"><label for="prix">Prix</label><input type="text" id="prix" name="prix" required></div>
            <div class="form-group"><label for="image">Image</label><input type="file" id="image" name="image"></div>
            <button type="submit" class="btn-submit">Ajouter</button>
        </form>
    </div>
    <div class="admin-section">
        <h2>Gérer les Destinations</h2>
        <ul class="dest-list">
            {% for i in range(data.destinations|length) %}
            <li class="dest-item">
                <span>{{ data.destinations[i].nom }}</span>
                <div class="dest-actions">
                    <span class="order-arrows">
                        {% if not loop.first %}
                        <a href="{{ url_for('move_destination_up', index=i) }}">⬆️</a>
                        {% endif %}
                        {% if not loop.last %}
                        <a href="{{ url_for('move_destination_down', index=i) }}">⬇️</a>
                        {% endif %}
                    </span>
                    <a href="{{ url_for('edit_destination', index=i) }}">Modifier</a>
                    <a href="{{ url_for('delete_destination', index=i) }}" onclick="return confirm('Êtes-vous sûr ?')" class="delete">Supprimer</a>
                </div>
            </li>
            {% endfor %}
        </ul>
    </div>
</div>
{% endblock %}
'''

edit_destination_template = '''
{% extends "base.html" %}
{% block content %}
<style>
    .edit-container { padding: 2rem 1rem; max-width: 800px; margin: 2rem auto; background: #f8f9fa; border-radius: 15px; box-shadow: var(--shadow); }
    h2 { font-size: 1.8rem; color: var(--primary); border-bottom: 3px solid var(--accent); padding-bottom: 0.5rem; margin-bottom: 1.5rem; }
    .form-group { margin-bottom: 1rem; }
    label { font-weight: 600; display: block; margin-bottom: 0.5rem; }
    input, textarea { width: 100%; padding: 0.8rem; border-radius: 8px; border: 1px solid #ccc; font-size: 1rem; font-family: 'Poppins', sans-serif; }
    .btn-submit { background: var(--primary); color: white; padding: 0.8rem 2rem; border-radius: 50px; border: none; cursor: pointer; font-size: 1rem; font-weight: 600; transition: all 0.3s; display: inline-block; margin-top: 1rem; }
    .current-image { max-width: 200px; margin-top: 1rem; border-radius: 8px; }
</style>
<div class="page-header"><h1>Modifier une Destination</h1></div>
<div class="edit-container">
    <h2>{{ destination.nom }}</h2>
    <form method="post" enctype="multipart/form-data">
        <div class="form-group"><label for="nom">Nom</label><input type="text" id="nom" name="nom" value="{{ destination.nom }}" required></div>
        <div class="form-group"><label for="description">Description</label><textarea id="description" name="description" rows="4" required>{{ destination.description }}</textarea></div>
        <div class="form-group"><label for="prix">Prix</label><input type="text" id="prix" name="prix" value="{{ destination.prix }}" required></div>
        <div class="form-group">
            <label for="image">Changer l'image (optionnel)</label>
            <input type="file" id="image" name="image">
            {% if destination.image %}
                <p style="margin-top: 1rem;">Image actuelle :</p>
                <img src="{% if 'http' in destination.image %}{{ destination.image }}{% else %}{{ url_for('static', filename=destination.image) }}{% endif %}" alt="{{ destination.nom }}" class="current-image">
            {% endif %}
        </div>
        <button type="submit" class="btn-submit">Sauvegarder</button>
    </form>
</div>
{% endblock %}
'''

login_template = '''
<!DOCTYPE html>
<html lang="fr">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Connexion - Admin</title>
    <link href="https://fonts.googleapis.com/css2?family=Poppins:wght@300;400;500;600&display=swap" rel="stylesheet">
    <style>
        body { font-family: 'Poppins', sans-serif; background-color: #f0f2f5; display: flex; justify-content: center; align-items: center; height: 100vh; }
        .login-container { background: white; padding: 2.5rem; border-radius: 12px; box-shadow: 0 10px 30px rgba(0,0,0,0.1); width: 100%; max-width: 400px; text-align: center; }
        h1 { margin-bottom: 2rem; color: #2C5B61; }
        .form-group { margin-bottom: 1.5rem; text-align: left; }
        label { display: block; margin-bottom: 0.5rem; font-weight: 500; }
        input { width: 100%; padding: 0.8rem; border: 1px solid #ccc; border-radius: 8px; font-size: 1rem; }
        .btn-submit { background: #2C5B61; color: white; padding: 0.8rem 2rem; border-radius: 50px; border: none; cursor: pointer; font-size: 1rem; font-weight: 600; transition: all 0.3s; width: 100%; }
        .flash-message { padding: 1rem; margin-bottom: 1rem; border-radius: 8px; color: #721c24; background-color: #f8d7da; border: 1px solid #f5c6cb; }
    </style>
</head>
<body>
    <div class="login-container">
        <h1>Accès Admin</h1>
        {% with messages = get_flashed_messages(with_categories=true) %}
            {% if messages %}
                {% for category, message in messages %}
                    <div class="flash-message">{{ message }}</div>
                {% endfor %}
            {% endif %}
        {% endwith %}
        <form method="post">
            <div class="form-group"><label for="username">Nom d'utilisateur</label><input type="text" id="username" name="username" required></div>
            <div class="form-group"><label for="password">Mot de passe</label><input type="password" id="password" name="password" required></div>
            <button type="submit" class="btn-submit">Se Connecter</button>
        </form>
    </div>
</body>
</html>
'''

def write_templates():
    with open(os.path.join(templates_dir, 'base.html'), 'w', encoding='utf-8') as f: f.write(base_template)
    with open(os.path.join(templates_dir, 'index.html'), 'w', encoding='utf-8') as f: f.write(index_template)
    with open(os.path.join(templates_dir, 'services.html'), 'w', encoding='utf-8') as f: f.write(services_template)
    with open(os.path.join(templates_dir, 'destinations.html'), 'w', encoding='utf-8') as f: f.write(destinations_template)
    with open(os.path.join(templates_dir, 'contact.html'), 'w', encoding='utf-8') as f: f.write(contact_template)
    with open(os.path.join(templates_dir, 'admin.html'), 'w', encoding='utf-8') as f: f.write(admin_template)
    with open(os.path.join(templates_dir, 'edit_destination.html'), 'w', encoding='utf-8') as f: f.write(edit_destination_template)
    with open(os.path.join(templates_dir, 'login.html'), 'w', encoding='utf-8') as f: f.write(login_template)

if __name__ == '__main__':
    load_data()
    write_templates()
    print("🚀 Démarrage du serveur Flask...")
    app.run(debug=True)