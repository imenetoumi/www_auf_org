# encoding: utf-8

import json

from auf.django.references.models import Pays, Region
from django.http import HttpResponse


LAT_LONG = {
    'A': (45.5, -73.55),
    'ACGL': (3.867, 11.517),
    'AO': (14.683, -17.433),
    'AP': (21.033, 105.85),
    'C': (18.533, -72.333),
    'ECO': (44.433, 26.1),
    'EO': (50.833, 4.35),
    'M': (34.033, -6.833),
    'MO': (33.883, 35.5),
    'OI': (-18.933, 47.517),
}


def pays_json(request):
    data = {}
    for pays in Pays.objects.all():
        implantation = pays.region.implantation_set.filter(
            actif=True, type="Bureau")[0]
        try:
            adresse_physique = "<br/>".join([
                "<strong>" + implantation.nom + "</strong>",
                implantation.adresse_physique_bureau,
                " ".join([implantation.adresse_physique_no,
                          implantation.adresse_physique_rue]),
                " ".join([implantation.adresse_physique_ville,
                          implantation.adresse_physique_region,
                          implantation.adresse_physique_code_postal,
                          unicode(implantation.adresse_physique_pays)])
            ])
            adresse_postale = "<br/>".join([
                "<strong>" + implantation.nom + "</strong>",
                implantation.adresse_postale_bureau,
                " ".join([implantation.adresse_postale_no,
                          implantation.adresse_postale_rue]),
                " ".join([implantation.adresse_postale_ville,
                          implantation.adresse_postale_region,
                          implantation.adresse_postale_code_postal,
                          unicode(implantation.adresse_postale_pays.nom)])
            ])
        except:
            adresse_physique = ''
            adresse_postale = ''
        data[pays.code_iso3] = {
            'id': pays.code_iso3,
            'name': pays.nom,
            'fillKey': 'B' + pays.region.code,
            'adresse_physique': adresse_physique,
            'adresse_postale': adresse_postale,
        }
    return HttpResponse(json.dumps(data), mimetype='application/json')


def bureaux_json(request):
    regions = Region.objects.all()
    data = []
    for region in regions:
        if region.code in LAT_LONG:
            latitude, longitude = LAT_LONG[region.code]
            data.append({
                'latitude': latitude,
                'longitude': longitude,
                'radius': 4,
                'nom': 'Bureau ' + region.nom
            })
    return HttpResponse(json.dumps(data), mimetype='application/json')
