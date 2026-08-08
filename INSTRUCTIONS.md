# Guide de contribution

Ce document explique comment installer un poste de travail et contribuer au contenu du livre *Traitement de la donnée géospatiale avec Python — applications thématiques*.

## Portée

**Ce guide couvre uniquement l'édition des fichiers `.qmd`** (le texte et le code des chapitres).

La production du site HTML et du PDF n'est **pas** de votre ressort : elle est faite séparément, dans un conteneur Docker, par la personne responsable de la publication. Vous n'avez donc **ni Docker, ni LaTeX, ni environnement Python complet** à installer.

Concrètement :

| Vous faites | Vous ne faites pas |
|:---|:---|
| Modifier les `.qmd`, ajouter des images dans `images/` | Lancer `process.sh` |
| Ajouter des références dans `references.bib` | Modifier `docs/` (site généré) |
| Ouvrir une *pull request* | Modifier `notebooks/`, `marimo/` (générés) |

## 1. Installer VS Code

Téléchargez et installez VS Code : <https://code.visualstudio.com/download>

Sous Windows, installez la version **Windows** (pas la version Linux dans WSL) : VS Code s'exécute côté Windows et se connecte à WSL.

## 2. Installer WSL — *Windows seulement*

**Cette étape ne concerne que Windows.** Sous macOS ou Linux, passez directement à l'étape 3 : votre terminal fait déjà l'affaire.

Dans un terminal PowerShell **en tant qu'administrateur** :

```powershell
wsl --install
```

Redémarrez, puis créez votre nom d'utilisateur et mot de passe Linux au premier lancement d'Ubuntu.

Documentation : <https://learn.microsoft.com/fr-fr/windows/wsl/install>

## 3. Installer et configurer git

Dans le terminal WSL (ou votre terminal macOS/Linux) :

```bash
sudo apt update && sudo apt install git
```

**Configurez votre identité** — sans cela, vos commits ne vous seront pas attribués :

```bash
git config --global user.name "Prénom Nom"
git config --global user.email "votre.courriel@example.com"
```

Documentation : <https://learn.microsoft.com/fr-fr/windows/wsl/tutorials/wsl-git>

## 4. S'authentifier auprès de GitHub

Cette étape ne figure pas dans la liste minimale, mais elle est **indispensable** : sans elle vous pourrez cloner le dépôt, mais **pas y publier vos modifications** (`git push` échouera). GitHub n'accepte plus le mot de passe de compte en ligne de commande.

La méthode la plus simple est l'outil `gh` :

```bash
sudo apt install gh
gh auth login
```

Choisissez `GitHub.com` → `HTTPS` → `Login with a web browser`, puis suivez les instructions.

Documentation : <https://cli.github.com/>

## 5. Cloner le dépôt

```bash
git clone https://github.com/sfoucher/TraitementImagesPythonVol3.git
cd TraitementImagesPythonVol3
```

Clonez dans votre système de fichiers **Linux** (par exemple `~/projets/`), pas dans `/mnt/c/...`. Un dépôt placé du côté Windows est beaucoup plus lent à parcourir depuis WSL.

## 6. Ouvrir VS Code dans le dépôt

```bash
code .
```

Sous Windows, cette commande installe automatiquement le composant serveur au premier lancement, à condition que l'extension **WSL** soit présente dans VS Code : <https://marketplace.visualstudio.com/items?itemName=ms-vscode-remote.remote-wsl>

Cette extension manque dans la liste minimale ; sans elle, `code .` lancé depuis WSL ne s'ouvrira pas correctement. Vérifiez que la pastille en bas à gauche de VS Code affiche bien **WSL: Ubuntu**.

## 7. Installer l'extension Quarto

<https://marketplace.visualstudio.com/items?itemName=quarto.quarto>

Installez-la **dans WSL** (VS Code propose « Install in WSL: Ubuntu » — c'est ce qu'il faut choisir).

Elle apporte la coloration syntaxique, les extraits de code et l'autocomplétion pour les `.qmd`.

> **À savoir :** l'extension seule ne rend pas le document. Les commandes *Preview*, *Render* et l'éditeur visuel exigent le logiciel Quarto lui-même, qui n'est pas nécessaire ici puisque la production du HTML et du PDF se fait ailleurs. Si vous souhaitez tout de même une prévisualisation locale, voir la section optionnelle ci-dessous.

Documentation de l'extension : <https://quarto.org/docs/tools/vscode.html>

## Optionnel : prévisualiser localement

Non requis pour contribuer. Utile si vous voulez voir le rendu de votre texte pendant que vous écrivez.

Installez Quarto dans WSL (<https://quarto.org/docs/get-started/>), puis, dans VS Code, `Ctrl+Shift+P` → **Quarto: Preview**.

Attention : la prévisualisation **exécute le code Python** du chapitre. Les chapitres dont l'entête contient `eval: false` (c'est le cas de `00-SWOT.qmd`) ne posent pas de problème, mais un chapitre exécutable exigera les bibliothèques Python et les fichiers de données correspondants. En cas de doute, prévisualisez avec `eval: false`.

N'ajoutez jamais au dépôt les fichiers produits par une prévisualisation locale (voir « Ce qu'il ne faut pas modifier »).

## Workflow de contribution

```bash
git checkout main
git pull                                  # partir de la version à jour
git checkout -b ma-contribution           # une branche par contribution

# ... éditez les .qmd ...

git add 00-SWOT.qmd                       # nommez les fichiers, évitez git add -A
git commit -m "Corriger la section sur les produits PIXC"
git push -u origin ma-contribution
```

Ouvrez ensuite une *pull request* : <https://docs.github.com/fr/pull-requests/collaborating-with-pull-requests>

