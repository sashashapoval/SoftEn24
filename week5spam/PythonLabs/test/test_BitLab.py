import unittest

from PythonLabs.BitLab import *

class BitTest(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        print("\nBitLab:  ", end = "")

    def test_01_binary_codes(self):
        "Code(n) is the binary encoding of the integer n"
        
        # test a code that has the default length
        x = Code(15)
        self.assertEqual('1111', str(x), "wrong binary code for 15")
        self.assertEqual(4, len(x), "wrong length in binary code for 15")
        self.assertEqual(15, int(x), "wrong value of binary code for 15")
        self.assertEqual(Code, type(x), "wrong type for binary code for 15")

        # test code padded with leading 0s
        x = Code(15,6)
        self.assertEqual('001111', str(x), "wrong 6-digit code for 15")
        self.assertEqual(6, len(x), "wrong length in 6-digit code")
        self.assertEqual(15, int(x), "wrong value of 6-digit code")

        # test truncated code
        x = Code(15,2)
        self.assertEqual('11', str(x), "wrong 2-digit code for 15")
        self.assertEqual(2, len(x), "wrong length in 2-digit code")
        self.assertEqual(3, int(x), "wrong value of 2-digit code")

    def test_02_hex_codes(self):
        "Hex(n) is the hexadecimal encoding of the integer n"

        # test a code that has the default length
        x = Hex(63)
        self.assertEqual('3F', str(x), "wrong hex code for 63")
        self.assertEqual(2, len(x), "wrong length in hex code for 63")
        self.assertEqual(63, int(x), "wrong value of hex code for 63")
        self.assertEqual(Hex, type(x), "wrong type for hex code for 63")

        # test code padded with leading 0s
        x = Hex(63,3)
        self.assertEqual('03F', str(x), "wrong 3-digit hex code")
        self.assertEqual(3, len(x), "wrong length in 3-digit hex code")
        self.assertEqual(63, int(x), "wrong value of 3-digit hex code")

        # test truncated code
        x = Hex(63,1)
        self.assertEqual('F', str(x), "wrong 1-digit hex code")
        self.assertEqual(1, len(x), "wrong length in 1-digit hex code")
        self.assertEqual(15, int(x), "wrong value of 1-digit hex code")

    def test_03_slices(self):
        "Get and set individual bits in a code"
        x = Code(0,8)
        self.assertEqual('00000000', str(x), "wrong binary code")
        self.assertEqual('0', str(x[0]), "wrong first bit")
        self.assertEqual('0', str(x[7]), "wrong last bit")
        x[0] = 1
        x[7] = 1
        self.assertEqual('10000001', str(x), "wrong code after setting bits")
        self.assertEqual('1', str(x[0]), "wrong first bit")
        self.assertEqual('1', str(x[7]), "wrong last bit")        

    def test_04_hex_slices(self):
        "Get and set individual bits in a hex code"
        x = Hex(0,4)
        self.assertEqual('0000', str(x), "wrong hex code")
        self.assertEqual('0', str(x[0]), "wrong first digit")
        self.assertEqual('0', str(x[3]), "wrong last digit")
        x[0] = 15
        x[3] = 10
        self.assertEqual('F00A', str(x), "wrong code after setting digits")
        self.assertEqual('F', str(x[0]), "wrong first digit")
        self.assertEqual('A', str(x[3]), "wrong last digit")    
        
    def test_logic_ops(self):
        a = Code(12)                # 1100
        b = Code(10)                # 1010
        self.assertEqual('1000', str(a & b), "AND fail")    
        self.assertEqual('1110', str(a | b), "OR fail")    
        self.assertEqual('0110', str(a ^ b), "XOR fail")    
        self.assertEqual('0011', str(~a), "NOT fail")    

    def test_05_append(self):
        "Test the + operators"
        x = Code(5)
        x += 0
        self.assertEqual(4, len(x), "add: wrong length")
        self.assertEqual('1010', str(x), "add 0 fail")
        x += 1
        self.assertEqual('10101', str(x), "add 1 fail")
        x += Code(5)
        self.assertEqual('10101101', str(x), "add code fail")
    
    # def test_06_hex_append(self):
    #     "Test the append method for hex codes"
    #     x = Hex(15)
    #     x.append(10)
    #     self.assertEqual(2, len(x), "hex append: wrong length")
    #     self.assertEqual('FA', str(x), "append(10) fail")
    #     x.append(11)
    #     self.assertEqual('FAB', str(x), "append(11) fail")

    def test_07_extend(self):
        "Test the extend method"
        x = Code(5)
        x.extend(Code(0,2))
        self.assertEqual(5, len(x), "extend: wrong length")
        self.assertEqual('10100', str(x), "extend(Code(0,2)) fail")
        x.extend(Code(3))
        self.assertEqual('1010011', str(x), "append(Code(3)) fail")

    def test_08_hex_extend(self):
        "Test the extend method for hex codes"
        x = Hex(15)
        x.extend(Hex(128))
        self.assertEqual(3, len(x), "hex extend: wrong length")
        self.assertEqual('F80', str(x), "append(Hex(128)) fail")

    def test_09_parity_bits(self):
        "Test the parity bit methods"
        x = Code(5)
        self.assertEqual(0, x.parity_bit(), "wrong parity value for 101")
        self.assertTrue(x.even_parity(), "101 expected to have even parity")
        y = Code(4)
        self.assertEqual(1, y.parity_bit(), "wrong parity value for 100")
        self.assertFalse(y.even_parity(), "100 expected to have odd parity")
        x.add_parity_bit()
        self.assertEqual('1010', str(x), "wrong parity bit added to 101")
        y.add_parity_bit()
        self.assertEqual('1001', str(y), "wrong parity bit added to 100")
        self.assertTrue(x.even_parity(), "odd parity after adding parity bit to 101")
        self.assertTrue(y.even_parity(), "odd parity after adding parity bit to 100")

    def test_10_flip(self):
        "Test the flip method"
        x = Code(5)
        x.flip(0)
        self.assertEqual('001', str(x), "failed to flip first bit")
        x.flip(1)
        self.assertEqual('011', str(x), "failed to flip middle bit")
        x.flip(2)
        self.assertEqual('010', str(x), "failed to flip last bit")
        
    def test_11_char_codes(self):
        "Create a code for a character, test char and parity"
        x = Code('A',7)
        self.assertEqual(7, len(x), "expected character code to have 8 bits")
        self.assertEqual('1000001', str(x), "unexpected character code")
        self.assertEqual('A', x.char(), "chr does not return 'A'")
        x.add_parity_bit()
        self.assertEqual('10000010', str(x), "wrong parity bit attached to character")
        self.assertEqual('A', x.char(), "chr does not return 'A' after parity bit attached")
        x.flip(7)
        self.assertEqual('10000011', str(x), "flip did not change last character")
        self.assertEqual('\u2022', x.char(), "chr should return '°' for code with parity error")

    def test_12_char_hex_codes(self):
        "Create a hex code for a character"
        x = Hex('A')
        self.assertEqual(2, len(x), "expected hex character code to have 2 digits")
        self.assertEqual('41', str(x), "unexpected hex character code")
        self.assertEqual('A', x.char(), "chr does not return 'A'")
        
    # def test_13_unpacked_messages(self):
    #     "Create a message, add codes, iterate over bits"
    #     m = Message()
    #     self.assertEqual(0, len(m), "new message should have 0 bits")
    #     m.extend(Code(5))
    #     self.assertEqual(3, len(m), "message should have 3 bits")
    #     self.assertEqual('101', str(m), "wrong message string")
    #     m.extend(Code(5))
    #     self.assertEqual(6, len(m), "message should have 6 bits")
    #     self.assertEqual('101 101', str(m), "wrong message string")
    #     a = [b for b in each_bit(m)]
    #     self.assertEqual([1,0,1,1,0,1], a, "wrong list of bits")
    # 
    # def test_14_packed_messages(self):
    #     "Create and test packed messages"
    #     m = Message(packed = True)
    #     self.assertEqual(0, len(m), "new message should have 0 bits")
    #     m.extend(Code(5))
    #     self.assertEqual(3, len(m), "message should have 3 bits")
    #     self.assertEqual('101', str(m), "wrong message string")
    #     m.extend(Code(5))
    #     self.assertEqual(6, len(m), "message should have 6 bits")
    #     self.assertEqual('101101', str(m), "wrong message string")
    #     a = [b for b in each_bit(m)]
    #     self.assertEqual([1,0,1,1,0,1], a, "wrong list of bits")
    #     m.extend(Code(5))
    #     self.assertEqual(9, len(m), "message should have 9 bits")
    #     self.assertEqual('101101101', str(m), "wrong message string")
    #     self.assertEqual(2, len(m.list()), "packed message should have 2 words")
    #     
    # def test_15_packed_boundaries(self):
    #     "Test packing on 8-bit word boundaries"
    #     m = Message(packed = True)
    #     m.extend(Code(8))
    #     m.extend(Code(8))
    #     self.assertEqual('10001000', str(m), "8 bits all in one word?")
    #     self.assertEqual(1, len(m.list()), "array doesn't have one word")
    #     m.extend(Code(8))
    #     self.assertEqual('100010001000', str(m), "12 bits across 2 words?")
    #     self.assertEqual(2, len(m.list()), "array doesn't have 2 words")

    def test_16_make_codes(self):
        "Test the make_codes function"
        nt_code = make_codes(['a','t','c','g'])
        self.assertEqual(4, len(nt_code), "expected dictionary with 4 entries")
        self.assertEqual(Code(0,2), nt_code['a'], "unexpected code for 'a'")
        self.assertEqual(Code(3,2), nt_code['g'], "unexpected code for 'g'")

    def test_17_encode(self):
        "Test the encode function"
        m = encode('atg')
        self.assertEqual(3, len(m), "unexpected message length")
        self.assertEqual(Code('a'), m[0], "unexpected ASCII code in first byte of message")
        self.assertEqual(Code('g'), m[2], "unexpected ASCII code in last byte of message")
        
    def test_encode_error(self):
        "Can't encode a string with non-ASCII characters"
        boat = 'b' + chr(229) + 't'
        with self.assertRaises(ValueError) as context:
            encode(boat)
        self.assertEqual(type(context.exception), ValueError, "should not encode å")
        
    def test_encode_with_parity(self):
        "Test the encode function"
        m = encode('atg', True)
        self.assertEqual(3, len(m), "unexpected message length")
        ca = Code('a'); ca.add_parity_bit()
        self.assertEqual(ca, m[0], "unexpected parity code in first byte of message")

    def test_18_decode(self):
        s = "hello"
        self.assertTrue(s == decode(encode(s)), "could not decode an encoded message")
        self.assertTrue(s == decode(encode(s, True)), "could not decode message encoded with parity")

    def test_19_garbled(self):
        sent = "hello"
        m = encode(sent, True)
        recd = decode(garbled(m, 1))
        self.assertNotEqual(sent, recd, "expected message to change")
        self.assertEqual(1, recd.count('\u2022'), "expected one bullet char in decoded message")

    def test_20_priority_queue(self):
        pq = PriorityQueue()
        pq.insert(5)
        pq.insert(4)
        pq.insert(7)
        self.assertEqual(3, len(pq), "exected queue to have 3 items")
        self.assertEqual(4, pq[0], "expected 4 to be at front of queue")
        self.assertEqual(7, pq[-1], "expected 7 to be at end of queue")
        x = pq.pop()
        self.assertEqual(4, x, "didn't get lowest value from front of queue")
        self.assertEqual(2, len(pq), "queue not shorter after pop()")
        self.assertEqual([5,7], [x for x in pq], "iterator failed to traverse queue")
        self.assertEqual(str([5,7]), str(pq), "str(pq) is not the expected string")
        
    def test_21_huffman_tree(self):
        tree = build_tree(path_to_data('hafreq.txt'))
        self.assertEqual(1.0, tree._freq, "Root of tree should have frequency 1.0")
        codes = assign_codes(tree)
        self.assertEqual(13, len(codes), "Expected 13 codes for Hawaiian alphabet")
        self.assertEqual("10", str(codes['A']), "Code for 'A' should be 10")
        self.assertEqual("110010", str(codes['W']), "Code for 'W' should be 110010")

    def test_22_huffman_encode(self):
        tree = build_tree(path_to_data('hafreq.txt'))
        msg = huffman_encode("ALOHA", tree)
        self.assertEqual("100000010000110", str(msg), "Wrong encoding of 'ALOHA'")
        self.assertEqual("ALOHA", huffman_decode(msg, tree), "Couldn't decode Huffman-encoded bit string")
        
        