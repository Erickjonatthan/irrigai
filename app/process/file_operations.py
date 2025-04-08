import os

def criar_diretorios(inDir, latitude, longitude, area):
    if not os.path.exists(inDir):
        os.makedirs(inDir)
    _localdataName = f"{inDir}/{latitude}_{longitude}_{area}"
    if not os.path.exists(_localdataName):
        os.makedirs(_localdataName)
    _graficos = os.path.join(_localdataName, "resultados")
    if not os.path.exists(_graficos):
        os.makedirs(_graficos)
    return _localdataName, _graficos