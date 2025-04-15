import json
import os
import folium
import geopandas as gpd
from shapely.geometry import Polygon

def criar_mapa(latitude, longitude, _quadrado, _graficos):
    """
    Cria um mapa com base nas coordenadas e salva como arquivo HTML.
    """
    data_Json = {
        "type": "FeatureCollection",
        "features": [
            {
                "type": "Feature",
                "properties": {},
                "geometry": {
                    "coordinates": [
                        [
                            _quadrado[0],
                            _quadrado[1],
                            _quadrado[2],
                            _quadrado[3],
                            _quadrado[0]
                        ]
                    ],
                    "type": "Polygon"
                }
            }
        ]
    }

    quadrado = Polygon(_quadrado)
    quadrado_gdf = gpd.GeoSeries(quadrado)
    geo_json_data = quadrado_gdf.to_json()
    mapa = folium.Map(location=[latitude, longitude])

    folium.GeoJson(geo_json_data).add_to(mapa)

    mapa_path = os.path.join(_graficos, "map.html")
    mapa.save(mapa_path)

    return mapa_path, data_Json, geo_json_data