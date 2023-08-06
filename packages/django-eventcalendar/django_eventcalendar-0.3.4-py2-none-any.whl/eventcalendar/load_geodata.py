import os
from django.contrib.gis.utils import LayerMapping
from models import Neighborhood

neighborhood_mapping = {
    'name': 'MAPNAME',
    'geography': 'MULTIPOLYGON',
}
neighborhood_shp = os.path.abspath(os.path.join(os.path.dirname(__file__), 'fixtures/Neighborhoods_Philadelphia/Neighborhoods_Philadelphia.shp'))


def run(verbose=True):
    lm = LayerMapping(Neighborhood, neighborhood_shp, neighborhood_mapping,
                      transform=True, encoding='iso-8859-1')

    lm.save(strict=True, verbose=verbose)
