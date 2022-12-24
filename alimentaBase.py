import pandas as pd
import numpy as np
import sys
import re
import time

startTime = time.time()

data = pd.read_csv(sys.argv[1], sep = ";")

agregarBase = pd.read_csv(sys.argv[2], sep = ";")

newData = data.melt(id_vars="NrodeDoc")

newData["value"] = newData["value"].astype(str)
newData["value"] = newData["value"].str.replace("\.0$", "")

agregarBase["Telefonos"] = agregarBase["Telefonos"].astype(str)
agregarBase["Telefonos"] = agregarBase["Telefonos"].str.replace("\.0$", "")

agregarBase["variable"] = "Telefono " + agregarBase.groupby("NrodeDoc")["Telefonos"].rank(method="first").astype(int).astype(str)
agregarBase = agregarBase[["NrodeDoc", "variable", "Telefonos"]].rename({"Telefonos": "value"}, axis = 1)


baseFinal = pd.concat([newData, agregarBase])



baseFinal["variable"] = "Telefono " + baseFinal.groupby("NrodeDoc")["value"].rank(method="first").astype(int).astype(str)

baseFinal = pd.pivot_table(baseFinal, index = "NrodeDoc", columns = "variable", aggfunc=np.max)
baseFinal = baseFinal.droplevel(None, axis=1)


regex = re.compile("\d(\d)?")
columnas = [int(regex.search(e).group()) for e in list(baseFinal.columns)]
columnas.sort()

columnas = ["Telefono " + str(e) for e in columnas]


baseFinal = baseFinal.reset_index()

baseFinal = baseFinal[["NrodeDoc"] + columnas]
baseFinal = baseFinal.replace("nan", "")

baseFinal.to_csv("Nueva_base.csv", index = False, sep = ";")

endTime = time.time()

print("Total time %s" % str(endTime - startTime))
