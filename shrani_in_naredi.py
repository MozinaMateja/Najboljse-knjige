import requests
import re
import orodja

vzorec_bloka = re.compile(
    r'<tr itemscope itemtype="http://schema.org/Book">.*?'
    r'</div>\s*\n</div>\s*</td>\s*</tr>',
    flags=re.DOTALL
)
vzorec = re.compile(
    r'itemprop="url" href="/book/show/(?P<id>\d+).*'
    r"\n\s*<span itemprop='name'.*'4'>(?P<naslov>.*?)(\s\((?P<zbirka>.*?) #.*\))?</span>"
    r'(.|\n)*?'
    r'\n<a class="authorName".*href="https:.*?show/(?P<id_avtorja>\d+)..*?"><span itemprop="name">(?P<avtor>.*)</span></a>.*?'
    r'(.|\n)*?'
    r'\n\s*<span class="minirating">.*?</span></span> (?P<ocena>.*) avg rating &mdash; (?P<stevilo_ocen>.*) ratings</span>'
    r'\n\s*</span>\n\s*</div>\n{3}\s*<div style="margin-top(.|\n)*?and'
    r'</span>\n\s*<a id="loading_link.*?return false;">(?P<glasovi>.*) people voted'
)

vzorec_zbirke = re.compile(r"\n\s*<span itemprop='name'.*'4'>.*?\s\((?P<zbirka>.*?) #.*\)</span>", re.DOTALL)
vzorec_pomoznega_bloka = re.compile(
    r'<div id="details" class="uitext darkGreyText">.*?'
    r'<div class="buttons">'
)

vzorec_formata = re.compile(r'bookFormat">(.*?)</span>', re.DOTALL)
vzorec_stevila_strani = re.compile(r'numberOfPages">(.*?) pages</span>', re.DOTALL)
vzorec_leta = re.compile(r'Published.*?(?P<leto>\d{4})', re.DOTALL)
vzorec_jezika = re.compile(r"inLanguage'>(.*?)</div>")
vzorec_zanra = re.compile(r'actionLinkLite bookPageGenreLink".*?>(.*?)</a>')


def spremeni(blok):
    knjiga = vzorec.search(blok).groupdict()
    knjiga['id'] = int(knjiga['id'])
    knjiga['id_avtorja'] = int(knjiga['id_avtorja'])
    knjiga['avtor'] = knjiga['avtor'].replace("&#39", "'").replace("&amp;", "&").replace("&quot;", "'")
    knjiga['naslov'] = knjiga['naslov'].replace("&#39", "'").replace("&amp;", "&").replace("&quot;", "'")
    knjiga['ocena'] = float(knjiga['ocena'])
    knjiga['stevilo_ocen'] = int(knjiga['stevilo_ocen'].replace(',', ''))
    knjiga['glasovi'] = int(knjiga['glasovi'].replace(',', ''))
    zbirka = vzorec_zbirke.search(blok)
    if zbirka:
        knjiga['zbirka'] = knjiga['zbirka'].replace("&amp;", "&")
        if knjiga['zbirka'][-1] == ',':
            knjiga['zbirka'] = knjiga['zbirka'][:-1]
    else:
        knjiga['zbirka'] = None
    id_knjige = knjiga['id']
    url = "https://www.goodreads.com/book/show/" + str(id_knjige)
    dat = f'knjige_po_id/{id_knjige}.html'
    orodja.shrani_spletno_stran(url, dat)
    vsebina = orodja.vsebina_datoteke(dat)
    
    format = re.search(vzorec_formata, vsebina)
    if format:
        knjiga['format'] = format.group(1)
    else:
        knjiga['format'] = None

    stevilo_strani = re.search(vzorec_stevila_strani,vsebina)
    if stevilo_strani:
        knjiga['stevilo_strani'] = int(stevilo_strani.group(1))
    else:
        knjiga['stevilo_strani'] = None
    
    leto = re.search(vzorec_leta,vsebina)
    if leto:
        knjiga['leto'] = int(leto.group(1))
    else:
        knjiga['leto'] = None

    jezik = re.search(vzorec_jezika, vsebina)
    if jezik:
        knjiga['jezik'] = jezik.group(1)
    else:
        knjiga['jezik'] = None

    zanr = re.search(vzorec_zanra, vsebina)
    if zanr:
        knjiga['zanr'] = zanr.group(1)
    else:
        knjiga['zanr'] = None
    return knjiga
    
def ena_stran(stevilka):
    url=f'https://www.goodreads.com/list/show/1.Best_Books_Ever?page={stevilka}/'
    datoteka = f'najbolj-popularne-knjige/{stevilka}.html'
    orodja.shrani_spletno_stran(url, datoteka)
    vsebina = orodja.vsebina_datoteke(datoteka)
    for blok in vzorec_bloka.finditer(vsebina):
        yield spremeni(blok.group(0))
        
seznam = []
for stevilka_strani in range(1, 6):
    for i in ena_stran(stevilka_strani):
        seznam.append(i)
#orodja.zapisi_json(seznam, 'obdelani-podatki/knjige.json')
#orodja.zapisi_csv(seznam, ['id', 'naslov', 'zbirka', 'id_avtorja', 'avtor', 'ocena', 'stevilo_ocen', 'glasovi', 'format', 'stevilo_strani', 'leto', 'jezik', 'zanr'], 'obdelani-podatki/knjige.csv')

