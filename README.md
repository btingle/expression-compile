## expression-compile
Compiles arbitrary expressions into pseudo-machine code, which can be executed. Currently only supports basic arithmetic operations.

# Install
Install this file in (python path)/Python/Lib/site-packages
To use in your program, type
```
  from expression_compile import ExpressionCompiler
```
in the header

# Usage
`ExpressionCompiler("some-expression")` 
Creates a new ExpressionCompiler object, complete with instructions.

`ExpressionCompiler.execute(vals)` 
Execute "machine code" with given variable values, and return output.

`ExpressionCompiler.printinstructions()` 
Prints instructions, in case you're curious.

`ExpressionCompiler.vars`
Returns all variable names in expression.

`ExpressionCompiler.cons`
Returns all constants in expression

`ExpressionCompiler.addfunc(callback, name)`
Registers a new function in ExpressionCompiler class, that can be used by any ExpressionCompiler object.

This can be used to register other expressions as functions by `.addfunc(expression.execute, name)`

Default functions are sin, cos, and sqrt. These can be removed.

`ExpressionCompiler.delfunc(name)`
Deletes function with specified name from list

# Example
Code:
```
expressionString = "(sin(x) * x) + (y * y) + (5 * (z + 10))"
expression = ExpressionCompiler(expressionString)
result = expression.execute(1, 2, 3)
expression.printinstructions()
print(result)
```
Output:
```
STO V0 R0
FUN R0 R0
STO V0 R1
MUL R0 R1 R0
STO V1 R1
STO V1 R2
MUL R1 R2 R1
ADD R0 R1 R0
STO C0 R1
STO V2 R2
STO C1 R3
ADD R2 R3 R2
MUL R1 R2 R1
ADD R0 R1 R0
69.8414709848079            //result
```

# Future updates
Planned Expansions:
- More space for variables (currently only 32, and all must be lowercase alphabetical)
- More space for constants (currently only 64)
- ~~Add support for functions~~ Done! Only space for 8 functions unfortunately.
- Add support for comparative operators
- Add support for logical operators
- Add support for conditional statements

What this will hopefully look like:
```
expressionString =
"
foo = bar * y;
if (foo > 10) {
  baz = sin(bar);
} else {
  baz = sin(foo);
}
return baz;
"
expression = ExpressionCompiler(expressionString)
print(expression.exec(0, 5, 3, 0))
>>> -0.958924274661385
```

# Notes
If you somehow come across this project, I am fairly new to programming and would appreciate any advice or constructive criticism. I have little in-depth formal knowledge of how assembly language or machine instructions work, so I'm sure this could use some brushing up. Thanks!










    
