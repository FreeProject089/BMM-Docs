# Référence API

BMM fait tourner une API HTTP locale. C'est ce à quoi parlent les
[plugins](../features/plugins.md), ce que pilote le planificateur, et ce que tu peux
interroger toi-même au `curl`.

**URL de base :** `http://127.0.0.1:51274` — locale uniquement. 51274 est le défaut ; s'il
est pris, BMM en lie un autre et annonce le port effectif : lis-le depuis l'app plutôt que de
le coder en dur.

## S'authentifier

Chaque appel porte un token :

```bash
curl -H "Authorization: Bearer $TOKEN" http://127.0.0.1:51274/api/health
```

Il existe **deux sortes de tokens**, et la différence *est* le modèle de sécurité :

| Token | D'où il vient | Ce qu'il peut faire |
|---|---|---|
| **Token admin** | Paramètres — un par installation | Tout. Aucun contrôle de permission. |
| **Token de plugin** | Émis par plugin | Uniquement ce qui lui a été accordé. |

Utilise le token admin pour tes propres scripts, la CLI ou le testeur intégré. Donne à
**chaque plugin son propre token** — l'app le dit clairement : *chaque plugin devrait
s'authentifier avec son PROPRE token*. Ce n'est pas de la paperasse : c'est ce qui donne un
sens aux permissions, car BMM déduit *qui appelle* du token lui-même, jamais d'un en-tête
qu'un appelant pourrait inventer.

## Les permissions

**Les écritures sont contrôlées. Les lectures ne le sont pas.** Cette asymétrie est la chose
à comprendre avant de raisonner sur le reste.

Un endpoint d'écriture exige une permission précise : `POST /api/mods/enable` demande
`mods.write`, `POST /api/profiles/create` demande `profiles.write`. Un appelant sans
l'autorisation reçoit une erreur qui nomme exactement celle qui manque, plutôt qu'un silence.

Un endpoint de lecture (`GET /api/mods`, `/api/profiles`, `/api/plugins`, `/api/mods/active`)
n'exige **aucun token**. Ce qui le protège n'est pas une permission — c'est le CORS et
l'écoute en loopback : l'API n'écoute que sur `127.0.0.1`, et en build de release seules les
origines du WebView Tauri et `bettercommunity.ch` peuvent l'appeler depuis un navigateur. Un
site web quelconque ne peut pas lire ta liste de mods. Un programme tournant sur ton PC, si —
mais il pourrait de toute façon lire les fichiers de BMM directement : rien n'est perdu là.

Voici les permissions que le code exige réellement :

| Permission | Contrôle |
|---|---|
| `mods.write` | Activer / désactiver / supprimer un mod |
| `profiles.write` | Créer / activer / supprimer un profil |
| `modpacks.write` | Activer / désactiver / créer un modpack |
| `plugins.read` | `plugins/compare` |
| `plugins.write` | `plugins/apply` |
| `catalog.read` · `catalog.write` | [App Catalog](../features/apps.md) |
| `app.read` · `app.write` | Actions au niveau de l'app |
| `repo.write` | Actions [Dépôt Serveur](../features/repo.md) |

!!! note "Il n'existe ni `mods.read` ni `profiles.read`"

    Toutes les permissions ci-dessus sont des permissions d'écriture, sauf les permissions de
    lecture de `plugins`, `app` et `catalog` — les trois seuls domaines dont les routes GET
    sont contrôlées. Les lectures n'étant pas contrôlées ailleurs, une permission `mods.read`
    n'ouvrirait rien : elle n'existe donc pas. Pour donner à un plugin un accès en lecture
    seule à tes mods, ne lui accorde rien : il peut déjà appeler `GET /api/mods`.

    Les versions précédentes annonçaient `mods.read` / `profiles.read` dans **Plugins → API**
    et omettaient `modpacks.write`, `plugins.read`, `plugins.write` et `repo.write`. La liste
    affichée dans l'app correspond désormais à ce tableau.

Accorde-les par plugin dans **Plugins → Permissions**, ou via l'API :

| Endpoint | Rôle |
|---|---|
| `GET /api/plugins/permissions` | Une carte `plugin_id → [permissions]` — tous les plugins d'un coup. |
| `GET /api/plugins/{id}/permissions` | La liste d'un plugin. |
| `POST /api/plugins/{id}/permissions` | **Remplace** toute la liste. Ce n'est pas une fusion. |

!!! warning "Remplacement, pas ajout"

    Définir les permissions écrase la liste. Lis-la d'abord, ajoute à ce que tu as reçu,
    renvoie le tout — sinon tu révoques en silence tout ce que tu n'as pas mentionné.

## Les endpoints

74 au total. La forme est constante : `GET` lit, `POST` agit.

### Lecture

| Endpoint | Renvoie |
|---|---|
| `GET /api/health` | BMM est-il en vie. Sans authentification. |
| `GET /api/status` | Ce qu'il est en train de faire. |
| `GET /api/mods` | Chaque mod de la [Bibliothèque](../features/library.md). |
| `GET /api/mods/active` | Seulement ce qui est actif sur le profil courant. |
| `GET /api/profiles` | Chaque [profil](../features/profiles.md). |
| `GET /api/modpacks` | Chaque [modpack](../features/modpacks.md). |
| `GET /api/plugins` | Les plugins installés. |
| `GET /api/creator-id` | Ton creator ID — l'identité sous laquelle les [dépôts](../features/repo.md) te connaissent. |
| `GET /api/check-update` | Une mise à jour de BMM est-elle disponible. |

### Action

| Endpoint | Rôle |
|---|---|
| `POST /api/mods/enable` · `/api/mods/disable` | Active ou désactive un mod. `mods.write`. |
| `POST /api/mod/check-updates` | Interroge les [dépôts](../features/repo.md) liés. |
| `POST /api/profiles` (création) · `/api/profiles/activate` | `profiles.write`. |
| `POST /api/modpacks/create` · `/enable` · `/disable` | `modpacks.write`. |
| `POST /api/plugins/apply` | Exécute la liste de mods d'un plugin. |
| `POST /api/plugins/compare` | Ce qui *changerait* — sans rien changer. |
| `POST /api/launchpack/run` | Lance un pack. |
| `POST /api/data/export-auto` | Déclenche un export des données. |

!!! tip "compare avant apply"

    `plugins/compare` répond à « qu'est-ce que ça ferait ? » sans rien toucher. Utilise-le
    avant `apply` — surtout en [mode strict](../features/plugins.md#strict-mode), où apply
    désactive tout ce qui n'est pas dans la liste.

## Essayer sans écrire de code

**Plugins → API** embarque un testeur : choisis un endpoint, envoie, lis la réponse. Il
utilise le token admin, donc il voit tout — ce qui en fait le mauvais endroit pour vérifier
que les *permissions* d'un plugin sont correctes. Pour ça, sers-toi du token du plugin.

<!-- TODO(contenu) : la liste complète des 74 endpoints avec corps de requête/réponse. Les
     noms et chemins ci-dessus sont lus dans src-tauri/src/api/mod.rs et les chaînes Lang ;
     les corps demandent une capture du testeur ou une passe sur les handlers. -->
