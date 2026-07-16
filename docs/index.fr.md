# BetterModsManager

BMM installe, organise et partage tes mods — sur plusieurs jeux, sans jamais toucher aux
fichiers d'origine plus qu'il ne le faut.

Si tu débutes, lis cette page. Elle est courte, et elle explique l'idée unique sur laquelle
tout le reste est bâti. La sauter, c'est la raison pour laquelle on se perd au troisième
écran.

## L'idée unique : tes mods et tes configurations sont deux choses distinctes

La plupart des gestionnaires de mods mettent les mods *dans le jeu*. BMM les garde à part :

- La **[Bibliothèque](features/library.md)** contient chaque mod que tu possèdes. C'est une
  étagère. Un mod qui y dort ne fait rien.
- Un **[Profil](features/profiles.md)** décide lesquels sont *actifs*, et dans quel ordre,
  pour un jeu donné.

Cette séparation est tout l'intérêt. Comme BMM le dit lui-même sur son écran de profil vide :

> Un profil est ton filet de sécurité : active, désactive et réordonne tes mods librement,
> une mise à jour du jeu n'effacera plus jamais ta configuration.

Parce que les mods vivent dans la Bibliothèque, une mise à jour, une réinstallation ou un
mod foireux ne peuvent pas les emporter. Tu reconstruis en rallumant un profil, pas en
retéléchargeant quoi que ce soit.

C'est aussi pour ça que **désinstaller un mod d'un profil ne le supprime pas**. Il redevient
un mod sur une étagère, prêt pour un autre profil. Les débutants s'attendent à une
suppression ; BMM leur offre une annulation.

## À quoi sert chaque écran

| Écran | Quand l'utiliser |
|---|---|
| **[Bibliothèque](features/library.md)** | Voir, ajouter ou vérifier les mods que tu possèdes. |
| **[Profils](features/profiles.md)** | Une configuration par jeu — ou plusieurs par jeu (léger, chargé, test). |
| **[Listes .MM](features/modlist.md)** | Transmettre ta configuration exacte à quelqu'un, liens compris. |
| **[Modpacks](features/modpacks.md)** | Activer/désactiver tout un lot de mods d'un coup. |
| **[Dépôt Serveur](features/repo.md)** | Une source qui prévient BMM quand un mod a une mise à jour. |
| **[Plugins & API](features/plugins.md)** | Faire faire à BMM ce qu'il ne fait pas d'origine. |
| **[App Catalog](features/apps.md)** | Les outils *autour* du modding, installés en un clic. |
| **[Mapper](features/mapper.md)** | Les dossiers d'un mod ne correspondent pas à ce qu'attend le jeu. |
| **[BetterCommunity](features/community.md)** | Les actus et articles des blogs du projet. |
| **[Paramètres](features/settings.md)** | Thèmes, mises à jour, limites de disque, export des données. |

## Les conflits, en un paragraphe

Deux mods qui livrent le même fichier sont en **conflit** — le dernier activé gagne et
écrase l'autre. BMM le détecte *avant* que tu valides, te dit exactement quels fichiers se
chevauchent, et te laisse décider de l'ordre. Tu croiseras ça dès que tu activeras deux gros
mods : autant connaître le mot maintenant. Voir [Bibliothèque](features/library.md#conflicts).

## Et ensuite

1. **[Installer BMM](getting-started/install.md)** — quelques minutes.
2. **[Premier lancement](getting-started/first-launch.md)** — créer un profil, ajouter un mod, l'activer.
3. Puis va à l'écran qui correspond à ce que tu cherches à faire.

!!! tip "Il y a un tutoriel *dans* l'app"

    **Help & other → Interactive Tutorial Hub** t'apprend BMM pas à pas, et embarque de
    petits jeux et un pack de mods pour t'entraîner sans risquer une vraie installation. Si
    tu apprends en faisant plutôt qu'en lisant, commence là et garde ce site en référence.
