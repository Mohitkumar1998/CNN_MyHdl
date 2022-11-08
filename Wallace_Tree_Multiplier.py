from myhdl import *
import random

#random.seed(9)
randrange = random.randrange


@block
def FullAdder(a, b, c, cout, s):
    @always_comb
    def fa_logic():
        s.next = a ^ b ^ c
        cout.next = (a and b) or (b and c) or (a and c)

    return fa_logic


@block
def Adder4b(ina, inb, cin, cOut, sum4):
    cl = [Signal(bool()) for i in range(0, 4)]
    sl = [Signal(bool()) for i in range(4)]
    FullAdder0 = FullAdder(ina[0], inb[0], cin, cl[1], sl[0])
    FullAdder1 = FullAdder(cl[1], ina[1], inb[1], cl[2], sl[1])
    FullAdder2 = FullAdder(cl[2], ina[2], inb[2], cl[3], sl[2])
    FullAdder3 = FullAdder(cl[3], ina[3], inb[3], cOut, sl[3])
    sc = ConcatSignal(*reversed(sl))

    @always_comb
    def list2intbv():
        sum4.next = sc

    return instances()


@block
def HalfAdder(a, b, cout, s):
    @always_comb
    def ha_logic():
        s.next = a ^ b
        cout.next = a and b

    return ha_logic


