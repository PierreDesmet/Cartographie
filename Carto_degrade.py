import folium 
import pandas as pd
import numpy as np

# Les polygones sont sur Github : https://github.com/gregoiredavid/france-geojson/tree/master/regions
"""
Documentation : 
Ce script fournit les fonctions permettant la représentation d'une carte de France avec un dégradé.
Important : les noms des regions doivent matcher ceux de "departments_regions_france_2016.csv", obtenables ici : 
https://gist.github.com/gzurbach/b0ccdeda51ec2fe135d5
Les noms
Usage : 
    - pour les régions : 
    df_by_region = ajoute_couleur(df_by_region, "nb de salariés", coul_deb=(255, 230, 230), coul_fin=(204,1,1), nb_coul=4)
    carte_france = cree_carte(df_by_region, regionName='regionName', couleur_name='Couleur_degrade', maille='region')
    dico_textes = {'Alsace-Champagne-Ardenne-Lorraine':'<h5>5,14%</h5>', 
                   'Aquitaine-Limousin-Poitou-Charentes':'<h5>2,38%</h5>',
                  "Auvergne-Rhône-Alpes":'<h5>5,73%</h5>', 
                   "Bourgogne-Franche-Comté":'<h5>0.82%</h5>', 
                   'Bretagne':'<h5>2.66%</h5>',
                   'Centre-Val de Loire':'<h5>2.39%</h5>',
                   'Ile-de-France':'<h5>62,21%</h5>',
                   "Languedoc-Roussillon-Midi-Pyrénées":'<h5>2.89%</h5>',
                   "Nord-Pas-de-Calais-Picardie":'<h5>6.77%</h5>',
                   'Normandie':'<h5>5.11%</h5>',
                   'Pays de la Loire':'<h5>0.72%</h5>',
                   "Provence-Alpes-Côte d'Azur":'<h5>3.17%</h5>'}

    carte_france = add_text_by_region(dico_textes, carte_france)
    carte_france.save(outfile='Densité_portefeuille_régions.html')
    
    - pour les départements : 
    df_by_dép = ajoute_couleur(df_by_dép, "Effectif", coul_deb=(255, 230, 230), coul_fin=(204,1,1), nb_coul=6)
    carte_france = cree_carte(df_by_dép, regionName='departmentName', couleur_name='Couleur_degrade', maille='departement')
    #carte_france = add_text_by_region(dico_textes, carte_france)
    carte_france.save(outfile='Densité_portefeuille_département.html')
"""

def get_new_regionName(oldRegionName):
    old_regions_to_new = {'Alsace': 'Grand Est', 'Champagne-Ardennes':'Grand Est', 'Lorraine': 'Grand Est',
 'Aquitaine': 'Aquitaine-Limousin-Poitou-Charentes',
 'Auvergne': 'Auvergne-Rhône-Alpes', 'Rhône-Alpes': 'Auvergne-Rhône-Alpes',
 'Bourgogne': 'Bourgogne-Franche-Comté', 'Franche-Comté': 'Bourgogne-Franche-Comté',
 'Centre': 'Centre-Val de Loire',
 'Languedoc-Roussillon': 'Languedoc-Roussillon-Midi-Pyrénées', 'Midi-Pyrénées': 'Languedoc-Roussillon-Midi-Pyrénées',
 'Limousin': 'Aquitaine-Limousin-Poitou-Charentes', 'Poitou-Charentes': 'Aquitaine-Limousin-Poitou-Charentes',
 'Basse-Normandie':'Normandie', 'Haute-Normandie':'Normandie',
 'Picardie': 'Hauts-de-France', 'Nord Pas-de-Calais':'Hauts-de-France'}
    if oldRegionName in old_regions_to_new:
        return old_regions_to_new[oldRegionName]
    else:
        return oldRegionName

def ajoute_couleur(df_by_region, col_name_to_plot, coul_deb=(255, 230, 230), coul_fin=(204,1,1), nb_coul=5):
    # ajoute une couleur à un df à partir des quantiles de @col_name_to_plot
    # @col_name_to_plot : par ex. "Nombre de salaries", ou "températures"
    
    def get_color(df_by_region, col_val, n_vals, color_begin, color_end, colname=col_name_to_plot):
        # Usage : df_by_region['Couleur_nb_salaries'] = df_by_region['nb de salariés'].apply(lambda nb_salariés : get_color(df_by_region, nb_salariés, 10, (255, 230, 230), (204,1,1) ))
        # Les valeurs ci-dessous sont obtenues à partir des quantiles des nb de salariés
        for i in range(1, n_vals):
            if col_val < df_by_region[colname].quantile(i/n_vals) : return echelle(color_begin, color_end, n_vals)[i-1]
        if col_val >= df_by_region[colname].quantile(i/n_vals) : 
            return echelle(color_begin, color_end, n_vals)[i]

    def echelle(color_begin, color_end, n_vals):
        # Usage : echelle((248,224,224), (128,1,1), 3)
        # Retourne un degrade de @n_vals couleurs en hexadecimal entre @color_begin et @color_end
        r1, g1, b1 = color_begin #, color_begin, color_begin
        r2, g2, b2 = color_end  #, color_end, color_end
        degrade = []
        etendue = n_vals - 1
        for i in range(n_vals):
            alpha = 1 - i / etendue
            beta = i / etendue
            r = int(r1 * alpha + r2 * beta)
            g = int(g1 * alpha + g2 * beta)
            b = int(b1 * alpha + b2 * beta)
            degrade.append('#%02x%02x%02x' %(r, g, b))
            #print(degrade)
        return degrade
    
    df_by_region['Couleur_degrade'] = df_by_region[col_name_to_plot].apply(lambda x : get_color(df_by_region, x, nb_coul, coul_deb, coul_fin ))
    return df_by_region



