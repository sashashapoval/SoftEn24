# MARS (Memory Array Redcode Simulator) -- a virtual machine for Corewar

# __all__ = [ ]

from math import sqrt
from copy import copy
from random import randint
import re
import os
import PythonLabs
from .Canvas import Canvas
from .Tools import classname, path_to_data

## Error types for this module

class MARSError(Exception):  pass
class MARSRuntimeException(Exception):  pass
class RedcodeSyntaxError(Exception):  pass

## Program counter objects have a thread id and a memory location

class PC:
    """
    [MARSLab] The PC (program counter) class is used to keep track of the next instruction 
    to execute when a program is running.  A PC object has an array of locations to hold 
    the next instruction from each thread, plus the index of the thread to use on the next
    instruction fetch cycle.
    """
    
    def __init__(self, tag, addr, memsize, hmax = 10):
        """
        [MARSLab] Create a new program counter.  The tag argument is a string that can be 
        used to identify which program is running at this location.  The PC is intialized 
        with one thread starting at location addr.  The hmax argument is the number of 
        items to save in the history array (used in visualization).
        """
        self._tag = tag
        self._addrs = [addr]
        self._memsize = memsize
        # self._history = [ [] ]
        self._history = [ ]
        self._thread = 0
        self._current = {'thread' : None, 'addr' : None}
        self._first = addr
        self._hmax = hmax
        
    def __repr__(self):
        # s = "<" + classname(self) + " "
        s = "[ "
        for (i, loc) in enumerate(self._addrs):
            if i == self._thread:  s += '*'
            s += str(loc)
            s += ' '
        s += "]"
        return s
        
    def reset(self):
        """
        [MARSLab] Restore this program counter to its original state, a single thread starting
        at the location passed when the object was created.
        """
        self._addrs = [self._first]
        # self._history = [ [] ]
        self._history = [ ]
        self._thread = 0
        self._current = {'thread' : None, 'addr' : None}
        return self._first
        
    def next_instr(self):
        """
        [MARSLab] Return the address of the next instruction to execute for this program.
        """
        if len(self._addrs) == 0:  return None
        return self._addrs[self._thread]

    def increment(self):
        """
        [MARSLab] Return the address of the instruction to execute and update the PC.
        If more than one thread is active, make the next thread the current thread.
        """
        if len(self._addrs) == 0:  return None
        addr = self._addrs[self._thread]
        self.log(addr)
        self._current['thread'] = self._thread
        self._current['addr'] = addr
        self._addrs[self._thread] = (self._addrs[self._thread] + 1) % self._memsize
        self._thread = (self._thread + 1) % len(self._addrs)
        return addr
        
    def branch(self, loc):
        """
        [MARSLab] Implement a branch instruction by setting the next instruction address 
        for the current thread to loc.
        """
        self._addrs[self._current['thread']] = loc
        
    def add_thread(self, addr):
        """
        [MARSLab] Add a new thread, which will begin execution at location addr.
        """
        self._addrs.append(addr)
        # self._history.append([])
        # self
        
    def kill_thread(self):
        """
        [MARSLab] Remove the current thread from the list of active threads.  The return 
        value is the number of remaining threads.
        """
        if len(self._addrs) == 0:  return 0 
        self._addrs.pop(self._current['thread'])
        # self._history.pop(self._current['thread'])
        self._thread -= 1
        return len(self._addrs)
        
    def log(self, loc):
        """
        [MARSLab] Record the location of a memory operation in the history vector for the 
        current thread.  The history vector is used by the methods that display the progress 
        of a program on the PythonLabs canvas.
        """
        # a = self._history[self._current['thread']]
        # a.append(loc)
        # if len(a) > self._hmax:  a.pop(0)
        self._history.append(loc)
        if len(self._history) > self._hmax:  self._history.pop(0)

        
## Memory objects hold MARS instructions and data