@block
def WallaceTreeMultiplier(a, b, mult16):
    sl = [Signal(intbv(0)[1:]) for i in range(16)]

    # PARTIAL PRODUCTS : developing a memory containing the partial products
    # all partial products are independent so can be implemented using combinational logic

    partial_products = [[Signal(intbv(0)[1:]) for i in range(8)] for j in range(8)]
    for i in range(8):
        for j in range(8):
            partial_products[i][j] = Signal(intbv(int(a(i) and b(j)))[1:])

    # Stage 1
    sum_stage_1 = [Signal(intbv(0)[1:]) for i in range(19)]
    carry_stage_1 = [Signal(intbv(0)[1:]) for i in range(19)]

    sl[0] = partial_products[0][0]
    HalfAdder1_1 = HalfAdder(partial_products[1][0], partial_products[0][1], carry_stage_1[0], sum_stage_1[0])
    FullAdder1_2 = FullAdder(partial_products[2][0], partial_products[1][1], partial_products[0][2], carry_stage_1[1], sum_stage_1[1])
    FullAdder1_3 = FullAdder(partial_products[3][0], partial_products[1][2], partial_products[2][1], carry_stage_1[2], sum_stage_1[2])
    FullAdder1_4 = FullAdder(partial_products[3][1], partial_products[4][0], partial_products[0][4], carry_stage_1[3], sum_stage_1[3])
    HalfAdder1_5 = HalfAdder(partial_products[1][3], partial_products[2][2], carry_stage_1[4], sum_stage_1[4])
    FullAdder1_6 = FullAdder(partial_products[5][0], partial_products[4][1], partial_products[0][5], carry_stage_1[5], sum_stage_1[5])
    FullAdder1_7 = FullAdder(partial_products[1][4], partial_products[2][3], partial_products[3][2], carry_stage_1[6], sum_stage_1[6])
    FullAdder1_8 = FullAdder(partial_products[2][4], partial_products[3][3], partial_products[4][2], carry_stage_1[7], sum_stage_1[7])
    FullAdder1_9 = FullAdder(partial_products[5][1], partial_products[1][5], partial_products[6][0], carry_stage_1[8], sum_stage_1[8])
    FullAdder1_10 = FullAdder(partial_products[2][5], partial_products[4][3], partial_products[3][4], carry_stage_1[9], sum_stage_1[9])
    FullAdder1_11 = FullAdder(partial_products[5][2], partial_products[1][6], partial_products[6][1], carry_stage_1[10], sum_stage_1[10])
    HalfAdder1_12 = HalfAdder(partial_products[7][0], partial_products[0][7], carry_stage_1[11], sum_stage_1[11])
    FullAdder1_13 = FullAdder(partial_products[2][6], partial_products[5][3], partial_products[6][2], carry_stage_1[12], sum_stage_1[12])
    FullAdder1_14 = FullAdder(partial_products[7][1], partial_products[1][7], partial_products[3][5], carry_stage_1[13], sum_stage_1[13])
    FullAdder1_15 = FullAdder(partial_products[4][5], partial_products[5][4], partial_products[3][6], carry_stage_1[14], sum_stage_1[14])
    FullAdder1_16 = FullAdder(partial_products[2][7], partial_products[6][3], partial_products[7][2], carry_stage_1[15], sum_stage_1[15])
    FullAdder1_17 = FullAdder(partial_products[6][4], partial_products[5][5], partial_products[4][6], carry_stage_1[16], sum_stage_1[16])
    FullAdder1_18 = FullAdder(partial_products[6][5], partial_products[5][6], partial_products[4][7], carry_stage_1[17], sum_stage_1[17])
    FullAdder1_19 = FullAdder(partial_products[7][5], partial_products[6][6], partial_products[5][7], carry_stage_1[18], sum_stage_1[18])
    sl[1] = sum_stage_1[0]

    # Stage 2
    sum_stage_2 = [Signal(intbv(0)[1:]) for i in range(11)]
    carry_stage_2 = [Signal(intbv(0)[1:]) for i in range(11)]

    HalfAdder2_1 = HalfAdder(carry_stage_1[0], sum_stage_1[1], carry_stage_2[0], sum_stage_2[0])
    FullAdder2_2 = FullAdder(partial_products[0][3], carry_stage_1[1], sum_stage_1[2], carry_stage_2[1], sum_stage_2[1])
    FullAdder2_3 = FullAdder(carry_stage_1[2], sum_stage_1[3], sum_stage_1[4], carry_stage_2[2], sum_stage_2[2])
    FullAdder2_4 = FullAdder(carry_stage_1[3], carry_stage_1[4], sum_stage_1[5], carry_stage_2[3], sum_stage_2[3])
    FullAdder2_5 = FullAdder(carry_stage_1[5], carry_stage_1[6], sum_stage_1[7], carry_stage_2[4], sum_stage_2[4])
    FullAdder2_6 = FullAdder(carry_stage_1[7], carry_stage_1[8], sum_stage_1[9], carry_stage_2[5], sum_stage_2[5])
    FullAdder2_7 = FullAdder(carry_stage_1[10], carry_stage_1[11], sum_stage_1[12], carry_stage_2[6], sum_stage_2[6])
    FullAdder2_8 = FullAdder(carry_stage_1[12], carry_stage_1[13], sum_stage_1[14], carry_stage_2[7], sum_stage_2[7])
    FullAdder2_9 = FullAdder(carry_stage_1[14], carry_stage_1[15], sum_stage_1[16], carry_stage_2[8], sum_stage_2[8])
    FullAdder2_10 = FullAdder(carry_stage_1[16], sum_stage_1[17], partial_products[7][4], carry_stage_2[9], sum_stage_2[9])
    FullAdder2_11 = FullAdder(carry_stage_1[18], partial_products[6][7], partial_products[7][6], carry_stage_2[10], sum_stage_2[10])
    sl[2] = sum_stage_2[0]

    # Stage 3
    sum_stage_3 = [Signal(intbv(0)[1:]) for i in range(8)]
    carry_stage_3 = [Signal(intbv(0)[1:]) for i in range(8)]

    HalfAdder3_1 = HalfAdder(carry_stage_2[0], sum_stage_2[1], carry_stage_3[0], sum_stage_3[0])
    FullAdder3_2 = FullAdder(carry_stage_2[2], sum_stage_1[6], sum_stage_2[3], carry_stage_3[1], sum_stage_3[1])
    FullAdder3_3 = FullAdder(carry_stage_2[3], sum_stage_1[8], sum_stage_2[4], carry_stage_3[2], sum_stage_3[2])
    FullAdder3_4 = FullAdder(sum_stage_2[5], sum_stage_1[10], sum_stage_1[11], carry_stage_3[3], sum_stage_3[3])
    FullAdder3_5 = FullAdder(carry_stage_1[9], sum_stage_1[13], sum_stage_2[6], carry_stage_3[4], sum_stage_3[4])
    FullAdder3_6 = FullAdder(carry_stage_2[6], sum_stage_1[15], sum_stage_2[7], carry_stage_3[5], sum_stage_3[5])
    FullAdder3_7 = FullAdder(partial_products[3][7], partial_products[7][3], sum_stage_2[8], carry_stage_3[6], sum_stage_3[6])
    FullAdder3_8 = FullAdder(carry_stage_1[17], carry_stage_2[9], sum_stage_1[18], carry_stage_3[7], sum_stage_3[7])
    sl[3] = sum_stage_3[0]

    # Stage 4
    sum_stage_4 = [Signal(intbv(0)[1:]) for i in range(6)]
    carry_stage_4 = [Signal(intbv(0)[1:]) for i in range(6)]

    FullAdder4_1 = FullAdder(carry_stage_3[0], sum_stage_2[2], carry_stage_2[1], carry_stage_4[0], sum_stage_4[0])
    FullAdder4_2 = FullAdder(carry_stage_3[1], sum_stage_3[2], partial_products[0][6], carry_stage_4[1], sum_stage_4[1])
    FullAdder4_3 = FullAdder(carry_stage_3[2], carry_stage_2[4], sum_stage_3[3], carry_stage_4[2], sum_stage_4[2])
    FullAdder4_4 = FullAdder(carry_stage_2[5], sum_stage_3[4], partial_products[4][4], carry_stage_4[3], sum_stage_4[3])
    FullAdder4_5 = FullAdder(carry_stage_3[5], carry_stage_2[7], sum_stage_3[6], carry_stage_4[4], sum_stage_4[4])
    FullAdder4_6 = FullAdder(carry_stage_3[6], carry_stage_2[8], sum_stage_2[9], carry_stage_4[5], sum_stage_4[5])
    sl[4] = sum_stage_4[0]

    # Stage 5
    sum_stage_5 = [Signal(intbv(0)[1:]) for i in range(3)]
    carry_stage_5 = [Signal(intbv(0)[1:]) for i in range(3)]

    HalfAdder5_1 = HalfAdder(carry_stage_4[0], sum_stage_3[1], carry_stage_5[0], sum_stage_5[0])
    FullAdder5_2 = FullAdder(carry_stage_4[2], carry_stage_3[3], sum_stage_4[3], carry_stage_5[1], sum_stage_5[1])
    FullAdder5_3 = FullAdder(carry_stage_4[3], carry_stage_3[4], sum_stage_3[5], carry_stage_5[2], sum_stage_5[2])
    sl[5] = sum_stage_5[0]

    # Stage 6
    sum_stage_6 = Signal(intbv(0)[1:])
    carry_stage_6 = Signal(intbv(0)[1:])

    HalfAdder6_1 = HalfAdder(carry_stage_5[0], sum_stage_4[1], carry_stage_6, sum_stage_6)
    sl[6] = sum_stage_6

    # Stage 7 (1 Carry Look Ahead Adder to generate SL: 7, 8, 9, 10)
    input_1_stage_7 = [sum_stage_4[2], sum_stage_5[1], sum_stage_5[2], sum_stage_4[4]]
    input_2_stage_7 = [carry_stage_4[1], Signal(intbv(0)[1:]), carry_stage_5[1], carry_stage_5[2]]
    output_stage_7 = Signal(intbv(0)[4:])
    cout_sl_10 = Signal(intbv(0)[1:])

    ClaAdder_4_Bit_1 = Adder4b(input_1_stage_7, input_2_stage_7, carry_stage_6, cout_sl_10, output_stage_7)
    sl[7] = output_stage_7(0)
    sl[8] = output_stage_7(1)
    sl[9] = output_stage_7(2)
    sl[10] = output_stage_7(3)

    # Stage 8 (1 Carry Look Ahead Adder to generate SL: 11, 12, 13, 14, 15)
    input_1_stage_8 = [sum_stage_4[5], sum_stage_3[7], sum_stage_2[10], partial_products[7][7]]
    input_2_stage_8 = [carry_stage_4[4], carry_stage_4[5], carry_stage_3[7], carry_stage_2[10]]
    output_stage_8 = Signal(intbv(0)[4:])
    cout_sl_15 = Signal(intbv(0)[1:])

    ClaAdder_4_Bit_2 = Adder4b(input_1_stage_8, input_2_stage_8, cout_sl_10, cout_sl_15, output_stage_8)
    sl[11] = output_stage_8(0)
    sl[12] = output_stage_8(1)
    sl[13] = output_stage_8(2)
    sl[14] = output_stage_8(3)
    sl[15] = cout_sl_15
    sc = ConcatSignal(*reversed(sl))

    @always_comb
    def wt_multiplier():
        mult16.next = sc

    return instances()


@block
def test_multiplier():
    a = Signal(intbv(4)[8:])
    b = Signal(intbv(9)[8:])
    mult16 = Signal(modbv(0)[16:])

    multiplier_1 = WallaceTreeMultiplier(a, b, mult16)

    @instance
    def stimulus():
        print("a b mult")
        yield delay(10)
        print("%s %s %s" % (int(a), int(b), int(mult16)))

    return multiplier_1, stimulus


tb = test_multiplier()
tb.run_sim()