def cree_carte(df_by_region, regionName='regionName', isNum=False, couleur_name='Couleur_degrade', maille='region', couleur_vide="#ffffcc"):
    """
    @couleur_vide : la couleur quand on n'a pas l'info
    @isNum : indique si le département est renseigné en nombre ('01', '02', ... '95') ou en noms de départements. Ne s'applique pas aux regions.
    """
    region2couleur = {k:v for k, v in zip(df_by_region[regionName], df_by_region[couleur_name]) }

    # Création de la carte : 
    carte = folium.Map(location=[47.26, 2.34], tiles='Mapbox Bright', zoom_start=6) #  [48.68, 2.35]
    d = dict(fillOpacity=0.6, color='#BD2027', weight=0.9)
    
    
    def try_color(clé): # P. ex : clé = 'Alsace-Champagne-Ardenne-Lorraine', ou 'Finistère'
        try : 
            if isNum : # Si le département est renseigné au format numérique : #and re.match(r"\d", clé)
                return region2couleur[string2numdep[clé]]
            else:
                return region2couleur[clé]
        except :
            return couleur_vide
    
    
    if maille=='region':
        regions_exhaustives = ['Grand Est', 'Aquitaine-Limousin-Poitou-Charentes', 'Auvergne-Rhône-Alpes', 'Bourgogne-Franche-Comté','Bretagne',
        'Centre-Val de Loire', 'Ile-de-France', 'Hauts-de-France', 'Languedoc-Roussillon-Midi-Pyrénées', 'Normandie', 'Pays-de-la-Loire', "Provence-Alpes-Côte d'Azur"]
        region_inconnues = [c for c in regions_exhaustives if c not in region2couleur.keys()]
        print('Les régions suivantes sont inconnues :') if region_inconnues else print('', end='')
        for reg in region_inconnues:
            print('\t- ' + reg)
                
        # Ajout des régions et des couleurs. 
        # ATTENTION : les noms des regions doivent matcher ceux de "departments_regions_france_2016.csv", obtenables ici : https://gist.github.com/gzurbach/b0ccdeda51ec2fe135d5
        prefixe = "geojsons/Régions/region-"
        folium.GeoJson( prefixe+"grand-est.geojson", style_function = lambda x: {**d, 'fillColor': try_color('Grand Est')}).add_to(carte)
        folium.GeoJson( prefixe+"nouvelle-aquitaine.geojson", style_function = lambda x: {**d, 'fillColor': try_color('Aquitaine-Limousin-Poitou-Charentes')}).add_to(carte)
        folium.GeoJson( prefixe+"auvergne-rhone-alpes.geojson", style_function = lambda x: {**d, 'fillColor': try_color('Auvergne-Rhône-Alpes')}).add_to(carte)
        folium.GeoJson( prefixe+"bourgogne-franche-comte.geojson", style_function = lambda x: {**d, 'fillColor': try_color('Bourgogne-Franche-Comté')}).add_to(carte)
        folium.GeoJson( prefixe+"bretagne.geojson", style_function = lambda x: {**d, 'fillColor': try_color('Bretagne')}).add_to(carte)
        folium.GeoJson( prefixe+"centre-val-de-loire.geojson", style_function = lambda x: {**d, 'fillColor': try_color('Centre-Val de Loire')}).add_to(carte)
        folium.GeoJson( prefixe+"ile-de-france.geojson", style_function = lambda x: {**d, 'fillColor': try_color('Ile-de-France')}).add_to(carte)
        folium.GeoJson( prefixe+"hauts-de-france.geojson", style_function = lambda x: {**d, 'fillColor': try_color('Hauts-de-France')}).add_to(carte)
        folium.GeoJson( prefixe+"occitanie.geojson", style_function = lambda x: {**d, 'fillColor': try_color('Languedoc-Roussillon-Midi-Pyrénées')}).add_to(carte)
        folium.GeoJson( prefixe+"normandie.geojson", style_function = lambda x: {**d, 'fillColor': try_color('Normandie')}).add_to(carte)
        folium.GeoJson( prefixe+"pays-de-la-loire.geojson", style_function = lambda x: {**d, 'fillColor': try_color('Pays-de-la-Loire')}).add_to(carte)
        folium.GeoJson( prefixe+"provence-alpes-cote-d-azur.geojson", style_function = lambda x: {**d, 'fillColor': try_color("Provence-Alpes-Côte d'Azur")}).add_to(carte)
        folium.GeoJson( prefixe+"corse.geojson", style_function = lambda x: {**d, 'fillColor': try_color("Corse")}).add_to(carte)
        return carte
    
    if maille=="departement":
        string2numdep = {'Ain': '01', 'Aisne': '02', 'Allier': '03', 'Alpes-Maritimes': '06', 'Alpes-de-Haute-Provence': '04', 'Ardennes': '08', 'Ardèche': '07', 'Ariège': '09', 'Aube': '10', 'Aude': '11', 'Aveyron': '12', 'Bas-Rhin': '67', 'Bouches-du-Rhône': '13', 'Calvados': '14', 'Cantal': '15', 'Charente': '16', 'Charente-Maritime': '17', 'Cher': '18', 'Corrèze': '19', 'Corse-du-Sud': '2A', 'Creuse': '23', "Côte-d'or": '21', "Côtes-d'armor": '22', 'Deux-Sèvres': '79', 'Dordogne': '24', 'Doubs': '25', 'Drôme': '26', 'Essonne': '91', 'Eure': '27', 'Eure-et-Loir': '28', 'Finistère': '29', 'Gard': '30', 'Gers': '32', 'Gironde': '33', 'Guadeloupe': '971', 'Guyane': '973', 'Haut-Rhin': '68', 'Haute-Corse': '2B', 'Haute-Garonne': '31', 'Haute-Loire': '43', 'Haute-Marne': '52', 'Haute-Savoie': '74', 'Haute-Saône': '70', 'Haute-Vienne': '87', 'Hautes-Alpes': '05', 'Hautes-Pyrénées': '65', 'Hauts-de-Seine': '92', 'Hérault': '34', 'Ille-et-Vilaine': '35', 'Indre': '36', 'Indre-et-Loire': '37', 'Isère': '38', 'Jura': '39', 'La Réunion': '974', 'Landes': '40', 'Loir-et-Cher': '41', 'Loire': '42', 'Loire-Atlantique': '44', 'Loiret': '45', 'Lot': '46', 'Lot-et-Garonne': '47', 'Lozère': '48', 'Maine-et-Loire': '49', 'Manche': '50', 'Marne': '51', 'Martinique': '972', 'Mayenne': '53', 'Mayotte': '976', 'Meurthe-et-Moselle': '54', 'Meuse': '55', 'Morbihan': '56', 'Moselle': '57', 'Nièvre': '58', 'Nord': '59', 'Oise': '60', 'Orne': '61', 'Paris': '75', 'Pas-de-Calais': '62', 'Puy-de-Dôme': '63', 'Pyrénées-Atlantiques': '64', 'Pyrénées-Orientales': '66', 'Rhône': '69', 'Saint-Pierre-et-Miquelon': '975', 'Sarthe': '72', 'Savoie': '73', 'Saône-et-Loire': '71', 'Seine-Maritime': '76', 'Seine-Saint-Denis': '93', 'Seine-et-Marne': '77', 'Somme': '80', 'Tarn': '81', 'Tarn-et-Garonne': '82', 'Territoire de Belfort': '90', "Val-d'oise": '95', 'Val-de-Marne': '94', 'Var': '83', 'Vaucluse': '84', 'Vendée': '85', 'Vienne': '86', 'Vosges': '88', 'Yonne': '89', 'Yvelines': '78'}
        numdep2string = {v:k for k,v in zip(string2numdep.keys(), string2numdep.values())}
        
        if isNum : 
            dép_inconnus = [d for d in string2numdep.values() if d not in region2couleur.keys()]  
        else :
            dép_inconnus = [d for d in string2numdep.keys() if d not in region2couleur.keys()]
        
        print('Les départements suivants sont inconnus :') if dép_inconnus else print('', end='')
        for dep in dép_inconnus:
            if isNum : print('\t- ' + dep, numdep2string[dep])
            if not isNum : print('\t- ' + dep, string2numdep[dep])
        
        # TODO : aligner les lignes suivantes : 
        prefixe = "geojsons/Départements/departement-"
        folium.GeoJson( prefixe+"01-ain.geojson", style_function = lambda x: {**d, 'fillColor': try_color('Ain')}).add_to(carte)
        folium.GeoJson( prefixe+"02-aisne.geojson", style_function = lambda x: {**d, 'fillColor': try_color('Aisne')}).add_to(carte)
        folium.GeoJson( prefixe+"03-allier.geojson", style_function = lambda x: {**d, 'fillColor': try_color('Allier')}).add_to(carte)
        folium.GeoJson( prefixe+"04-alpes-de-haute-provence.geojson", style_function = lambda x: {**d, 'fillColor': try_color('Alpes-de-Haute-Provence')}).add_to(carte)
        folium.GeoJson( prefixe+"05-hautes-alpes.geojson", style_function = lambda x: {**d, 'fillColor': try_color('Hautes-Alpes')}).add_to(carte)
        folium.GeoJson( prefixe+"06-alpes-maritimes.geojson", style_function = lambda x: {**d, 'fillColor': try_color('Alpes-Maritimes')}).add_to(carte)
        folium.GeoJson( prefixe+"07-ardeche.geojson", style_function = lambda x: {**d, 'fillColor': try_color('Ardèche')}).add_to(carte)
        folium.GeoJson( prefixe+"08-ardennes.geojson", style_function = lambda x: {**d, 'fillColor': try_color('Ardennes')}).add_to(carte)
        folium.GeoJson( prefixe+"09-ariege.geojson", style_function = lambda x: {**d, 'fillColor': try_color('Ariège')}).add_to(carte)
        folium.GeoJson( prefixe+"10-aube.geojson", style_function = lambda x: {**d, 'fillColor': try_color('Aube')}).add_to(carte)
        folium.GeoJson( prefixe+"11-aude.geojson", style_function = lambda x: {**d, 'fillColor': try_color('Aude')}).add_to(carte)
        folium.GeoJson( prefixe+"12-aveyron.geojson", style_function = lambda x: {**d, 'fillColor': try_color('Aveyron')}).add_to(carte)
        folium.GeoJson( prefixe+"13-bouches-du-rhone.geojson", style_function = lambda x: {**d, 'fillColor': try_color('Bouches-du-Rhône')}).add_to(carte)
        folium.GeoJson( prefixe+"14-calvados.geojson", style_function = lambda x: {**d, 'fillColor': try_color('Calvados')}).add_to(carte)
        folium.GeoJson( prefixe+"15-cantal.geojson", style_function = lambda x: {**d, 'fillColor': try_color('Cantal')}).add_to(carte)
        folium.GeoJson( prefixe+"16-charente.geojson", style_function = lambda x: {**d, 'fillColor': try_color('Charente')}).add_to(carte)
        folium.GeoJson( prefixe+"17-charente-maritime.geojson", style_function = lambda x: {**d, 'fillColor': try_color('Charente-Maritime')}).add_to(carte)
        folium.GeoJson( prefixe+"18-cher.geojson", style_function = lambda x: {**d, 'fillColor': try_color('Loir-et-Cher')}).add_to(carte)
        folium.GeoJson( prefixe+"19-correze.geojson", style_function = lambda x: {**d, 'fillColor': try_color('Corrèze')}).add_to(carte)
        folium.GeoJson( prefixe+"21-cote-d-or.geojson", style_function = lambda x: {**d, 'fillColor': try_color("Côte-d'or")}).add_to(carte)
        folium.GeoJson( prefixe+"22-cotes-d-armor.geojson", style_function = lambda x: {**d, 'fillColor': try_color("Côtes-d'armor")}).add_to(carte)
        folium.GeoJson( prefixe+"23-creuse.geojson", style_function = lambda x: {**d, 'fillColor': try_color('Creuse')}).add_to(carte)
        folium.GeoJson( prefixe+"24-dordogne.geojson", style_function = lambda x: {**d, 'fillColor': try_color('Dordogne')}).add_to(carte)
        folium.GeoJson( prefixe+"25-doubs.geojson", style_function = lambda x: {**d, 'fillColor': try_color('Doubs')}).add_to(carte)
        folium.GeoJson( prefixe+"26-drome.geojson", style_function = lambda x: {**d, 'fillColor': try_color('Drôme')}).add_to(carte)
        folium.GeoJson( prefixe+"27-eure.geojson", style_function = lambda x: {**d, 'fillColor': try_color('Eure')}).add_to(carte)
        folium.GeoJson( prefixe+"28-eure-et-loir.geojson", style_function = lambda x: {**d, 'fillColor': try_color('Eure-et-Loir')}).add_to(carte)
        folium.GeoJson( prefixe+"29-finistere.geojson", style_function = lambda x: {**d, 'fillColor': try_color('Finistère')}).add_to(carte)
        folium.GeoJson( prefixe+"2A-corse-du-sud.geojson", style_function = lambda x: {**d, 'fillColor': try_color('Corse-du-Sud')}).add_to(carte)
        folium.GeoJson( prefixe+"2B-haute-corse.geojson", style_function = lambda x: {**d, 'fillColor': try_color('Haute-Corse')}).add_to(carte)
        folium.GeoJson( prefixe+"30-gard.geojson", style_function = lambda x: {**d, 'fillColor': try_color('Gard')}).add_to(carte)
        folium.GeoJson( prefixe+"31-haute-garonne.geojson", style_function = lambda x: {**d, 'fillColor': try_color('Haute-Garonne')}).add_to(carte)
        folium.GeoJson( prefixe+"32-gers.geojson", style_function = lambda x: {**d, 'fillColor': try_color('Gers')}).add_to(carte)
        folium.GeoJson( prefixe+"33-gironde.geojson", style_function = lambda x: {**d, 'fillColor': try_color('Gironde')}).add_to(carte)
        folium.GeoJson( prefixe+"34-herault.geojson", style_function = lambda x: {**d, 'fillColor': try_color('Hérault')}).add_to(carte)
        folium.GeoJson( prefixe+"35-ille-et-vilaine.geojson", style_function = lambda x: {**d, 'fillColor': try_color('Ille-et-Vilaine')}).add_to(carte)
        folium.GeoJson( prefixe+"36-indre.geojson", style_function = lambda x: {**d, 'fillColor': try_color('Indre')}).add_to(carte)
        folium.GeoJson( prefixe+"37-indre-et-loire.geojson", style_function = lambda x: {**d, 'fillColor': try_color('Indre-et-Loire')}).add_to(carte)
        folium.GeoJson( prefixe+"38-isere.geojson", style_function = lambda x: {**d, 'fillColor': try_color('Isère')}).add_to(carte)
        folium.GeoJson( prefixe+"39-jura.geojson", style_function = lambda x: {**d, 'fillColor': try_color('Jura')}).add_to(carte)
        folium.GeoJson( prefixe+"40-landes.geojson", style_function = lambda x: {**d, 'fillColor': try_color('Landes')}).add_to(carte)
        folium.GeoJson( prefixe+"41-loir-et-cher.geojson", style_function = lambda x: {**d, 'fillColor': try_color('Loir-et-Cher')}).add_to(carte)
        folium.GeoJson( prefixe+"42-loire.geojson", style_function = lambda x: {**d, 'fillColor': try_color('Loire')}).add_to(carte)
        folium.GeoJson( prefixe+"43-haute-loire.geojson", style_function = lambda x: {**d, 'fillColor': try_color('Haute-Loire')}).add_to(carte)
        folium.GeoJson( prefixe+"44-loire-atlantique.geojson", style_function = lambda x: {**d, 'fillColor': try_color('Loire-Atlantique')}).add_to(carte)
        folium.GeoJson( prefixe+"45-loiret.geojson", style_function = lambda x: {**d, 'fillColor': try_color('Loiret')}).add_to(carte)
        folium.GeoJson( prefixe+"46-lot.geojson", style_function = lambda x: {**d, 'fillColor': try_color('Lot')}).add_to(carte)
        folium.GeoJson( prefixe+"47-lot-et-garonne.geojson", style_function = lambda x: {**d, 'fillColor': try_color('Lot-et-Garonne')}).add_to(carte)
        folium.GeoJson( prefixe+"48-lozere.geojson", style_function = lambda x: {**d, 'fillColor': try_color('Lot-et-Garonne')}).add_to(carte)
        folium.GeoJson( prefixe+"49-maine-et-loire.geojson", style_function = lambda x: {**d, 'fillColor': try_color('Maine-et-Loire')}).add_to(carte)
        folium.GeoJson( prefixe+"50-manche.geojson", style_function = lambda x: {**d, 'fillColor': try_color('Manche')}).add_to(carte)
        folium.GeoJson( prefixe+"51-marne.geojson", style_function = lambda x: {**d, 'fillColor': try_color('Marne')}).add_to(carte)
        folium.GeoJson( prefixe+"52-haute-marne.geojson", style_function = lambda x: {**d, 'fillColor': try_color('Haute-Marne')}).add_to(carte)
        folium.GeoJson( prefixe+"53-mayenne.geojson", style_function = lambda x: {**d, 'fillColor': try_color('Mayenne')}).add_to(carte)
        folium.GeoJson( prefixe+"54-meurthe-et-moselle.geojson", style_function = lambda x: {**d, 'fillColor': try_color('Meurthe-et-Moselle')}).add_to(carte)
        folium.GeoJson( prefixe+"55-meuse.geojson", style_function = lambda x: {**d, 'fillColor': try_color('Meuse')}).add_to(carte)
        folium.GeoJson( prefixe+"56-morbihan.geojson", style_function = lambda x: {**d, 'fillColor': try_color('Morbihan')}).add_to(carte)
        folium.GeoJson( prefixe+"57-moselle.geojson", style_function = lambda x: {**d, 'fillColor': try_color('Moselle')}).add_to(carte)
        folium.GeoJson( prefixe+"58-nievre.geojson", style_function = lambda x: {**d, 'fillColor': try_color('Nièvre')}).add_to(carte)
        folium.GeoJson( prefixe+"59-nord.geojson", style_function = lambda x: {**d, 'fillColor': try_color('Nord')}).add_to(carte)
        folium.GeoJson( prefixe+"60-oise.geojson", style_function = lambda x: {**d, 'fillColor': try_color('Oise')}).add_to(carte)
        folium.GeoJson( prefixe+"61-orne.geojson", style_function = lambda x: {**d, 'fillColor': try_color('Orne')}).add_to(carte)
        folium.GeoJson( prefixe+"62-pas-de-calais.geojson", style_function = lambda x: {**d, 'fillColor': try_color('Pas-de-Calais')}).add_to(carte)
        folium.GeoJson( prefixe+"63-puy-de-dome.geojson", style_function = lambda x: {**d, 'fillColor': try_color('Puy-de-Dôme')}).add_to(carte)
        folium.GeoJson( prefixe+"64-pyrenees-atlantiques.geojson", style_function = lambda x: {**d, 'fillColor': try_color('Pyrénées-Atlantiques')}).add_to(carte)
        folium.GeoJson( prefixe+"65-hautes-pyrenees.geojson", style_function = lambda x: {**d, 'fillColor': try_color('Hautes-Pyrénées')}).add_to(carte)
        folium.GeoJson( prefixe+"66-pyrenees-orientales.geojson", style_function = lambda x: {**d, 'fillColor': try_color('Pyrénées-Orientales')}).add_to(carte)
        folium.GeoJson( prefixe+"67-bas-rhin.geojson", style_function = lambda x: {**d, 'fillColor': try_color('Bas-Rhin')}).add_to(carte)
        folium.GeoJson( prefixe+"68-haut-rhin.geojson", style_function = lambda x: {**d, 'fillColor': try_color('Haut-Rhin')}).add_to(carte)
        folium.GeoJson( prefixe+"69-rhone.geojson", style_function = lambda x: {**d, 'fillColor': try_color('Rhône')}).add_to(carte)
        folium.GeoJson( prefixe+"70-haute-saone.geojson", style_function = lambda x: {**d, 'fillColor': try_color('Haute-Saône')}).add_to(carte)
        folium.GeoJson( prefixe+"71-saone-et-loire.geojson", style_function = lambda x: {**d, 'fillColor': try_color('Saône-et-Loire')}).add_to(carte)
        folium.GeoJson( prefixe+"72-sarthe.geojson", style_function = lambda x: {**d, 'fillColor': try_color('Sarthe')}).add_to(carte)
        folium.GeoJson( prefixe+"73-savoie.geojson", style_function = lambda x: {**d, 'fillColor': try_color('Savoie')}).add_to(carte)
        folium.GeoJson( prefixe+"74-haute-savoie.geojson", style_function = lambda x: {**d, 'fillColor': try_color('Haute-Savoie')}).add_to(carte)
        folium.GeoJson( prefixe+"75-paris.geojson", style_function = lambda x: {**d, 'fillColor': try_color('Paris')}).add_to(carte)
        folium.GeoJson( prefixe+"76-seine-maritime.geojson", style_function = lambda x: {**d, 'fillColor': try_color('Seine-Maritime')}).add_to(carte)
        folium.GeoJson( prefixe+"77-seine-et-marne.geojson", style_function = lambda x: {**d, 'fillColor': try_color('Seine-et-Marne')}).add_to(carte)
        folium.GeoJson( prefixe+"78-yvelines.geojson", style_function = lambda x: {**d, 'fillColor': try_color('Yvelines')}).add_to(carte)
        folium.GeoJson( prefixe+"79-deux-sevres.geojson", style_function = lambda x: {**d, 'fillColor': try_color('Deux-Sèvres')}).add_to(carte)
        folium.GeoJson( prefixe+"80-somme.geojson", style_function = lambda x: {**d, 'fillColor': try_color('Somme')}).add_to(carte)
        folium.GeoJson( prefixe+"81-tarn.geojson", style_function = lambda x: {**d, 'fillColor': try_color('Tarn')}).add_to(carte)
        folium.GeoJson( prefixe+"82-tarn-et-garonne.geojson", style_function = lambda x: {**d, 'fillColor': try_color('Tarn-et-Garonne')}).add_to(carte)
        folium.GeoJson( prefixe+"83-var.geojson", style_function = lambda x: {**d, 'fillColor': try_color('Var')}).add_to(carte)
        folium.GeoJson( prefixe+"84-vaucluse.geojson", style_function = lambda x: {**d, 'fillColor': try_color('Vaucluse')}).add_to(carte)
        folium.GeoJson( prefixe+"85-vendee.geojson", style_function = lambda x: {**d, 'fillColor': try_color('Vendée')}).add_to(carte)
        folium.GeoJson( prefixe+"86-vienne.geojson", style_function = lambda x: {**d, 'fillColor': try_color('Vienne')}).add_to(carte)
        folium.GeoJson( prefixe+"87-haute-vienne.geojson", style_function = lambda x: {**d, 'fillColor': try_color('Haute-Vienne')}).add_to(carte)
        folium.GeoJson( prefixe+"88-vosges.geojson", style_function = lambda x: {**d, 'fillColor': try_color('Vosges')}).add_to(carte)
        folium.GeoJson( prefixe+"89-yonne.geojson", style_function = lambda x: {**d, 'fillColor': try_color('Yonne')}).add_to(carte)
        folium.GeoJson( prefixe+"90-territoire-de-belfort.geojson", style_function = lambda x: {**d, 'fillColor': try_color('Territoire de Belfort')}).add_to(carte)
        folium.GeoJson( prefixe+"91-essonne.geojson", style_function = lambda x: {**d, 'fillColor': try_color('Essonne')}).add_to(carte)
        folium.GeoJson( prefixe+"92-hauts-de-seine.geojson", style_function = lambda x: {**d, 'fillColor': try_color('Hauts-de-Seine')}).add_to(carte)
        folium.GeoJson( prefixe+"93-seine-saint-denis.geojson", style_function = lambda x: {**d, 'fillColor': try_color('Seine-Saint-Denis')}).add_to(carte)
        folium.GeoJson( prefixe+"94-val-de-marne.geojson", style_function = lambda x: {**d, 'fillColor': try_color('Val-de-Marne')}).add_to(carte)
        folium.GeoJson( prefixe+"95-val-d-oise.geojson", style_function = lambda x: {**d, 'fillColor': try_color("Val-d'oise")}).add_to(carte)
        folium.GeoJson( prefixe+"971-guadeloupe.geojson", style_function = lambda x: {**d, 'fillColor': try_color('Guadeloupe')}).add_to(carte)
    return carte