class Memory:
    """
    [MARSLab] An object of the Memory class is a 1-D array of the specified size.  Items 
    in a Memory are Word objects.

    According to the Corewar standard, memory should be initialized with DAT #0 instructions
    before each contest.  For efficiency, newly (re)initialized Memory objects have None
    at each location, but  is treated the same as DAT #0.
    """
    
    def __init__(self, size):
        """
        [MARSLab] Create a new memory with the specified number of words. According to the 
        Corewar standard, memory should be initialized with DAT #0 instructions before each 
        contest.  For efficiency, newly (re)initialized Memory objects have None at each 
        location, but None is converted to DAT #0 by the fetch method.
        """
        self._array = [None] * size
        
    def __repr__(self):
        return "<%s [0..%d]>" % (classname(self), len(self._array)-1)
        
    def dump(self, loc, n):
        "[MARSLab] # Print the n words in memory starting at loc."
        pass
        
    def size(self):
        "[MARSLab] Return the size of this Memory object (number of words that can be stored)."
        return len(self._array)
        
    def fetch(self, loc):
        "[MARSLab] Return the Word object stored in location loc in this Memory object."
        if self._array[loc]:
            return self._array[loc]
        else:
            return Word('DAT', '#0', '#0')
            
    def store(self, loc, val):
        "[MARSLab] Store val (a Word object) in location loc in this memory."
        self._array[loc] = copy(val)
        
    def fetch_field(self, loc, field):
        """
        [MARSLab] Same as fetch, but return only the designated field of the Word stored 
        at location loc.
        """
        word = self.fetch(loc)
        return word._a if field == 'a' else word._b
        
    def store_field(self, loc, val, field):
        """
        [MARSLab] Same as store, but overwrite only the designated field of the Word in 
        location loc, preserving the same addressing mode as the original.
        """
        word = self.fetch(loc)
        part = word._a if field == 'a' else word._b
        mode = part[0] if re.match(r'[@<#]', part) else ''
        if field == 'a':
            word._a = mode + str(val)
        else:
            word._b = mode + str(val)
        self.store(loc, word)


## Word 

# An object of the Word class represents a single item from memory, either a machine 
# instruction or a piece of data.  Attributes are the opcode, the A operand mode, and 
# the B operand (all strings).  Instruction execution proceeds according to the description 
# in Durham's spec.

