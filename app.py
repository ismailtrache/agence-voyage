from flask import Flask, render_template, request, redirect, url_for, flash
import os
from werkzeug.utils import secure_filename
import json

app = Flask(__name__)
app.secret_key = 'votre_cle_secrete_ici'

# Configuration pour l'upload de fichiers
UPLOAD_FOLDER = 'static/uploads'
ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif'}
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

# Créer le dossier d'upload s'il n'existe pas
os.makedirs(UPLOAD_FOLDER, exist_ok=True)

def allowed_file(filename):
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

# Données de base pour le site (avec les nouvelles destinations)
site_data = {
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
        # Destinations existantes
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
        
        # VOS NOUVELLES DESTINATIONS AJOUTÉES ICI
        {
            'nom': 'Istanbul, Turquie',
            'description': 'Un pont entre l\'Europe et l\'Asie, riche d\'histoire et de saveurs.',
            'prix': '€480',
            'image': 'https://images.unsplash.com/photo-1527838832700-5059252407fa?auto=format&fit=crop&w=800&q=60'
        },
        {
            'nom': 'Sharm El Sheikh, Égypte',
            'description': 'Plongée de classe mondiale dans les eaux cristallines de la mer Rouge.',
            'prix': '€550',
            'image': 'static/uploads/destinantions/SharmElSheikh.jpg'
        },
        {
            'nom': 'Sousse, Tunisie',
            'description': 'Combine des plages dorées avec une médina historique classée à l\'UNESCO.',
            'prix': '€390',
            'image': 'static/uploads/destinantions/sousse.jpg'
        },
        {
            'nom': 'Guangzhou, Chine',
            'description': 'Mégapole moderne et dynamique, cœur du commerce et de la gastronomie cantonaise.',
            'prix': '€850',
            'image': 'static/uploads/destinantions/guangzhou.jpg'
        },
        {
            'nom': 'Toronto, Canada',
            'description': 'La métropole cosmopolite du Canada, avec sa skyline iconique et sa scène culturelle vibrante.',
            'prix': '€720',
            'image': 'static/uploads/destinantions/toronto.jpg'
        }
    ],
    'contact_info': {
        'telephone': '+213 662 90 10 49',
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

# ==============================================
# ROUTES DE L'APPLICATION
# ==============================================

@app.route('/')
def index():
    return render_template('index.html', data=site_data)

@app.route('/services')
def services():
    return render_template('services.html', data=site_data)

@app.route('/destinations')
def destinations():
    # Ajout du paramètre de recherche pour filtrer les destinations
    query = request.args.get('query')
    if query:
        filtered_destinations = [
            dest for dest in site_data['destinations'] if query.lower() in dest['nom'].lower() or query.lower() in dest['description'].lower()
        ]
        return render_template('destinations.html', data=site_data, destinations=filtered_destinations)
    return render_template('destinations.html', data=site_data, destinations=site_data['destinations'])


@app.route('/contact')
def contact():
    return render_template('contact.html', data=site_data)

@app.route('/contact_form', methods=['POST'])
def contact_form():
    nom = request.form.get('nom')
    flash(f'Merci {nom}, votre message a bien été envoyé ! Nous vous répondrons rapidement.', 'success')
    return redirect(url_for('contact'))

# ==============================================
# ROUTES DE L'ADMINISTRATION (FONCTIONNELLES)
# ==============================================

@app.route('/admin')
def admin():
    return render_template('admin.html', data=site_data)

@app.route('/upload_logo', methods=['POST'])
def upload_logo():
    if 'logo' not in request.files:
        flash('Aucun fichier sélectionné')
        return redirect(url_for('admin'))
    
    file = request.files['logo']
    if file.filename == '':
        flash('Aucun fichier sélectionné')
        return redirect(url_for('admin'))
    
    if file and allowed_file(file.filename):
        filename = secure_filename(file.filename)
        file_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
        file.save(file_path)
        
        # Mettre à jour les données du site
        site_data['logo'] = f'uploads/{filename}'
        flash('Logo mis à jour avec succès!')
        
    return redirect(url_for('admin'))

@app.route('/upload_destination_image', methods=['POST'])
def upload_destination_image():
    destination_index = int(request.form.get('destination_index'))
    
    if 'image' not in request.files:
        flash('Aucun fichier sélectionné')
        return redirect(url_for('admin'))
    
    file = request.files['image']
    if file.filename == '':
        flash('Aucun fichier sélectionné')
        return redirect(url_for('admin'))
    
    if file and allowed_file(file.filename):
        filename = secure_filename(file.filename)
        file_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
        file.save(file_path)
        
        # Mettre à jour les données du site
        site_data['destinations'][destination_index]['image'] = f'uploads/{filename}'
        flash(f'Image mise à jour pour {site_data["destinations"][destination_index]["nom"]}!')
        
    return redirect(url_for('admin'))


# ==============================================
# TEMPLATES HTML (Le reste du code est inchangé)
# ==============================================

templates_dir = 'templates'
os.makedirs(templates_dir, exist_ok=True)

# ----------------------------------------------
# BASE.HTML
# ----------------------------------------------
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
        :root {
            --primary: #2C5B61; --secondary: #3A7C89; --accent: #EAB308;
            --light: #F8F9FA; --dark: #1B262C; --text-primary: #333;
            --text-secondary: #666; --shadow: 0 10px 30px rgba(0, 0, 0, 0.1);
            --border-radius: 12px;
        }
        * { margin: 0; padding: 0; box-sizing: border-box; }
        body { font-family: 'Poppins', sans-serif; color: var(--text-primary); background-color: #FFFFFF; overflow-x: hidden; }
        .container { max-width: 1200px; margin: 0 auto; padding: 0 2rem; }
        header {
            background: white; padding: 1rem 0; position: sticky;
            width: 100%; top: 0; z-index: 1000; box-shadow: 0 2px 15px rgba(0,0,0,0.05);
        }
        nav { display: flex; justify-content: space-between; align-items: center; }
        .logo-container { display: flex; align-items: center; gap: 15px; }
        .logo { width: 70px; height: 70px; border-radius: 50%; object-fit: cover; }
        .company-name { font-size: 1.8rem; font-weight: 700; color: var(--primary); }
        .nav-links { display: flex; list-style: none; gap: 1rem; }
        .nav-links a {
            color: var(--primary); text-decoration: none; font-weight: 500; padding: 0.5rem 1rem;
            border-radius: 25px; transition: all 0.3s ease;
        }
        .nav-links a:hover, .nav-links a.active {
            background-color: var(--primary);
            color: white;
        }
        main { min-height: 70vh; }
        .page-header {
            background: linear-gradient(rgba(0,0,0,0.5), rgba(0,0,0,0.5)), url('https://images.unsplash.com/photo-1501785888041-af3ef285b470?auto=format&fit=crop&w=1600&q=80') no-repeat center center/cover;
            padding: 6rem 0; text-align: center; color: white;
        }
        .page-header h1 { font-size: 3rem; font-weight: 700; }
        .section { padding: 6rem 0; }
        .section-light { background-color: var(--light); }
        .section-title {
            text-align: center; font-size: 2.5rem; font-weight: 700;
            color: var(--primary); margin-bottom: 3rem; position: relative;
        }
        .section-title::after {
            content: ''; position: absolute; bottom: -10px; left: 50%;
            transform: translateX(-50%); width: 60px; height: 4px;
            background-color: var(--accent); border-radius: 2px;
        }
        .section-subtitle { text-align: center; color: var(--text-secondary); max-width: 600px; margin: 0 auto 4rem auto; }
        footer { background-color: var(--primary); color: white; padding: 4rem 2rem 2rem; }
        .footer-content { display: grid; grid-template-columns: repeat(auto-fit, minmax(250px, 1fr)); gap: 2rem; max-width: 1200px; margin: 0 auto; }
        .footer-section h3 { color: var(--accent); margin-bottom: 1rem; }
        .footer-section p, .footer-section a { color: rgba(255,255,255,0.8); text-decoration: none; margin-bottom: 0.5rem; transition: color 0.3s; }
        .footer-section a:hover { color: var(--accent); }
        .footer-bottom { text-align: center; margin-top: 3rem; padding-top: 2rem; border-top: 1px solid var(--secondary); }
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
            <ul class="nav-links">
                <li><a href="{{ url_for('index') }}" class="{{ 'active' if request.path == url_for('index') else '' }}">Accueil</a></li>
                <li><a href="{{ url_for('services') }}" class="{{ 'active' if request.path == url_for('services') else '' }}">Services</a></li>
                <li><a href="{{ url_for('destinations') }}" class="{{ 'active' if request.path.startswith(url_for('destinations')) else '' }}">Destinations</a></li>
                <li><a href="{{ url_for('contact') }}" class="{{ 'active' if request.path == url_for('contact') else '' }}">Contact</a></li>
                <li><a href="{{ url_for('admin') }}" class="{{ 'active' if request.path == url_for('admin') else '' }}">Admin</a></li>
            </ul>
        </nav>
    </header>
    
    {% with messages = get_flashed_messages(with_categories=true) %}
        {% if messages %}
            <div style="padding: 1rem; text-align: center;">
            {% for category, message in messages %}
                <div class="alert-{{ category }}" style="background-color: #d4edda; color: #155724; padding: 1rem; border-radius: 8px; max-width: 800px; margin: 1rem auto;">{{ message }}</div>
            {% endfor %}
            </div>
        {% endif %}
    {% endwith %}

    <main>
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
</body>
</html>
'''

# ----------------------------------------------
# INDEX.HTML
# ----------------------------------------------
index_template = '''
{% extends "base.html" %}
{% block title %}{{ super() }} - Accueil{% endblock %}
{% block content %}
<style>
    .hero {
        height: 90vh; color: white; display: flex; align-items: center;
        justify-content: center; text-align: center; position: relative;
        background: linear-gradient(rgba(0,0,0,0.5), rgba(0,0,0,0.5)), url('https://images.unsplash.com/photo-1476514525535-07fb3b4ae5f1?auto=format&fit=crop&w=1600&q=80') no-repeat center center/cover;
    }
    .hero-content { z-index: 2; }
    .hero h1 { font-size: 3.5rem; font-weight: 800; margin-bottom: 1rem; }
    .hero p { font-size: 1.3rem; margin-bottom: 2rem; }
    .search-bar {
        background: rgba(255, 255, 255, 0.9); backdrop-filter: blur(10px);
        padding: 1.5rem; border-radius: 50px; display: flex; align-items: center;
        gap: 1rem; box-shadow: 0 10px 40px rgba(0,0,0,0.2); max-width: 800px;
        margin: 2rem auto 0 auto;
    }
    .search-input { flex-grow: 1; border: none; background: transparent; font-size: 1rem; color: #333; }
    .search-input:focus { outline: none; }
    .search-btn {
        background: var(--primary); color: white; padding: 0.8rem 2rem;
        border-radius: 50px; text-decoration: none; font-weight: 600;
        border: none; cursor: pointer; transition: all 0.3s;
    }
    .search-btn:hover { background: var(--secondary); transform: scale(1.05); }
    .services-grid, .destinations-grid, .why-us-grid { display: grid; gap: 2rem; }
    .services-grid { grid-template-columns: repeat(auto-fit, minmax(300px, 1fr)); }
    .service-card { background: white; padding: 2rem; border-radius: var(--border-radius); text-align: center; box-shadow: var(--shadow); transition: all 0.3s ease; }
    .service-card:hover { transform: translateY(-10px); box-shadow: 0 20px 40px rgba(0,0,0,0.1); }
    .service-icon { font-size: 3rem; color: var(--primary); margin-bottom: 1rem; }
    .service-card h3 { color: var(--primary); margin-bottom: 1rem; }
    .destinations-grid { grid-template-columns: repeat(auto-fit, minmax(280px, 1fr)); }
    .destination-card { background: white; border-radius: var(--border-radius); overflow: hidden; box-shadow: var(--shadow); transition: all 0.3s ease; position: relative; }
    .destination-card:hover { transform: translateY(-10px); }
    .destination-card img { width: 100%; height: 350px; object-fit: cover; }
    .dest-overlay { position: absolute; top: 0; left: 0; width: 100%; height: 100%; background: linear-gradient(to top, rgba(0,0,0,0.8) 0%, transparent 100%); }
    .dest-content { position: absolute; bottom: 0; left: 0; padding: 1.5rem; color: white; width: 100%; }
    .dest-content h3 { font-size: 1.5rem; margin-bottom: 0.5rem; }
    .dest-price { position: absolute; top: 1rem; right: 1rem; background: var(--accent); color: var(--dark); padding: 0.5rem 1rem; border-radius: 50px; font-weight: 700; }
    .why-us-grid { grid-template-columns: repeat(auto-fit, minmax(300px, 1fr)); text-align: center; }
    .why-us-icon { font-size: 2.5rem; color: var(--accent); margin-bottom: 1rem; }
</style>
<section class="hero">
    <div class="hero-content">
        <h1>Le Voyage de Vos Rêves Commence Ici</h1>
        <p>Découvrez des destinations incroyables et créez des souvenirs inoubliables.</p>
        <form action="{{ url_for('destinations') }}" method="get">
            <div class="search-bar">
                <i class="fas fa-search" style="color: #999;"></i>
                <input type="text" name="query" placeholder="Essayez 'Paris', 'plage', 'montagne'..." class="search-input">
                <button type="submit" class="search-btn">Rechercher</button>
            </div>
        </form>
    </div>
</section>
<section class="section"><div class="container"><h2 class="section-title">Nos Services Exclusifs</h2><p class="section-subtitle">Nous nous occupons de tout pour que votre seule préoccupation soit de profiter.</p><div class="services-grid">{% for service in data.services[:3] %}<div class="service-card"><div class="service-icon"><i class="fas {{ service.icon }}"></i></div><h3>{{ service.nom }}</h3><p>{{ service.description }}</p></div>{% endfor %}</div></div></section>
<section class="section section-light"><div class="container"><h2 class="section-title">Destinations Populaires</h2><p class="section-subtitle">Laissez-vous inspirer par notre sélection des destinations les plus prisées du moment.</p><div class="destinations-grid">{% for destination in data.destinations[:3] %}<div class="destination-card"><img src="{{ destination.image }}" alt="{{ destination.nom }}"><div class="dest-overlay"></div><div class="dest-price">{{ destination.prix }}</div><div class="dest-content"><h3>{{ destination.nom }}</h3><p>{{ destination.description }}</p></div></div>{% endfor %}</div></div></section>
<section class="section"><div class="container"><h2 class="section-title">Pourquoi Nous Choisir ?</h2><div class="why-us-grid">{% for item in data.why_us %}<div class="why-us-card"><div class="why-us-icon"><i class="fas {{ item.icon }}"></i></div><h3>{{ item.title }}</h3><p>{{ item.description }}</p></div>{% endfor %}</div></div></section>
{% endblock %}
'''

# ----------------------------------------------
# SERVICES.HTML
# ----------------------------------------------
services_template = '''
{% extends "base.html" %}
{% block title %}{{ super() }} - Nos Services{% endblock %}
{% block content %}
<div class="page-header">
    <h1>Nos Services</h1>
</div>
<section class="section">
    <div class="container">
        <h2 class="section-title">Une Gamme Complète Pour Votre Confort</h2>
        <p class="section-subtitle">
            De la planification à la réalisation de votre voyage, nous couvrons tous les aspects
            pour vous garantir une expérience exceptionnelle et sans souci.
        </p>
        <div class="services-grid" style="grid-template-columns: repeat(auto-fit, minmax(300px, 1fr)); gap: 2rem;">
            {% for service in data.services %}
            <div class="service-card" style="background: white; padding: 2rem; border-radius: var(--border-radius); text-align: center; box-shadow: var(--shadow); transition: all 0.3s ease;">
                <div class="service-icon" style="font-size: 3rem; color: var(--primary); margin-bottom: 1rem;"><i class="fas {{ service.icon }}"></i></div>
                <h3 style="color: var(--primary); margin-bottom: 1rem;">{{ service.nom }}</h3>
                <p style="color: var(--text-secondary);">{{ service.description }}</p>
            </div>
            {% endfor %}
        </div>
    </div>
</section>
{% endblock %}
'''
# ----------------------------------------------
# DESTINATIONS.HTML
# ----------------------------------------------
destinations_template = '''
{% extends "base.html" %}
{% block title %}{{ super() }} - Destinations{% endblock %}
{% block content %}
<style>
    .destination-card { background: white; border-radius: var(--border-radius); overflow: hidden; box-shadow: var(--shadow); transition: all 0.3s ease; position: relative; }
    .destination-card:hover { transform: translateY(-10px); }
    .destination-card img { width: 100%; height: 350px; object-fit: cover; }
    .dest-overlay { position: absolute; top: 0; left: 0; width: 100%; height: 100%; background: linear-gradient(to top, rgba(0,0,0,0.8) 0%, transparent 100%); }
    .dest-content { position: absolute; bottom: 0; left: 0; padding: 1.5rem; color: white; width: 100%; }
    .dest-content h3 { font-size: 1.5rem; margin-bottom: 0.5rem; }
    .dest-price { position: absolute; top: 1rem; right: 1rem; background: var(--accent); color: var(--dark); padding: 0.5rem 1rem; border-radius: 50px; font-weight: 700; }
</style>
<div class="page-header">
    <h1>Explorez le Monde</h1>
</div>
<section class="section">
    <div class="container">
        <h2 class="section-title">Toutes Nos Destinations</h2>
        <p class="section-subtitle">
            {% if request.args.get('query') %}
                Résultats de la recherche pour : <strong>{{ request.args.get('query') }}</strong>
            {% else %}
                Des métropoles vibrantes aux plages paradisiaques, trouvez l'inspiration
                pour votre prochaine aventure.
            {% endif %}
        </p>
        <div class="destinations-grid" style="display: grid; grid-template-columns: repeat(auto-fit, minmax(320px, 1fr)); gap: 2.5rem;">
            {% for destination in destinations %}
            <div class="destination-card">
                <img src="{{ destination.image if destination.image else url_for('static', filename='uploads/placeholder.jpg') }}" alt="{{ destination.nom }}">
                <div class="dest-overlay"></div>
                <div class="dest-price">{{ destination.prix }}</div>
                <div class="dest-content">
                    <h3>{{ destination.nom }}</h3>
                    <p>{{ destination.description }}</p>
                </div>
            </div>
            {% else %}
            <p>Aucune destination trouvée pour votre recherche.</p>
            {% endfor %}
        </div>
    </div>
</section>
{% endblock %}
'''
# ----------------------------------------------
# CONTACT.HTML
# ----------------------------------------------
contact_template = '''
{% extends "base.html" %}
{% block title %}{{ super() }} - Contact{% endblock %}
{% block content %}
<style>
    .contact-grid { display: grid; grid-template-columns: 1fr 1fr; gap: 4rem; align-items: center; }
    .contact-info p { display: flex; align-items: center; gap: 1rem; margin-bottom: 1.5rem; font-size: 1.1rem; }
    .contact-info i { font-size: 1.5rem; color: var(--primary); width: 30px; }
    .contact-form .form-group { margin-bottom: 1.5rem; }
    .contact-form label { display: block; margin-bottom: 0.5rem; font-weight: 500; }
    .contact-form input, .contact-form textarea {
        width: 100%; padding: 1rem; border: 1px solid #ccc;
        border-radius: var(--border-radius); font-family: 'Poppins', sans-serif; font-size: 1rem;
    }
    .btn-submit {
        background: var(--primary); color: white; padding: 1rem 2.5rem; border-radius: 50px;
        border: none; cursor: pointer; font-size: 1rem; font-weight: 600; transition: all 0.3s;
    }
    .btn-submit:hover { background: var(--secondary); transform: scale(1.05); }
    .flash-success {
        padding: 1rem; background-color: #d4edda; color: #155724;
        border: 1px solid #c3e6cb; border-radius: var(--border-radius); margin-bottom: 2rem;
    }
    @media (max-width: 768px) { .contact-grid { grid-template-columns: 1fr; } }
</style>
<div class="page-header">
    <h1>Contactez-Nous</h1>
</div>
<section class="section">
    <div class="container">
        <h2 class="section-title">Prenons Contact</h2>
        <p class="section-subtitle">
            Une question ? Une demande de devis ? Notre équipe est à votre écoute pour vous aider
            à planifier le voyage parfait.
        </p>
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
                    <div class="form-group">
                        <label for="nom">Nom Complet</label>
                        <input type="text" id="nom" name="nom" required>
                    </div>
                    <div class="form-group">
                        <label for="email">Email</label>
                        <input type="email" id="email" name="email" required>
                    </div>
                    <div class="form-group">
                        <label for="message">Message</label>
                        <textarea id="message" name="message" rows="5" required></textarea>
                    </div>
                    <button type="submit" class="btn-submit">Envoyer</button>
                </form>
            </div>
        </div>
    </div>
</section>
{% endblock %}
'''

# ----------------------------------------------
# ADMIN.HTML
# ----------------------------------------------
admin_template = '''
{% extends "base.html" %}
{% block title %}{{ super() }} - Administration{% endblock %}
{% block content %}
<style>
    .admin-container { padding: 2rem; max-width: 800px; margin: 2rem auto; background: #f8f9fa; border-radius: 15px; box-shadow: var(--shadow); }
    .admin-section { margin-bottom: 3rem; }
    .admin-section h2 { font-size: 1.8rem; color: var(--primary); border-bottom: 3px solid var(--accent); padding-bottom: 0.5rem; margin-bottom: 1.5rem; }
    .form-group { margin-bottom: 1rem; }
    label { font-weight: 600; display: block; margin-bottom: 0.5rem; }
    input[type="file"], select { width: 100%; padding: 0.8rem; border-radius: 8px; border: 1px solid #ccc; }
    .btn-submit {
        background: var(--primary); color: white; padding: 0.8rem 2rem; border-radius: 50px;
        border: none; cursor: pointer; font-size: 1rem; font-weight: 600; transition: all 0.3s; display: inline-block; margin-top: 1rem;
    }
    .btn-submit:hover { background: var(--secondary); }
    .current-logo { max-width: 100px; border-radius: 50%; display: block; margin-top: 1rem; }
</style>
<div class="page-header">
    <h1>Panneau d'Administration</h1>
</div>
<div class="admin-container">
    <div class="admin-section">
        <h2>Gérer le Logo</h2>
        <form action="{{ url_for('upload_logo') }}" method="post" enctype="multipart/form-data">
            <div class="form-group">
                <label for="logo">Téléverser un nouveau logo</label>
                <input type="file" name="logo" id="logo" required>
            </div>
            <button type="submit" class="btn-submit">Mettre à jour le logo</button>
        </form>
        {% if data.logo %}
            <p style="margin-top: 1rem;"><strong>Logo actuel :</strong></p>
            <img src="{{ url_for('static', filename=data.logo) }}" alt="Logo actuel" class="current-logo">
        {% endif %}
    </div>

    <div class="admin-section">
        <h2>Gérer les Images des Destinations</h2>
        <form action="{{ url_for('upload_destination_image') }}" method="post" enctype="multipart/form-data">
            <div class="form-group">
                <label for="destination_index">Choisir une destination</label>
                <select name="destination_index" id="destination_index" required>
                    {% for i in range(data.destinations|length) %}
                        <option value="{{ i }}">{{ data.destinations[i].nom }}</option>
                    {% endfor %}
                </select>
            </div>
            <div class="form-group">
                <label for="image">Téléverser une nouvelle image</label>
                <input type="file" name="image" id="image" required>
            </div>
            <button type="submit" class="btn-submit">Mettre à jour l'image</button>
        </form>
    </div>
</div>
{% endblock %}
'''

# Écrire tous les fichiers templates
def write_templates():
    with open(os.path.join(templates_dir, 'base.html'), 'w', encoding='utf-8') as f:
        f.write(base_template)
    with open(os.path.join(templates_dir, 'index.html'), 'w', encoding='utf-8') as f:
        f.write(index_template)
    with open(os.path.join(templates_dir, 'services.html'), 'w', encoding='utf-8') as f:
        f.write(services_template)
    with open(os.path.join(templates_dir, 'destinations.html'), 'w', encoding='utf-8') as f:
        f.write(destinations_template)
    with open(os.path.join(templates_dir, 'contact.html'), 'w', encoding='utf-8') as f:
        f.write(contact_template)
    with open(os.path.join(templates_dir, 'admin.html'), 'w', encoding='utf-8') as f:
        f.write(admin_template)

# Démarrer l'application
if __name__ == '__main__':
    write_templates() # Crée les fichiers HTML au démarrage
    print("✅ Fichiers templates créés/mis à jour.")
    print("🚀 Démarrage du serveur Flask...")
    app.run(debug=True)