Si vous n'avez pas les droits d'écriture sur le dépôt, commencez par le *forker* (bouton **Fork** sur GitHub) et travaillez sur votre copie.

Préférez `git add <fichier>` à `git add -A` : cela évite d'ajouter par mégarde des fichiers générés localement.

## Conventions de rédaction

### Blocs encadrés

Le livre utilise sept blocs personnalisés : `bloc_objectif`, `bloc_package`, `bloc_notes`, `bloc_astuce`, `bloc_attention`, `bloc_aller_loin`, `bloc_exercice`.

**L'imbrication des `:` est 6 / 4 / 3 et doit être respectée exactement :**

```markdown
:::::: bloc_astuce
:::: bloc_astuce-header
::: bloc_astuce-icon
:::

**Titre du bloc**
::::

::: bloc_astuce-body
Le contenu du bloc.
:::
::::::
```

Un nombre de `:` erroné (5 au lieu de 6, par exemple) **s'affiche correctement** dans le navigateur : rien ne signale l'erreur. En revanche l'outil qui rassemble les exercices, `make_exercices.py`, cherche la chaîne exacte `:::::: bloc_exercice` et n'extraira rien. Comptez les `:`.

### Ne jamais mettre une cellule de code dans un bloc

Un bloc encadré ne doit contenir que du texte. **Placez la cellule `{python}` après la fermeture du bloc, jamais à l'intérieur :**

````markdown
:::::: bloc_package
:::: bloc_package-header
::: bloc_package-icon
:::

**Installation**
::::

::: bloc_package-body
Les bibliothèques suivantes doivent être installées.
:::
::::::

```{python}
!pip install ...
```
````

Là encore, rien ne se voit dans le HTML ni dans le PDF : les deux formats s'affichent normalement. Le dégât n'apparaît que dans le **notebook exporté**. Les chapitres sont convertis en `.ipynb`, ce qui découpe le texte en cellules : l'ouverture et la fermeture du bloc se retrouvent alors dans deux cellules différentes, que l'outil de nettoyage ne peut plus apparier. Il reste un `::::::` orphelin en tête de cellule, visible par les personnes qui téléchargent le notebook.

### Titres et renvois

Un chapitre commence par un titre de niveau 1 muni d'une ancre :

```markdown
# Titre du chapitre {#sec-monchapitre}
```

On y renvoie ensuite avec `[chapitre @sec-monchapitre]` ou `[section @sec-masection]`. Une ancre inexistante produit un `?@sec-...` dans la sortie : le livre est actuellement **sans renvoi cassé**, donc tout `?@sec-` qui apparaît vient d'être introduit.

Documentation : <https://quarto.org/docs/authoring/cross-references.html>

### Caractères spéciaux

Le PDF est produit par `pdflatex`, qui **échoue** sur certains caractères Unicode dans le texte courant, notamment `≤` et `≥`. Écrivez « au plus » / « au moins », ou utilisez le mode mathématique (`$\leq$`, `$1\sigma$`, `$\mu$rad`), qui passe sans problème.

Les caractères `×`, `—`, `œ` et toutes les lettres accentuées sont acceptés.

### Citations

Les références bibliographiques vont dans `references.bib` et se citent avec `[@cle2024]`.

Documentation : <https://quarto.org/docs/authoring/citations.html>

### Images

Placez les images dans `images/` et référencez-les en chemin relatif :

```markdown
![Légende de la figure](images/mon-image.png){#fig-monimage width="80%" fig-align="center"}
```

Compressez vos images avant de les ajouter : elles sont versionnées dans le dépôt, donc leur poids est permanent.

### Syntaxe Quarto générale

<https://quarto.org/docs/authoring/markdown-basics.html>

## Ce qu'il ne faut pas modifier

Ces fichiers sont **générés**. Toute modification manuelle sera écrasée à la prochaine production :

- **`docs/`** — le site HTML publié et le PDF. Produit par `process.sh`.
- **`notebooks/`, `marimo/`** — les exports des chapitres en notebooks.
- **`08-Exercices.qmd`** — s'il existe, il est assemblé par `make_exercices.py` à partir des blocs `bloc_exercice` des chapitres. Corrigez l'exercice **dans le chapitre**, pas dans ce fichier.

Ne lancez pas `process.sh` : la production se fait dans un conteneur Docker, sur le poste de la personne responsable de la publication.

## Résumé des liens

| Ressource | Lien |
|:---|:---|
| VS Code | <https://code.visualstudio.com/download> |
| Installer WSL | <https://learn.microsoft.com/fr-fr/windows/wsl/install> |
| git dans WSL | <https://learn.microsoft.com/fr-fr/windows/wsl/tutorials/wsl-git> |
| Extension WSL | <https://marketplace.visualstudio.com/items?itemName=ms-vscode-remote.remote-wsl> |
| Extension Quarto | <https://marketplace.visualstudio.com/items?itemName=quarto.quarto> |
| Quarto dans VS Code | <https://quarto.org/docs/tools/vscode.html> |
| Installer Quarto (optionnel) | <https://quarto.org/docs/get-started/> |
| GitHub CLI (`gh`) | <https://cli.github.com/> |
| Pull requests | <https://docs.github.com/fr/pull-requests/collaborating-with-pull-requests> |
| Syntaxe Quarto | <https://quarto.org/docs/authoring/markdown-basics.html> |
| Renvois | <https://quarto.org/docs/authoring/cross-references.html> |
| Citations | <https://quarto.org/docs/authoring/citations.html> |
| Dépôt du livre | <https://github.com/sfoucher/TraitementImagesPythonVol3> |
| Site publié | <https://sfoucher.github.io/TraitementImagesPythonVol3/> |