class Word:
    """docstring for Word"""
    
    def __init__(self, op = 'DAT', a = '#0', b = '#0', lineno = None):
        if op in Word._optable:
            self._op = op
            self._a = a
            self._b = b
            self._lineno = lineno
            self._func = Word._optable[op]
        else:
            raise MARSError("Unknown opcode: " + str(op))

    def __repr__(self):
        return "%s %s %s" % (self._op, self._a, self._b)
        
    @staticmethod
    def field_value(field):
        if re.match(r'[@<#]', field):
            return int(field[1:])
        else:
            return int(field)
    
    @staticmethod
    def dereference(field, pc, mem):
        """
        [MARSLab] Return the address of an operand; note that for immediate operands 
        the address is the address of the current instruction.
        """
        if field[0] == '#':
          return pc._current['addr']
        elif field[0] == '@':
          ptrloc = (Word.field_value(field) + pc._current['addr']) % mem.size()
          ptr = mem.fetch(ptrloc)
          return (Word.field_value(ptr._b) + ptrloc) % mem.size()
        elif field[0] == '<':
          ptrloc = (Word.field_value(field) + pc._current['addr']) % mem.size()
          ptr = mem.fetch(ptrloc)
          newb = Word.field_value(ptr._b) - 1
          mem.store_field(ptrloc, (newb % mem.size()), 'b')
          return (newb + ptrloc) % mem.size()
        else:
          return (Word.field_value(field) + pc._current['addr']) % mem.size()
        end

    def execute(self, pc, mem):
        self._func(self, pc, mem)
        return 'halt' if self._op == 'DAT' else 'continue'
        
    # The DAT instruction is effectively a "halt", but we still need to dereference
    # both its operands to generate the side effects in auto-decrement modes.

    def DAT(self, pc, mem):
        Word.dereference(self._a, pc, mem)
        Word.dereference(self._b, pc, mem)

    # Durham isn't clear on how to handle immediate moves -- does the immediate value
    # go in the A or B field of the destination?  Guess:  B, in case the destination
    # is a DAT.

    def MOV(self, pc, mem):
        if self._b[0] == '#':
            raise MARSRuntimeException("MOV: immediate B-field not allowed")
        src = Word.dereference(self._a, pc, mem)
        val = mem.fetch(src)
        dest = Word.dereference(self._b, pc, mem)
        if self._a[0] == '#':
            mem.store_field(dest, Word.field_value(val._a), 'b')
        else:
            mem.store(dest, val)
        # pc.log(src)
        pc.log(dest)

    # Ambiguity on how to handle immediate A values:  add operand to the A or B
    # field of the destination?  Guess:  B (for same reasons given for MOV)

    def ADD(self, pc, mem):
        if self._b[0] == '#':
            raise MARSRuntimeException("ADD: immediate B-field not allowed")
        src = Word.dereference(self._a, pc, mem)
        left_operand = mem.fetch(src)
        dest = Word.dereference(self._b, pc, mem)
        right_operand = mem.fetch(dest)
        if self._a[0] == '#':
            mem.store_field(dest, Word.field_value(left_operand._a) + Word.field_value(right_operand._b), 'b')
        else:
            mem.store_field(dest, Word.field_value(left_operand._a) + Word.field_value(right_operand._a), 'a')
            mem.store_field(dest, Word.field_value(left_operand._b) + Word.field_value(right_operand._b), 'b')
            # pc.log(src)
        pc.log(dest)

    # See note for ADD, re immediate A operand.

    def SUB(self, pc, mem):
        if self._b[0] == '#':
            raise MARSRuntimeException("SUB: immediate B-field not allowed")
        src = Word.dereference(self._a, pc, mem)
        right_operand = mem.fetch(src)
        dest = Word.dereference(self._b, pc, mem)
        left_operand = mem.fetch(dest)
        if self._a[0] == '#':
            mem.store_field(dest, Word.field_value(left_operand._b) - Word.field_value(right_operand._a), 'b')
        else:
            mem.store_field(dest, Word.field_value(left_operand._a) - Word.field_value(right_operand._a), 'a')
            mem.store_field(dest, Word.field_value(left_operand._b) - Word.field_value(right_operand._b), 'b')
            # pc.log(src)
        pc.log(dest)

    # Durham doesn't mention this explicitly, but since a B operand is allowed it implies
    # we have to dereference it in case it has a side effect.

    def JMP(self, pc, mem):
        if self._a[0] == '#':
            raise MARSRuntimeException("JMP: immediate A-field not allowed")
        target = Word.dereference(self._a, pc, mem) % mem.size()
        Word.dereference(self._b, pc, mem)
        pc.branch(target)

    # Branch to address specified by A if the B-field of the B operand is zero.

    def JMZ(self, pc, mem):
        if self._a[0] == '#':
            raise MARSRuntimeException("JMZ: immediate A-field not allowed")
        target = Word.dereference(self._a, pc, mem) % mem.size()
        operand = mem.fetch(Word.dereference(self._b, pc, mem))
        if Word.field_value(operand._b) == 0:
            pc.branch(target)

    # As in JMZ, but branch if operand is non-zero

    def JMN(self, pc, mem):
        if self._a[0] == '#':
            raise MARSRuntimeException("JMZ: immediate A-field not allowed")
        target = Word.dereference(self._a, pc, mem) % mem.size()
        operand = mem.fetch(Word.dereference(self._b, pc, mem))
        if Word.field_value(operand._b) != 0:
            pc.branch(target)

    # DJN combines the auto-decrement mode dereference logic with a branch -- take
    # the branch if the new value of the B field of the pointer is non-zero.

    def DJN(self, pc, mem):
        if self._a[0] == '#':
            raise MARSRuntimeException("JMZ: immediate A-field not allowed")
        target = Word.dereference(self._a, pc, mem) % mem.size()
        operand_addr = Word.dereference(self._b, pc, mem)
        operand = mem.fetch(operand_addr)
        newb = Word.field_value(operand._b) - 1
        mem.store_field(operand_addr, (newb % mem.size()), 'b')
        if newb != 0:
            pc.branch(target)
        pc.log(operand_addr)

    # Durham just says "compare two fields" if the operand is immediate.  Since
    # B can't be immediate, we just need to look at the A operand and, presumably,
    # compare it to the A operand of the dereferenced operand fetched by the B field.
    # If A is not immediate compare two full Words -- including op codes.  
    # The call to pc.increment increments the program counter for this thread, which causes 
    # the skip.

    def CMP(self, pc, mem):
        if self._b[0] == '#':
            raise MARSRuntimeException("SUB: immediate B-field not allowed")
        right = mem.fetch(Word.dereference(self._b, pc, mem))
        if self._a[0] == '#':
            left = Word.field_value(self._a)
            right = Word.field_value(right._a)
        else:
            left = mem.fetch(Word.dereference(self._a, pc, mem))
        if left == right:
            pc.increment()

    # More ambiguity here -- what does it mean for a word A to be "less than"
    # word B?  First assumption, don't compare opcodes.  Second, we're just going
    # to implement one-field comparisons of B fields.  Otherwise for full-word operands
    # we'd need to do a lexicographic compare of A and B fields of both operands, skipping
    # modes and just comparing values.

    def SLT(self, pc, mem):
        if self._b[0] == '#':
            raise MARSRuntimeException("SUB: immediate B-field not allowed")
        if self._a[0] == '#':
            left = Word.field_value(self._a)
        else:
            left = Word.field_value(mem.fetch(Word.dereference(self._a, pc, mem))._b)
        right = Word.field_value(mem.fetch(Word.dereference(self._b, pc, mem))._b)
        if left < right: 
            pc.increment()

    # Fork a new thread at the address specified by A.  The new thread goes at the end
    # of the queue.  Immediate operands are not allowed.  Durham doesn't mention it, but
    # implies only A is dereferenced, so ignore B.

    def SPL(self, pc, mem):
        if self._a[0] == '#':
            raise MARSRuntimeException("JMZ: immediate A-field not allowed")
        target = Word.dereference(self._a, pc, mem)
        pc.add_thread(target)
        
    _optable = {
        'DAT' : DAT,
        'MOV' : MOV,
        'ADD' : ADD,
        'SUB' : SUB,
        'JMP' : JMP,
        'JMZ' : JMZ,
        'JMN' : JMN,
        'DJN' : DJN,
        'CMP' : CMP,
        'SLT' : SLT,
        'SPL' : SPL,
    }

