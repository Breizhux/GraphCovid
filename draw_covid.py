import os
from shutil import copy
from requests import get
from matplotlib import pyplot

input_test = "https://www.data.gouv.fr/fr/datasets/r/dd0de5d9-b5a5-4503-930a-7b08dc0adc7c"
input_hosp = "https://www.data.gouv.fr/fr/datasets/r/63352e38-d353-4b54-bfd1-f1b3ee1cabd7"
base_test = "donnees/base_donnees_national_tests.csv"
base_hosp = "donnees/base_donnees_departemental_hospitalisations.csv"
national_test = "donnees/donnees_national_tests.csv"
departmt_hosp = "donnees/donnees_departemental_hospitalisations.csv"
national_hosp = "donnees/donnees_national_hospitalisations.csv"
result_path = "donnees/result.csv"
date_depart = "" #ex : 2020-10-16

color = {
    'redstart' : '\033[91m',
    'redstop' : '\033[0m',
}

def wl(line, file=result_path, mode='a') :
    """ write line in file"""
    with open(file, mode) as f :
        f.write(line)
def wc(infos, del_colonne, file=result_path, mode='a') :
    """write good colonne"""
    if isinstance(infos, str) : infos = infos.split(';')
    n_colonne = [i for i in range(len(infos)) if not i in del_colonne]
    line = []
    for i in n_colonne : line.append(infos[i])
    wl(";".join([str(i) for i in line])+'\n', file=file, mode=mode)
def colorprint(list_tuple) :
    """ print text with color. Required list of tuple :
    (texte1, color), (text2, color), etc... """
    result_text = ""
    for i in list_tuple :
        if len(i) != 1 :
            start_color = color['{}start'.format(i[1])]
            stop_color = color['{}stop'.format(i[1])]
        else :
            start_color = stop_color = ""
        result_text += start_color
        result_text += i[0]
        result_text += stop_color
    print(result_text)

def print_colonnes_name(displaytoday=True) :
    """ Display colonne name with the number of the colonne"""
    print("[Descriptif] Description des colonnes du fichier de résultat final :")
    with open(result_path, 'r') as file :
        colonnes = file.readline()
        today_statistic = file.readlines()[-1].replace('\n', '').split(';')
        today_statistic[0] = "ajd"
    colonnes = colonnes.replace('\n', '').replace('test', ' test ').split(';')

    line1 = "+" #line
    line2 = "|" #name
    line3 = "|" #index
    line4 = "|" #today
    for i in colonnes : line1 += '{}+'.format('-'*len(i))
    for i in colonnes : line2 += '{}|'.format(i)
    for c, i in enumerate(colonnes) :
        line3 += "{}|".format(str(c).center(len(i)))
    for c, i in enumerate(today_statistic) :
        line4 += "{}|".format(str(i).center(len(colonnes[c])))

    print(line1, line2, line1, line3, line1, sep='\n')
    if displaytoday : print(line4, line1, sep='\n')

### GET SOURCES FILES PART ###
def download_files() :
    """ Download csv files from governmental website """
    print("[Téléchargement] Statistique des tests national...")
    print("    → {}".format(input_test))
    if not os.path.exists(os.path.dirname(national_test)) :
        os.makedirs(os.path.dirname(national_test))
    with open(national_test, 'wb') as file :
        response = get(input_test)
        file.write(response.content)
    print("[Téléchargement] Statistique des hospitalisations départementale...")
    print("    → {}".format(input_hosp))
    with open(departmt_hosp, 'wb') as file :
        response = get(input_hosp)
        file.write(response.content)
    copy(national_test, base_test)
    copy(departmt_hosp, base_hosp)
def reset_data() :
    """ Reset the base working data files"""
    os.remove(national_test)
    os.remove(departmt_hosp)
    copy(base_test, national_test)
    copy(base_hosp, departmt_hosp)

### MAKE TRAITMENT ON SOURCES DATAS TO CREATE ONE RESULT FILE FOR NATIONAL STATS ###
def hospi_to_national() :
    """ Compile les informations en données national métropolitaine"""
    print("[Conversion] Stats hospitalisation départemental en national...")
    hospfile = open(national_hosp, 'w')
    with open(departmt_hosp, 'r+') as file :
        file.readline()
        infos = {'date' : 'date', 'hosp' : 'hospitalisation', 'rea' : 'reanimation', 'dc' : 'cumul décès', 'rad' : 'cumul retour à domicile'}
        for line in file.readlines() :
            i = line.split(';')
            if i[2] == infos['date'] :
                # Exclue les département d'outre-mer
                if len(i[0].replace('"', '')) <= 2 and int(i[1].replace('"','')) == 0 :
                    infos['hosp'] += int(i[3])
                    infos['rea'] += int(i[4])
                    infos['dc'] += int(i[9])
                    infos['rad'] += int(i[8])
            else :
                L = [infos['date'], str(infos['hosp']), str(infos['rea']), str(infos['dc']), str(infos['rad'])]
                hospfile.write(";".join(L)+"\n")
                infos = {'date' : i[2],
                         'hosp' : int(i[3]),
                         'rea' : int(i[4]),
                         'dc' : int(i[9]),
                         'rad' : int(i[8])}
    hospfile.close()

