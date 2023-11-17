import math
import hashlib
import struct

MAX_PAYLOAD_BITS = 448
WORDS_PER_BLOCK = 16
BITS_PER_WORD = 32
MAX_LENGTH = 64
BLOCK_SIZE = 512
BITS_PER_CHAR = 8
ARRAYS_CONSTANT = 4294967296
BUFFER_A = 0x67452301
BUFFER_B = 0xEFCDAB89
BUFFER_C = 0x98BADCFE
BUFFER_D = 0x10325476

#Works properly
def init_buffers(hex_value):
    return to_binary(hex_value, True, False)

#Works properly
def get_constants_array():
    t_array = list(range(64))
    for i in range(64):
        t_array[i] = to_binary(int(ARRAYS_CONSTANT*abs(math.sin(i+1))), True, False)    
    return t_array


def to_binary(msg, needs_32, is_hex):
    bin_list = list()
    if isinstance(msg, int):
        if needs_32:
            bin_message =  format(int(bin(msg), base=2), "032b")
        elif is_hex:
            bin_message = format(int(bin(msg), base=2), "08b")
        else:
            bin_message = format(int(bin(msg), base=2), "08b")
    else:
        for letter in msg:
            binary = format(ord(letter), "08b")
            bin_list.append(binary)
        bin_message = "".join(bin_list)    
    return bin_message


def calc_padding(length):
    bin_length = to_binary(length, False, False)
    list_padding = list()
    zeroes = MAX_LENGTH - len(bin_length)
    for i in range(zeroes):
        list_padding.append("0")
    list_padding.append(bin_length)
    padding = "".join(list_padding)
    return padding


def get_words(payload):
    word_blocks = [payload[i:i+32][::-1] for i in range(0, len(payload), 32)]
    return word_blocks

#BIT OPERATORS

def and_operator(s1, s2):
    buffer = list()
    for bit_s1, bit_s2 in zip(s1, s2):
        if bit_s1 == "1" and bit_s2 == "1":
            buffer.append("1")
        else:
            buffer.append("0")
    result = "".join(buffer)
    return result


def or_operator(s1, s2):
    buffer = list()
    for bit_s1, bit_s2 in zip(s1, s2):
        if bit_s1 == "1" or bit_s2 == "1":
            buffer.append("1")
        else:
            buffer.append("0")
    result = "".join(buffer)
    return result


def xor_operator(s1, s2):
    buffer = list()
    for bit_s1, bit_s2 in zip(s1, s2):
        if (bit_s1 == "1" and bit_s2 == "1") or (bit_s1 == "0" and bit_s2 == "0"):
            buffer.append("0")
        else:
            buffer.append("1")
    result = "".join(buffer)
    return result


def not_operator(s):
    buffer = list()
    for bit in s:
        if bit == "0":
            buffer.append("1")
        else:
            buffer.append("0")
    result = "".join(buffer)
    return result

def circular_shifting(sequence, rotations):
    buffer = list()
    for bit in sequence:
        buffer.append(bit)
    for i in range(rotations):
        circular_bit = buffer[0]
        for j, bit in enumerate(buffer):
            if j < len(buffer)-1:
                buffer[j] = buffer[j+1]
            else:
                buffer[j] = circular_bit
    result = "".join(buffer)
    return result

#Works properly
def bit_addition(*sequences):
    bin_result = 0
    for sequence in sequences:
        bin_result += int(sequence, 2)
        bin_result %= 2**32  # Ensure the result fits into 32 bits
    result = format(bin_result, "032b")
    return result
    
# NON-LINEAR FUNCTIONS


def f_non_linear(x, y, z):
    #F(X,Y,Z) = (X AND Y) OR (NOT(X) AND Z)
    """
    x_and_y = and_operator(x,y)
    not_x = not_operator(x)
    not_x_and_z = and_operator(not_x, z)
    result = or_operator(x_and_y, not_x_and_z)"""
    #F(X,Y,Z) = Z XOR (X AND (Y XOR Z))
    y_xor_z = xor_operator(y, z) 
    x_and_y_xor_z = and_operator(x, y_xor_z)
    result = xor_operator(z, x_and_y_xor_z)  
    return result


