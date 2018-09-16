class ExpressionCompiler:

	tokens    = [ '(' , ')', '+', '-', '*', '/' ]	# static
	alphabet  = "abcdefghijklmnopqrstuvwxyz"		# static
	numerical = "1234567890"						# static
	
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
		cons       = []
		vars       = []
		tokens     = ExpressionCompiler.tokens
		alphabet   = ExpressionCompiler.alphabet
		numerical  = ExpressionCompiler.numerical
		
		for char in expstring:

			if char in numerical:
				const += char
			else:
				if const != "":
					cons.append(int(const))
					newexpbuff += chr(cons.index(int(const)) + 64)
					const = ""
					
			if char in tokens[0:2]:
				newexpbuff += chr(ord(char) + 214) # converts to reserved values for ( and ), which are 254 and 255 respectively
				
			if char in tokens[2:6]:
				newexpbuff += chr(ord(char) - 42 ) # converts to reserved values for ops, which are 0x0 - 0x7
				
			if char in alphabet:
				if char in vars:
					newexpbuff += chr(vars.index(char) + 32)
				else:
					vars.append(char)
					newexpbuff += chr(vars.index(char) + 32)
		
		return newexpbuff, vars, cons

	# Some explanation, as this one is a little weird.
	# This basically removes parentheses in favor of a "length" statement that encodes the length of the expression after it. This makes assembling easier.
	### Second pass of expression
	@staticmethod
	def secondpass( expstring ):
		
		solstring = [' '] # have to use char buffer as strings are immutable in python. ' ' char will eventually hold total expression length
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
					solstring.append(' ') # placeholder for expression length
					j += 1
					i += 1
					count(1)
				
				elif expstring[i] is chr(1) or expstring[i] is chr(3): # +/-
					if not par: # if this is an add block, it should stop at the next addition/subtraction operator
						amount -= 1
						break
					amount += 1
					solstring.append(expstring[i]) # adds the +/- operator
					solstring.append(' ') # placeholder for expression length
					j += 2
					i += 1
					count(0)
				
				else:
					solstring.append(expstring[i])
					j += 1
					i += 1
			
			i += par
			
			if amount % 2 is 0:
				print(amount)
				raise NameError("Unexpected number of statements in expression.")
				
			solstring[countpos] = chr(16 + (amount // 2))
		
		count(1)
		
		return "".join(("".join(solstring)).split(chr(0x10))) # optimizes out length 0 LEN statements (which are just single expressions)
	
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
				return chr(ord(char))
			if ord(char) < 16 and ord(char) > 7: 	# func (unused)
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
			
			if   expval is 0:
				raise NameError("Unexpected operator")
				
			elif expval is 1:
				raise NameError("Dunno how you did that")
				
			elif expval is 3:
				instructions.append( chr(0) + chr(0) + chr(ord(expstring[i])-32) + chr(2) + chr(memloc) )	# chr(0) = STO, chr(0) = VAR, chr(2) = REG
				i += 1
				
			elif expval is 4:
				instructions.append( chr(0) + chr(1) + chr(ord(expstring[i])-64) + chr(2) + chr(memloc) )	# chr(0) = STO, chr(1) = CON, chr(2) = REG
				i += 1
				
			else:
				length = ord(expstring[i]) - 16
				i += 1
				assembleblock(memloc)
				for j in range(length):
					op = optable.get(ord(expstring[i]))
					i += 1
					assembleblock(memloc + 1)
					instructions.append( op + chr(2) + chr(memloc) + chr(2) + chr(memloc+1) + chr(2) + chr(memloc))  # op = MUL/ADD/SUB/DIV, chr(2) = REG, chr(2) = REG, chr(2) = REG
					
		assembleblock( 0 )
		return instructions
	
	### Prints translated assembly instructions, in case you're curious
	def printinstructions( self ):
		
		for instruction in self.instructions:
			if instruction[0] == chr(0):
				if instruction[1] == chr(0):
					print("STO V" + str(ord(instruction[2])) + " R" + str(ord(instruction[4])))
				if instruction[1] == chr(1):
					print("STO C" + str(ord(instruction[2])) + " R" + str(ord(instruction[4])))
					
			if instruction[0] == chr(1): # if MUL
				print("MUL R" + str(ord(instruction[2])) + " R" + str(ord(instruction[4])) + " R" + str(ord(instruction[2])))
				
			if instruction[0] == chr(2): # if ADD
				print("ADD R" + str(ord(instruction[2])) + " R" + str(ord(instruction[4])) + " R" + str(ord(instruction[2])))
				
			if instruction[0] == chr(3): # if SUB
				print("SUB R" + str(ord(instruction[2])) + " R" + str(ord(instruction[4])) + " R" + str(ord(instruction[2])))
				
			if instruction[0] == chr(4): # if DIV
				print("DIV R" + str(ord(instruction[2])) + " R" + str(ord(instruction[4])) + " R" + str(ord(instruction[2])))
	
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
					
			if instruction[0] == chr(1): # if MUL
				mem[ord(instruction[2])] = mem[ord(instruction[2])] * mem[ord(instruction[4])]
				
			if instruction[0] == chr(2): # if ADD
				mem[ord(instruction[2])] = mem[ord(instruction[2])] + mem[ord(instruction[4])]
				
			if instruction[0] == chr(3): # if SUB
				mem[ord(instruction[2])] = mem[ord(instruction[2])] - mem[ord(instruction[4])]
				
			if instruction[0] == chr(4): # if DIV
				mem[ord(instruction[2])] = mem[ord(instruction[2])] / mem[ord(instruction[4])]
				
		return mem[0]
				


if __name__ == "__main__":
	expr = ExpressionCompiler("(x*x) + (y*y) + (6 * (5 + (8 * (2 + 9))))")
	result = expr.execute(5, 7)
	expr.printinstructions()
	print(result)

	
		

		
		
		
		
		
		

