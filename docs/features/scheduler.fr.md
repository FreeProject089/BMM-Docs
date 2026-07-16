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
| `Toujours` | Sans condition. |
| `Profil actif` | Un [profil](profiles.md) donné est le courant. |
| `Mod activé` / `Mod désactivé` | L'état d'un mod donné. |
| `Modpack actif` | Un [modpack](modpacks.md) est appliqué. |
| `Tous les mods du profil actif sont on` | Rien n'est éteint dans le profil. |
| `App en cours d'exécution` | Un processus tourne — le jeu, par exemple. |
| `Jour de la semaine` | Lundi…dimanche. |
| `Heure comprise dans` | Une plage horaire. |
| `Comparaison de valeur` | `si X > Y` — une comparaison numérique. |
| `La commande réussit` | Une commande externe sort en 0. |

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

<!-- TODO(contenu) : les opérandes de la comparaison de valeur et les options de boucle
     attendent leur capture + spec. -->
