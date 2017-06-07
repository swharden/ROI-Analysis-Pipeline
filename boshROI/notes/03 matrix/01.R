# Notes related to multidimensional data
# A vector is locked at 1D
# A matrix is an array locked a 2D
# An array can be any number of dimensions

### MATRIX ### (good for 2d)

message("\n -- Create a list of consecutive numbers")
l <- (1:20)
message("list/set length:",length(l))

message("\n  --  reshaping list into a 2d matrix")
m2d <- matrix(l, ncol=4)
message("matrix length:",length(m2d))
message("matrix rows: ",dim(m2d)[1])
message("matrix columns: ",dim(m2d)[2])
print(m2d)

### ARRAY ### (good for higher dimensions)
message("\n  --  creating empty 3d array")
arr<-array(0,dim=c(5,4,3)) # (rows, cols, slices)
print(dim(arr))
#print(arr)
