from Element_PI import VariancePersist
from Element_PI import VariancePersistv1
import pandas as pd
import numpy as np
from sklearn.model_selection import KFold
from sklearn.kernel_ridge import KernelRidge

from tpot import TPOTRegressor
from sklearn.model_selection import train_test_split

y=pd.read_excel('Int_Energies.xlsx',usecols=[1])

#Some PI hyperparameters
pixelsx=150
pixelsy=150
spread=.08
Max=2.5

samples=218

X=np.zeros((samples,pixelsx*pixelsy))

for i in range(1,samples):
    X[i,:]=VariancePersistv1('babel/{}.xyz'.format(i+1), pixelx=pixelsx, pixely=pixelsy, myspread=spread, myspecs={"maxBD": Max, "minBD":-.10}, showplot=False)

X_train, X_test, y_train, y_test = train_test_split(X, np.array(y), train_size=0.75, test_size=0.25, random_state=42)

tpot = TPOTRegressor(generations=5, population_size=50, verbosity=2, random_state=42)
tpot.fit(X_train, y_train)
print(tpot.score(X_test, y_test))
tpot.export('./tpot_PI_pipeline.py')
