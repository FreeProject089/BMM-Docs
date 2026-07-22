# Installer BMM

BMM est une application **Windows**. L'installation tient en trois étapes :

1. Télécharge la dernière version — l'installeur est un `.exe` Windows (NSIS), un `.msi` est
   aussi disponible.
2. Lance-le. Windows peut afficher un avertissement SmartScreen la première fois (il le fait
   pour tout nouvel éditeur) — choisis **Informations complémentaires → Exécuter quand même**.
3. Démarre BMM.

C'est tout : aucun compte à créer, rien à configurer au préalable. Ta première configuration
se fait *dans* l'app — voir [Premier lancement](first-launch.md).

!!! tip "Choisis un dossier d'installation que tu contrôles"

    Installe BMM dans un dossier qui t'appartient (ton dossier utilisateur, un disque de jeux)
    plutôt qu'au fond de `Program Files` si tu préfères éviter les demandes de permission de
    Windows quand il se met à jour. BMM ne touche jamais à tes dossiers de jeu tant que *tu*
    n'as pas activé un mod.

## Quelle version ?

La **stable**, sauf raison contraire. Dans **Paramètres → Mises à jour**, tu peux opter pour
les **pré-versions** : elles reçoivent les correctifs en premier et les bugs en premier. C'est
un vrai compromis — d'où l'interrupteur plutôt qu'un défaut. Si tu aimes être en avance et que
signaler une aspérité de temps en temps ne te dérange pas, active-les ; si tu veux juste que
tes mods marchent, laisse coupé.

## Mise à jour automatique

Activée par défaut. BMM vérifie, te prévient, se met à jour. Tu peux la couper au même endroit
— mais mets alors à jour à la main, car un gestionnaire de mods avec un an de retard finira
par ne plus s'entendre avec les dépôts qu'il lit.

!!! note "Limité par GitHub ?"

    Les vérifications de mise à jour et les téléchargements passent par GitHub. Si tu vois un
    jour des erreurs de limite de débit, ajoute un **token GitHub** optionnel dans **Paramètres
    → Identité & API** — il relève la limite. Purement optionnel ; la plupart des gens n'en ont
    jamais besoin.
