import unittest

from PythonLabs.MARSLab import *

class MARSTest(unittest.TestCase):
    
    @classmethod
    def setUpClass(cls):
        print("\nMARSLab:  ", end = "")
        
    # Simulate normal instruction flow, branches, wraparound, thread start and stop

    def test_00_pc(self):
        pc = PC('demo', 0, 100)
        self.assertEqual(0, pc.next_instr(), "first address expected to be 0")
        self.assertEqual(0, pc.increment(), "should have fetched from 0")
        self.assertEqual(1, pc.increment(), "should have fetched from 1")
        
        pc.branch(10)
        self.assertEqual(10, pc.increment(), "wrong address after branch")
        self.assertEqual([0,1,10], pc._history, "inaccuracies in the historical record")
        
        pc.branch(99)
        self.assertEqual(99, pc.increment(), "should have fetched from 99 after branch")
        self.assertEqual(0, pc.increment(), "didn't wrap around at end of memory")
        
        pc.reset()
        self.assertEqual(0, pc.increment(), "first address expected to be 0 after reset")
        
        pc.add_thread(10)
        for i in range(4):  pc.increment()
        self.assertEqual([0, 1, 10, 2, 11], pc._history, "threads not interleaved")
        self.assertEqual(1, pc.kill_thread(), "should be only one thread after kill")
        self.assertEqual(3, pc.increment(), "should continue in first thread")
        self.assertEqual(4, pc.increment(), "should continue in first thread")
        self.assertEqual(0, pc.kill_thread(), "should be no more threads")
        self.assertEqual(None, pc.increment(), "should be nothing to fetch")

    # Assembling these instructions should lead to one error per line, and
    # no code generated.

    def test_01_errors(self):
        source = [
          "@label  mov #0, #1      ; label needs to be alphanumeric",
          "l@bel   mov #0, #1      ; label needs to be alphanumeric",
          "mov #0, #1              ; unlabeled line must start with space",
          "label @bogus #0, #1     ; opcode with non-alphanumeric",
          "label b@gus #0, #1      ; opcode with non-alphanumeric",
          "label muv #0, #1        ; unknown opcode",
          "   mov #b@gus, #1       ; messed up operand",
          "   mov #0 #1            ; missing comma",
          "  EQU 3                 ; missing label on pseudo-op",
          "x EQU 3x                ; arg not an integer",
          "  END foo               ; undefined label",
        ]

        name, code, symbols, errors = MARS.assemble(source)

        self.assertEqual(len(source), len(errors), "every line should generate an error")
        self.assertEqual(0, len(code), "should be no instructions generated")

    # A program from the ICWS archives -- has a wide variety of instructions, each
    # addressing mode, and a pseudo-op.  Should produce no errors, and one machine
    # instruction for each operation (inclduing DAT).

    def test_02_assembly(self):
        source = [
          ";redcode",
          ";name Mice",
          ";author Chip Wendell",
          ";strategy 1st place in ICWST'86",
          ";strategy replicator",
          ";assert 1",
          "PTR     DAT             #0",
          "START   MOV     #12    ,PTR",
          "LOOP    MOV     @PTR   ,<COPY",
          "        DJN     LOOP   ,PTR",
          "        SPL     @COPY  ,0",
          "        ADD     #653   ,COPY",
          "        JMZ     START  ,PTR",
          "COPY    DAT             #833",
          "        END     START",
        ]
        
        name, code, symbols, errors = MARS.assemble(source)

        self.assertEqual("Mice", name, "didn't find program name" )
        self.assertEqual(0, len(errors), "should be no syntax errors in this program" )
        self.assertEqual(8, len(code), "expected 8 instructions" )
        self.assertEqual(0, symbols["PTR"], "wrong label value" )
        self.assertEqual(1, symbols["START"], "wrong label value" )
        self.assertEqual(2, symbols["LOOP"], "wrong label value" )
        self.assertEqual(7, symbols["COPY"], "wrong label value" )

    # Assemble and run a synthetic program that has 4 MOV instructions.  Each
    # instruction uses a different addressing mode to find the data source, and
    # each copies its data to the same location.

    def test_03_modes(self):
        source = [
          "immed      mov #1, target        ; moves #1",
          "direct     mov dsrc, target      ; moves #2",
          "indir      mov @ptr, target      ; moves #3",
          "auto       mov <ptr2, target     ; moves #4, decrements ptr2",
          "target     dat #0, #0            ; place to store data",
          "dsrc       dat #2, #2            ; source for direct mode",
          "ptr        dat #0, isrc          ; a pointer to the indirect source",
          "isrc       dat #3, #3            ; source for indirect mode",
          "ptr2       dat #0, dummy         ; this pointer should be decremented",
          "           dat #4, #4            ; source for auto-decrement",
          "dummy      dat #0, #0            ; not used",
        ]

        name, code, symbols, errors = MARS.assemble(source)
        self.assertEqual(0, len(errors), "should be no syntax errors in this program" )
        target = symbols['TARGET']
        ptr2 = symbols['PTR2']

        m = MiniMARS(source)
        self.assertEqual("DAT #0 #0", str(m._mem.fetch(target)), "wrong value before first MOV")
        
        # value after MOV with immediate mode -- note only B field is copied
        m.step()
        self.assertEqual("DAT #0 #1", str(m._mem.fetch(target)))
        
        # value after MOV with direct mode -- note both A and B are moved
        m.step()
        self.assertEqual("DAT #2 #2", str(m._mem.fetch(target)))
        
        # value after MOV with indirect mode -- both A and B moved
        m.step()
        self.assertEqual("DAT #3 #3", str(m._mem.fetch(target)))
        
        # value of the pointer before the auto-decrement:
        self.assertEqual("DAT #0 2", str(m._mem.fetch(ptr2)))
        
        # value after MOV with auto-decrement mode -- both A and B moved
        m.step()
        self.assertEqual("DAT #4 #4", str(m._mem.fetch(target)))
        
        # value of the pointer after the auto-decrement:
        self.assertEqual("DAT #0 1", str(m._mem.fetch(ptr2)))

    # A DAT instruction is effectively a halt instruction.  Note that the
    # operands of a DAT are dereferenced, so the auto-decrement mode should
    # cause the pointer to decrement.

    def test_04_DAT(self):
        m = MiniMARS([" DAT #0, <1", " DAT #0, #1"])

        self.assertEqual("DAT #0 #1", str(m._mem.fetch(1)), "wrong pointer before dereference")
        m.step()
        self.assertEqual('halt', m._state, "machine didn't halt after executing DAT")
        self.assertEqual("DAT #0 #0", str(m._mem.fetch(1)), "wrong pointer after dereference")

    # Test the MOV instruction by executing the IMP program for two steps.  A
    # second test verifies a runtime error occurs if the second operand is immediate.
    
    def test_05_MOV(self):
        m = MiniMARS([" MOV 0, 1"], 10)
        m.step()
        m.step()
        self.assertEqual('continue', m._state, "machine halted?")
        self.assertEqual(2, m._pc.next_instr(), "wrong PC after MOV")
        self.assertEqual(str(m._mem.fetch(0)), str(m._mem.fetch(1)), "IMP didn't replicate")
        
        m = MiniMARS([" MOV 0, #1"])
        with self.assertRaises(MARSRuntimeException) as context:
            m.step()
        self.assertEqual(type(context.exception), MARSRuntimeException, "MOV immediate didn't raise exception")

    # ADD tests
    #   "ADD #A, dest" adds the constant A to the B field of dest
    #   "ADD src, dest" adds the A and B fields to src to the A and B of dest
    #   "ADD src, #B" is a runtime error (B can't be immediate)

    def test_06_ADD(self):
        source = [
        "     ADD #3,  sum",
        "     ADD  x,  y",
        "     ADD  x, #0",
        "sum  DAT #1, #2",
        "x    DAT #3, #4",
        "y    DAT #5, #6",
        ]

        m = MiniMARS(source)

        m.step()
        self.assertEqual("DAT #1 #5", str(m._mem.fetch(3)), "incorrect sum after ADD immediate")

        m.step()
        self.assertEqual("DAT #8 #10", str(m._mem.fetch(5)), "incorrect sum after ADD direct")

        with self.assertRaises(MARSRuntimeException) as context:
            m.step()
        self.assertEqual(type(context.exception), MARSRuntimeException, "ADD immediate didn't raise exception")

    # SUB tests -- same as ADD, but subtracting A from B

    def test_07_SUB(self):
        source = [
          "     SUB #3,  sum",
          "     SUB  x,  y",
          "     SUB  x, #0",
          "sum  DAT #1, #10",
          "x    DAT #3, #4",
          "y    DAT #5, #6",
        ]

        m = MiniMARS(source)

        m.step()
        self.assertEqual("DAT #1 #7", str(m._mem.fetch(3)), "incorrect sum after SUB immediate")

        m.step()
        self.assertEqual("DAT #2 #2", str(m._mem.fetch(5)), "incorrect sum after SUB direct")

        with self.assertRaises(MARSRuntimeException) as context:
            m.step()
        self.assertEqual(type(context.exception), MARSRuntimeException, "SUB immediate didn't raise exception")

    # JMP tests
    #     JMP x should set the program counter to x
    #     JMP #x is an error -- the operand can't be immediate

    def test_08_JMP(self):
        source = [
          "     JMP   x",
          "     DAT  #0, #0",
          "x    JMP  #0",
        ]

        m = MiniMARS(source)
        
        m.step()
        self.assertEqual(2, m._pc.next_instr(), "branch not taken")

        with self.assertRaises(MARSRuntimeException) as context:
            m.step()
        self.assertEqual(type(context.exception), MARSRuntimeException, "JMP immediate didn't raise exception")

    # JMZ tests
    #     JMZ x y should set the program counter to x if y is 0
    #     JMP #x y is an error -- the operand can't be immediate

    def test_09_JMZ(self):
        source = [
          "     JMZ   x, #1",
          "     JMZ   x, #0",
          "     DAT  #0, #0",
          "x    JMZ  #0, #0",
        ]

        m = MiniMARS(source)
        
        m.step()
        self.assertEqual(1, m._pc.next_instr(), "conditional branch taken")

        m.step()
        self.assertEqual(3, m._pc.next_instr(), "conditional branch not taken")

        with self.assertRaises(MARSRuntimeException) as context:
            m.step()
        self.assertEqual(type(context.exception), MARSRuntimeException, "JMZ immediate didn't raise exception")

    # JMN tests -- same as JMZ, but branch on non-zero

    def test_10_JMN(self):
        source = [
          "     JMN   x, #0",
          "     JMN   x, #1",
          "     DAT  #0, #0",
          "x    JMN  #0, #0",
        ]

        m = MiniMARS(source)
        
        m.step()
        self.assertEqual(1, m._pc.next_instr(), "conditional branch taken")

        m.step()
        self.assertEqual(3, m._pc.next_instr(), "conditional branch not taken")

        with self.assertRaises(MARSRuntimeException) as context:
            m.step()
        self.assertEqual(type(context.exception), MARSRuntimeException, "JMN immediate didn't raise exception")

    # DJN combines auto-decrement processing with a branch instruction.  As with
    # other branches, immediate mode is not allowed for the A operand.

    def test_11_DJN(self):
        source = [
          "     DJN   y, x",
          "     DJN   y, x",
          "x    DAT  #0, #1",
          "y    DJN  #0, #0",
        ]

        m = MiniMARS(source)

        m.step()
        self.assertEqual(1, m._pc.next_instr(), "conditional branch taken")

        m.step()
        self.assertEqual(3, m._pc.next_instr(), "conditional branch not taken")

        with self.assertRaises(MARSRuntimeException) as context:
            m.step()
        self.assertEqual(type(context.exception), MARSRuntimeException, "DJN immediate didn't raise exception")

    # CMP fetches the two operands and compares them; if they're the same
    # the next instruction is skipped.

    def test_12_CMP(self):
        source = [
            "     CMP   #1, x",    # don't skip
            "     CMP   #0, x",    # skip
            "     DAT   #0, #0",
            "     CMP   x,  y",    # don't skip
            "     CMP   x,  x",    # skip
            "     DAT   #0, #0",
            "     CMP   x,  #0",   # illegal
            "x    DAT  #0,  #0",
            "y    DAT  #0,  #1",
        ]

        m = MiniMARS(source)

        m.step()
        self.assertEqual(1, m._pc.next_instr(), "conditional branch taken")

        m.step()
        self.assertEqual(3, m._pc.next_instr(), "conditional branch not taken")

        m.step()
        self.assertEqual(4, m._pc.next_instr(), "conditional branch taken")

        m.step()
        self.assertEqual(6, m._pc.next_instr(), "conditional branch not taken")

        with self.assertRaises(MARSRuntimeException) as context:
            m.step()
        self.assertEqual(type(context.exception), MARSRuntimeException, "CMP immediate didn't raise exception")
        
    # In our implementation SLT only works for immediate A operands.  Skip the
    # next instruction if A is less than the A-field of the dereferenced B operand.

    def test_13_SLT(self):
        source = [
            "     SLT   #3, x",    # don't skip
            "     SLT   #1, x",    # skip
            "     DAT   #0, #0",
            "     SLT    x, z",    # don't skip
            "     SLT    z, x",    # skip
            "     DAT   #0, #0",
            "     SLT   #0, #0",   # illegal B operand
            "x    DAT   #2",
            "z    DAT   #0",
        ]

        m = MiniMARS(source)

        m.step()
        self.assertEqual(1, m._pc.next_instr(), "conditional branch taken")

        m.step()
        self.assertEqual(3, m._pc.next_instr(), "conditional branch not taken")

        m.step()
        self.assertEqual(4, m._pc.next_instr(), "conditional branch taken")

        m.step()
        self.assertEqual(6, m._pc.next_instr(), "conditional branch not taken")

        with self.assertRaises(MARSRuntimeException) as context:
            m.step()
        self.assertEqual(type(context.exception), MARSRuntimeException, "SLT immediate didn't raise exception")
    
    # SPL forks a new thread that starts execution at the address specified by A.
    # The pc object maintains a list of locations, with one location per thread.
    # After the split in this test, the location list should have 2 items, one the
    # continuation of the original thread and the other the first instruction in
    # the new thread.

    def test_14_SPL(self):
        source = [
            "     SPL   x",
            "     DAT   #0, #0",    # space filler
            "     DAT   #0, #0",
            "x    MOV   0,  1",
        ]

        # TODO: threads can't be tested with MiniMARS -- run this program in main machine

        # m = MiniMARS(source)
        # m.step()
        # self.assertEqual([1,3], m._pc._addrs, "didn't split")

    # The program counter object should have a history of memory references for each
    # thread.  m._pc.history() is the history vector for thread i in machine m

    def test_15_threads(self):
        source = [
            "     MOV   x, y",      # should log source and target references
            "     SPL   z",         # start new thread
            "     ADD   x, y",      # first thread logs two memory references
            "     DAT   #0",        # first thread halts
            "z    SUB   x, y",      # second thread logs two memory references
            "     DAT   #0",        # second thread halts
            "x    DAT   #1",
            "y    DAT   #0",
        ]

        # TODO: threads can't be tested with MiniMARS -- run this program in main machine
        
        # m = MiniMARS(source)
        # self.assertEqual(1, len(m._pc.history()), "should have only one thread")
        # self.assertEqual([], m._pc.history()[0])

        # m.step()
        # self.assertEqual([0,6,7], m._pc.history()[0], "MOV didn't log instr and both operands")

        
    # The code that loads programs needs to reserve a buffer before and after the code
    # and also deal with potential wraparounds on either side
    
    def test_16_reserve_memory(self):
        MARS_runtime_options['buffer'] = 10
        
        MARS.use_loc(500,10)
        self.assertEqual( [(490, 519)], MARS.mem_used, "block not allocated in right location")

        del MARS.mem_used[:]
        MARS.use_loc(5,10)
        self.assertEqual( [(0, 24),(4091, 4095)], MARS.mem_used, "block start did not wrap around")

        del MARS.mem_used[:]
        MARS.use_loc(4090,10)
        self.assertEqual( [(4080, 4095),(0, 13)], MARS.mem_used, "block end did not wrap around")
  