# CI/CD de ce dépôt

Les deux workflows GitHub Actions de BMM Docs : ce qui les déclenche, ce qu'ils vérifient, ce qui
les fait échouer, et comment lancer la même chose en local. (Les workflows de l'app BMM elle-même sont
documentés dans le site : `docs/how-it-works/ci-cd.fr.md`.) English: [CI-CD.md](CI-CD.md).

| Workflow | Fichier | Se lance sur | Bloque sur |
|---|---|---|---|
| Docs | `.github/workflows/docs.yml` | push sur `master`, chaque pull request, à la main | un replay qui est un pointeur LFS ou qui manque, des annotations de captures périmées, un lien cassé (`mkdocs build --strict`), un navigateur absent, un PDF tronqué |
| Security | `.github/workflows/security.yml` | push sur `master`, chaque pull request, lundi 04:23 UTC, à la main | un secret dans l'historique, ou un résultat Semgrep / Trivy au seuil ou au-dessus |

Chaque action est épinglée par SHA de commit complet, avec son tag en commentaire. Chaque image
Docker est épinglée par digest. Chaque workflow part de `permissions: {}`, et chaque job ne demande
que ce qu'il utilise.

## Docs (`docs.yml`)

Le job **build** a `contents: read`. Il :

1. fait le checkout avec `lfs: true` et vérifie les replays ;
2. installe l'outillage avec `pip install --require-hashes -r requirements.txt` ;
3. vérifie les annotations (`python tools/annotate.py --check`) ;
4. construit le site avec `mkdocs build --strict` ;
5. construit les éditions PDF sombre et claire, puis relit les quatre avec `tools/check_pdf.py` ;
6. envoie les PDF comme artefact `bettermodsmanager-pdf`.

Sur `master`, le job **deploy** publie le site sur GitHub Pages. C'est le seul job qui a
`pages: write` et `id-token: write`.

`requirements.txt` est un **lock complet** : chaque paquet transitif, avec le sha256 de chaque fichier
que PyPI sert pour lui, généré depuis `requirements.in`. Modifie `requirements.in`, puis régénère :

```bash
uv pip compile requirements.in --universal --python-version 3.12 --generate-hashes -o requirements.txt
```

`--universal` garde le lock valable aussi sous Windows : les paquets propres à une plateforme, comme
`colorama`, y figurent avec leurs marqueurs.

- **Secrets :** aucun. **Variables :** aucune.
- **En local :** `pip install -r requirements.txt`, puis `mkdocs build --strict`. Le PDF a besoin des
  bibliothèques pango et harfbuzz listées dans le workflow ; sous Windows, utilise plutôt
  `python tools/build_pdf_chrome.py`.

## Security (`security.yml`)

| Job | Outil | Ce qu'il lit | Échoue quand |
|---|---|---|---|
| Gate self-test | `node --test` | `.github/scripts/security-gate.test.mjs` | le gate lui-même est faux |
| Secrets | Gitleaks 8.30.1 | tout l'historique git | un résultat non revu dans `.gitleaks.toml` / `.gitleaksignore`, ou zéro commit lu |
| SAST | Semgrep 1.178.0 | tout le checkout : `tools/`, `pdf_event_hook.py`, le JS du lecteur de replays, les workflows | un résultat au seuil Semgrep ou au-dessus |
| Dépendances | Trivy 0.74.0 | le lock `requirements.txt`, donc chaque paquet transitif | un résultat au seuil Trivy ou au-dessus |
| Envoi SARIF vers code scanning | `codeql-action/upload-sarif` | les trois fichiers SARIF | un envoi qui échoue sur un dépôt qui accepte le code scanning |
| Commentaire de PR | `gh api` | les trois verdicts | n'échoue jamais une pull request à lui seul |

Chaque scanner écrit son rapport et sort en 0. **Un seul script décide :**
`.github/scripts/security-gate.mjs`, le même fichier dans BMM Docs, BMM, BetterInstaller et BCW.

