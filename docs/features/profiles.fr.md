# Profils

Un profil est une réponse enregistrée à « quels mods sont actifs, dans quel ordre, pour ce
jeu ». C'est l'écran sur lequel tout le reste s'appuie — l'onboarding de BMM l'appelle
lui-même *ton point de départ*.

Son vrai rôle est écrit sur l'écran vide :

> Un profil est ton filet de sécurité : active, désactive et réordonne tes mods librement,
> une mise à jour du jeu n'effacera plus jamais ta configuration.

![L'écran Profils](../assets/screens/profiles.annotated.png)

| | | |
|---|---|---|
| **1** | **Carte de profil** | Clique pour l'activer. Tout ce que tu actives atterrit ici. |
| **2** | **Dossier du jeu** | Là où ce profil se déploie. Voir l'avertissement ci-dessous. |
| **3** | **Nouveau profil** | Un par *configuration*, pas un par jeu — tu peux en avoir plusieurs. |

## Pourquoi plusieurs profils pour un même jeu

Parce que basculer ne coûte rien et revenir en arrière est immédiat. Un découpage typique :

- **Presque vanilla** — deux ou trois correctifs, pour quand tu veux le vrai jeu.
- **Chargé** — la pile complète, pour quand tu ne veux pas.
- **Test** — là où un nouveau mod atterrit d'abord, pour qu'un mod foireux ne touche jamais
  les deux autres.

Changer de profil ne retélécharge rien : les mods vivent déjà dans la
[Bibliothèque](library.md).

## L'erreur qui fait mal : partager un dossier

BMM prévient explicitement, et ça mérite d'être répété.

!!! danger "Deux profils, un seul dossier de jeu"

    D'après l'avertissement de BMM lui-même : partager le même dossier entre plusieurs
    profils est *une source majeure d'erreur humaine*.

    Les deux profils se déploient au même endroit, et aucun ne sait ce que l'autre y a mis.
    Des fichiers survivent au changement de profil, et tu finis par déboguer un mod que tu
    croyais désactivé. Donne à chaque profil son propre dossier, sauf si tu sais exactement
    pourquoi tu fais autrement.

## Les rendre tiens

Un profil accepte une **icône** et une **image de fond** (avec une étape de recadrage pour
respecter le format). Ce n'est pas de la déco gratuite : avec cinq profils, un coup d'œil à
une icône va plus vite que lire cinq noms — et se tromper de profil est précisément
l'erreur que cet écran existe pour éviter.

## Ton premier profil

Dès sa création, BMM te dit ce qui vient de changer :

> Ton premier profil est prêt ! Tout ce que tu actives désormais est enregistré ici — à
> l'abri des mises à jour et des réinstallations.

C'est le contrat. À partir de là, [ajoute un mod](library.md) et active-le.

<!-- TODO(contenu) : l'export/import de profil et le journal de déploiement attendent leur
     capture + spec avant d'être documentés honnêtement. -->
