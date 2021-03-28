# Compilateur de statistique COVID - FRANCE

## Origine des statistiques
Les fichiers de bases proviennent directement du site du gouvernement français.

 - Statistique pour les hospitalisations :

   - Site : [https://www.data.gouv.fr/fr/datasets/donnees-hospitalieres-relatives-a-lepidemie-de-covid-19/](https://www.data.gouv.fr/fr/datasets/donnees-hospitalieres-relatives-a-lepidemie-de-covid-19/)

   - CSV : [https://www.data.gouv.fr/fr/datasets/r/63352e38-d353-4b54-bfd1-f1b3ee1cabd7](https://www.data.gouv.fr/fr/datasets/r/63352e38-d353-4b54-bfd1-f1b3ee1cabd7)

 - Statistique pour les tests :

   - Site : [https://www.data.gouv.fr/fr/datasets/donnees-relatives-aux-tests-de-depistage-de-covid-19-realises-en-laboratoire-de-ville/](https://www.data.gouv.fr/fr/datasets/donnees-relatives-aux-tests-de-depistage-de-covid-19-realises-en-laboratoire-de-ville/)

   - CSV : [https://www.data.gouv.fr/fr/datasets/r/b4ea7b4b-b7d1-4885-a099-71852291ff20](https://www.data.gouv.fr/fr/datasets/r/b4ea7b4b-b7d1-4885-a099-71852291ff20)

## Usage

Il n'y a pas d'installation à effectuer. On lance seulement le programme `draw_covid.py`. Pour cela :
> python3 draw_covid.py [options]

Dépendance python : matplotlib
> Systèmes Debian : `apt install -y python3-matplotlib`
> Python : `pip install matplotlib`

### options disponbiles :

|		option			|		Fonctionnalités			|
|	:-------------:		|		:--------------			|
|	-h ou - -help		|		Affiche l'aide			|
|	-c ou - -colonnes	| Pour le graphique : affiche seulement les colonnes dont les numéros sont donnés après. |
|	-r ou - -no-recalcul| Permet de ne pas refaire le calcul du fichier de résultat |
|	-e ou - -exclude	| Pour le fichier résultat : permet d'exclure les colonnes indiquées par leurs numéros lors de la génération de ce fichier. Voir les tableaux suivant pour trouver leurs numéros. |
|		- -no-draw		| Pour ne pas afficher le graphique et seulement générer le fichier de résultat |
|	- -print-colonnes	| Lorsqu'on n'affiche pas le graphique, permet d'afficher un tableau avec les noms des colonnes du fichier de résultat et les derniers chiffres disponibles. |
|	- -from-date		| Permet de choisir la date à laquelle commencer les statistiques. |

## Résultat obtenu
Les résultats bruts se trouvent dans le fichier [result.csv](donnees/result.csv)

Un nouveau CSV contenant la compilation des chiffres au niveau national pour les points suivants (dans l'ordre des colonnes du CSV généré) :

 - Colonnes des chiffres :

| Date | Nombre de test | Nombre de positif | Nombre d'hospitalisation | Nombre de réanimation |
| :--: | :------------: | :---------------: | :----------------------: | :-------------------: |
|  0   |       1        |         2         |            3             |           4           |
| Date des chiffres | Nombre de test effectué ce jour là | Nombre de test positif ce jour là | Nombre d'hospitalisation ce jour là | Nombre de réanimation ce jour là |

 - Colonnes des chiffres qui sont récupérés du gouvernement mais par défaut non gardés dans le fichier de résultat :

| Cumul des décès | Cumul de retour à domicile |
| :-------------: | :------------------------: |
|        5        |              6             |
| Nombre de décès total à cette date. | Nombre total de retour à domicile à cette date |


 - Colonnes calculées grâces aux statistiques précédentes :

| Nombre de décès | Nombre de malades* | Nombre de retour à domicile | % cas positif | % mort | % d'hospitalisation | % réanimation |
| :-------------: | :---------------: | :-------------------------: | :-----------: | :----: | :-----------------: | :-----------: |
|        7        |         8         |              9              |       10      |   11   |         12          |       13      |
| Nombre de décès ce jour-là | Nombre de malade* ce jour-là | Nombre de retour à domicile ce jour-là | pourcentage de cas positif ce jour-là | % de mort de jour là | % d'hospitalisation | % de réanimation ce jour-là |

**\* Le nombre de malades est calculé en faisant la somme du nombre des nouveaux cas des 7 jours précédents. Ces chiffres n'ont aucune signification pour les 7 premiers jours...**

### Calculs effectués sur les chiffres :
 - Nombre de décès : [Nombre de décès du jour] - [Nombre de décès de la veille]

 - Nombre de malades : (SOMME des malades d'aujourd'hui et des 6 jours précédents)

 - Nombre de retours à domicile : [Nombre de rad du jour] - [Nombre de rad de la veille]

 - Pourcentage de cas positif : [Nombre de cas positif] / [Nombre de personne testé] * 100

 - Pourcentage de mort : [Nombre de mort ce jour-là] / [Nombre de malade ce jour mà] * 100

 - Pourcentage d'hospitalisé : [Nombre d'hospitalisé du jour] / [Nombre de malade du jour] * 100


## Fonctionnement du code

J'ai écrit ce code très rapidement, il n'est donc pas très propre du tout... Mais il marche (enfin, je crois)...

### Etapes

 1 - Téléchargements des données depuis le site du gouvernement. Cible : donnees/. On y retrouve les fichiers base* qui correspondent aux données qui ne seront pas modifiées. Les deux autres sont les mêmes fichiers mais qui pourront être modifié par la suite. Il est possible de sauter cette étape avec l'option `--no-download`.

 2 - Compilation des données. On nettoie sur les fichiers pour obtenir les résultats nationaux (et non départementaux), tout sexe confondue.
 
 Ensuite on génère un fichier "resultat" qui accueil le mixe des deux fichiers précédents. Il est possible de choisir les colonnes qui seront gardées dans ce fichier avec l'option `--exclude <numeros des colonnes>` : _(voir les tableaux au-dessus pour trouver facilement les numéros de colonnes)_.

 3 - Affichage des données sous forme d'un graphique brut. Il utilise matplotlib, dont je ne connais pas super bien les options... Donc il n'est pas des plus jolies... Il est possible de choisir les données à afficher grâce à l'option `--colonnes <numeros des colonnes>` : _(voir la sortie standard du terminal pour trouver les numéros de colonnes)_.


### Première parties du code : 4 fonctions utilitaires

 - `wl` : Écrit juste une ligne dans le fichier de résultat.
 - `wc` : Écrit les colonnes choisis dans le fichier résultat. On lui donne la ligne sous forme de liste, les colonnes à ne pas mettre. Et il appelle `wl` avec la ligne en syntaxe csv.
 - `colorprint` : fait juste un `print` avec de la couleur.
 - `print_colonnes_name` : Affiche le nom des colonnes présentent dans le fichier result.csv. Affiche également les derniers chiffres disponible _(ATTENTION : il est affiché "ajd" mais les chiffres s'arrête parfois 3-4 jours avant...)_.

### Seconde parties du code : téléchargement des données

 - `download_files` : Télécharge simplement les csv depuis le site du gouvernement _(voir liens plus haut)_.
 - `reset_data` : Si l'utilisateur utilise l'option `--no-download`, les fichiers utilisés pour le traitement sont supprimés, et les fichiers base* sont copiés pour être utilisé. Cela à fin de ne pas re-télécharger toujours les données pour afficher des graphiques différents.

### Troisième partie du code : traitement des données

 - `hospi_to_national` : Compile les données d'hospitalisation pour n'en faire plus qu'un fichier de données national. Normalement, le fichier reste intact durant les calculs. On ne garde donc que les données des deux sexes réunit, et fait l'addition de tout les départements sauf ceux d'outre-mer.
 - `to_same_date` : Enlève les données au début des deux fichiers de données nationales afin qu'ils commencent au même date. Si une date est mentionnée avec l'option `--from-date`, les données avant cette date sont supprimées.
 - `sort_file` : Fonction qui assemble les deux fichiers de données national dans le fichier result.csv, avec les colonnes suivantes : jour, nombre de tests du jour, nombre de cas positif du jour, nombre d'hospitalisations du jour, nombre de réanimations du jour, cumul des décès à ce jour, cumul du nombre de retour à domicile.
 - `complete_file` : Il prend le fichier result.csv et ajoute des données en faisant des calculs sur les données déjà présentes. _(voir le tableau plus haut pour voir les données calculées)_.

### Quatrième partie du code : Affichage des données

 - `draw` : Affiche les colonnes indiquées en paramètre sur un graphique à l'aide de matplotlib. Il y a sûrement beaucoup d'amélioration à faire de ce côté, mais j'ai pas le temps...

Il reste une dernière petite fonction qui resservira sûrement d'autres fois : `read_args`, elle lit les arguments en paramètres du programme et les range dans un dictionnaire avec +/- le bon type...


### Codes d'erreurs :

| N° erreur | signification |
| :-------: | :------------ |
| 0         | Pas d'erreur  |
| 1         | Incohérence dans les paramètres. |
| 2         | Date de départ trop faible |