def g_non_linear(x, y, z):
#G(X,Y,Z) = (X AND Z) OR (Y AND NOT(Z))
    """
    x_and_z = and_operator(x,z)
    not_z = not_operator(z)
    y_and_not_z = and_operator(y, not_z)
    result = or_operator(x_and_z, y_and_not_z)"""
#G(X,Y,Z) = Y XOR (Z AND (X XOR Y))
    x_xor_y = xor_operator(x, y) 
    z_and_x_xor_y = and_operator(z, x_xor_y)
    result = xor_operator(y, z_and_x_xor_y)  
    return result

#H(X,Y,Z) = X XOR Y XOR Z
def h_non_linear(x, y, z):
    x_xor_y = xor_operator(x,y)
    result = xor_operator(x_xor_y, z)
    return result

#I(X,Y,Z) = Y XOR (X OR NOT(Z))
def i_non_linear(x, y, z):
    not_z = not_operator(z)
    x_or_not_z = or_operator(x, not_z)
    result = xor_operator(y, x_or_not_z)
    return result

def bytes_to_bits(byte_string):
    # Convert each byte to 8 bits and concatenate
    bits = ''.join(format(byte, '08b') for byte in byte_string)
    return bits

def convert_to_byte(sequence):
    byte_sequence = bytearray()
    for i in range(0, len(sequence), 8):  # 8 bits in a byte
        byte = sequence[i:i + 8]
        byte_sequence.extend(struct.pack('>B', int(byte[::-1], 2)))
    return byte_sequence


def process_block(buffer_a, buffer_b, buffer_c, buffer_d, x_array, t_array):
    initial_buffer_a = buffer_a
    initial_buffer_b = buffer_b
    initial_buffer_c = buffer_c
    initial_buffer_d = buffer_d
    #Round 1
    for i in range (16):
        if i == 0 or i%4 == 0:
            parenth = circular_shifting(bit_addition(buffer_a, f_non_linear(buffer_b, buffer_c, buffer_d), x_array[i], t_array[i]), 7)
            buffer_a = bit_addition(buffer_b, parenth)
        elif i%4 == 1: 
            parenth = circular_shifting(bit_addition(buffer_d, f_non_linear(buffer_a, buffer_b, buffer_c), x_array[i], t_array[i]), 12)
            buffer_d = bit_addition(buffer_a, parenth)
        elif i%4 == 2: 
            parenth = circular_shifting(bit_addition(buffer_c, f_non_linear(buffer_d, buffer_a, buffer_b), x_array[i], t_array[i]), 17)
            buffer_c = bit_addition(buffer_d, parenth)
        else:
            parenth = circular_shifting(bit_addition(buffer_b, f_non_linear(buffer_c, buffer_d, buffer_a), x_array[i], t_array[i]), 22)
            buffer_b = bit_addition(buffer_c, parenth)
    #Round 2

    for i in range (16):
        k = 1 + 5*i
        while k>15:
            k -= 16
        if i == 0 or i%4 == 0:
            parenth = circular_shifting(bit_addition(buffer_a, g_non_linear(buffer_b, buffer_c, buffer_d), x_array[k], t_array[16+i]), 5)
            buffer_a = bit_addition(buffer_b, parenth)
        elif i%4 == 1: 
            parenth = circular_shifting(bit_addition(buffer_d, g_non_linear(buffer_a, buffer_b, buffer_c), x_array[k], t_array[16+i]), 9)
            buffer_d = bit_addition(buffer_a, parenth)
        elif i%4 == 2: 
            parenth = circular_shifting(bit_addition(buffer_c, g_non_linear(buffer_d, buffer_a, buffer_b), x_array[k], t_array[16+i]), 14)
            buffer_c = bit_addition(buffer_d, parenth)
        else:
            parenth = circular_shifting(bit_addition(buffer_b, g_non_linear(buffer_c, buffer_d, buffer_a), x_array[k], t_array[16+i]), 20)
            buffer_b = bit_addition(buffer_c, parenth)
    #Round 3
    
    for i in range (16):
        k = 5 + 3*i
        while k>15:
            k -= 16
        if i == 0 or i%4 == 0:
            parenth = circular_shifting(bit_addition(buffer_a, h_non_linear(buffer_b, buffer_c, buffer_d), x_array[k], t_array[32+i]), 4)
            buffer_a = bit_addition(buffer_b, parenth)
        elif i%4 == 1: 
            parenth = circular_shifting(bit_addition(buffer_d, h_non_linear(buffer_a, buffer_b, buffer_c), x_array[k], t_array[32+i]), 11)
            buffer_d = bit_addition(buffer_a, parenth)
        elif i%4 == 2: 
            parenth = circular_shifting(bit_addition(buffer_c, h_non_linear(buffer_d, buffer_a, buffer_b), x_array[k], t_array[32+i]), 16)
            buffer_c = bit_addition(buffer_d, parenth)
        else:
            parenth = circular_shifting(bit_addition(buffer_b, h_non_linear(buffer_c, buffer_d, buffer_a), x_array[k], t_array[32+i]), 23)
            buffer_b = bit_addition(buffer_c, parenth)
    #Round 4    
    
    for i in range (16):
        k = 7*i
        while k>15:
            k -= 16
        if i == 0 or i%4 == 0:
            parenth = circular_shifting(bit_addition(buffer_a, i_non_linear(buffer_b, buffer_c, buffer_d), x_array[k], t_array[48+i]), 6)
            buffer_a = bit_addition(buffer_b, parenth)
        elif i%4 == 1: 
            parenth = circular_shifting(bit_addition(buffer_d, i_non_linear(buffer_a, buffer_b, buffer_c), x_array[k], t_array[48+i]), 10)
            buffer_d = bit_addition(buffer_a, parenth)
        elif i%4 == 2: 
            parenth = circular_shifting(bit_addition(buffer_c, i_non_linear(buffer_d, buffer_a, buffer_b), x_array[k], t_array[48+i]), 15)
            buffer_c = bit_addition(buffer_d, parenth)
        else:
            parenth = circular_shifting(bit_addition(buffer_b, i_non_linear(buffer_c, buffer_d, buffer_a), x_array[k], t_array[48+i]), 21)
            buffer_b = bit_addition(buffer_c, parenth)
    #Final adition
    
    buffer_a = bit_addition(buffer_a, initial_buffer_a)
    buffer_b = bit_addition(buffer_b, initial_buffer_b)
    buffer_c = bit_addition(buffer_c, initial_buffer_c)
    buffer_d = bit_addition(buffer_d, initial_buffer_d)

    return buffer_a, buffer_b, buffer_c, buffer_d


