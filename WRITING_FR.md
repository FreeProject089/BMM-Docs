# Rédiger la documentation BMM

**Il n'y a qu'une seule source.** `BMM Docs/docs/*.md` est le seul endroit où la
documentation s'écrit. `scripts/sync-docs.mjs` copie ces fichiers dans l'application : le
site mkdocs et le **Help & other** de BMM rendent donc *les mêmes* fichiers, avec deux
moteurs différents.

C'est la chose la plus importante à savoir ici, et la plus facile à se tromper : il n'existe
**pas** de « documentation in-app » séparée à mettre à jour. Modifier une page met les deux à
jour.

```
BMM Docs/docs/<langue>/…/page.md    ← tu écris ici
        │
        ├── mkdocs build             → le site publié
        └── node scripts/sync-docs.mjs
              → frontend/assets/docs/<langue>/…/page.md   ← BMM lit ceci
              → frontend/assets/docs/manifest.json
```

---

## La boucle

```bash
# 1. modifie une page sous BMM Docs/docs/
# 2. copie-la dans l'application
node scripts/sync-docs.mjs
# 3. vérifie que tout tient
npm run ci
```

`npm run ci` lance `sync-docs --check`, qui **échoue si la copie est périmée**. Oublier
l'étape 2 est donc attrapé, pas livré. Il lance aussi `check-docs-xref`, la porte qui lit
réellement ta prose — voir [Ce que la CI vérifie](#ce-que-la-ci-vérifie).

Pour prévisualiser le site :

```bash
cd "BMM Docs" && mkdocs serve
```

---

## Ce qui rend dans LES DEUX

Écris ça librement — ça fonctionne sur le site comme dans l'application.

| Syntaxe | Remarques |
|---|---|
| Titres, listes, liens, `**gras**`, `*italique*`, `***les deux***` | |
| Tableaux GFM | Les pages de référence sont de longs tableaux ; la prose ne peut pas les porter |
| Blocs de code balisés, avec un langage | C'est le langage qui les colore dans l'app |
| Blocs ` ```mermaid ` | Rendus en SVG des deux côtés. 56 diagrammes en dépendent |
| `!!! note "Titre"` + un corps indenté de 4 espaces | Encadrés. Types : `note` `tip` `success` `warning` `danger` |
| `??? note "Titre"` / `???+ note` | Repliable ; le `+` l'ouvre par défaut |
| `=== "Onglet"` + corps indenté, répété | Onglets de contenu |
| `## Titre {#ancre-personnalisée}` | Donne une cible de lien stable |
| Images en chemin relatif | |

!!! tip "Un titre d'encadré peut contenir des guillemets"

    Échappe-les : `!!! note "\"Conflict rules\" = the order"`. Un guillemet interne non
    échappé faisait rendre tout le bloc en texte brut `!!! note …` — la CI l'attrape
    désormais.

---

## Ce qui ne rend que sur le SITE

Ce sont des fonctions mkdocs/Material que le moteur de l'application n'implémente pas.
Ne les utilise que si la page est destinée au site, ou accepte que l'app affiche le texte brut.

| Syntaxe | Dans l'application |
|---|---|
| `++ctrl+k++` (pymdownx.keys) | Affiche les signes plus littéralement |
| Listes d'attributs `{: .une-classe }` autres que `{#ancre}` | Ignorées ou affichées |
| Blocs HTML bruts | Échappés et montrés comme du texte |
| Notes de bas de page, listes de définitions | Non implémentées |

### Les touches clavier sont le piège

Les deux moteurs ont **chacun** leur syntaxe, et aucun ne comprend celle de l'autre :

| | Site (mkdocs) | App (md-lite) |
|---|---|---|
| `++ctrl+k++` | touches stylées | littéral `++ctrl+k++` |
| `:kbd[Ctrl+K]` | littéral `:kbd[Ctrl+K]` | touches stylées |

Aucune forme ne marche des deux côtés. Choisis selon l'endroit qui compte le plus, ou écris
les touches en texte simple (`Ctrl + K`) — ce que font la plupart des pages, et ça se lit
bien partout.

!!! warning "Vérifie avant de t'y fier"

    Le test honnête n'est pas ce tableau, c'est `npm run ci`. `check-docs-xref` rend chaque
    page avec le moteur de l'application et échoue sur tout balisage qui ressort en texte
    visible.

---

## Ce qui ne fonctionne que dans l'APP

Deux choses existent pour BMM et sont inertes sur le site :

- **Les blocs `bmm-replay`** — un enregistrement de session qui se joue dans la page. Les gros
  ne sont pas embarqués : l'app va les chercher sur le site publié.
- **Les deeplinks internes** — `bmm://docs/open?page=…`. Il y en a 42, et la CI vérifie que
  chacun pointe vers une page réelle.

---

## Ajouter une page

1. Crée le fichier sous `BMM Docs/docs/en/…`, et son pendant français sous `docs/fr/…` au
   **même chemin relatif**.
2. Ajoute-la au `nav:` de `mkdocs.yml`. **C'est aussi ce qui l'ordonne dans l'app** :
   `sync-docs` lit ce nav pour construire l'ordre du manifeste, donc une page absente du nav
   est absente de la liste de l'application.
3. Lance `node scripts/sync-docs.mjs` puis `npm run ci`.

!!! note "Le français n'est pas optionnel pour le nav"

    Une page sans fichier français apparaît quand même dans l'app en français, avec son texte
    anglais et une note qui le signale. C'est volontaire — une page vide serait pire — mais
    c'est un manque à combler, pas un état d'arrivée.

---

## Images, diagrammes et enregistrements

- **Diagrammes** : préfère un bloc ` ```mermaid ` à une capture d'écran. Il reste lisible dans
  les deux thèmes, survit à un changement de thème, et se compare dans un diff. La CI vérifie
  que les 56 traversent intacts l'échappement HTML de l'app.
- **Images** : chemins relatifs. Garde-les légères ; tout ce qui est sous `docs/` est embarqué
  dans l'application et voyage avec chaque installation.
- **Enregistrements** : il y a un plafond par fichier (8 Mo) et un budget média total (48 Mo).
  Au-delà, `sync-docs` laisse le fichier sur le site et l'app le diffuse — tu n'as rien à
  faire, mais un très gros enregistrement ne sera pas disponible hors ligne.

---

## Ce que la CI vérifie

`npm run ci` est le contrat. Les portes qui concernent la rédaction :

| Porte | Échoue quand |
|---|---|
| `sync-docs --check` | La copie embarquée est périmée — tu as modifié une page sans resynchroniser |
| `check-docs-xref` | Un lien croisé, une cible `docsPath` ou un `bmm://docs/open` ne pointe sur rien |
| | Une page affiche un `!!! …` visible, un commentaire HTML, du HTML brut, ou les accolades `{#ancre}` |
| | Une source mermaid ne survit pas à l'échappement de l'app |
| `check-encoding` | Un fichier n'est pas de l'UTF-8 propre |
| `check-markup` | Un guillemet typographique (`"` `"`) apparaît dans un attribut HTML |

La dernière mord plus souvent qu'on ne croit : coller depuis un traitement de texte
transforme `"` en `"`, et dans un attribut ça casse l'élément en silence.

---

## Style de la maison

- **Dis ce que ça fait, puis pourquoi.** Un lecteur qui comprend le *pourquoi* devinera le
  *quoi* la fois suivante.
- **Nomme la panne.** « Si le manifeste est injoignable, le navigateur de dépôts est vide ;
  rejoindre par URL directe marche toujours » vaut mieux que « assure-toi que le manifeste
  est joignable ».
- **Des chiffres plutôt que des adjectifs.** « 72 heures », pas « un court délai de grâce ».
- **Deuxième personne, présent.** « Tu choisis un pool », pas « l'utilisateur sélectionnera
  un pool ».
- **Ne promets pas ce qui n'existe pas.** Si c'est prévu, dis-le dans la même phrase.

---

## Modifier la documentation de BetterCommunity

Système différent, à ne pas confondre avec celui-ci. Les docs du site vivent dans sa base de
données et se modifient **dans le navigateur**, sur `/docs`, par quiconque détient la
capacité `manage_docs` (ou un admin). Elles supportent la syntaxe à blocs de BCWEB
(`:::cards`, `::toc`, `:icon[…]`), ont des révisions et des commentaires par page, et sont
initialisées par `apps/api/src/seed-docs.mjs` et `seed-site-guide.mjs`.

En résumé : **BMM l'application → ce dépôt. Le site → le navigateur.**