def to_same_date() :
    """ Enlève les débuts de fichier pour qu'il soit
    tous les deux dans les mêmes intervalles de dates"""
    print("[Conversion] Mise à jour des fichiers pour les mêmes dates...")
    with open(national_test, 'r') as test :
        first_test = test.readline()
        first_date_test = int(test.readline().split(';')[1].replace('-',''))
    with open(national_hosp, 'r') as hospi :
        first_hospi = hospi.readline()
        first_date_hosp = int(hospi.readline().split(';')[0].replace('-','').replace('"',''))

    if date_depart != "" :
        if first_date_hosp > date_depart and first_date_test > date_depart :
            if first_date_hosp > first_date_test : date = first_date_hosp
            else : date = first_date_test
            colorprint([('[ERROR]','red'),
                (" La date indiqué est trop faible. Date minimum : {}".format(date),)])
            sys.exit(2)
        start_date = int(date_depart.replace('-', ''))
    elif first_date_test > first_date_hosp :
        start_date = first_date_test
    else :
        start_date = first_date_hosp

    if start_date > first_date_hosp :
        with open(national_hosp, 'r') as hospi :
            hospi.readline() #go to end first line
            with open('tmp.tmp', 'w') as file :
                file.write(first_hospi)
                while start_date > first_date_hosp :
                    line = hospi.readline()
                    first_date_hosp = int(line.split(';')[0].replace('-','').replace('"',''))
                file.write(line)
                for line in hospi.readlines() :
                    file.write(line)
        os.rename("tmp.tmp", national_hosp)

    if start_date > first_date_test :
        with open(national_test, 'r') as test :
            test.readline() #go to end first line
            with open('tmp.tmp', 'w') as file :
                file.write(first_test)
                while start_date > first_date_test :
                    line = test.readline()
                    first_date_test = int(line.split(';')[1].replace('-','').replace('"',''))
                file.write(line)
                for line in test.readlines() :
                    file.write(line)
        os.rename("tmp.tmp", national_test)

def sort_file() :
    """ trie les colonnes pour ne garder que les chiffres
    national par jour : cas positif, cas testé, nombre de
    mort, nombre d'hospitalisation"""
    with open(national_test, 'r') as test :
        line = test.readline().split(';')
        with open(national_hosp, 'r') as hospi :
            hospi.readline() #place le cureseur en fin de première ligne
            wl("jour;test;positif;hospitalisation;reanimation;cumul_deces;cumul_retour_domicile\n", mode='w')
            for line in test.readlines()[1:] :
                infos = line.replace('\n','').split(';')
                if infos[8] == '0' :
                    line = hospi.readline().replace('"', '').replace('\n','')
                    infos += line.split(';')
                    infos = infos[1], infos[7], infos[4], infos[11], infos[12], infos[13], infos[14]
                    wl(";".join(infos)+"\n")

def complete_file(del_colonne, displaytoday=True) :
    """ Rajoute des informations calculé à partir des autres colonnes.
    Peut supprimer les colonnes en indiquant leurs numéros, défaut 5,6."""
    print("[Calcul] Calcul de nouvel information sur la base des premières...")
    print("    → colonnes à exclure : {}".format(" ".join([str(i) for i in del_colonne])))
    with open(result_path, 'r') as file :
        #           0  ;  1 ;   2   ;      3        ;     4     ;    5      ;       6
        colonne = "jour;test;positif;hospitalisation;reanimation;cumul_deces;cumul_retour_domicile;"
        #                7   ;    8     ;         9         ;      10    ;   11    ;        12          ;   13
        colonne += "nbr_deces;nbr_malade;nbr_retour_domicile;%cas positif;%mort/cas;%hospitalisation/cas;%réa/cas"
        wc(colonne, del_colonne, file="tmp.tmp", mode='w')

        i = 0
        latest_cas = [0,0,0,0,0,0,0]
        latest_infos = file.readline().split(';')
        for line in file.readlines() :
            infos = line[:-1].split(';')
            infos = [infos[0],] + [int(i) for i in infos[1:]]

            #nbr deces
            infos.append(infos[5] - latest_infos[5] if isinstance(latest_infos[5], int) else 0)
            #nbr de malade : nbr malade = somme des cas des 7 derniers jours
            latest_cas.append(infos[2])
            latest_cas = latest_cas[1:]
            somme = 0
            for i in latest_cas : somme += i
            infos.append(somme)
            #nbr retour domicile
            infos.append(infos[6] - latest_infos[6] if isinstance(latest_infos[6], int) else 0)
            #% cas positif
            infos.append(round((infos[2]/infos[1])*100, 2))
            #%mort / cas
            infos.append(round((infos[7]/infos[2])*100, 2))
            #hospitalisation / cas
            infos.append(round((infos[3]/infos[2])*100, 2))
            #%réanimation / cas
            infos.append(round((infos[4]/infos[2])*100, 2))

            latest_infos = infos
            wc(infos, del_colonne, file="tmp.tmp")

    os.rename("tmp.tmp", result_path)
    #Just to display informtions
    print_colonnes_name(displaytoday=displaytoday)

