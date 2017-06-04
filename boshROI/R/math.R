# add two numbers together and return the result (a+b)
add <- function(a, b){
	ans=a+b
	cat(sprintf("%f + %f = %f\n",a,b,ans))
	return(ans)
}

# subtract two numbers together and return the result (a-b)
subtract <- function(a, b){
	ans=a-b
	cat(sprintf("%f - %f = %f\n",a,b,ans))
	return(ans)
}

# multiply two numbers together and return the result (a*b)
multiply <- function(a, b){
	ans=a*b
	cat(sprintf("%f * %f = %f\n",a,b,ans))
	return(ans)
}

# divide two numbers together and return the result (a/b)
divide <- function(a, b){
	ans=a/b
	cat(sprintf("%f / %f = %f\n",a,b,ans))
	return(ans)
}