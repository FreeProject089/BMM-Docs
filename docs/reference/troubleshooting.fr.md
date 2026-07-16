# Dépannage

Commence ici avant de réinstaller quoi que ce soit.

## Le jeu fait comme si le mod n'existait pas

Presque toujours l'empaquetage, pas BMM. L'archive a un dossier de trop : le jeu cherche
`Data/` et trouve `MonMod-v3/Data/`. Ouvre le [Mapper](../features/mapper.md), lance le
**Diagnostic de structure**, et vérifie le chemin final *avant* d'appliquer.

## Un mod que j'ai désactivé est toujours actif

Deux profils pointant vers le même dossier de jeu. BMM prévient à la configuration — c'est
*une source majeure d'erreur humaine*. Les deux se déploient au même endroit et aucun ne sait
ce que l'autre a laissé. Donne à chaque profil son dossier. Voir
[Profils](../features/profiles.md).

## Deux mods se battent — l'un écrase l'autre

C'est un [conflit](../features/library.md#conflicts), et c'est attendu : ils livrent le même
fichier. BMM te montre exactement quels fichiers se chevauchent et te laisse fixer l'ordre
d'activation. Le dernier activé gagne.

## BMM dit qu'un mod n'a pas de mise à jour, mais je sais que si

Si la source du mod est un **téléchargement direct**, BMM est honnête :

> Un téléchargement direct n'a pas de version, BMM ne peut donc pas savoir s'il est plus
> récent.

Il n'y a rien à comparer. Lie le mod à un [dépôt](../features/repo.md) qui publie des
versions, ou utilise le retéléchargement direct.

## Mon PC rame pendant l'activation des mods

**Paramètres → Stockage**. Active **Smart I/O** et lance l'**auto-calibration** une fois :
elle teste tes disques et rythme les copies pour que l'activation cesse d'affamer le reste.

## Un modpack ne s'applique pas entièrement

La carte dira que des mods sont manquants ou corrompus, et proposera **Réparer**. Fais-le. Un
pack qui ne s'applique pas complètement explique bien plus de bugs que le jeu.

## Quelque chose ne va vraiment pas

**Paramètres → Données → Exporter**, d'abord, toujours. Ensuite la section Debug a un dossier
de logs de crash et une réinitialisation d'usine. Le reset n'a pas de retour arrière —
exporte avant de t'en approcher.