def add_text_by_region(dico_textes, carte, maille='region'):
    # @liste_textes : une liste de textes à afficher sur chaque région 
    # Important : l'ordre des textes doit être le même que l'ordre alphabétique des région : alsace, aquitaine, aubergne, bourgogne...
    if maille=='region':
        regions =  {'Grand Est':                           [48.5, 5.49],
                    'Aquitaine-Limousin-Poitou-Charentes': [45.65, 0.05],
                    'Auvergne-Rhône-Alpes':                [45.25, 4.29],
                    'Bourgogne-Franche-Comté':             [47, 4.85],
                    'Bretagne':                            [48, -3], 
                    'Centre-Val de Loire':                 [47.4, 1.69],
                    'Ile-de-France':                       [48.3, 2.5], 
                    'Languedoc-Roussillon-Midi-Pyrénées':  [43.93, 2],
                    'Hauts-de-France':                     [50, 2.64], 
                    'Normandie':                           [48.7, -0.2], 
                    'Pays-de-la-Loire':                    [47.2, -0.94],
                    "Provence-Alpes-Côte d'Azur":          [43.7, 6.5],
                    'Corse':                               [42, 9.15]}
        for region in regions:
            folium.map.Marker(
                location=regions[region] ,
                icon=folium.DivIcon(
                    html=dico_textes[region], icon_size=(80,80)),
                ).add_to(carte)
    
    return carte




