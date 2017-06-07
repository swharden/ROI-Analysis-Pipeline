# Notes related to matrix

l <- (1:50)+100
m2d <- matrix(l, ncol=5)

message("sectioning demo")
print(m2d) # shows all the matrix
print(l[3]) # the 13th element
print(m2d[3]) # the 13th element (should be the same)
print(m2d[3,]) # shows the third row
print(m2d[,3]) # shows the third column
m2d[,3]<-m2d[,3]**2 # squares the third column
print(m2d) # shows all the matrix