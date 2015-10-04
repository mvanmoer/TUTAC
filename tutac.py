# TUTAC - TUTorial Automatic Computer
# TUTAC contains
# - card reader
# - zero memory button
# - load card button
# - 2000 word, 11 decimal digit memory
#   - this should be fixed size, could use numpy to fix the storage at
#     2000 words, then could do logic checks to make sure nothing
#     exceeds +/- 9,999,999,999 and not worry about having a 2D array or
#     anything like that. The question is, what to do with the sign digit.
#     Do I just not actually store that and only present that to the user?
#   - need to store as strings because do need the leading zeros in many cases.
#     So, store as string, if it's an instruction, grab the appropriate slices
#     if it's data, convert to int? how does fixed point affect this?
#     And shifting... 
#     So anything in memory should be a string, padded with zeros and with
#     a sign digit for sure. But inside the accumulator it should be a
#     number. 08 is /10, 09 is * 10, both truncate. 60-63 are as expected,
#     except that for 62, the answer starts in the R-register and for 63,
#     the R-register contains the remainder.

# - 11 digit accumulator
# - 10 digit R-register
# - instruction pointer
# - typewriter
# - STOP light
# - OVERFLOW light
# - op codes
# 00 STOP
# 08 SR
# 09 SL
# 15 STORE
# 25 WRITE
# 30 UT
# 31 TOZ
# 32 TOP
# 50 COPY
# 60 ADD
# 61 SUB
# 62 MULT
# 63 DIV

# note to self. There is a Decimal module, which might be easier
# to use, especially for division.

import sys
import time 

