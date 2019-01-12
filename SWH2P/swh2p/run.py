import os
import sys
sys.path.append(os.path.abspath('../'))
import swh2p

if __name__=="__main__":
#    swh2p.index_tseries_all(R'X:\Data\2P01\2016\2017-01-11 PVN astrocyte')
    swh2p.index_tseries_single(R"X:\Data\2P01\2016\2017-01-11 PVN astrocyte\TSeries-01272017-1255-1217")
    print("DONE")