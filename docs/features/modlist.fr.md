# Listes .MM

Un fichier `.MM`, c'est ta **configuration complète, écrite** — et contrairement à un
[modpack](modpacks.md), il embarque les liens de téléchargement : la personne qui le reçoit
n'a pas besoin de posséder les mods au préalable.

La définition de BMM lui-même :

> Un fichier JSON contenant ta liste complète de mods, les liens de téléchargement, l'ordre
> d'installation et les règles de conflit.

Toute la différence est là. Un modpack dit *quels mods* ; une liste `.MM` dit *quels mods,
où les prendre, dans quel ordre, et quoi faire quand ils se marchent dessus*.

![L'écran Listes .MM](../assets/screens/modlist.annotated.png)

| | | |
|---|---|---|
| **1** | **Exporter** | Écrit le fichier `.MM`. |
| **2** | **Importer** | En lit un, puis télécharge et installe. |
| **3** | **Profil auto** | Génère un profil dédié pour la liste importée. |

## Le partage

> Envoie ton fichier `.MM` à d'autres utilisateurs pour reproduire exactement ta
> configuration.

*Exactement* est le mot qui compte, et c'est pourquoi l'ordre et les règles de conflit
voyagent avec la liste. Deux personnes avec les mêmes mods et un ordre d'activation
différent n'ont **pas** le même jeu — voir [les conflits](library.md#conflicts).

### Inclure les hashes ?

Une option d'export, et un vrai compromis, dans les mots de BMM :

> Vérifiable par les destinataires — plus lent pour les gros mods.

Inclus-les quand l'exactitude compte (tu publies une liste, ou tu débogues celle de
quelqu'un). Passe-t'en pour un envoi rapide à un ami avec une bonne connexion.

## L'import

BMM récupère les archives et les extrait (*Installation en cours…*), puis respecte l'ordre
porté par la liste. Coche **profil auto** et il construit un [profil](profiles.md) dédié
plutôt que de tout mélanger à ta configuration actuelle — ce qui est presque toujours ce
qu'on veut en essayant la config de quelqu'un d'autre.

<!-- TODO(contenu) : la partie « règles de conflit » du format mérite sa propre page. -->
