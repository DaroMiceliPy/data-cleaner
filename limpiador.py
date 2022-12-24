import pandas as pd
import numpy as np
import re
import sys
import time



startTime = time.time()
data = pd.read_csv(sys.argv[1], sep = ";")
quitarBase = pd.read_csv(sys.argv[2], sep = ";")


newData = data.melt(id_vars="NrodeDoc") #Ponemos en un formato adecuado para cruzar

#Convertimos a string
newData["value"] = newData["value"].astype(str)
newData["value"] = newData["value"].str.replace("\.0$", "")

quitarBase["Telefonos"] = quitarBase["Telefonos"].astype(str)
quitarBase["Telefonos"] = quitarBase["Telefonos"].str.replace("\.0$", "")



#Hacemos el cruce y limpiamos la base
mergeo = quitarBase.merge(newData, how = "right", left_on="Telefonos", right_on="value")

baseLimpia = mergeo[mergeo["Telefonos"].isna()]

dataInvalida = mergeo[~mergeo["Telefonos"].isna()]

#Agregamos dnis de clientes los cuales todos tenian telefonos erroneos
checking = baseLimpia.rename({"NrodeDoc": "dni"}, axis=1)

agregarDnis = dataInvalida.merge(checking.drop_duplicates(subset = ["dni"]), 
    how = "left", left_on="NrodeDoc", right_on="dni")


agregarDnis = agregarDnis[agregarDnis["dni"].isna()]["NrodeDoc"]

agregarDnis = pd.DataFrame(data = {"NrodeDoc": agregarDnis, "variable": np.nan, "value": np.nan})


baseLimpiaFinal = pd.concat([baseLimpia[["NrodeDoc", "variable", "value"]], agregarDnis])



#Ordenamos por numeros de telefonos, pivoteamos la base para tenerla en el formato original y eliminamos los nulos.
baseLimpiaFinal["variable"] = "Telefono " + baseLimpiaFinal.groupby("NrodeDoc")["value"].rank(method="first").astype(int).astype(str)


baseLimpiaFinal = pd.pivot_table(baseLimpiaFinal, index = "NrodeDoc", columns = "variable", aggfunc=np.max)
baseLimpiaFinal = baseLimpiaFinal.droplevel(None, axis=1)


regex = re.compile("\d(\d)?")
columnas = [int(regex.search(e).group()) for e in list(baseLimpiaFinal.columns)]
columnas.sort()

columnas = ["Telefono " + str(e) for e in columnas]


baseLimpiaFinal = baseLimpiaFinal.reset_index()

baseLimpiaFinal = baseLimpiaFinal[["NrodeDoc"] + columnas]
baseLimpiaFinal = baseLimpiaFinal.replace("nan", "")

baseLimpiaFinal.to_csv("Nueva_base.csv", index = False, sep = ";")

endTime = time.time()

print("Total time %s" % str(endTime - startTime))