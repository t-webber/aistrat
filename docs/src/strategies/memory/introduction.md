# Stratégie 'Avec Mémoire'

L'objectif de cette stratégie est de conserver la mémoire des événements et des données d'un tour au suivant, assurant ainsi une continuité et une cohérence dans le déroulement des actions. Pour ce faire, les informations sont stockées grâce à une [API](./player.md) spécifiquement dédiée à cet effet.

Ces données sont ensuite exploitées pour prendre des décisions. Elles permettent également de conserver des informations sur les unités, désignés comme `targets` (cf. [la doc de l'attaque](../../stages/attaque.md)).

De plus, ces informations sont utilisées pour retenir des détails pertinents concernant les ressources financières sous forme d'or et les divers ennemis. Cette approche vise à optimiser la gestion et l'utilisation des données pour améliorer la prise de décision et renforcer la stratégie globale du jeu.