def draw(colonnes) :
    """ Dessine des graphiques avec les courbes suivantes :
         - Nombre de malade.
         - Pourcentage de nouveau cas.
         - Pourcentage d'hospitalisé
    Indiquer à colonne les numéros de colonne à afficher : la
    colonne 0 des dates est affiché par défaut.
    """
    print("[Affichage] dessin des courbes sur le graphique")
    Dates = []
    Data = [] #list of list of data ;)
    for i in range(len(colonnes)) : Data.append([0,0])

    with open(result_path, 'r') as file :
        colonnes_name = file.readline().split(';') #met le curseur à la fin de la première ligne
        for line in file.readlines() :
            infos = line.split(';')
            infos = [infos[0],] + [float(i) for i in infos[1:]]
            Dates.append(infos[0])

            for i in range(len(colonnes)) :
                if colonnes[i] < len(colonnes_name) :
                    Data[i].append(infos[colonnes[i]])
                else :
                    colorprint([('[ERROR]', 'red'),
                        (" La colonne n°{} n'existe pas dans le fichier de résultat.".format(colonnes[i]),)])
                    colonnes.remove(colonnes[i])

    matplot_color = ['r','b','g','c','m','y','k',
        'r--','b--','g--','c--','m--','y--','k--']
    color_name = ['rouge', 'bleu', 'vert', 'cyan', 'mauve', 'jaune', 'noir']
    for i in range(len(colonnes)) :
        pyplot.plot(Data[i], matplot_color[i])
        print("    → [{}]\t:  {}".format(color_name[i%7], colonnes_name[colonnes[i]]))
    pyplot.xticks(range(len(Data[0])), Dates, rotation=45)
    pyplot.show()


def read_args(argv) :
    """ Read and parse argv. Return dict."""
    error = False
    argd = {
        'colonnes' : [],
        'exclude' : [],
        'download' : True,
        'recalcul' : True,
        'help' : False,
        'draw' : True,
        'print_colonnes' : False,
        'from_date' : '',
        }
    key="" #latest used key
    for arg in argv :
        if arg[0] == '-' :
            if arg in ['-c', '--colonnes'] : key = 'colonnes'
            elif arg in ['-e', '--exclude'] : key = 'exclude'
            elif arg in ['-d', '--no-download'] : argd['download'] = False
            elif arg in ['-r', '--no-recalcul'] : argd['recalcul'] = False
            elif arg in ['-h', '--help'] : argd['help'] = True
            elif arg == '--no-draw' : argd['draw'] = False
            elif arg == '--print-colonnes' :
                if not '-r' in argv and not '--recalcul' in argv :
                    argd['print_colonnes'] = True
            elif arg == '--from-date' : key = 'from_date'
            else :
                error = True
                colorprint([("[ERROR]",'red'), (" Argument invalide : {}".format(arg),)])
        else :
            try : value = int(arg)
            except : value = arg
            if isinstance(value, int) : argd[key].append(value)
            else : argd[key] = value
    if not os.path.exists(result_path) and not argd['download'] :
        colorprint([('[ERROR]', 'red'), (" Données manquantes. Incohérence des options.",)])
        error = True
    if argd['download'] and not argd['recalcul'] and argd['draw'] and not os.path.exists(base_test) :
        argd['recalcul'] = True
    if error : sys.exit(1)
    return argd
if __name__ == "__main__" :
    import sys
    argd = read_args(sys.argv[1:])
    if argd['help'] :
        print("usage : python3 draw_covid.py <option1> <option2> [option_args1 option_args2]\n")
        print("Available options :")
        print(" -h|--help : display manual.\n")
        print(" -c|--colonnes n1 n2 : to select colonnes to display in graph.")
        print("    default : 8 10 12\n")
        print(" -r|--no-recalcul : to recalcul the result withouth download latest data.\n")
        print(" -d|--no-download : to no download latest data from government website.\n")
        print(" -e|--exclude n1 n2 : to select number of colonne for exclude in result csv.")
        print("    default : 5 6\n")
        print(" --no-draw : no draw the graphic\n")
        print(" --print-colonnes : print results colonnes.\n")
        print(" --from-date <date> : keep statistics from the given date.")
        print("    example syntaxe : 2020-10-16")
        sys.exit(0)

    #Downloading
    if argd['download'] :
        download_files()

    # Calculating
    if argd['recalcul'] :
        if not argd['download'] : reset_data()
        date_depart = argd['from_date']
        hospi_to_national()
        to_same_date()
        sort_file()
        if len(argd['exclude']) == 0 : argd['exclude'] = [5, 6]
        elif argd['exclude'][0] == 0 : argd['exclude'] = []
        complete_file(del_colonne=argd['exclude'])

    # Display colonnes of result file with latest stats
    if argd['print_colonnes'] :
        print_colonnes_name()

    #Drawing
    if len(argd['colonnes']) == 0 : argd['colonnes'] = [8, 9, 10]
    if argd['draw'] : draw(argd['colonnes'])

    sys.exit(0)