## Warrior class

class Warrior:
    """
    [MARSLab] A Warrior is an assembled Redcode program ready to be loaded into memory 
    and run.  An object of this class is a simple struct that has the program name, code, 
    starting location, and symbol table of an assembled program.
    """
    
    def __init__(self, prog):
        """
        Call the assembler to create the code and symbol table for a program.  The argument
        is either a list of instructions or the name of a file containing the instructions.
        """
        if type(prog) == str:
            # if prog[0] == ':':
            #     prog = os.path.join(PythonLabs.datadir, "mars", prog[1:])
            with open(prog) as progfile:
                self._name, self._code, self._symbols, self._errors = MARS.assemble(progfile)
        else:
            self._name, self._code, self._symbols, self._errors = MARS.assemble(prog)
        if len(self._errors) > 0:
            print("Syntax errors:")
            for s in self._errors:
                print(s)
            self._code = []
    
    def __repr__(self):
        s = "<" + classname(self)
        s += " name: %s" % self._name
        s += " instructions: %d" % len(self._code)
        s += ">"
        return s
    

## Top level MARS class.

# This class defines a singleton object.  Attributes are the system memory, an
# array of PC objects (one per competing program), and descriptions of the competing
# programs.  

# Static methods are used to assemble, load, and execute programs.  Functions that have
# names starting with underscores are helpers, not intended to be called directly by
# users.

# Note: memory size and memory layout is fixed at compile time.  Attributes are defined
# as symbolic names but they should not be modified...

_cell_rows = 32
_cell_cols = 128
_memsize = _cell_rows * _cell_cols 
_maxentries = 3

_default_view_options = {           # actual options saved in MARS.view_options when
    'cellSize' : 8,                 # display is initialized
    'padding' : 20,
    'traceSize' : 10,
    'emptyCellColor' : '#EEEEEE',
    'cellColor' : '#CCCCCC',
}

