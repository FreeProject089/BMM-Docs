# Planification & automatisation

> Planifie des actions BMM (ponctuelles ou récurrentes) — activer un mod, un modpack, un
> profil…

Accessible depuis [Plugins & API](plugins.md). C'est la partie de BMM qui agit pendant que tu
regardes ailleurs.

![Le planificateur](../assets/screens/scheduler.annotated.png)

| | | |
|---|---|---|
| **1** | **Déclencheur** | *Quand* ça tourne. |
| **2** | **Règles** | *Si* ça tourne, et ce que ça fait. |
| **3** | **Nouvelle tâche** | Une tâche, un travail. |

## Une tâche a trois parties

**Déclencheur → règles → action.** Le déclencheur demande *quand*, les règles demandent *si*,
l'action est *quoi*.

### 1. Déclencheur — quand

| Type | Se déclenche |
|---|---|
| `once` | Une fois, à une date et une heure. |
| `interval` | Toutes les N minutes. |
| `hourly` | Toutes les N heures. |

Il existe aussi une option mensuelle, construite via les classes de planification du système
plutôt qu'avec une simple cmdlet — elle existe, elle est juste assemblée autrement dessous.

### 2. Règles — si

Une règle, c'est `SI <condition> ALORS <action>`. C'est là que le planificateur cesse d'être
une minuterie et devient utile. Les conditions :

| Condition | Vraie quand |
|---|---|
| `Toujours` | Sans condition (par défaut). |
| `Profil actif` | Un [profil](profiles.md) donné est le courant. |
| `Mod activé` / `Mod désactivé` | L'état d'un mod donné. |
| `Modpack actif` / `Modpack inactif` | Tous les mods d'un [modpack](modpacks.md) sont on / off. |
| `Tous les mods du profil actif sont on` | Rien n'est éteint dans le profil. |
| `App en cours` / `App non lancée` | Un processus (par nom) tourne ou non — le jeu, par exemple. |
| `En ligne` | La machine a une connexion internet. |
| `Jour de la semaine` | Aujourd'hui est un des jours choisis. |
| `Plage horaire` / `Heure atteinte` | L'horloge est dans une plage / a dépassé une heure. |
| `Fichier existe` / `hash` / `taille` / `type` | Vérifs de fichier — un chemin existe, ou son hash (blake3/sha256), sa taille ou son type correspond. |
| `La commande réussit` | Une commande externe s'exécute et sort en `0`. |
| `Comparaison de valeur` | Un nombre capté se compare à un seuil (plus bas). |

!!! warning "La première qui correspond gagne"

    D'après l'état vide du planificateur lui-même : *Aucune règle — ajoutes-en une. **La
    première ligne qui correspond gagne** (de haut en bas).*

    Ordonne tes règles **de la plus spécifique à la plus générale**, exactement comme des
    règles de pare-feu. Une règle `Toujours` en haut rend toutes celles du dessous du code
    mort — et rien ne te le dira, puisque du point de vue du planificateur, il a fait son
    travail.

### 3. Action — quoi

| | |
|---|---|
| **Mods** | Activer / désactiver un mod · tout activer · tout désactiver · scanner le dossier |
| **Profils** | Activer un profil |
| **Modpacks** | Activer / désactiver |
| **App** | Lancer une app · lancer un benchmark · appliquer un thème |
| **Autres** | Afficher une notification · exécuter un deeplink `bmm://` · lancer une commande |

## Tourner quand BMM est fermé

> Exécuter même quand BMM est fermé.

Ça enregistre la tâche auprès du **planificateur de ton système**, pas de la boucle interne
de BMM. Le système la réveille à l'heure, que l'app tourne ou non — tout l'intérêt d'un
« prépare mon modpack à 6h ».

Ça veut aussi dire que la tâche vit en dehors de BMM. La supprimer dans BMM supprime aussi la
tâche système ; si tu fouilles la liste des tâches de ton OS, ce sont ces entrées-là.

## Les commandes personnalisées

> Autoriser les commandes personnalisées.

Désactivé par défaut, et à raison : une tâche planifiée capable d'exécuter n'importe quelle
commande est une tâche capable de tout, à une heure où tu ne regardes pas. Active-la quand tu
en as besoin, et sache ce que fait la commande.

## Un exemple

Le planificateur en fournit un, et c'est une bonne forme à copier :

> Toutes les heures, boucle 3× et affiche une notification à chaque fois.

Pars de là, remplace la notification par une vraie action, et ajoute une condition pour
qu'elle ne se déclenche que quand il le faut.

### La condition `Comparaison de valeur`

Elle compare un nombre que BMM a capté plus tôt dans l'exécution — par exemple la vitesse
d'écriture mesurée d'un disque (`disk.write_mbps`) ou un résultat de benchmark
(`benchmark.mbps`) — à un seuil que tu fixes, via l'un de six opérateurs :

`>` · `<` · `>=` · `<=` · `==` · `!=`

Ainsi « *si `disk.write_mbps` `<` 50, affiche un avertissement* » devient une vraie règle. Si
la valeur source n'a jamais été captée, la condition est simplement fausse — elle ne se
déclenche pas sur une donnée manquante. Chaque condition peut aussi être **niée**.

## Boucles & attente

Au-delà d'une liste plate d'actions, une tâche peut se ramifier et se répéter :

| Bloc | Rôle |
|---|---|
| **`si`** | Exécute un jeu d'étapes quand une condition tient, un autre (`sinon`) quand elle ne tient pas. |
| **`répéter`** | Exécute ses étapes en boucle — `tant que` une condition tient, `jusqu'à` ce qu'une tienne, ou un nombre fixe de `fois`. `everySec` fixe l'écart entre itérations, et **`maxIters` est un plafond de sécurité strict** pour qu'une boucle `tant que`/`jusqu'à` ne tourne jamais indéfiniment. |
| **`attendre`** | Met en pause jusqu'à ce qu'une condition devienne vraie, en sondant toutes les `pollSec`, jusqu'à `timeoutSec`. Au timeout, elle **abandonne** la tâche ou **continue** quand même — au choix. |

L'exemple fourni est un `répéter` en mode `fois` (boucle 3×). Change le mode en
`tant que`/`jusqu'à` avec une condition `Comparaison de valeur` ou `App en cours`, et tu
obtiens des automatisations comme « *continue de vérifier jusqu'à ce que le processus du jeu
sorte, puis exporte mes données* ».

