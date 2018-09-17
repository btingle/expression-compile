from math import sin, cos, sqrt

class ExpressionCompiler:

	tokens    = [ '(' , ')', '+', '-', '*', '/', ',' ]							# static
	alphabet  = "abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ"			# static
	numerical = "1234567890"													# static
	funcnames = [ "sin", "cos", "sqrt" ]										# static
	funccallb = [  sin ,  cos ,  sqrt  ]										# static
	
	def __init__(self, expression):
		self.expression, self.vars, self.cons = ExpressionCompiler.initpass('('+ expression + ')')
		self.expression   = ExpressionCompiler.secondpass(self.expression)
		self.instructions = ExpressionCompiler.assemble(self.expression)
		self.mem          = [0 for i in range(255)]	# self, memory storage for execution, makes up 255 registers
		
	### Initial pass of expression
	@staticmethod
	def initpass( expstring ):

		expstring  = "".join(expstring.split(" "))
		newexpbuff = ""
		const      = ""
		varn       = ""
		cons       = []
		vars       = []
		tokens     = ExpressionCompiler.tokens
		alphabet   = ExpressionCompiler.alphabet
		numerical  = ExpressionCompiler.numerical
		funcnames  = ExpressionCompiler.funcnames
		
		for char in expstring:

			if char in numerical or char is '.': # gets constant values
				const += char
			else:
				if const != "":
					if '.' in const:
						cons.append(float(const))
						newexpbuff += chr(cons.index(float(const)) + 64)
						const = ""
					else:
						cons.append(int(const))
						newexpbuff += chr(cons.index(int(const)) + 64)
						const = ""
					
			if char in alphabet: # gets vars/functions
				varn += char
			else:
				if varn != "":
					if char != '(':
						if varn in vars:
							newexpbuff += chr(vars.index(varn) + 32)
						else:
							vars.append(varn)
							newexpbuff += chr(vars.index(varn) + 32)
					else:
						newexpbuff += chr(funcnames.index(varn) + 8)
					varn = ""
					
			if char in tokens[0:2]:
				newexpbuff += chr(ord(char) + 214) # converts to reserved values for ( and ), which are 254 and 255 respectively
				
			if char in tokens[2:7]:
				newexpbuff += chr(ord(char) - 42 ) # converts to reserved values for ops, which are 0 - 7
		
		return newexpbuff, vars, cons

	# Some explanation, as this one is a little weird.
	# This basically removes parentheses in favor of a "length" statement that encodes the length of the expression after it. This makes assembling easier.
	### Second pass of expression
	@staticmethod
	def secondpass( expstring ):
		
		solstring = ['&'] # have to use char buffer as strings are immutable in python. '&' char will eventually hold total expression length
		i = 1
		j = 0
		
		def count( par ):
		
			nonlocal i
			nonlocal j
			nonlocal solstring
			amount = 0
			countpos = j
			
			while expstring[i] is not chr(255): # ')'

				amount += 1
				if expstring[i] is chr(254): # '('
					solstring.append('&') # placeholder for expression length
					j += 1
					i += 1
					count(1)
				
				elif expstring[i] is chr(1) or expstring[i] is chr(3): # +/-
					if not par: # if this is an add block, it should stop at the next addition/subtraction operator
						amount -= 1
						break
					amount += 1
					solstring.append(expstring[i]) # adds the +/- operator
					solstring.append('&') # placeholder for expression length
					j += 2
					i += 1
					count(0)
				
				elif ord(expstring[i]) < 16 and ord(expstring[i]) > 7:
					solstring.append(expstring[i])
					amount -= 1
					i += 1
					j += 1
				
				else:
					solstring.append(expstring[i])
					j += 1
					i += 1
			
			i += par
			
			if amount % 2 is 0:
				print(amount)
				for char in solstring:
					print(hex(ord(char)))
				raise NameError("Unexpected number of statements in expression.")
				
			solstring[countpos] = chr(16 + (amount // 2))
		
		count(1)
		
		# Ok so this is a bit of a hack, but in general, LEN 0 statements can be removed, such as (x) or (5), but when they are part of a function, they shouldn't be, e.g f(x)
		# So this just goes through the solution string and increments LEN statements after functions
		# Later, when assembling, length statements after functions are decremented by one
		for i in range(len(solstring)):	
			if ord(solstring[i]) > 7 and ord(solstring[i]) < 16:
				solstring[i+1] = chr(ord(solstring[i+1])+1)
		
		return "".join(("".join(solstring)).split(chr(0x10))) # optimizes out length 0 LEN statements (which are just single constants or variables)
	
	### Creates a set of instructions for the ExpressionCompiler to execute, emulates machine language
	@staticmethod
	def assemble( expstring ):

		i    = 0
		instructions = []
		optable = {
			0 : chr(1),	# MUL
			1 : chr(2),	# ADD
			3 : chr(3),	# SUB
			5 : chr(4)	# DIV
		}
		
		def convert( char ):
			if ord(char) < 8: 						# op // shouldn't be encountered
				return -1
			if ord(char) < 16 and ord(char) > 7: 	# func
				return 1
			if ord(char) < 32 and ord(char) > 15:	# count
				return 2
			if ord(char) < 64 and ord(char) > 31:	# var
				return 3
			if ord(char) < 128 and ord(char) > 63:	# const
				return 4
			return -1								# if something else is encountered // shouldn't happen
		
		def assembleblock( memloc ):
		
			nonlocal i
			nonlocal instructions
			nonlocal optable
			expval = convert(expstring[i])
					
			if   expval is 1:	# function instruction assembly
				length = ord(expstring[i + 1]) - 17 # subtraction val is 17 because of hack mentioned prior
				funcinst = chr(ord(expstring[i]))
				i += 2
				assembleblock(memloc)
				funcinst += chr(2) + chr(memloc)
				for j in range(length):
					i += 1
					assembleblock(memloc + j + 1)
					funcinst += chr(2) + chr(memloc + j + 1)
				funcinst += chr(2) + chr(memloc)
				instructions.append(funcinst)
			
			elif expval is 2:	# evaluates len statements
				length = ord(expstring[i]) - 16
				i += 1
				assembleblock(memloc)
				for j in range(length):
					op = optable.get(ord(expstring[i]))
					i += 1
					assembleblock(memloc + 1)
					instructions.append( op + chr(2) + chr(memloc) + chr(2) + chr(memloc+1) + chr(2) + chr(memloc))  # op = MUL/ADD/SUB/DIV, chr(2) = REG, chr(2) = REG, chr(2) = REG
				
			elif expval is 3:	# stores var in register
				instructions.append( chr(0) + chr(0) + chr(ord(expstring[i])-32) + chr(2) + chr(memloc) )	# chr(0) = STO, chr(0) = VAR, chr(2) = REG
				i += 1
				
			elif expval is 4:	# stores const in register
				instructions.append( chr(0) + chr(1) + chr(ord(expstring[i])-64) + chr(2) + chr(memloc) )	# chr(0) = STO, chr(1) = CON, chr(2) = REG
				i += 1
		
		assembleblock( 0 )
		
		return instructions
		
	@staticmethod
	def funceval( funcval, memvals ):	# wrapper function to pass arguments to specified function
		
		functioncallbacks = ExpressionCompiler.funccallb
		functionindex = ord(funcval) - 8
		
		function = functioncallbacks[functionindex]	# if this fails, function does not exist (not sure how this would happen, as nonexistent functions would return an error on initial pass)
		return function(*memvals)	# unwraps memvals list and passes to function
		
	@staticmethod
	def addfunc( function , functionname ):	# allows adding custom functions. This also allows adding other ExpressionCompiler execute functions.
		ExpressionCompiler.funcnames.append(functionname)
		ExpressionCompiler.funccallb.append(function)
		
	@staticmethod
	def delfunc( functionname ):	# and deletes them by providing the name
		index = ExpressionCompiler.funcnames.index(functionname)
		ExpressionCompiler.funcnames.remove(ExpressionCompiler.funcnames[index])
		ExpressionCompiler.funccallb.remove(ExpressionCompiler.funccallb[index])
	
	### Prints translated assembly instructions, in case you're curious
	def printinstructions( self ):
		
		### Instruction reference
		# Instructions have the following format:
		# [Instruction Type] [Memory Location 1] ... [Memory location N] [Result Register]
		# For example:
		# [0] [0] [1] [2] [0]
		# [0] 				  Tells the machine that this is a STORE instruction
		#     [0] 			  Tells the machine to grab variable from memory...
		#		  [1] 		  ...With index 1
		# 			  [2]     Tells the machine to store value of variable in register...
		#				  [0] ...With index 0
		### Cheat Sheet
		# Opcodes:
		# [0] : Store
		# [1] : Multiply
		# [2] : Add
		# [3] : Subtract
		# [4] : Divide
		# [>7]: Function
		# Memory:
		# [0] : Variable
		# [1] : Constant
		# [2] : Register
		
		for instruction in self.instructions:
			if instruction[0] == chr(0):
				if instruction[1] == chr(0):
					print("STO V" + str(ord(instruction[2])) + " R" + str(ord(instruction[4])))
				if instruction[1] == chr(1):
					print("STO C" + str(ord(instruction[2])) + " R" + str(ord(instruction[4])))
					
			elif instruction[0] == chr(1): # if MUL
				print("MUL R" + str(ord(instruction[2])) + " R" + str(ord(instruction[4])) + " R" + str(ord(instruction[2])))
				
			elif instruction[0] == chr(2): # if ADD
				print("ADD R" + str(ord(instruction[2])) + " R" + str(ord(instruction[4])) + " R" + str(ord(instruction[2])))
				
			elif instruction[0] == chr(3): # if SUB
				print("SUB R" + str(ord(instruction[2])) + " R" + str(ord(instruction[4])) + " R" + str(ord(instruction[2])))
				
			elif instruction[0] == chr(4): # if DIV
				print("DIV R" + str(ord(instruction[2])) + " R" + str(ord(instruction[4])) + " R" + str(ord(instruction[2])))
				
			else:
				print("FUN", end="")
				for i in range(1, len(instruction)):
					if i % 2 == 0:
						print(" R" + str(ord(instruction[i])), end="")
				print()
	
	### Executes "assembly" instructions generated by assemble(), and returns result, which will be in the first memory entry
	def execute( self , *vals ): 

		cons = self.cons
		mem  = self.mem

		for instruction in self.instructions:
		
			if instruction[0] == chr(0): # if STO
				try:
					if instruction[1] == chr(0): # if VAR
						mem[ord(instruction[4])] = vals[ord(instruction[2])]
					if instruction[1] == chr(1): # if CON
						mem[ord(instruction[4])] = cons[ord(instruction[2])]
				except IndexError:
					print("Not enough arguments")
					break
					
			elif instruction[0] == chr(1): # if MUL
				mem[ord(instruction[2])] = mem[ord(instruction[2])] * mem[ord(instruction[4])]
				
			elif instruction[0] == chr(2): # if ADD
				mem[ord(instruction[2])] = mem[ord(instruction[2])] + mem[ord(instruction[4])]
				
			elif instruction[0] == chr(3): # if SUB
				mem[ord(instruction[2])] = mem[ord(instruction[2])] - mem[ord(instruction[4])]
				
			elif instruction[0] == chr(4): # if DIV
				mem[ord(instruction[2])] = mem[ord(instruction[2])] / mem[ord(instruction[4])]
				
			else:
				memvals = []
				for i in range(2, len(instruction) - 2, 2): # Gets the register values of each instruction
					memvals.append(mem[ord(instruction[i])])
				mem[ord(instruction[2])] = ExpressionCompiler.funceval(instruction[0], memvals)  # and passes parameters to function
				
		return mem[0]


if __name__ == "__main__":
	expression = ExpressionCompiler("x * x")

	ExpressionCompiler.addfunc(expression.execute, "square")
	
	newexpression = ExpressionCompiler("square(5) + 10")
	newexpression.printinstructions()
	
	print(newexpression.execute())

	
		

		
		
		
		
		
		

