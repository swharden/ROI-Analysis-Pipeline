source("math.R")

message("\nGENERATING RANDOM NUMBERS FOR A AND B")
a<-runif(1, 11, 99) # 1 random number between 11 and 99
b<-runif(1, 11, 99) # 1 random number between 11 and 99
message("a = ",a)
message("b = ",b)

message("\nDOING SOME MATH")
total<-0
total<-total+add(a,b)
total<-total+subtract(a,b)
total<-total+multiply(a,b)
total<-total+divide(a,b)
message("The running total is:" ,total)