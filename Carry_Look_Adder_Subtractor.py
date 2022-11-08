from myhdl import *
import random

random.seed(9)
randrange = random.randrange


@block
def CarryLookAheadAdder(ina, inb, cOut, sum4):
    @always_comb
    def cl_adder():
        sl = [Signal(bool()) for i in range(8)]
        p0 = ina[0] ^ inb[0]
        sl[0] = p0
        g0 = ina[0] and inb[0]

        c1 = g0
        p1 = ina[1] ^ inb[1]
        sl[1] = p1 ^ c1
        g1 = ina[1] and inb[1]

        c2 = g1 or (p1 and g0)
        p2 = ina[2] ^ inb[2]
        sl[2] = p2 ^ c2
        g2 = ina[2] and inb[2]

        c3 = g2 or (p2 and g1) or (p2 and p1 and g0)
        p3 = ina[3] ^ inb[3]
        sl[3] = p3 ^ c3
        g3 = ina[3] and inb[3]

        c4 = g3 or (p3 and g2) or (p3 and p2 and g1) or (p3 and p2 and p1 and g0)
        p4 = ina[4] ^ inb[4]
        sl[4] = p4 ^ c4
        g4 = ina[4] and inb[4]

        c5 = g4 or (p4 and c4)
        p5 = ina[5] ^ inb[5]
        sl[5] = p5 ^ c5
        g5 = ina[5] and inb[5]

        c6 = g5 or (p5 and g4) or (p5 and p4 and c4)
        p6 = ina[6] ^ inb[6]
        sl[6] = p6 ^ c6
        g6 = ina[6] and inb[6]

        c7 = g6 or (p6 and g5) or (p6 and p5 and g4) or (c4 and p4 and p5 and p6)
        p7 = ina[7] ^ inb[7]
        sl[7] = p7 ^ c7
        g7 = ina[7] and inb[7]
        c8 = g7 or (p7 and g6) or (p7 and p6 and g5) or (p7 and p6 and p5 and g4) or (c4 and p4 and p5 and p6 and p7)

        sc = ConcatSignal(*reversed(sl))
        sum4.next = sc
        cOut.next = c8
    return cl_adder


@block
def test_adder():
    a = Signal(intbv(178, 0, 255))
    b = Signal(intbv(128, 0, 255))
    sum = Signal(intbv(0, 0, 255))

    cout = Signal(bool(0))

    adder_1 = CarryLookAheadAdder(a, b, cout, sum)

    @instance
    def stimulus():
        yield delay(10)

        print(sum)
        print("a b sum cout")
        for i in range(12):
            a.next, b.next = randrange(0, 128), randrange(0, 128)
            yield delay(10)
            print("%s %s %s %s" % (int(a), int(b), int(sum), cout))

    return adder_1, stimulus


tb = test_adder()
tb.config_sim(trace=True, tracebackup = False)
tb.run_sim()
