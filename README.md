# Traitement de la donnée géospatiale avec Python — applications thématiques

Volume 3 de la série. Livre [Quarto](https://quarto.org) (français) : les chapitres sont les fichiers `NN-*.qmd`, le site généré est écrit dans `docs/`.

* Site publié : <https://sfoucher.github.io/TraitementImagesPythonVol3/>
* En cours d'écriture — le contenu n'est pas complet.

Le livre est organisé par **thématiques d'application** : chaque chapitre part d'un besoin concret et déroule la chaîne complète, de l'accès aux données jusqu'à l'interprétation.

## Contribuer au contenu

**Pour écrire ou corriger un chapitre, lisez [INSTRUCTIONS.md](INSTRUCTIONS.md).**

Ce guide couvre l'édition des fichiers `.qmd` : installation de VS Code, WSL, git et de l'extension Quarto, puis le déroulé branche → commit → *pull request*, ainsi que les conventions de rédaction du livre.

**Aucun des outils décrits ci-dessous n'est nécessaire pour contribuer au contenu** : ni Docker, ni LaTeX, ni environnement Python. La suite de ce README ne concerne que la personne responsable de la production.

## Générer le livre avec Docker

> Quarto s'exécute **dans un conteneur Docker**, pas sur l'hôte. Le Quarto de
> l'hôte est un environnement différent — utilisez le conteneur pour des
> constructions reproductibles.

### Prérequis

* [Docker](https://docs.docker.com/get-docker/) installé et démarré.
* L'image de construction `tipvol3:quarto-1.9.38` (voir ci-dessous pour la bâtir).

### 1. Construire l'image Docker

Nécessaire au premier usage, ou après modification des dépendances
(`docker/dependencies/requirements.txt`, `docker/dependencies/install_packages.R`,
`docker/dependencies/tl_packages`) :

```bash
docker build --build-arg QUARTO_VERSION=1.9.38 \
  -t tipvol3:quarto-1.9.38 -f docker/linux/Dockerfile .
```

L'étiquette de l'image encode la version de Quarto. L'image contient Quarto,
Python (dont `rasterio`, `geopandas`, `earthaccess`…), R et TeX Live. La
construction est longue (~20 min, image ~11 Go).

> **Le nom de l'image est propre au volume 3** (`tipvol3`), afin qu'une
> reconstruction ici n'écrase jamais l'image du volume 1
> (`mlsysbook-linux:quarto-*`). Les deux dépôts partagent le même Dockerfile
> mais pas la même liste de dépendances : `docker/dependencies/requirements.txt`
> a été réduit à ce que le volume 3 utilise réellement.

### 2. Générer tout le livre (recommandé)

Le script `process.sh` construit tout : site HTML, PDF LaTeX, PDF Typst
(expérimental), et exporte chaque chapitre en `.ipynb` (et en script marimo `.py`).

```bash
./process.sh
```

Sorties :

| Dossier      | Contenu                                             |
|--------------|-----------------------------------------------------|
| `docs/`      | Site HTML + le PDF téléchargeable                   |
| `pdf/`       | Le PDF LaTeX (nom dérivé du titre du livre)         |
| `typst-out/` | Le PDF Typst, expérimental (non versionné)          |
| `notebooks/` | Chapitres et annexes exportés en `.ipynb`           |
| `marimo/`    | Chapitres convertis en scripts marimo `.py`         |

### 3. Commandes manuelles

Toutes les commandes montent le dépôt sur `/workspace` dans le conteneur.
Les options `--user` et `-e HOME=/tmp` font que les fichiers produits
appartiennent à votre compte et non à `root`.

**Site HTML :**

```bash
docker run --rm --user "$(id -u):$(id -g)" -e HOME=/tmp -v "$PWD":/workspace \
  tipvol3:quarto-1.9.38 quarto render --to html --output-dir ./docs
```

**PDF** (nécessite le profil `production`, où le format `pdf` est défini) :

```bash
docker run --rm --user "$(id -u):$(id -g)" -e HOME=/tmp -v "$PWD":/workspace \
  tipvol3:quarto-1.9.38 quarto render --profile production --to pdf --output-dir ./pdf
```

**Aperçu interactif** (rechargement automatique, sur <http://localhost:3508>) :

```bash
docker run --rm --network=host -p 3508:3508 --user "$(id -u):$(id -g)" \
  -e HOME=/tmp -v "$PWD":/workspace \
  tipvol3:quarto-1.9.38 quarto preview --port 3508 --host 0.0.0.0
```

## Publication

GitHub Pages sert le livre depuis la branche **`main`, dossier `/docs`**. Le
dossier `docs/` étant versionné, publier revient à : générer → committer → pousser.
Il n'y a ni branche `gh-pages`, ni workflow de publication.

## Notes et pièges

* **Un rendu HTML seul supprime `docs/*.pdf`.** Quarto élague du dossier de
  sortie tout ce que le rendu HTML n'a pas produit, et le PDF vient d'un rendu
  *séparé*. La construction réussit et le PDF disparaît en silence ; un
  `git add -A` qui suit committe sa suppression. `process.sh` est sûr (l'étape
  PDF suit le HTML et recopie), mais pas un rendu HTML lancé à la main.
  Restaurez avec `cp -f pdf/*.pdf docs/` et vérifiez `ls docs/*.pdf` avant de
  committer.
* **Nom du PDF.** Dérivé du **titre du livre**, donc il change avec lui (accents
  et ponctuation compris). Ne le codez pas en dur : `process.sh` le retrouve par
  `ls -t ./pdf/*.pdf | head -1`. Le champ `output:` de `_quarto-production.yml`
  est inactif pour les projets `book`.
* **`lua/` et `tex-hacks/` sont des sources**, pas des artefacts : le profil
  `production` en dépend. Ne les remettez pas dans `.gitignore`, sinon la
  construction du PDF échoue sur tout clone neuf.
* **Cache d'exécution.** L'exécution des cellules est mise en cache
  (`.jupyter_cache/`, `execute: cache: true`) : les re-rendus réutilisent la
  sortie mise en cache. Supprimez le cache pour forcer une ré-exécution.
* **Ajouter une dépendance Python** sans reconstruire toute l'image (~20 min) :
  patch en couche —
  `docker build -t tipvol3:quarto-1.9.38 - <<< $'FROM tipvol3:quarto-1.9.38\nRUN pip install <paquet>'`.
  L'image diverge alors du Dockerfile jusqu'à une reconstruction propre.
* **Tests.** Les outils en Python pur se testent sur l'hôte, sans dépendances :
  `python3 -m unittest tests.test_clean_notebooks tests.test_make_exercices`.

Les détails d'ingénierie (conventions, pièges de rendu, dépendances) sont
consignés dans [CLAUDE.md](CLAUDE.md).
