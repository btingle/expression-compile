## expression-compile
Compiles arbitrary expressions into pseudo-machine code, which can be executed.

# Install
Install this file in (python path)/Python/Lib/site-packages
To use in your program, type
```
  from expression-compile import ExpressionCompiler
```
in the header

# Usage
`ExpressionCompiler("some-expression")` 
Creates a new ExpressionCompiler object, complete with instructions.
`ExpressionCompiler.execute(vals)` 
Execute "machine code" with given variable values, and return output.
`ExpressionCompiler.printinstructions()` 
Prints instructions, in case you're curious.

# Example
Code:
```
expressionString = "(x * x) + (y * y) + (5 * (z + 10))"
expression = ExpressionCompiler(expressionString)
result = expression.execute(5, 7, 9)
expression.printinstructions()
print(result)
```
Output:
```
STO V0 R0
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
169            //result
```

# Future updates
Planned Expansions:
- More space for variables (currently only 32, and all must be lowercase alphabetical)
- More space for constants (currently only 64)
- Add support for functions
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










    