- **Secrets :** aucun à créer. Les jobs d'envoi et de commentaire utilisent `GITHUB_TOKEN`.
- **Artefacts** (gardés 30 jours) : `security-gitleaks`, `security-semgrep` et `security-trivy`.
  Chacun contient le rapport JSON, le SARIF, un tableau `*-summary.md` et un verdict `*.result.json`.
- **Pas de DAST (ZAP, Nuclei) :** le site est du HTML statique. Il n'y a ni serveur de staging ni code
  côté serveur, et le seul hôte en ligne est le site de production, qu'aucun scan ici ne doit viser.

### Lire les résultats

- **Log et résumé du job :** un tableau par outil ; chaque résultat bloquant est une annotation
  `::error`. Gitleaks tourne avec `--redact`, donc aucune valeur n'atteint un log.
- **Commentaire de PR :** un commentaire par pull request, modifié à chaque run et retrouvé grâce à sa
  première ligne cachée `<!-- bmm-docs-security-gate -->`. Il montre une ligne par outil, un verdict
  global `PASSED`, `FAILED` ou `INCOMPLETE`, et un lien vers le run et ses artefacts. `INCOMPLETE` veut
  dire qu'un scan n'a pas produit de verdict ; ce n'est jamais un succès. Un fork ou Dependabot reçoit
  un token en lecture seule : une notice, pas de commentaire.
- **Code scanning (onglet Security) :** une catégorie par outil (`gitleaks`, `semgrep`, `trivy`). Les
  alertes sont suivies dans le temps et annotées sur les lignes des pull requests. Elles sont envoyées
  même quand un gate a échoué. Le job vérifie d'abord que le code scanning est disponible (ce dépôt
  est public). S'il ne l'est pas, il affiche une notice et garde le SARIF dans les artefacts.

Le code scanning est une vue. **C'est le gate qui fait échouer le build**, et une alerte écartée le
refait échouer au run suivant tant que l'outil la signale.

### Seuils

Variables de dépôt (**Settings > Secrets and variables > Actions > Variables**) :

| Variable | Valeurs | Défaut |
|---|---|---|
| `SECURITY_GATE_SEVERITY` | `critical`, `high`, `medium`, `low` | `high` |
| `SECURITY_GATE_SEVERITY_SEMGREP` | les mêmes | la valeur globale |
| `SECURITY_GATE_SEVERITY_TRIVY` | les mêmes | la valeur globale |

`high` et au-dessus bloquent par défaut. `medium` ne bloque que si on le choisit. `low` ne bloque qu'à
`low`, et `info` jamais. Gitleaks n'a pas de seuil. Une valeur inconnue fait échouer le run : une faute
de frappe ne doit jamais vouloir dire que rien ne bloque.

### Lancer les scans à la main