MARS_runtime_options = {            # users may access and possible modify these options
    'maxRounds' : 1000,
    'buffer' : 100,
    'tracing' : False,
    'pause' : 0.01,
}

Canvas.delay = 0.01

class MARSView:
    def __init__(self, cells, palettes, options):
        self.cells = cells
        self.palettes = palettes
        self.options = options

class MARS:
    
    memory = Memory(_memsize)           # an array of Word objects
    pcs = [ ]                           # one PC (program counter) per active program
    entries = [ ]                       # one Warrior project for each program loaded
    mem_used = [ ]                      # set of memory segments used by loaded programs
    
    _opcodes = ("DAT", "MOV", "ADD", "SUB", "JMP", "JMZ", "JMN", "DJN", "CMP", "SPL", "END", "SLT", "EQU")
    _max_entries = 3
    
    def __init__(self):
        """don't do this"""
        raise MARSError("MARS is a singleton object")
    
    # Parsing methods strip off and return the item they are looking for, or raise
    # an error if the line doesn't start with a well-formed item

    # Labels start in column 0, can be any length
    
    def _parse_label(s):
        if s.startswith((' ', '\t')):
            return (None, s)
        m = re.match(r'\w+', s)
        if m == None:
            raise RedcodeSyntaxError("illegal label in '%s'" % s)
        label = s[0:m.end()]
        if label in MARS._opcodes:
            raise RedcodeSyntaxError("can't use opcode '%s' as a label" % s)
        return (label, s[m.end():])
        
    # Expect opcodes to be separated from labels (or start of line) by white space
    
    def _parse_opcode(s):
        if not s.startswith((' ', '\t')): 
            raise RedcodeSyntaxError("illegal label in '%s'" % s)
        s = s.lstrip(' \t')
        m = re.match(r'\w+', s)
        if m == None:
            raise RedcodeSyntaxError("illegal opcode in '%s'" % s)
        opcode = s[0:m.end()].upper()
        if not opcode in MARS._opcodes:
            raise RedcodeSyntaxError("unknown opcode: '%s'" % opcode)
        return (opcode, s[m.end():])
    
    # Operands have an optional addressing mode character
    
    def _parse_operand(s):
        s = s.lstrip(' \t')
        if len(s) == 0:
            return ('', '')
        m = re.match(r'[@<#]?[+-]?\w+', s)
        if m == None:
            raise RedcodeSyntaxError("illegal operand in '%s'" % s)
        operand = s[0:m.end()]
        return (operand.upper(), s[m.end():])
    
    # Operands are separated by a comma
    
    def _parse_separator(s):
        s = s.lstrip(' \t')
        if len(s) == 0:
            return ('', '')
        if s[0] != ',':
            raise RedcodeSyntaxError("operands must be separated by a comma in '%s'" % s)
        return (',', s[1:])
        
    # On pass 2, translate labels into integers
    
    def _translate(s, symbols, loc):
        if len(s) == 0:
            return '#0'
        if re.match(r'[@<#]', s):
            mode = s[0]
            sym = s[1:]
        else:
            mode = ''
            sym = s
        if re.match(r'[+-]?\d+$', sym):
            return mode + sym
        elif sym in symbols:
            return mode + str(symbols[sym] - loc)
        else:
            raise RedcodeSyntaxError("unknown/illegal label: %s" % sym)  
    
    # Top level parser, called for each line in a file
    
    def parse(s):
        """
        [MARSLab] Helper method called by the assembler to break an input line into its constituent
        parts.  Calls its own helpers named parse_label, parse_opcode, and parse_operand.
        """
        label, s = MARS._parse_label(s)
        op, s = MARS._parse_opcode(s)
        a, s = MARS._parse_operand(s)
        x, s = MARS._parse_separator(s)
        b, s = MARS._parse_operand(s)
        return (label, op, a, b)
        
    def assemble(strings):
        """
        [MARSLab] A simple two-pass assembler for Redcode.  The input is an array of strings read
        from a file.  The result of the call is a tuple of 4 items:  
           the name of the program (if there was a name pseudo-op in the source code)
           the assembled code, in the form of a list of Word objects
           a dictionary with labels and their values
           a list of error messages
        """
        code = []
        symbols = {}
        errors = []
        name = "unknown" + str(len(MARS.entries))
        
        symbols[':start'] = 0            # default starting address
        
        # Pass 1 -- Create a list of Word objects, build the symbol table
        
        for (lineno, line) in enumerate(strings):
            line = line.rstrip()
            if len(line) == 0:  continue
            if line[0] == ';':          # extract metadata before skipping comment line
                m = re.match(r';\s*name\s+(\w+)', line)
                if m:
                    name = m.group(1)
                continue
            n = line.find(';')          # strip comments from the end of the line
            if n > 0:
                line = line[0:n]
            try:
                label, op, a, b = MARS.parse(line)
                if op == 'EQU':         # rhs of EQU command can only be an integer
                    if label == None:
                        raise RedcodeSyntaxError("EQU must have a label")
                    if re.match(r'^[+-]?\d+$', a):
                        symbols[label.upper()] = int(a)
                    else:
                        raise RedcodeSyntaxError("EQU operand must be an integer")
                elif op == 'END':       # if END pseudo-op has label it must be defined previously
                    if len(a) > 0:
                        if a in symbols:
                            symbols[':start'] = symbols[a]
                        else:
                            raise RedcodeSyntaxError("unknown operand in END: %s" % a)
                else:
                    if label:
                        symbols[label.upper()] = len(code)
                    code.append(Word(op, a, b, lineno + 1))
            except RedcodeSyntaxError as e:
                errors.append("  line %d: %s" % (lineno + 1, e.args[0]))
        
        # Pass 2 -- translate labels into ints on each instruction
        
        for (loc, instr) in enumerate(code):
            if instr._op == 'DAT' and len(instr._b) == 0:       # if DAT has only one operand
                instr._a, instr._b = instr._b, instr._a         # it needs to be the B operand
            try:
                instr._a = MARS._translate(instr._a, symbols, loc)
                instr._b = MARS._translate(instr._b, symbols, loc)
            except RedcodeSyntaxError as e:
                errors.append("  line %d: %s" % (loc, e.args[0]))
                
        return name, code, symbols, errors

    def check_loc(lb, ub):
        """
        [MARSLab] See if the range of addresses between lb and ub overlap any of the
        memory segments currently in use.
        """
        for (i, j) in MARS.mem_used:
            if not (ub < i or lb > j):  return False
        return True
        
    def use_loc(addr, n):
        """
        [MARSLab] Reserve memory locations for a program of size n being loaded into
        addr.  The runtime parameter named 'buffer' is an amount to reserve on either
        size of the program, e.g. if 'buffer' is 10 and the request is to load a 5-word
        program into location 100 reserve locations 90 to 115. If the request extends
        past the end of memory add two segments to the mem_used list, one at the end
        of memory and one for the wraparound.
        """
        buf = MARS_runtime_options['buffer']
        lb = addr - buf
        ub = addr + n + buf - 1
        if lb < 0:
            MARS.mem_used.append( (0, ub) )
            MARS.mem_used.append( (_memsize + lb, _memsize - 1) )
        elif ub >= _memsize:
            MARS.mem_used.append( (lb, _memsize - 1) )
            MARS.mem_used.append( (0, ub - _memsize) )
        else:
            MARS.mem_used.append( (lb, ub) )
        
        
    def load(prog, addr = None):
        """
        [MARSLab] Load a program (either a list of Redcode instructions or a text file)
        into a random location in the main MARS machine's memory.  If no address is
        specified the program is loaded into a random address sufficiently far from
        any other program currently in memory.
        """
        slot = len(MARS.entries)
        
        if slot == _maxentries:
            print("Maximum number of entries (%d) already loaded" % _maxentries)
            return None
        
        w = Warrior(prog)
        
        if len(w._code) > _memsize // 4:
            print("Exceeds maximum program size (%d); code not loaded" % _memsize // 4)
            return None
        
        if addr is not None:
#             if not MARS.check_loc(addr, addr + len(w._code)):
#                 print("Too close to another program; choose a different address")
#                 return None
            pass
        else:
            while True:
                addr = randint(0, _memsize-1)
                if MARS.check_loc(addr, addr + len(w._code)):  break
        
        w._start = addr
        addrlist = []
        MARS.use_loc(addr, len(w._code))
        for (i, instr) in enumerate(w._code):
            MARS.memory.store(addr+i, instr)
            addrlist.append(addr+i)
        
        MARS.entries.append(w)
        MARS.pcs.append( PC(w._name, addr+w._symbols[':start'], _memsize) )
        if Canvas.view:
            MARS.update_cells(addrlist, slot)
        
        return w
        
    def alive(i):
        """
        [MARSLab] Return True if program i is still alive.
        """
        if i < len(MARS.entries):
            if len(MARS.pcs[i]._addrs) > 0:
                return True
        return False
        
    def num_alive():
        """
        [MARSLab] Return the number of programs that are still alive.
        """
        n = 0
        for pc in MARS.pcs:
            if len(pc._addrs) > 0:  n += 1
        return n
        
    def status():
        """
        [MARSLab] Print information about programs loaded into memory.
        """
        if len(MARS.entries) == 0:
            print("No programs loaded")
        for (i, w) in enumerate(MARS.entries):
            print("%-10s: %4d..%-4d  PC: %s" % (w._name, w._start, w._start+len(w._code)-1, str(MARS.pcs[i])))
    
    def step():
        """
        [MARSLab] Execute one instruction from each program.  Each program has its
        own PC object.  A PC manages threads internally -- a call to pc.increment
        gets the address of the next instruction in the current thread switches to
        the next thread.  The call to increment returns None if there are no surviving
        threads.
        """
        if len(MARS.entries) == 0:
            print("No programs loaded")
            return 0
                
        for (i, pc) in enumerate(MARS.pcs):
            addr = pc.increment()
            if addr != None:
                instr = MARS.memory.fetch(addr)
                # print(i, addr, ":", instr)
                try:
                    state = instr.execute(pc, MARS.memory)
                except MARSRuntimeException as e:
                    print("Program %s at address %d: %s" % (MARS.entries[i]._name, addr, e.args[0]))
                    state = 'halt'
                if state == 'halt':
                    pc.kill_thread()
                    if Canvas.view:
                        MARS.blacken_cell(addr)
                elif Canvas.view:
                    MARS.update_cells(pc._history, i)
        if Canvas.view:
            Canvas.update()

    def run(nsteps = None, single = False):
        """
        [MARSLab] Run all programs for the specified number of steps (if the argument
        is None the number of steps is the runtime option named maxRounds).  In the
        default mode (single = False) execution stops early if the number of surviving 
        programs drops to 1, i.e. one program has won the war.  To continue running
        a single program (e.g. for debugging) set single to True.
        """
        if nsteps == None:
            nsteps = MARS_runtime_options['maxRounds']
        minsurvivors = 1 if single else 2
        while nsteps > 0 and MARS.num_alive() >= minsurvivors:
            MARS.step()
            nsteps -= 1
        if nsteps > 0:
            return "halted"

    def reset():
        """
        [MARSLab] Clear all the programs from memory.
        """
        MARS.memory = Memory(_memsize)
        MARS.pcs = [ ]
        MARS.entries = [ ]
        MARS.mem_used = [ ]
        if Canvas.view:
            MARS.view(**Canvas.view.options)

    def view(**view_options):
        """
        [MARSLab] Initialize the canvas with a drawing of the MARS VM main memory.  The
        display will show one rectangle for each memory cell.  When a core warrior is 
        loaded into memory, the rectangles for the cells it occupies will change color,
        with a different color for each contestant.  As a program runs, any memory cells
        it references will be filled with that program's color.  To keep the screen from
        having too much color, cells gradually fade back to gray.
        """
        options = dict(_default_view_options)
        options.update(view_options)
        
        cellsize = options['cellSize']
        padding = options['padding']
        
        width = cellsize * _cell_cols + 3 * padding
        height = cellsize * _cell_rows + 3 * padding
        
        Canvas.init(width, height, "MARS (Memory Array Redcode Simulator)")

        cells = []
        for i in range(_memsize):
            x = (i % _cell_cols) * cellsize + padding
            y = (i // _cell_cols) * cellsize + padding
            cells.append(Canvas.Rectangle( x, y, x+cellsize, y+cellsize, outline = "#888888", fill = options['emptyCellColor'] )) 
        
        palettes = [
            Canvas.palette( (204,204,204), (204,100,100), options['traceSize']-2 ), 
            Canvas.palette( (204,204,204), (100,100,204), options['traceSize']-2 ),
            Canvas.palette( (204,204,204), (100,204,100), options['traceSize']-2 ),
        ]
        palettes[0].append("#FF0000")
        palettes[1].append("#0000FF")
        palettes[2].append("#00FF00")
        
        view = MARSView(cells, palettes, options)
        Canvas.register(view)
        
        return view
        
    def close_view():
        "[MARSLab] Close the MARS visualization window."
        Canvas.close()
        
    def update_cells(a, t):
        """
        [MARSLab] Update the colors of the cells for addresses in list a using the color
        palette for thread t.
        """
        # a.append(MARS.pcs[t].next_instr())
        palette = Canvas.view.palettes[t]
        d = len(palette) - len(a)
        for (ax, addr) in enumerate(a):
            cell = Canvas.view.cells[addr]
            px = max(0, ax + d)
            Canvas.drawing.itemconfigure(cell.id, fill = palette[px])
            
    def blacken_cell(addr):
        """
        [MARSLab] A thread just died; color its cell black in the display.
        """
        cell = Canvas.view.cells[addr]
        Canvas.drawing.itemconfigure(cell.id, fill = 'black')
        
## MiniMARS

class MiniMARS(object):
    """
    [MARSLab] A miniature machine (MiniMARS) object is used to test a Redcode program.  It 
    is essentially a MARS VM connected to a "thumb drive" that contains the assembled code 
    for a single program.  By single-stepping through the program users can learn how the 
    code works or debug a program they are developing.
    """
    
    def __init__(self, prog, size = None):
        """
        Load the program (arg is either a list of instructions or the name of a file), create
        the memory (by default just big enough to hold the program), initialize the PC.
        """
        w = Warrior(prog)
        if size == None:
            self._mem = Memory(len(w._code))
        else:
            self._mem = Memory(size)
        for (loc, word) in enumerate(w._code):
            self._mem.store(loc, word)
        self._pc = PC(w._name, w._symbols[':start'], self._mem.size())
        self._state = 'ready'
        
    def __repr__(self):
        s = "<" + classname(self)
        s += " name: %s" % self._pc._tag
        s += " PC: %d" % self._pc.next_instr()
        s += " status: %s" % self._state
        s += ">"
        return s
        
    def dump(self, startloc = 0, endloc = -1):
        """
        [MARSLab] Print the state of the machine, including a listing of the code with a
        pointer to the next instruction to execute.
        """
        if endloc == -1:
            endloc = self._mem.size()-1
#         print(self)
#         for i in range(self._mem.size()):
        for i in range(startloc, endloc+1):
            mark = ">" if i == self._pc.next_instr() else " "
            print(" %s%02d: %s" % (mark, i, str(self._mem.fetch(i))))
    
    def step(self):
        """
        [MARSLab] Execute the next instruction in the program loaded into this VM.  The
        return value is the Word object for the instruction that was executed.
        """
        if self._state == 'halt':
#             raise MARSRuntimeException("MiniMARS program has halted")
            return 'machine halted'
        instr = self._mem.fetch(self._pc.increment())
        if instr._op == 'SPL':
            raise MARSRuntimeException("MiniMARS programs are single-threaded")
        self._state = instr.execute(self._pc, self._mem)
        return instr
        
    def run(self, nsteps = 1000):
        """
        [MARSLab] Execute instructions in the program loaded into this VM until it hits
        a HALT (DAT) instruction.  The return value is the number of instructions
        executed. The optional argument is a maximum number of steps to execute; afer 
        executing this number of instructions the method will return, whether or not the 
        program has halted.
        """
        count = 0
        for i in range(nsteps):
            if self._state == 'halt':  break
            self.step()
            count += 1
        return count
        
## Utilities

    