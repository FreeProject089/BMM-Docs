# Paramètres

Les Paramètres forment une longue page, mais la plupart se règlent une fois pour toutes. Ce
tour commence par la poignée qui change la *sensation* de BMM, puis parcourt le reste section
par section pour que rien ne reste un mystère.

## Les quatre qui comptent le plus

### Thèmes & Apparence

> Personnalise chaque couleur, police et élément de BMM. Partage tes thèmes en un clic.

Ce n'est pas un interrupteur clair/sombre — c'est un éditeur de thèmes. Tu peux remplacer les
images intégrées de BMM (logo, fond d'écran, même la mascotte Tasky), et *ajouter tes propres
boutons, bannières, badges ou widgets n'importe où dans BMM*. Un thème s'exporte et s'importe
en fichier, et un catalogue de thèmes fonctionne comme l'[App Catalog](apps.md). Vois
[Thèmes](themes.md) pour tout le moteur.

Pars d'un des préréglages intégrés et ajuste. Le conseil de l'éditeur lui-même : survole un
libellé pour l'aide, clique sur **?** pour la doc MDN de la propriété CSS.

### Stockage & Smart I/O

Le réglage à connaître si BMM rend ton PC poussif pendant l'activation des mods :

> Limite la vitesse de lecture/écriture sur tes disques pendant l'activation des mods pour
> éviter les ralentissements. (0 = illimité)

L'**auto-calibration** teste tes disques et suggère une limite d'E/S pour chacun. Lance-la une
fois ; c'est la différence entre « les mods s'activent en arrière-plan » et « ma machine a
gelé trente secondes ». Les limites sont par disque : un NVMe rapide et un disque externe lent
ont chacun leur plafond.

### Mises à jour

Vérifie une nouvelle version de BMM, opte pour les **pré-versions**, ou coupe la **mise à jour
automatique**. Les pré-versions reçoivent les correctifs en premier et les bugs en premier —
l'interrupteur existe pour que ce soit ton choix, pas une surprise. Un contrôle distinct
vérifie tes *mods* (voir [Mises à jour de mods](modlist.md)), à ne pas confondre avec la mise
à jour de l'app elle-même.

### Données

Exporte tout, réimporte. Fais un export avant toute manip dont tu n'es pas sûr : c'est
l'assurance la moins chère de l'app.

!!! danger "Réinitialisation d'usine"

    La section Debug peut remettre BMM à zéro. Elle demande confirmation. Il n'y a pas de
    retour en arrière — exporte tes données avant de t'en approcher.

## Tout le reste, section par section

### Langue

Change la langue de l'interface. Les traductions sont éditables par la communauté — les mêmes
fichiers que lit ce sélecteur peuvent être exportés, traduits, et réimportés (voir les outils
de traduction plus bas).

### Identité & API

> Tous tes identifiants importants au même endroit. Clique sur l'icône œil pour révéler une
> valeur.

Ton **creator ID**, le **token API** local, l'**URL et le port** de l'API, et la version de
l'app. L'[API locale](../reference/api.md) se lie à `127.0.0.1` sur le port **51274** par
défaut ; tu peux changer le port ici (effet après redémarrage). C'est aussi là que tu révèles
ou réinitialises le token API avec lequel les plugins et scripts s'authentifient.

### Confidentialité & Télémétrie

Accepte ou refuse les données d'usage anonymes, et gère les sous-options (rejeux de session,
capture complète, partage de benchmark) indépendamment. Tout est coupé sauf si tu l'actives, et
la page détaille exactement ce que chaque interrupteur envoie.

### Sécurité (confiance des plugins)

Choisis la liberté accordée aux plugins : **accès complet** ou mode **limité/en bac à sable**.
C'est le garde-fou global des permissions par plugin que tu accordes dans
[Plugins & API](plugins.md) — resserre-le si tu exécutes des plugins que tu ne connais pas.

### Discord Rich Presence

Affiche ce que tu fais dans BMM sur ton profil Discord, ou coupe-le. Purement cosmétique.

### Launch Packs

Regroupe plusieurs apps/exécutables en un pack que tu lances ensemble — pratique pour « lancer
le jeu, l'outil de reconnaissance vocale et l'app de carte » en un clic. Crée, édite et
supprime des packs ici ; lance-les depuis ici, l'[API](../reference/api.md), ou un deeplink.

### Planification & automatisation

Enregistre des tâches — appliquer un modpack, lancer un launch pack, exporter tes données — et
déclenche-les sur planning ou à la demande. Voir [Planificateur](scheduler.md) pour le tableau
complet.

### Outils de stockage : intégrité & benchmark

Au-delà des limites Smart I/O ci-dessus, cette zone tient le contrôle de **recalcul SHA**
(reconstruire les hachages par fichier que vérifie le moteur d'intégrité) et le **benchmark**
(mesurer la vitesse à laquelle BMM déplace les fichiers sur ton matériel — le moteur qu'utilise
l'auto-calibration).

### Tags

Gère tes tags de mods personnalisés — les libellés par lesquels tu filtres la
[Bibliothèque](library.md). Renomme-les ou supprime-les ici, au même endroit.

### Son & raccourcis clavier

Active/coupe les sons de l'interface, et consulte les raccourcis clavier auxquels BMM répond.

### Token GitHub

Un token d'accès personnel optionnel, utilisé quand BMM parle à GitHub (vérifs de release,
téléchargements bruts) pour éviter la limite de débit anonyme plus stricte. Optionnel — n'en
ajoute un que si tu atteins les limites.

### Tutoriel

Rejoue les tutoriels interactifs de l'app à tout moment. Nouveau sur BMM ? Commence ici.

### Debug & outils développeur

Diagnostics, outils de rapports de crash, et la **réinitialisation d'usine** notée plus haut.
Pratique quand quelque chose cloche ; la réinit est le seul contrôle de toute l'app sans retour
en arrière, donc protégé par une confirmation.
