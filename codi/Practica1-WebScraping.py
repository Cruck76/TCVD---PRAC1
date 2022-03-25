#!/usr/bin/env python
# coding: utf-8

# In[5]:


from bs4 import BeautifulSoup
import requests
import pandas as pd


headers = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/99.0.4844.51 Safari/537.36"}
producte_buscat = "iphone"
url = "https://www.backmarket.es/search?q="+producte_buscat

page = requests.get(url, headers=headers)
soup = BeautifulSoup(page.content, "html.parser")


pagina = soup.find("nav", {'data-test':'pagination', 'class':'space-x-1 _31EPVef96AFhNgE_OT5e6e'}) 
# Manera per obtenir el número de pàgines. "num_pag" és el número de pàgines de les que s'ha de treure info
num_pag = 1
for titol in pagina:
    if len(titol.text) > 1:
        num_pag = titol.text.strip()
num_pag = int(num_pag)



total_productes = list()
total_garanties = list()    
total_prices = list()    
total_pagines = list()

# Funció que afegeix els productes d'una certa url, la seva garantia, preu i pàgina url específica a les llistes d'aquestes variables   
def get_productes(pagina):
    url = pagina
    page = requests.get(url, headers=headers)
    soup = BeautifulSoup(page.content, "html.parser")

    product = soup.find_all("h2", {"class": ["duration-200 line-clamp-1 md:mb-1 md:mt-0 mt-1 normal-case overflow-ellipsis overflow-hidden text-black transition-all font-body text-3 leading-3 font-bold", 
                                  "duration-200 line-clamp-2 md:mb-1 md:mt-0 mt-1 normal-case overflow-ellipsis overflow-hidden text-black transition-all font-body text-3 leading-3 font-bold"]})
    for p in product:
        total_productes.append(p.get_text().strip())


    garantia = soup.find_all("span", class_="text-black font-body text-2 leading-2 font-light")
    for gar in garantia:
        total_garanties.append(gar.get_text().strip())

        
    price = soup.find_all("span", class_="text-black font-body text-2 leading-2 font-bold")
    for pr in price:
        if len(pr.text.strip()[0:pr.text.find("x")-1]) > 6: 
        # Fem que si el numero és un miler o més, elimini el punt corresponent al miler. 
            total_prices.append(pr.text.strip()[0:pr.text.find("x")-1].replace(",",".").replace(".","",1))
        else:
            total_prices.append(pr.text.strip()[0:pr.text.find("x")-1].replace(",","."))
        
        
    pag = soup.find_all("a", class_="focus:outline-none group md:box-border relative")
    for p in pag:
        total_pagines.append("https://www.backmarket.es"+p.get("href"))



# Iteració de totes les pàgines (1, 2, 3...) per cercar els elements (es crida la funció amb cada una de les pàgines)
for i in range(1, num_pag+1):
    get_productes("https://www.backmarket.es/search?page="+str(i)+"&q="+producte_buscat)
    
# Un cop tenim totes les url de cada producte a "total_pagines", per cada producte, busquem a la seva url altres valors:
# característiques (Giges, color i lliure d'operador), empresa reacondicionadora, país des d'on s'envia el producte i puntuació.

caracteristiques = list()
enviat = list()
reacondicionador = list()
puntuacions = list()
    
for a in total_pagines:
    page = requests.get(a)
    soup = BeautifulSoup(page.content, "html.parser")

    
    caracterist = soup.find("span", class_="block mt-2 md:mt-1 font-body text-3 leading-3 font-light")
    if caracterist is None: # Si no hi ha característiques
        caracteristiques.append('NAN')

    if caracterist is not None:
        caracteristiques.append(caracterist.text.strip())

    
    empresa = soup.find_all("p", class_="mb-1 overflow-hidden font-body text-3 leading-3 font-bold")
    if len(empresa) == 0: # Si no hi ha empresa reacondicionadora
        reacondicionador.append('NAN')
    else:    
        for p in empresa:
            reacondicionador.append(p.text[30:].strip())
        
    
    envio = soup.find_all("span", class_="text-grey-500 font-body text-2 leading-2 font-bold")
    if len(envio) == 0: # Si no indica des d'on s'envia
        enviat.append('NAN')
    else:
        for p in envio:
            enviat.append(p.text.strip())
    
    
    puntuacio = soup.find("span", class_="ml-1 text-primary font-body text-2 leading-2 font-bold")
    if puntuacio is None:
        puntuacions.append('NAN')
    if puntuacio is not None:
        puntuacions.append(puntuacio.text.strip()[0:puntuacio.text.find("\/")-1])
        


# Creem el dataset
df = pd.DataFrame({"Producte": total_productes, "Caracteristiques": caracteristiques, "Preu": total_prices, 
                   "Puntuacio": puntuacions, "Reacondicionador": reacondicionador, "Origen_enviament": enviat, 
                   "Garantia": total_garanties, "Url": total_pagines,}) 

# NETEJA DE DADES
# Filtrem els productes que comencin per "iphone" ja que al buscar iphone també es mostren com a resultat fundes i altres
# telèfons mòbils, i per tant també s'han registrat les dades d'aquests. S'ha observat que quan són iphone, el nom del
# producte sempre comença per "iphone".
df = df[df["Producte"].str.contains(r"^"+producte_buscat, regex=True, case=False)]

# Dividim la columna de Caracteristiques en tres columnes: Giges, color i llibertat d'operador, variables contingudes
# en aquesta mateixa columna de "Caracteristiques".
df[["Capacitat","Color","Operador"]] = df.Caracteristiques.str.split('\s+-\s+', expand=True)

# Reordenem les columnes al nostre gust i transformem les numèriques en float
df = df[["Producte", "Capacitat", "Color", "Operador", "Preu", "Puntuacio", "Reacondicionador", "Origen_enviament", "Garantia", "Url"]]
df = df.astype({"Preu": "float", "Puntuacio": "float"})

# Ho exportem a un CSV.
df.to_csv("PRAC1_Iphone-Backmarket.csv", sep=';', index=False)


# In[ ]:




