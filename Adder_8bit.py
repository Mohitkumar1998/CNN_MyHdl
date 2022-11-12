from myhdl import *
import random


@block
def CarryLookAheadAdder(a, b, c0, c8, sum4, clk):
    @always(clk.posedge)
    def cl_adder():
        sl = [Signal(bool(0)) for i in range(8)]
        p0, p1, p2, p3, p4, p5, p6, p7 = [Signal(bool(0)) for i in range(8)]
        g0, g1, g2, g3, g4, g5, g6, g7 = [Signal(bool(0)) for i in range(8)]
        c1, c2, c3, c4, c5, c6, c7 = [Signal(bool(0)) for i in range(7)]

        p0 = a(0) ^ b(0)
        sl[0] = p0 ^ c0
        g0 = a(0) and b(0)

        c1 = g0 or (p0 and c0)
        p1 = a(1) ^ b(1)
        sl[1] = p1 ^ c1
        g1 = a(1) and b(1)

        c2 = g1 or (p1 and c1)
        p2 = a(2) ^ b(2)
        sl[2] = p2 ^ c2
        g2 = a(2) and b(2)

        c3 = g2 or (p2 and c2)
        p3 = a(3) ^ b(3)
        sl[3] = p3 ^ c3
        g3 = a(3) and b(3)

        c4 = g3 or (p3 and c3)
        p4 = a(4) ^ b(4)
        sl[4] = p4 ^ c4
        g4 = a(4) and b(4)

        c5 = g4 or (p4 and c4)
        p5 = a(5) ^ b(5)
        sl[5] = p5 ^ c5
        g5 = a(5) and b(5)

        c6 = g5 or (p5 and c5)
        p6 = a(6) ^ b(6)
        sl[6] = p6 ^ c6
        g6 = a(6) and b(6)

        c7 = g6 or (p6 and c6)
        p7 = a(7) ^ b(7)
        sl[7] = p7 ^ c7
        g7 = a(7) and b(7)

        c8.next = g7 or (p7 and c7)
        sum4.next = intbv(intbv(str(int(sl[7])) + "_" + str(int(sl[6])) + "_" + str(int(sl[5])) + "_" + str(int(sl[4])) + "_" + str(int(sl[3])) + "_" + str(int(sl[2])) + "_" + str(int(sl[1])) + "_" + str(int(sl[0])))[8:]).signed()

    return cl_adder


@block
def test_adder():

    clk = Signal(bool(0))
    a, b, sum8 = [Signal(intbv(0)[8:].signed()) for i in range(3)]
    c0, c8 = [Signal(intbv(0)[1:]) for i in range(2)]
    dff_inst = CarryLookAheadAdder(a, b, c0, c8, sum8, clk)

    @always(delay(10))
    def clkgen():
        clk.next = not clk

    @always(clk.negedge)
    def stimulus():
        a.next = random.randint(-128, 127)
        b.next = random.randint(-128, 127)
        print(str(int(a)) + " + " + str(int(b)) + " = " + str(int(sum8)) + " , " + str(int(c8)))
    return dff_inst, clkgen, stimulus


def simulate(timesteps):
    simInst = test_adder()
    simInst.config_sim()
        # trace=True, tracebackup=False)
    simInst.run_sim(timesteps, quiet=0)

simulate(2000)