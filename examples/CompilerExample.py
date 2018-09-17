from expression_compile import ExpressionCompiler

expression = ExpressionCompiler("1 + 1")
cmd = ""

while not cmd == "exit":
	cmd = input("What would you like to do? ")
	cmds = cmd.split(" ")
	cmd = cmds[0]
	
	if cmd == "expr":
		expr = input("Enter an expression\n")
		try:
			expression = ExpressionCompiler(expr)
			print("Compiled!")
		except:
			print("Uh oh, something went wrong with compilation. Are you sure you entered the expression correctly?")
		if len(expression.vars) == 0:
			try:
				print("Result:")
				print(expression.execute())
			except:
				print("Uh oh, something went wrong with execution.")
	
	if cmd == "eval":
		vals = []
		if len(expression.vars) > 0:
			inpvals = input("Enter variable values, separated by spaces\n")
			inpvals = inpvals.split(" ")
			for val in inpvals:
				vals.append(float(val))
		try:
			print("Result:")
			print(expression.execute(*vals))
		except:
			print("Uh oh, something went wrong with execution. Are you sure you entered in correct values?")
			
	if cmd == "addf":
		fname = input("Enter desired name for function\n")
		ExpressionCompiler.addfunc(expression.execute, fname)
		
	if cmd == "delf":
		fname = input("Enter function to be deleted. Warning: Deletion of built-in functions cannot be undone.\n")
		ExpressionCompiler.delfunc(fname)
		
	if cmd == "showf":
		print(ExpressionCompiler.funcnames)
			
	if cmd == "inst":
		expression.printinstructions()
		
	if cmd == "help":
		if len(cmds) == 1:
			print("Commands:\nhelp, expr, eval, inst, addf, delf, showf. To view more information on a particular command, type \"help [cmd]\"")
		elif cmds[1] == "help":
			print("Provides information on functions")
		elif cmds[1] == "expr":
			print("Allows entering in a mathematical expression to be evaluated with \"eval\".\nThis expression can be added to available functions with \"addf\" or removed with \"delf\"")
			print("Expressions with variables, constants, arithmetical operators, and available functions are supported by the compiler.")
		elif cmds[1] == "eval":
			print("Requests variable values for expression, then evaluates expression with those values")
		elif cmds[1] == "inst":
			print("Prints machine instructions associated with current expression")
		elif cmds[1] == "addf":
			print("Adds current expression to ExpressionCompiler function library. Max 8 functions.")
		elif cmds[1] == "delf":
			print("Deletes a function from the ExpressionCompiler function library.")
		elif cmds[1] == "showf":
			print("Lists all available functions for use in expressions")
		else:
			print("Command not recognized")
		
