# Synchro & dépôts serveur

Un dépôt serveur transforme le profil d'une personne en **source de vérité hébergée**. Tous les
abonnés convergent vers exactement les mêmes mods, versions et ordre — et le restent à mesure que le
propriétaire le met à jour.

## Comment un client reste synchronisé

Le client ne re-télécharge jamais à l'aveugle. Il récupère le **manifeste** du dépôt — une liste de
fichiers avec leurs empreintes BLAKE3 — et la compare à ce qu'il possède déjà. Seules les différences
bougent.

```mermaid
sequenceDiagram
    participant Host as Dépôt serveur
    participant Client as BMM du membre
    Client->>Host: GET manifeste (fichiers + hachages)
    Host-->>Client: manifeste
    Note over Client: diff avec l'index local
    Client->>Host: demander seulement manquants / modifiés
    Host-->>Client: ces fichiers
    Note over Client: vérifier les hachages, puis déployer
```

Voilà pourquoi une petite mise à jour d'une collection de 10&nbsp;Go coûte quelques Mo : le diff du
manifeste isole le seul mod modifié, et le hachage d'intégrité garantit que les octets transférés sont
corrects.

## Accès & authenticité

```mermaid
flowchart TB
    REPO["Dépôt serveur"] --> GATE{Accès}
    GATE -- public --> ANY["quiconque a le lien"]
    GATE -- e-mail --> WL["comptes en liste blanche"]
    GATE -- mot de passe --> PW["détenteurs du mot de passe"]
    REPO --> FP["Empreinte (BCR-XXXX-XXXX)"]
    FP --> VERIFY["les membres vérifient qu'ils sont<br/>sur le vrai dépôt, pas un imposteur"]
```

Un dépôt peut être ouvert, ou protégé par e-mail/mot de passe, et chacun porte une **empreinte** stable
pour que les membres confirment qu'ils sont abonnés à la source authentique.

!!! info "À voir dans l'app"
    Aide &amp; autre → Développeur → **Mode serveur**, **Flux d'hébergement** et **Hébergement dédié**.
    Guide utilisateur : [Dépôt Serveur](../features/repo.md).
