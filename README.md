# Le Wordle (Clone Wordle en Français)

Une version française du célèbre jeu Wordle, jouable directement dans votre navigateur.

## 🎮 Comment jouer

Il suffit d'ouvrir le fichier `index.html` dans votre navigateur web préféré.

Le but est de deviner le **MOT CACHÉ** de 5 lettres en 6 essais.
- Les accents sont automatiquement gérés (tapez 'E', cela peut correspondre à 'É', 'È', 'Ê', etc.).
- Les lettres changent de couleur pour vous guider :
  - **Vert** : Lettre bien placée.
  - **Jaune** : Lettre présente mais mal placée.
  - **Gris** : Lettre absente.

## 📂 Structure du projet

Le projet est organisé comme suit :

- **Racine** : Contient l'application web (`index.html`, `game.js`, `style.css`) et le fichier de mots utilisé par le jeu (`words_smart_filtered.js`).
- **`scripts/`** : Contient les scripts Python utilisés pour générer et filtrer la liste de mots.
- **`data/`** : Contient les données brutes (dictionnaires, listes intermédiaires).

## 📚 Origine des mots (Détails techniques)

La qualité de la liste de mots est cruciale pour un bon clone de Wordle. Voici comment nous avons obtenu et nettoyé les données :

1.  **Source** : Dictionnaire français open-source de LibreOffice (Hunspell `fr_FR.dic`). Ici: https://github.com/wachin/libreoffice-dictionaries-collection/blob/main/dicts/dict-fr/fr.dic
2.  **Extraction** : Le script `extract_from_libreoffice.py` lit le fichier binaire `.dic`, extrait tous les mots, et ne conserve que ceux de 5 lettres. Il gère également l'expansion des ligatures (par exemple, "cœur" devient "coeur").
3.  **Filtrage Intelligent** : Le script `smart_filter.py` applique des règles strictes pour nettoyer la liste :
    *   Suppression des noms propres (mots commençant par une majuscule).
    *   Suppression des mots aux structures improbables (pas de voyelles, trop de consonnes consécutives, etc.).
4.  **Validation Orthographique** : Une validation finale est effectuée à l'aide de la bibliothèque `pyenchant` (basée sur Hunspell) pour s'assurer que chaque mot conservé est bien un mot français valide reconnu.
5.  **Normalisation** : Pour le jeu, tous les accents sont retirés (`é` devient `e`), permettant de jouer avec un clavier standard sans se soucier des caractères spéciaux.

Le résultat final est une liste propre de mots communs, stockée dans `words_smart_filtered.js`.

## 🛠️ Génération de la liste (pour les développeurs)

Si vous souhaitez régénérer la liste de mots vous-même :

1.  Assurez-vous d'avoir Python installé avec la librairie `pyenchant`.
2.  Placez le fichier `fr_FR.dic` dans le dossier `data/`.
3.  Exécutez les commandes suivantes :

```bash
cd scripts
python extract_from_libreoffice.py  # Extrait les mots de 5 lettres vers data/french_words_raw.txt
python smart_filter.py              # Filtre, valide et génère le fichier JS final
```
