<div align="center">

# 🇧🇫 Environnement du Burkina Faso

### Plateforme sémantique d'exploration de la biodiversité

---

[![Flask](https://img.shields.io/badge/Flask-3.0-000000?style=for-the-badge&logo=flask&logoColor=white)](https://flask.palletsprojects.com/)
[![Python](https://img.shields.io/badge/Python-3.12-3776AB?style=for-the-badge&logo=python&logoColor=white)](https://www.python.org/)
[![Apache Jena](https://img.shields.io/badge/Apache_Jena_Fuseki-5.5.0-E84E2F?style=for-the-badge&logo=apache&logoColor=white)](https://jena.apache.org/)
[![OWL](https://img.shields.io/badge/OWL_2-DL-8B5CF6?style=for-the-badge&logo= owl&logoColor=white)](https://www.w3.org/TR/owl2-overview/)
[![Fly.io](https://img.shields.io/badge/Fly.io-Deploy-8B5CF6?style=for-the-badge&logo=flydotio&logoColor=white)](https://fly.io)
[![License](https://img.shields.io/badge/License-MIT-green?style=for-the-badge)](LICENSE)

**🔗 Application en ligne :** [**burkina-environnement.fly.dev**](https://burkina-environnement.fly.dev)

---

*Un projet académique de l'**IBAM / UJKZ** — Institut Burkinabè des Arts et Métiers*
*Université Joseph Ki-Zerbo, Ouagadougou*

</div>

---

## 📋 Table des matières

- [Présentation du projet](#-présentation-du-projet)
- [Caractéristiques principales](#-caractéristiques-principales)
- [Architecture technique](#-architecture-technique)
- [Arborescence du projet](#-arborescence-du-projet)
- [Prérequis](#-prérequis)
- [Installation locale](#-installation-locale)
- [Mise en place de l'ontologie](#-mise-en-place-de-lontologie)
- [Lancement de l'application](#-lancement-de-lapplication)
- [Déploiement cloud](#-déploiement-cloud)
- [Design et interface](#-design-et-interface)
- [API endpoints](#-api-endpoints)
- [Ontologie OWL](#-ontologie-owl)
- [Équipe](#-équipe)

---

## 🌍 Présentation du projet

**Environnement du Burkina Faso** est une application web sémantique conçue pour explorer, interroger et visualiser les données environnementales du Burkina Faso : **faune**, **flore**, **réseau hydrographique** et **habitats**.

Contrairement à une application classique reposant sur une base de données relationnelle, toutes les données ici proviennent **entièrement d'une ontologie OWL 2** interrogeable en **SPARQL** et **GeoSPARQL** via un triplestore Apache Jena Fuseki.

> **« Les données ne sont pas stockées — elles sont déduites. »**
> Chaque page de l'application interroge l'ontologie en temps réel via des requêtes SPARQL.

### Sources des données

| Domaine | Nombre d'entités | Description |
|---------|-----------------|-------------|
| 🦁 Faune | **172** espèces animales | Classification zoologique complète, statut UICN, milieux de vie |
| 🌿 Flore | **126** espèces végétales | Usages médicinaux, alimentaires, artisanaux, ornementaux |
| 💧 Cours d'eau | **24** cours d'eau | Fleuves, rivières, marigots — bassins versants, affluents |
| 📍 Habitats | **31** localités | Parcs, réserves, zones humides, localités urbaines |
| 🚨 Menacées | **13** espèces | Classées CR (danger critique) ou EN (danger) par l'UICN |
| 🗺️ Localités | **31** géoréférencées | Coordonnées WKT pour recherche spatiale par rayon |
| 👥 Entités admin | **272** | Régions, provinces, communes |
| 🏥 Pathologies | **17** | Maladies soignées par la médecine traditionnelle |
| 💊 Usages médicinaux | **97** | Préparations et usages thérapeutiques |

---

## ✨ Caractéristiques principales

<table>
<tr>
<td width="50%">

**Recherche et exploration**
- 🔍 Recherche globale multi-domaine
- 🎯 Filtres combinables (type, famille, statut, localité)
- 📄 Fiches détaillées pour chaque entité
- 📊 Compteurs animés en temps réel

</td>
<td width="50%">

**Carte spatiale interactive**
- 🗺️ Carte Leaflet/OpenStreetMap
- 📍 31 localités géoréférencées
- 📐 Recherche par rayon (Haversine)
- 🏛️ Couches administratives (régions, provinces, communes)

</td>
</tr>
<tr>
<td>

**Ontologie sémantique**
- 🧠 55 classes OWL, 59 propriétés objet, 56 propriétés datatype
- ⚙️ 10 règles SWRL validées
- 🔗 9 AllDisjointClasses (53 classes disjointes)
- 🌐 Namespace : `burkina-environnement#`

</td>
<td>

**Interface responsive**
- 🎨 Palette matériaux burkinabè
- 📱 Design mobile-first
- ♿ Accessibilité WCAG
- 🌙 Animation Faso Dan Fani

</td>
</tr>
</table>

---

## 🏗️ Architecture technique

```
┌─────────────────────────────────────────────────────────┐
│                    Navigateur Web                        │
│   Leaflet · Vanilla JS · HTML5 · CSS3                  │
└───────────────────────┬─────────────────────────────────┘
                        │ HTTP (JSON / HTML)
                        ▼
┌─────────────────────────────────────────────────────────┐
│                 Flask 3.0  (Python 3.12)                │
│  ┌─────────┐ ┌─────────┐ ┌─────────┐ ┌──────────────┐ │
│  │ Accueil │ │  Faune  │ │  Flore  │ │ Cours d'eau  │ │
│  └────┬────┘ └────┬────┘ └────┬────┘ └──────┬───────┘ │
│       │           │           │              │          │
│  ┌────┴────┐ ┌────┴────┐ ┌───┴────┐  ┌─────┴───────┐ │
│  │  Carte  │ │Habitats │ │Menacées│  │  Backend     │ │
│  └────┬────┘ └────┬────┘ └───┬────┘  │  SPARQL      │ │
│       │           │          │        └──────┬───────┘ │
└───────┼───────────┼──────────┼───────────────┼─────────┘
        │           │          │               │
        ▼           ▼          ▼               ▼
┌─────────────────────────────────────────────────────────┐
│          Apache Jena Fuseki 5.5.0  (Triplestore)       │
│                                                         │
│    ┌─────────────────────────────────────────────┐     │
│    │   Dataset: environnement (TDB2)             │     │
│    │   Ontologie: burkina-environnement.rdf      │     │
│    │   Endpoint: /environnement/query             │     │
│    │   Port: 13030 (interne) / 3030 (défaut)    │     │
│    └─────────────────────────────────────────────┘     │
│                                                         │
│    Requêtes SPARQL → Résultats JSON → Flask → HTML     │
└─────────────────────────────────────────────────────────┘
```

### Flux de données

1. **L'utilisateur** navigue vers une page (ex: `/faune`)
2. **Flask** construit une requête SPARQL dynamique avec les filtres
3. La requête est **envoyée** au triplestore Fuseki via HTTP POST
4. Fuseki **interroge** l'ontologie et retourne les résultats en JSON
5. Flask **parse** les résultats et les transmet au template Jinja2
6. Le navigateur **affiche** les données avec le design matériaux burkinabè

---

## 📁 Arborescence du projet

```
app_web_semanique/
│
├── 📄 app.py                          # Point d'entrée Flask (factory create_app)
├── 📄 requirements.txt                # Dépendances Python
├── 📄 Dockerfile                      # Build multi-stage (Fuseki + Flask)
├── 📄 fly.toml                        # Configuration Fly.io
├── 📄 render.yaml                     # Configuration Render.com
├── 📄 start.sh                        # Script de démarrage Docker
├── 📄 .gitignore                      # Fichiers ignorés par Git
├── 📄 .dockerignore                   # Fichiers ignorés par Docker
│
├── 📂 backend/                        # Logique métier (requêtes SPARQL)
│   ├── __init__.py
│   ├── sparql.py                      # Client SPARQL + utilitaires
│   ├── commun.py                      # Stats, recherche globale, rayon
│   ├── faune.py                       # Logique faune (172 espèces)
│   ├── flore.py                       # Logique flore (126 plantes)
│   ├── cours_eau.py                   # Logique hydro (24 cours d'eau)
│   └── habitat.py                     # Logique habitats (31 localités)
│
├── 📂 web/                            # Blueprints Flask (routes)
│   ├── __init__.py
│   ├── accueil.py                     # Route: / (accueil + API stats)
│   ├── faune.py                       # Routes: /faune, /menacees, /api/faune/*
│   ├── flore.py                       # Routes: /flore, /api/flore/*
│   ├── hydro.py                       # Routes: /cours-deau, /api/cours-deau/*
│   ├── carte.py                       # Routes: /carte, /api/carte/*
│   └── habitat.py                     # Routes: /habitats, /api/habitat/*
│
├── 📂 templates/                      # Gabarits HTML (Jinja2)
│   ├── base.html                      # Layout de base (header/footer/nav)
│   ├── index.html                     # Page d'accueil
│   ├── faune.html                     # Liste des espèces animales
│   ├── espece_animale.html            # Fiche espèce animale
│   ├── flore.html                     # Liste des espèces végétales
│   ├── espece_vegetale.html           # Fiche espèce végétale
│   ├── cours_eau.html                 # Liste des cours d'eau
│   ├── cours_eau_fiche.html           # Fiche cours d'eau
│   ├── habitats.html                  # Liste des habitats
│   ├── habitat_fiche.html             # Fiche habitat
│   ├── carte.html                     # Carte spatiale (Leaflet)
│   └── menacees.html                  # Espèces menacées (CR/EN)
│
├── 📂 static/
│   ├── css/
│   │   └── style.css                  # Design system complet (palette matériaux burkinabè)
│   ├── js/
│   │   ├── commun.js                  # Utilitaires partagés (fetch, esc, debounce)
│   │   ├── accueil.js                 # Compteurs animés + recherche globale
│   │   ├── faune.js                   # Filtres, pagination, cartes d'aperçu
│   │   ├── flore.js                   # Filtres, pagination, cartes d'aperçu
│   │   ├── hydro.js                   # Filtres, pagination, cartes d'aperçu
│   │   └── carte.js                   # Leaflet, couches admin, recherche rayon
│   └── images/
│       ├── logo_BF.jpg                # Armoiries du Burkina Faso
│       └── drapeau_BF.jpg             # Drapeau national
│
├── 📂 images/                         # Assets image (drapeaux, logos)
│
├── 📂 Manuel_Utilisation/             # Manuel d'utilisation (LaTeX + PDF)
│   ├── Manuel_Utilisation.tex
│   ├── Manuel_Utilisation.pdf
│   └── images/                        # Captures d'écran de l'application
│
├── 📄 ontologie_environnement.owx     # Ontologie OWL 2 (Protégé XML, 62 283 lignes)
└── 📄 ontologie_environnement.rdf     # Ontologie OWL 2 (RDF/XML, 19 456 lignes)
```

---

## 📦 Prérequis

### Pour le développement local

| Composant | Version minimale | Rôle |
|-----------|-----------------|------|
| **Java** (JRE) | 11+ | Exécution d'Apache Jena Fuseki |
| **Python** | 3.10+ | Exécution de l'application Flask |
| **Git** | 2.x | Gestion de version |

### Pour le déploiement Docker

| Composant | Version | Rôle |
|-----------|---------|------|
| **Docker** | 20.10+ | Build et exécution du conteneur |
| **flyctl** | 0.4+ | CLI Fly.io (optionnel) |

---

## 🚀 Installation locale

### 1. Cloner le projet

```bash
git clone https://github.com/VyDonald/burkina-environnement.git
cd burkina-environnement
```

### 2. Installer Python et les dépendances

```bash
# Créer un environnement virtuel
python -m venv venv

# Activer l'environnement
# Windows :
venv\Scripts\activate
# macOS/Linux :
source venv/bin/activate

# Installer les dépendances
pip install -r requirements.txt
```

Le fichier `requirements.txt` contient :

```
Flask>=3.0
requests>=2.31
rdflib>=7.0
gunicorn>=22.0
```

### 3. Télécharger et configurer Apache Jena Fuseki

```bash
# Télécharger Fuseki 5.5.0
wget https://archive.apache.org/dist/jena/binaries/apache-jena-fuseki-5.5.0.zip
unzip apache-jena-fuseki-5.5.0.zip

# Lancer Fuseki
cd apache-jena-fuseki-5.5.0
./fuseki-server --port=3030
```

> Fuseki sera accessible sur `http://localhost:3030`

### 4. Créer le jeu de données et charger l'ontologie

1. Ouvrir l'interface Fuseki : `http://localhost:3030`
2. Cliquer **« Create new dataset »**
3. Nommer le dataset : `environnement`
4. Choisir **TDB2** (stockage persistent)
5. Cliquer **« Create Dataset »**
6. Aller dans l'onglet **« Upload data »**
7. Sélectionner le fichier `ontologie_environnement.rdf`
8. Cliquer **« Upload »**

Vérification rapide :

```
SELECT (COUNT(*) as ?total) WHERE { ?s ?p ?o }
# → devrait retourner ~1 500+ triples
```

---

## ⚙️ Mise en place de l'ontologie

### Structure de l'ontologie

L'ontologie `burkina-environnement` suit le standard **OWL 2 DL** et contient :

| Élément | Nombre | Description |
|---------|--------|-------------|
| **Classes** | 55 | EspeceAnimale, EspeceVegetale, Fleuve, Riviere, Localite, etc. |
| **Propriétés objet** | 59 | aPourFamille, aMilieuDeVie, aStatutUICN, habiteLocalite, etc. |
| **Propriétés datatype** | 56 | nomCommun, nomScientifique, description, longueur, etc. |
| **Individus** | 1 598 | Espèces, cours d'eau, habitats, familles, etc. |
| **Règles SWRL** | 10 | Priorité conservation, classement auto, propagation, etc. |
| **AllDisjointClasses** | 9 | 53 classes mutuellement exclusives |

### Namespace

```
http://www.ibam-ujkz.bf/ontologies/burkina-environnement#
```

### Hiérarchie taxonomique

```
Taxon
├── Regne ─── Animalia / Plantae
├── Embranchement
├── ClasseZoologique (Mammifères, Oiseaux, Reptiles, etc.)
├── ClasseBotanique (Eudicotylédones, Monocotylédones, etc.)
├── Ordre
├── FamilleZoologique (Félidés, Canidés, Accipitridés, etc.)
└── FamilleBotanique (Fabaceae, Malvaceae, etc.)
```

### Hiérarchie administrative

```
Localite
├── Region (13)
├── Province (45)
├── Departement
├── Commune (350+)
├── Arrondissement
├── Secteur
├── Quartier
└── Village
```

### Règles SWRL (exemples)

| Règle | Description |
|-------|-------------|
| **R-A1** | Priorité de conservation : espèce CR/EN → classification automatique |
| **R-A2** | Classement automatique par nom scientifique → famille |
| **R-E1** | Appartenance cours d'eau → bassin versant |
| **R-F1** | Raccourci espèce → pathologie (via usage médicinal) |
| **R-F2** | Propagation présence vers localités englobantes |
| **R-F5** | Espèce stratégique sécurité alimentaire |

---

## ▶️ Lancement de l'application

### Vérifier que Fuseki est en cours d'exécution

```bash
# Vérifier le endpoint
curl "http://localhost:3030/environnement/query" \
  --data-urlencode "query=SELECT (COUNT(*) as ?n) WHERE { ?s ?p ?o }"
```

### Lancer Flask

```bash
# Depuis la racine du projet
python app.py
```

L'application sera accessible sur `http://127.0.0.1:5000`

### Variables d'environnement

| Variable | Défaut | Description |
|----------|--------|-------------|
| `FUSEKI_ENDPOINT` | `http://localhost:3030/environnement/query` | URL du endpoint SPARQL |
| `FLASK_DEBUG` | `false` | Mode debug Flask |
| `PORT` | `5000` | Port de l'application |

---

## ☁️ Déploiement cloud

### Fly.io (recommandé)

```bash
# Installer flyctl
curl -L https://fly.io/install.sh | sh

# Connexion
fly auth login

# Créer l'app
fly launch

# Déployer
fly deploy
```

L'application est accessible sur : **https://burkina-environnement.fly.dev**

| Paramètre | Valeur |
|-----------|--------|
| Région | `cdg` (Paris) |
| RAM | 512 MB |
| CPU | Shared, 1 core |
| HTTPS | Automatique |
| Cold start | Non (VM toujours active) |

### Render.com (secondaire)

Déploiement automatique au push sur `main` :

**https://burkina-environnement.onrender.com**

> ⚠️ Mise en veille après inactivité (~30-60s de cold start)

### Docker (local ou serveur)

```bash
# Build
docker build -t burkina-environnement .

# Run
docker run -p 5000:5000 burkina-environnement
```

Le Dockerfile utilise un **build multi-stage** :
1. **Stage 1** (`eclipse-temurin:17-jre-alpine`) : téléchargement de Fuseki 5.5.0
2. **Stage 2** (`python:3.12-slim`) : installation de Python + JRE + copie de Fuseki

---

## 🎨 Design et interface

### Palette matériaux burkinabè

Inspirée des tissus et matériaux traditionnels du Burkina Faso :

| Couleur | Code | Utilisation |
|---------|------|-------------|
| 🔴 **Latérite** | `#A8462F` | Badges danger (CR/EN), indicateurs de menace |
| 🟡 **Écru** | `#E9DFC8` | Fond de page, tons chauds |
| 🔵 **Indigo** | `#232C3D` | Header, footer, titres |
| 🟢 **Vert savane** | `#74823E` | Boutons principaux, accents stats |
| 🟠 **Ocre banco** | `#C68A3D` | Liens, boutons d'action, bordures |
| ⚫ **Encre charbon** | `#2B2620` | Texte principal |

### Typographie

| Rôle | Police | Usage |
|------|--------|-------|
| **Titres** | Fraunces | H1, H2, H3, H4 — caractère élégant, weights 400-800 |
| **Corps** | Public Sans | Texte, boutons, labels — lisibilité optimale |
| **Noms scientifiques** | IBM Plex Mono (italic) | Noms latins d'espèces — convention taxonomique |

### Éléments visuels

- **Motif Faso Dan Fani** : animation CSS `repeating-linear-gradient` imitant le tissu traditionnel
- **Badge UICN** : rouge (CR/EN), ocre (VU), bleu (NT), vert (LC)
- **Cartes arrondies** : `border-radius: 16-18px`, ombres douces
- **Barre tricolore** : dégradé latérite → ocre → vert savane (drapeau)
- **Compteurs animés** : `IntersectionObserver` + `requestAnimationFrame` pour un défilement fluide
- **Responsive** : collapse en colonne unique sous 860px
- **prefers-reduced-motion** : désactivation des animations pour l'accessibilité

---

## 📡 API endpoints

### Accueil

| Méthode | Route | Description |
|---------|-------|-------------|
| `GET` | `/` | Page d'accueil (HTML) |
| `GET` | `/api/stats` | Compteurs statistiques (JSON) |
| `GET` | `/api/recherche?q=` | Recherche globale multi-domaine (JSON) |

### Faune

| Méthode | Route | Description |
|---------|-------|-------------|
| `GET` | `/faune` | Liste des espèces animales |
| `GET` | `/faune/<nom>` | Fiche détaillée d'une espèce |
| `GET` | `/menacees` | Espèces menacées (CR/EN) |
| `GET` | `/api/faune/filtres` | Options de filtres (JSON) |
| `GET` | `/api/faune/especes?page=&q=&groupe=&famille=&milieu=&statut=&localite=` | Liste paginée (JSON) |
| `GET` | `/api/faune/espece/<nom>` | Fiche espèce (JSON) |
| `GET` | `/api/menacees` | Espèces menacées (JSON) |

### Flore

| Méthode | Route | Description |
|---------|-------|-------------|
| `GET` | `/flore` | Liste des espèces végétales |
| `GET` | `/flore/<nom>` | Fiche détaillée d'une plante |
| `GET` | `/api/flore/filtres` | Options de filtres (JSON) |
| `GET` | `/api/flore/plantes?page=&q=&famille=&usage=&zone=&condition=&localite=` | Liste paginée (JSON) |
| `GET` | `/api/flore/plante/<nom>` | Fiche plante (JSON) |

### Cours d'eau

| Méthode | Route | Description |
|---------|-------|-------------|
| `GET` | `/cours-deau` | Liste des cours d'eau |
| `GET` | `/cours-deau/<nom>` | Fiche détaillée d'un cours d'eau |
| `GET` | `/api/cours-deau/filtres` | Options de filtres (JSON) |
| `GET` | `/api/cours-deau?page=&q=&type=&bassin=` | Liste paginée (JSON) |
| `GET` | `/api/cours-deau/<nom>` | Fiche cours d'eau (JSON) |

### Carte spatiale

| Méthode | Route | Description |
|---------|-------|-------------|
| `GET` | `/carte` | Carte interactive (Leaflet) |
| `GET` | `/api/carte` | Localités géoréférencées (JSON) |
| `GET` | `/api/carte/rayon?lat=&lon=&rayon=` | Localités dans un rayon (Haversine, JSON) |
| `GET` | `/api/carte/administratif?couche=` | Couches admin régions/provinces/communes (JSON) |

### Habitats

| Méthode | Route | Description |
|---------|-------|-------------|
| `GET` | `/habitats` | Liste des habitats |
| `GET` | `/habitats/<nom>` | Fiche détaillée d'un habitat |
| `GET` | `/api/habitats` | Liste JSON |
| `GET` | `/api/habitat/<nom>` | Fiche habitat (JSON) |

> 🔒 **Sécurité** : tous les paramètres `<nom>` sont validés par regex `^[A-Za-z0-9_]+$`

---

## 🧠 Ontologie OWL

### Formats disponibles

| Fichier | Format | Lignes | Usage |
|---------|--------|--------|-------|
| `ontologie_environnement.owx` | OWL/XML (Protégé) | 62 283 | Édition dans Protégé |
| `ontologie_environnement.rdf` | RDF/XML | 19 456 | Chargement dans Fuseki |

### Propriétés objet clés

| Propriété | Domaine | Range | Description |
|-----------|---------|-------|-------------|
| `aPourFamilleZoologique` | EspeceAnimale | FamilleZoologique | Classification taxonomique |
| `aPourFamilleBotanique` | EspeceVegetale | FamilleBotanique | Classification botanique |
| `aMilieuDeVie` | EspeceAnimale | MilieuDeVie | Habitat naturel |
| `aStatutUICN` | EspeceAnimale | StatutConservation | Niveau de menace |
| `habiteLocalite` | EspeceAnimale | Localite | Zones d'observation |
| `aUnUsageMedicinal` | EspeceVegetale | UsageMedicinal | Usage thérapeutique |
| `appartientABassinVersant` | CoursEau | BassinVersant | Bassin hydrographique |

### Propriétés datatype notables

| Propriété | Type | Description |
|-----------|------|-------------|
| `nomCommun` | `xsd:string` | Nom français |
| `nomScientifique` | `xsd:string` | Nomenclature binomiale |
| `nomLocal` | `xsd:string` | Nom en langue locale |
| `description` | `xsd:string` | Description textuelle |
| `longueur` | `xsd:float` | Longueur en km |
| `dateCreation` | `xsd:date` | Date de création dans l'ontologie |
| `geometrieWKT` | `xsd:string` | Géométrie WKT (POINT) |

---

## 👥 Équipe

| Rôle | Membres |
|------|---------|
| **Flora (Groupes 1, 21, 28)** | Étudiants IBAM/UJKZ |
| **Faune (Groupes 25, 35)** | Étudiants IBAM/UJKZ |
| **Cours d'eau (Groupes 7, 14)** | Étudiants IBAM/UJKZ |
| **Encadrant** | Professeur IBAM/UJKZ |

**Institution** : Institut Burkinabè des Arts et Métiers (IBAM) / Université Joseph Ki-Zerbo (UJKZ)

---

<div align="center">

### 🇧🇫 Patrie et Progrès 🇧🇫

*Burkina Faso — Environnement du Burkina Faso*

---

Fait avec ❤️ pour la préservation de la biodiversité burkinabè

</div>