class TUTAC:
        
    def __init__(self, step=False):
        self._step = step
        self.MAX_INT = 10**10 - 1
        self.MIN_INT = -self.MAX_INT
        self.MEMSIZE = 2000
        self._stopped = False
        self._stoplight = False
        self._overflow = False
        self._memory = [None] * self.MEMSIZE # replace this with numpy fixed size array
        self._accumulator = 0
        self._r_register = 0
        self._ip = 0

    def load_cards(self, input_deck):
        with open(input_deck, 'r') as deck:
            for line in deck:
                word = line.split(' ')[0].rstrip()
                cell = int(word[:4])

                self._memory[cell] = word[4:]
        self._run()

    def dump_core(self):
        i = 0
        for cell in self._memory:
            self._print_cell(i, cell)
            i += 1

    def dump_non_zero(self):
        i = 0
        for cell in self._memory:
            if cell != '00000000000':
               self._print_cell(i, cell)
            i += 1 

    def _print_cell(self, address, cell):
        print('{0:04d}: {1}'.format(address, cell))

    def zero_memory(self):
        self._memory = ['00000000000'] * 2000;

    def _run(self):
        while not self._stopped:
            time.sleep(1/3000)
            instruction = self._memory[self._ip][1:3]
            arg = int(self._memory[self._ip][3:7])

            if self._step:
                print(self._accumulator,instruction, arg)
            if instruction == '00':
               print('STOP_INSTRUCTION')
               self._stop()
            elif instruction == '08':
                self._shift_right(arg)
            elif instruction == '09':
                self._shift_left(arg)
            elif instruction == '15':
                self._store(arg)
            elif instruction == '25':
                self._write(arg)
            elif instruction == '30':
                self._unconditional_transfer(arg)
                continue
            elif instruction == '31':
                self._transfer_on_zero(arg)
                continue
            elif instruction == '32':
                self._transfer_on_plus(arg)
                continue
            elif instruction == '50':
                self._copy(arg)
            elif instruction == '60':
                self._add(arg)
            elif instruction == '61':
                self._subtract(arg)
            elif instruction == '62':
                self._multiply(arg)
            elif instruction == '63':
                self._divide(arg)
            else:
                self._unknown_instruction()
            self._ip += 1
            if self._ip >= self.MEMSIZE:
                self._stop()

    def _copy(self, address):
        if self._memory[address][0] == '0':
            self._accumulator = int(self._memory[address][1:])
        elif self._memory[address][0] == '1':
            self._accumulator = -int(self._memory[address][1:])
        else:
            self._stop()
             
    def _store(self, address):
        if self._accumulator >= 0:
            data = '{0:011d}'.format(self._accumulator)
        else:
            data = '1{0:010d}'.format(abs(self._accumulator))
        self._memory[address] = data

    def _write(self, address):
        print(self._memory[address])

    def _add(self, address):
        data = self.__convert(address)
        self._accumulator += data
        if self._accumulator > self.MAX_INT or self._accumulator < self.MIN_INT:
            self._overflow = True
            self._stop()
    
    def _subtract(self, address):
        data = self.__convert(address)
        self._accumulator -= data
        if self._accumulator > self.MAX_INT or self._accumulator < self.MIN_INT:
            self._overflow = True
            self._stop() 

    def _multiply(self, address):
        data = self.__convert(address)
        #print('data', data, 'accum', self._accumulator)
        product = data * self._accumulator
        #print('product', product)
        # Book doesn't directly address multiply overflow,
        # just says that if the product is larger than 
        # the r-reg, digits will be lost when shifting.
        
        # product starts from the r-register
        # and flows into the accumulator
        # r-register contains first 10 digits of product
        self._r_register = abs(product) % (self.MAX_INT + 1)
        #print('r-reg', self._r_register)
        self._accumulator = (abs(product) - self._r_register) //\
            (self.MAX_INT + 1)
        sign = -1 if product < 0 else 1
        self._accumulator *= sign
        #print('accum', self._accumulator)

    def _divide(self, address):
        # 1) numinator must be < then denominator
        denominator = self.__convert(address)
        numerator = self._accumulator
        if denominator < abs(numerator):
            self._overflow = True
            print('DIVIDE_OVERFLOW')
            self._stop()
        # 2) divide to 10 places goes into accumulator,
        #    starting from left. Remainder goes into
        #    r-register, starting from right.
        from math import trunc
        quotient = int(trunc(numerator / denominator * (self.MAX_INT + 1)))
        remainder = numerator * (self.MAX_INT + 1) % denominator

        self._accumulator = quotient
        self._r_regsiter = remainder

    def _shift_left(self, units):
        combo = self.__combine()
        combo = combo[0] + combo[1+units:] + '0'*units

        sign = combo[0]
        self._accumulator = int(combo[1:11])
        if sign == '1':
            self._accumulator = -self._accumulator
        self._r_register = int(combo[11:])

    def _shift_right(self, units):
        combo = self.__combine()
        combo = combo[0] + '0'*units + combo[1:11]
        sign = combo[0]
        self._accumulator = int(combo[1:11])
        if sign == '1':
            self._accumulator = -self.accumulator
        self._r_register = int(combo[11:])

    def _unconditional_transfer(self, address):
        self._ip = int(address)

    def _transfer_on_zero(self, address):
        if self._accumulator == 0:
            self._ip = int(address)
        else:
            self._ip += 1

    def _transfer_on_plus(self, address):
        if self._accumulator > 0:
            self._ip = int(address)
        else:
            self._ip += 1

    def _stop(self):
        self._stopped = True
        print('STOPPED')

    def __convert(self, address):
        #print('self._memory[address]', self._memory[address])
        sign = self._memory[address][0]
        data = int(self._memory[address][1:])
        if sign == '1':
            data = -data
        return data

    def __combine(self):
        if self._accumulator >= 0:
            combo = '{0:011d}'.format(self._accumulator)
        else:
            combo = '1{0:010d}'.format(abs(self._accumulator))
        combo += '{0:010d}'.format(self._r_register)
        #print('combo:',combo)
        return combo


if __name__ == '__main__':
    t = TUTAC()
    t.zero_memory()
    t.load_cards(sys.argv[1])