def main():
    buffer_a = init_buffers(BUFFER_A)
    buffer_b = init_buffers(BUFFER_B)
    buffer_c = init_buffers(BUFFER_C)
    buffer_d = init_buffers(BUFFER_D)
    t_array = get_constants_array()
    message = input("Write to convert to binary:")
    bin_message = to_binary(message, False, False)
    padding = calc_padding(len(bin_message))
    num_blocks = int(len(bin_message)/MAX_PAYLOAD_BITS) + 1
    for i in range(num_blocks):
        payload = bin_message[BLOCK_SIZE*i : MAX_PAYLOAD_BITS + BLOCK_SIZE*i]
        if i == num_blocks-1:
            last_block = list()
            for j in range(MAX_PAYLOAD_BITS - len(payload)):
                if j==0:
                    last_block.append("1")
                else:
                    last_block.append("0")
            block_padding = "".join(last_block)
            block = payload+block_padding+padding
        else:
            block = payload+padding 
        print(len(block))  
        words = get_words(block)
        for i, word in enumerate(words):
            print(f"Word {i} is: {word}")

        buffer_a, buffer_b, buffer_c, buffer_d = process_block(buffer_a, buffer_b, buffer_c, buffer_d, words, t_array)

    bytes_a = convert_to_byte(buffer_a)
    bytes_b = convert_to_byte(buffer_b)
    bytes_c = convert_to_byte(buffer_c)
    bytes_d = convert_to_byte(buffer_d)
    print(f"MD5 Hash is:  {bytes_d.hex()}{bytes_c.hex()}{bytes_b.hex()}{bytes_a.hex()}")
    print(f"From hashlib: {hashlib.md5(message.encode('utf-8')).hexdigest()}")


if __name__ == "__main__":
    main()