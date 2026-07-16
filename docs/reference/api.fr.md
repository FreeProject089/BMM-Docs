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

Huit, par paires lecture/écriture sur quatre domaines :

```
app.read       app.write
catalog.read   catalog.write
mods.read      mods.write
profiles.read  profiles.write
```

Un endpoint d'écriture exige le `*.write` correspondant : `POST /api/mods/enable` demande
`mods.write`, `POST /api/profiles/create` demande `profiles.write`. Un plugin qui appelle
sans l'autorisation reçoit une erreur qui nomme exactement celle qui lui manque, plutôt
qu'un silence.

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
| `GET /api/mods/{id}` | Un mod. |
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
| `POST /api/profiles/create` · `/api/profiles/activate` | `profiles.write`. |
| `POST /api/modpacks/create` · `/enable` · `/disable` | `catalog.write`. |
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
