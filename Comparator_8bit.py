from myhdl import *
import random

# random.seed(9)
randrange = random.randrange


@block
def Comparator(a, b, equal_bit, greater, lesser, clk):
    @always(clk.posedge)
    def comparator_8bit():
        temp_equal_bit = Signal(bool(True))
        temp_less_bit = Signal(bool(False))
        temp_greater_bit = Signal(bool(False))
        for i in range(8):
            temp_equal_bit = temp_equal_bit and (not (a(i) ^ b(i)))
        if not temp_equal_bit:
            if not a(7) and b(7):
                temp_greater_bit = True
            elif a(7) and not b(7):
                temp_less_bit = True
            else:
                for i in range(7, -1, -1):
                    if not temp_less_bit and not temp_greater_bit:
                        temp_less_bit = temp_less_bit or ((not a(i)) and b(i))
                        temp_greater_bit = temp_greater_bit or (a(i) and (not b(i)))
        equal_bit.next = temp_equal_bit
        lesser.next = temp_less_bit
        greater.next = temp_greater_bit

    return comparator_8bit


@block
def test_comparator():
    clk = Signal(bool(0))
    a, b = [Signal(intbv(0)[8:].signed()) for i in range(2)]
    equal, greater, lesser = [Signal(bool(0)) for i in range(3)]
    dff_inst = Comparator(a, b, equal, greater, lesser, clk)

    @always(delay(10))
    def clkgen():
        clk.next = not clk

    @always(clk.negedge)
    def stimulus():
        a.next = random.randint(-128, 127)
        b.next = random.randint(-128, 127)
        print(str(int(a)) + " vs " + str(int(b)) + " = Equal : " + str(equal) + ", Greater : " + str(
            greater) + ", Lesser : " + str(lesser))

        if a == b:
            assert equal and not greater and not lesser
        if a < b:
            assert not equal and not greater and lesser
        if a > b:
            assert not equal and greater and not lesser

    return dff_inst, clkgen, stimulus


def simulate(timesteps):
    simInst = test_comparator()
    simInst.config_sim(trace=True, tracebackup=False)
    simInst.run_sim(timesteps, quiet=0)


simulate(2000)