```bash
GITLEAKS=zricethezav/gitleaks:v8.30.1@sha256:c00b6bd0aeb3071cbcb79009cb16a60dd9e0a7c60e2be9ab65d25e6bc8abbb7f
SEMGREP=semgrep/semgrep:1.178.0@sha256:32e459968daabe7ab86968184a29109b9564aa00392401156f9788452b42786b
TRIVY=aquasec/trivy:0.74.0@sha256:62b1e65e8869bc4b4c6aa4fa2b21595256c7c2f6018a9d9ad61caf87187c1969
mkdir -p reports

# Secrets (le log doit dire « N commits scanned », N > 0)
docker run --rm -v "$PWD:/repo" -e GIT_CONFIG_COUNT=1 -e GIT_CONFIG_KEY_0=safe.directory -e GIT_CONFIG_VALUE_0='*' \
  "$GITLEAKS" git /repo --config /repo/.gitleaks.toml --redact --verbose \
  --report-format json --report-path /repo/reports/gitleaks.json --exit-code 0
node .github/scripts/security-gate.mjs --tool gitleaks --report reports/gitleaks.json

# SAST, avec les règles au commit épinglé
REF=$(grep -oE 'SEMGREP_RULES_REF: [0-9a-f]{40}' .github/workflows/security.yml | cut -d' ' -f2)
git init -q ../semgrep-rules && git -C ../semgrep-rules fetch -q --depth 1 https://github.com/semgrep/semgrep-rules "$REF" \
  && git -C ../semgrep-rules checkout -q FETCH_HEAD
CFG=$(grep -v '^#' .github/security/semgrep-rules.txt | grep . | sed 's#^#--config=/rules/#')
docker run --rm -v "$PWD:/src" -v "$PWD/../semgrep-rules:/rules:ro" -w /src \
  -e GIT_CONFIG_COUNT=1 -e GIT_CONFIG_KEY_0=safe.directory -e GIT_CONFIG_VALUE_0='*' \
  "$SEMGREP" semgrep scan --metrics=off $CFG --json-output=reports/semgrep.json .
node .github/scripts/security-gate.mjs --tool semgrep --report reports/semgrep.json

# Dépendances
docker run --rm -v "$PWD:/src" -w /src "$TRIVY" fs --scanners vuln,misconfig --show-suppressed \
  --format json --output reports/trivy.json --exit-code 0 .
node .github/scripts/security-gate.mjs --tool trivy --report reports/trivy.json

# Le gate lui-même
node --test .github/scripts/security-gate.test.mjs
```

Sous Windows, utilise Git Bash avec `export MSYS_NO_PATHCONV=1`, et un clone propre : un `site/` local
fait parcourir à Trivy bien plus que la CI. Pour rendre le commentaire de PR en local, ajoute
`--json reports/<outil>.result.json` à chaque ligne de gate, puis lance
`node .github/scripts/security-gate.mjs --markdown --results reports/gitleaks.result.json --results reports/semgrep.result.json --results reports/trivy.result.json`.

### Ajouter, exclure, écarter

- **Règles Semgrep :** `.github/security/semgrep-rules.txt` liste des fichiers de règles de
  `semgrep/semgrep-rules` au commit `SEMGREP_RULES_REF`. Seules sont gardées les règles non marquées
  `subcategory: audit`, parce qu'une règle d'audit signale chaque usage d'un sink pour une revue
  manuelle. Un commit épinglé donne le même résultat l'an prochain ; le prix est de mettre la ref à
  jour à la main.
- **Chemins :** un `.semgrepignore` pour Semgrep, `--skip-dirs` dans l'étape `trivy fs` pour Trivy,
  chacun avec un commentaire qui dit pourquoi.
- **Faux positifs : préfère la config de l'outil à un rejet dans l'onglet Security.** La config est
  versionnée et relue, et elle vaut aussi pour le gate ; un rejet ne fait que cacher l'alerte.
  - Gitleaks, un résultat : son empreinte dans `.gitleaksignore`. Une classe de résultats : une
    allowlist dans `.gitleaks.toml` (voir l'entrée sur les en-têtes PEM).
  - Semgrep : `# nosemgrep: <id-de-règle>` sur la ligne, avec la raison au-dessus. Voir
    `tools/build_pdf_chrome.py`.
  - Trivy : `CVE-… exp:AAAA-MM-JJ` dans `.trivyignore`, sous un commentaire avec la raison.

  Un vrai secret n'est jamais exclu ; fais-le d'abord tourner (rotation). Ne rejette une alerte dans
  l'onglet Security que pour consigner une décision que la config ne sait pas exprimer, avec la
  justification dans le commentaire.

### Tester sans rien toucher en production

Les scans ne lisent que le checkout. Aucun job ne contacte le site publié ni un autre hôte, sauf pour
récupérer les images épinglées, la base d'alertes de Trivy et les règles épinglées. Lance-les sur une
branche, une pull request, avec **Run workflow**, ou en local avec les commandes ci-dessus. Le
déploiement Pages ne tourne que sur `master`.
