"""
demonstrate how to work with masked arrays.

OUTPUT:

    original data:
    [[10 11 12 13 14 15]
     [16 17 18 19 20 21]
     [22 23 24 25 26 27]
     [28 29 30 31 32 33]
     [34 35 36 37 38 39]]

    selectively unmasked:
    [[-- -- -- -- -- --]
     [-- 17 18 -- -- 21]
     [-- -- -- -- -- --]
     [-- 29 30 -- -- 33]
     [-- 35 36 -- -- 39]]

    unmasked values: [17 18 21 29 30 33 35 36 39]

"""
import numpy as np

data=np.arange(30).reshape((5,6))+10
print("original data:\n{}".format(data))

print()
data=np.ma.array(data,mask=True)
for x in [1,2,5]:
    for y in [1,3,4]:
        data.mask[y,x]=False
print("selectively unmasked:\n{}".format(data))


valid=data.compressed()
print("\nunmasked values: {}".format(valid))