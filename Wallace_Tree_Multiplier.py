from myhdl import *
import random

# random.seed(9)
randrange = random.randrange


@block
def WallaceTreeMultiplier(a, b, mult16, clk):
    @always(clk.posedge)
    def multiplier_16():
        sl = [Signal(intbv(0)[1:]) for i in range(16)]

        # pre-processing unit to better process negative inputs and handle all unsavoury error
        # due to no sign bit extension.
        s_b_req = a(7) ^ b(7)
        a_c = [Signal(intbv(0)[1:]) for i in range(8)]
        b_c = [Signal(intbv(0)[1:]) for i in range(8)]
        a_c_r = [Signal(intbv(0)[1:]) for i in range(8)]
        b_c_r = [Signal(intbv(0)[1:]) for i in range(8)]
        p0, p1, p2, p3, p4, p5, p6, p7 = [Signal(intbv(0)[1:]) for i in range(8)]
        g0, g1, g2, g3, g4, g5, g6, g7 = [Signal(intbv(0)[1:]) for i in range(8)]
        c1, c2, c3, c4, c5, c6, c7 = [Signal(intbv(0)[1:]) for i in range(7)]

        res_c = [Signal(intbv(0)[1:]) for i in range(8)]
        res_c_r = [Signal(intbv(0)[1:]) for i in range(8)]

        if a(7) == 1:
            for i in range(8):
                a_c[i] = not a(i)
            p0 = a_c[0] ^ Signal(intbv(1)[1:])
            a_c_r[0] = p0
            g0 = a_c[0] and Signal(intbv(1)[1:])

            c1 = g0
            p1 = a_c[1] ^ Signal(intbv(0)[1:])
            a_c_r[1] = p1 ^ c1
            g1 = a_c[1] and Signal(intbv(0)[1:])

            c2 = g1 or (p1 and g0)
            p2 = a_c[2] ^ Signal(intbv(0)[1:])
            a_c_r[2] = p2 ^ c2
            g2 = a_c[2] and Signal(intbv(0)[1:])

            c3 = g2 or (p2 and g1) or (p2 and p1 and g0)
            p3 = a_c[3] ^ Signal(intbv(0)[1:])
            a_c_r[3] = p3 ^ c3
            g3 = a_c[3] and Signal(intbv(0)[1:])

            c4 = g3 or (p3 and g2) or (p3 and p2 and g1) or (p3 and p2 and p1 and g0)
            p4 = a_c[4] ^ Signal(intbv(0)[1:])
            a_c_r[4] = p4 ^ c4
            g4 = a_c[4] and Signal(intbv(0)[1:])

            c5 = g4 or (p4 and c4)
            p5 = a_c[5] ^ Signal(intbv(0)[1:])
            a_c_r[5] = p5 ^ c5
            g5 = a_c[5] and Signal(intbv(0)[1:])

            c6 = g5 or (p5 and g4) or (p5 and p4 and c4)
            p6 = a_c[6] ^ Signal(intbv(0)[1:])
            a_c_r[6] = p6 ^ c6
            g6 = a_c[6] and Signal(intbv(0)[1:])

            c7 = g6 or (p6 and g5) or (p6 and p5 and g4) or (c4 and p4 and p5 and p6)
            p7 = a_c[7] ^ Signal(intbv(0)[1:])
            a_c_r[7] = p7 ^ c7
        else:
            for i in range(8):
                a_c_r[i] = a(i)

        if b(7) == 1:
            for i in range(8):
                b_c[i] = not b(i)
            p0 = b_c[0] ^ Signal(intbv(1)[1:])
            b_c_r[0] = p0
            g0 = b_c[0] and Signal(intbv(1)[1:])

            c1 = g0
            p1 = b_c[1] ^ Signal(intbv(0)[1:])
            b_c_r[1] = p1 ^ c1
            g1 = b_c[1] and Signal(intbv(0)[1:])

            c2 = g1 or (p1 and g0)
            p2 = b_c[2] ^ Signal(intbv(0)[1:])
            b_c_r[2] = p2 ^ c2
            g2 = b_c[2] and Signal(intbv(0)[1:])

            c3 = g2 or (p2 and g1) or (p2 and p1 and g0)
            p3 = b_c[3] ^ Signal(intbv(0)[1:])
            b_c_r[3] = p3 ^ c3
            g3 = b_c[3] and Signal(intbv(0)[1:])

            c4 = g3 or (p3 and g2) or (p3 and p2 and g1) or (p3 and p2 and p1 and g0)
            p4 = b_c[4] ^ Signal(intbv(0)[1:])
            b_c_r[4] = p4 ^ c4
            g4 = b_c[4] and Signal(intbv(0)[1:])

            c5 = g4 or (p4 and c4)
            p5 = b_c[5] ^ Signal(intbv(0)[1:])
            b_c_r[5] = p5 ^ c5
            g5 = b_c[5] and Signal(intbv(0)[1:])

            c6 = g5 or (p5 and g4) or (p5 and p4 and c4)
            p6 = b_c[6] ^ Signal(intbv(0)[1:])
            b_c_r[6] = p6 ^ c6
            g6 = b_c[6] and Signal(intbv(0)[1:])

            c7 = g6 or (p6 and g5) or (p6 and p5 and g4) or (c4 and p4 and p5 and p6)
            p7 = b_c[7] ^ Signal(intbv(0)[1:])
            b_c_r[7] = p7 ^ c7
        else:
            for i in range(8):
                b_c_r[i] = b(i)

        # PARTIAL PRODUCTS : developing a memory containing the partial products
        # all partial products are independent so can be implemented using combational logic
        partial_products = [[Signal(intbv(0)[1:]) for i in range(8)] for j in range(8)]
        for i in range(8):
            for j in range(8):
                partial_products[i][j] = Signal(intbv(int(a_c_r[i] and b_c_r[j]))[1:])

        # Stage 1
        sum_stage_1 = [Signal(intbv(0)[1:]) for i in range(19)]
        carry_stage_1 = [Signal(intbv(0)[1:]) for i in range(19)]

        sl[0] = partial_products[0][0]
        sum_stage_1[0] = partial_products[1][0] ^ partial_products[0][1]
        carry_stage_1[0] = partial_products[1][0] and partial_products[0][1]
        sum_stage_1[1] = partial_products[2][0] ^ partial_products[1][1] ^ partial_products[0][2]
        carry_stage_1[1] = (partial_products[2][0] and partial_products[1][1]) or (
                partial_products[2][0] and partial_products[0][2]) or (
                                   partial_products[1][1] and partial_products[0][2])
        sum_stage_1[2] = partial_products[3][0] ^ partial_products[1][2] ^ partial_products[2][1]
        carry_stage_1[2] = (partial_products[3][0] and partial_products[1][2]) or (
                partial_products[3][0] and partial_products[2][1]) or (
                                   partial_products[1][2] and partial_products[2][1])
        sum_stage_1[3] = partial_products[3][1] ^ partial_products[4][0] ^ partial_products[0][4]
        carry_stage_1[3] = (partial_products[3][1] and partial_products[4][0]) or (
                partial_products[3][1] and partial_products[0][4]) or (
                                   partial_products[4][0] and partial_products[0][4])
        sum_stage_1[4] = partial_products[1][3] ^ partial_products[2][2]
        carry_stage_1[4] = partial_products[1][3] and partial_products[2][2]
        sum_stage_1[5] = partial_products[5][0] ^ partial_products[4][1] ^ partial_products[0][5]
        carry_stage_1[5] = (partial_products[5][0] and partial_products[4][1]) or (
                partial_products[5][0] and partial_products[0][5]) or (
                                   partial_products[4][1] and partial_products[0][5])
        sum_stage_1[6] = partial_products[1][4] ^ partial_products[2][3] ^ partial_products[3][2]
        carry_stage_1[6] = (partial_products[1][4] and partial_products[2][3]) or (
                partial_products[1][4] and partial_products[3][2]) or (
                                   partial_products[2][3] and partial_products[3][2])
        sum_stage_1[7] = partial_products[2][4] ^ partial_products[3][3] ^ partial_products[4][2]
        carry_stage_1[7] = (partial_products[2][4] and partial_products[3][3]) or (
                partial_products[2][4] and partial_products[4][2]) or (
                                   partial_products[3][3] and partial_products[4][2])
        sum_stage_1[8] = partial_products[5][1] ^ partial_products[1][5] ^ partial_products[6][0]
        carry_stage_1[8] = (partial_products[5][1] and partial_products[1][5]) or (
                partial_products[5][1] and partial_products[6][0]) or (
                                   partial_products[1][5] and partial_products[6][0])
        sum_stage_1[9] = partial_products[2][5] ^ partial_products[4][3] ^ partial_products[3][4]
        carry_stage_1[9] = (partial_products[2][5] and partial_products[4][3]) or (
                partial_products[2][5] and partial_products[3][4]) or (
                                   partial_products[4][3] and partial_products[3][4])
        sum_stage_1[10] = partial_products[5][2] ^ partial_products[1][6] ^ partial_products[6][1]
        carry_stage_1[10] = (partial_products[5][2] and partial_products[1][6]) or (
                partial_products[5][2] and partial_products[6][1]) or (
                                    partial_products[1][6] and partial_products[6][1])
        sum_stage_1[11] = partial_products[7][0] ^ partial_products[0][7]
        carry_stage_1[11] = partial_products[7][0] and partial_products[0][7]
        sum_stage_1[12] = partial_products[2][6] ^ partial_products[5][3] ^ partial_products[6][2]
        carry_stage_1[12] = (partial_products[2][6] and partial_products[5][3]) or (
                partial_products[2][6] and partial_products[6][2]) or (
                                    partial_products[5][3] and partial_products[6][2])
        sum_stage_1[13] = partial_products[7][1] ^ partial_products[1][7] ^ partial_products[3][5]
        carry_stage_1[13] = (partial_products[7][1] and partial_products[1][7]) or (
                partial_products[7][1] and partial_products[3][5]) or (
                                    partial_products[1][7] and partial_products[3][5])
        sum_stage_1[14] = partial_products[4][5] ^ partial_products[5][4] ^ partial_products[3][6]
        carry_stage_1[14] = (partial_products[4][5] and partial_products[5][4]) or (
                partial_products[4][5] and partial_products[3][6]) or (
                                    partial_products[5][4] and partial_products[3][6])
        sum_stage_1[15] = partial_products[2][7] ^ partial_products[6][3] ^ partial_products[7][2]
        carry_stage_1[15] = (partial_products[2][7] and partial_products[6][3]) or (
                partial_products[2][7] and partial_products[7][2]) or (
                                    partial_products[6][3] and partial_products[7][2])
        sum_stage_1[16] = partial_products[6][4] ^ partial_products[5][5] ^ partial_products[4][6]
        carry_stage_1[16] = (partial_products[6][4] and partial_products[5][5]) or (
                partial_products[6][4] and partial_products[4][6]) or (
                                    partial_products[5][5] and partial_products[4][6])
        sum_stage_1[17] = partial_products[6][5] ^ partial_products[5][6] ^ partial_products[4][7]
        carry_stage_1[17] = (partial_products[6][5] and partial_products[5][6]) or (
                partial_products[6][5] and partial_products[4][7]) or (
                                    partial_products[5][6] and partial_products[4][7])
        sum_stage_1[18] = partial_products[7][5] ^ partial_products[6][6] ^ partial_products[5][7]
        carry_stage_1[18] = (partial_products[7][5] and partial_products[6][6]) or (
                partial_products[7][5] and partial_products[5][7]) or (
                                    partial_products[6][6] and partial_products[5][7])
        sl[1] = sum_stage_1[0]

        # Stage 2
        sum_stage_2 = [Signal(intbv(0)[1:]) for i in range(11)]
        carry_stage_2 = [Signal(intbv(0)[1:]) for i in range(11)]

        sum_stage_2[0] = carry_stage_1[0] ^ sum_stage_1[1]
        carry_stage_2[0] = carry_stage_1[0] and sum_stage_1[1]
        sum_stage_2[1] = partial_products[0][3] ^ carry_stage_1[1] ^ sum_stage_1[2]
        carry_stage_2[1] = (partial_products[0][3] and carry_stage_1[1]) or (
                partial_products[0][3] and sum_stage_1[2]) or (
                                   carry_stage_1[1] and sum_stage_1[2])
        sum_stage_2[2] = carry_stage_1[2] ^ sum_stage_1[3] ^ sum_stage_1[4]
        carry_stage_2[2] = (carry_stage_1[2] and sum_stage_1[3]) or (carry_stage_1[2] and sum_stage_1[4]) or (
                sum_stage_1[3] and sum_stage_1[4])
        sum_stage_2[3] = carry_stage_1[3] ^ carry_stage_1[4] ^ sum_stage_1[5]
        carry_stage_2[3] = (carry_stage_1[3] and carry_stage_1[4]) or (carry_stage_1[3] and sum_stage_1[5]) or (
                carry_stage_1[4] and sum_stage_1[5])
        sum_stage_2[4] = carry_stage_1[5] ^ carry_stage_1[6] ^ sum_stage_1[7]
        carry_stage_2[4] = (carry_stage_1[5] and carry_stage_1[6]) or (carry_stage_1[5] and sum_stage_1[7]) or (
                carry_stage_1[6] and sum_stage_1[7])
        sum_stage_2[5] = carry_stage_1[7] ^ carry_stage_1[8] ^ sum_stage_1[9]
        carry_stage_2[5] = (carry_stage_1[7] and carry_stage_1[8]) or (carry_stage_1[7] and sum_stage_1[9]) or (
                carry_stage_1[8] and sum_stage_1[9])
        sum_stage_2[6] = carry_stage_1[10] ^ carry_stage_1[11] ^ sum_stage_1[12]
        carry_stage_2[6] = (carry_stage_1[10] and carry_stage_1[11]) or (carry_stage_1[10] and sum_stage_1[12]) or (
                carry_stage_1[11] and sum_stage_1[12])
        sum_stage_2[7] = carry_stage_1[12] ^ carry_stage_1[13] ^ sum_stage_1[14]
        carry_stage_2[7] = (carry_stage_1[12] and carry_stage_1[13]) or (carry_stage_1[12] and sum_stage_1[14]) or (
                carry_stage_1[13] and sum_stage_1[14])
        sum_stage_2[8] = carry_stage_1[14] ^ carry_stage_1[15] ^ sum_stage_1[16]
        carry_stage_2[8] = (carry_stage_1[14] and carry_stage_1[15]) or (carry_stage_1[14] and sum_stage_1[16]) or (
                carry_stage_1[15] and sum_stage_1[16])
        sum_stage_2[9] = carry_stage_1[16] ^ sum_stage_1[17] ^ partial_products[7][4]
        carry_stage_2[9] = (carry_stage_1[16] and sum_stage_1[17]) or (
                carry_stage_1[16] and partial_products[7][4]) or (
                                   sum_stage_1[17] and partial_products[7][4])
        sum_stage_2[10] = carry_stage_1[18] ^ partial_products[6][7] ^ partial_products[7][6]
        carry_stage_2[10] = (carry_stage_1[18] and partial_products[6][7]) or (
                carry_stage_1[18] and partial_products[7][6]) or (partial_products[6][7] and partial_products[7][6])
        sl[2] = sum_stage_2[0]

        # Stage 3
        sum_stage_3 = [Signal(intbv(0)[1:]) for i in range(8)]
        carry_stage_3 = [Signal(intbv(0)[1:]) for i in range(8)]

        sum_stage_3[0] = carry_stage_2[0] ^ sum_stage_2[1]
        carry_stage_3[0] = carry_stage_2[0] and sum_stage_2[1]
        sum_stage_3[1] = carry_stage_2[2] ^ sum_stage_1[6] ^ sum_stage_2[3]
        carry_stage_3[1] = (carry_stage_2[2] and sum_stage_1[6]) or (carry_stage_2[2] and sum_stage_2[3]) or (
                sum_stage_1[6] and sum_stage_2[3])
        sum_stage_3[2] = carry_stage_2[3] ^ sum_stage_1[8] ^ sum_stage_2[4]
        carry_stage_3[2] = (carry_stage_2[3] and sum_stage_1[8]) or (carry_stage_2[3] and sum_stage_2[4]) or (
                sum_stage_1[8] and sum_stage_2[4])
        sum_stage_3[3] = sum_stage_2[5] ^ sum_stage_1[10] ^ sum_stage_1[11]
        carry_stage_3[3] = (sum_stage_2[5] and sum_stage_1[10]) or (sum_stage_2[5] and sum_stage_1[11]) or (
                sum_stage_1[10] and sum_stage_1[11])
        sum_stage_3[4] = carry_stage_1[9] ^ sum_stage_1[13] ^ sum_stage_2[6]
        carry_stage_3[4] = (carry_stage_1[9] and sum_stage_1[13]) or (carry_stage_1[9] and sum_stage_2[6]) or (
                sum_stage_1[13] and sum_stage_2[6])
        sum_stage_3[5] = carry_stage_2[6] ^ sum_stage_1[15] ^ sum_stage_2[7]
        carry_stage_3[5] = (carry_stage_2[6] and sum_stage_1[15]) or (carry_stage_2[6] and sum_stage_2[7]) or (
                sum_stage_1[15] and sum_stage_2[7])
        sum_stage_3[6] = partial_products[3][7] ^ partial_products[7][3] ^ sum_stage_2[8]
        carry_stage_3[6] = (partial_products[3][7] and partial_products[7][3]) or (
                partial_products[3][7] and sum_stage_2[8]) or (partial_products[7][3] and sum_stage_2[8])
        sum_stage_3[7] = carry_stage_1[17] ^ carry_stage_2[9] ^ sum_stage_1[18]
        carry_stage_3[7] = (carry_stage_1[17] and carry_stage_2[9]) or (carry_stage_1[17] and sum_stage_1[18]) or (
                carry_stage_2[9] and sum_stage_1[18])

        sl[3] = sum_stage_3[0]

        # Stage 4
        sum_stage_4 = [Signal(intbv(0)[1:]) for i in range(6)]
        carry_stage_4 = [Signal(intbv(0)[1:]) for i in range(6)]

        sum_stage_4[0] = carry_stage_3[0] ^ sum_stage_2[2] ^ carry_stage_2[1]
        carry_stage_4[0] = (carry_stage_3[0] and sum_stage_2[2]) or (carry_stage_3[0] and carry_stage_2[1]) or (
                sum_stage_2[2] and carry_stage_2[1])
        sum_stage_4[1] = carry_stage_3[1] ^ sum_stage_3[2] ^ partial_products[0][6]
        carry_stage_4[1] = (carry_stage_3[1] and sum_stage_3[2]) or (carry_stage_3[1] and partial_products[0][6]) or (
                sum_stage_3[2] and partial_products[0][6])
        sum_stage_4[2] = carry_stage_3[2] ^ carry_stage_2[4] ^ sum_stage_3[3]
        carry_stage_4[2] = (carry_stage_3[2] and carry_stage_2[4]) or (carry_stage_3[2] and sum_stage_3[3]) or (
                carry_stage_2[4] and sum_stage_3[3])
        sum_stage_4[3] = carry_stage_2[5] ^ sum_stage_3[4] ^ partial_products[4][4]
        carry_stage_4[3] = (carry_stage_2[5] and sum_stage_3[4]) or (carry_stage_2[5] and partial_products[4][4]) or (
                sum_stage_3[4] and partial_products[4][4])
        sum_stage_4[4] = carry_stage_3[5] ^ carry_stage_2[7] ^ sum_stage_3[6]
        carry_stage_4[4] = (carry_stage_3[5] and carry_stage_2[7]) or (carry_stage_3[5] and sum_stage_3[6]) or (
                carry_stage_2[7] and sum_stage_3[6])
        sum_stage_4[5] = carry_stage_3[6] ^ carry_stage_2[8] ^ sum_stage_2[9]
        carry_stage_4[5] = (carry_stage_3[6] and carry_stage_2[8]) or (carry_stage_3[6] and sum_stage_2[9]) or (
                carry_stage_2[8] and sum_stage_2[9])

        sl[4] = sum_stage_4[0]

        # Stage 5
        sum_stage_5 = [Signal(intbv(0)[1:]) for i in range(3)]
        carry_stage_5 = [Signal(intbv(0)[1:]) for i in range(3)]

        sum_stage_5[0] = carry_stage_4[0] ^ sum_stage_3[1]
        carry_stage_5[0] = carry_stage_4[0] and sum_stage_3[1]
        sum_stage_5[1] = carry_stage_4[2] ^ carry_stage_3[3] ^ sum_stage_4[3]
        carry_stage_5[1] = (carry_stage_4[2] and carry_stage_3[3]) or (carry_stage_4[2] and sum_stage_4[3]) or (
                carry_stage_3[3] and sum_stage_4[3])
        sum_stage_5[2] = carry_stage_4[3] ^ carry_stage_3[4] ^ sum_stage_3[5]
        carry_stage_5[2] = (carry_stage_4[3] and carry_stage_3[4]) or (carry_stage_4[3] and sum_stage_3[5]) or (
                carry_stage_3[4] and sum_stage_3[5])

        sl[5] = sum_stage_5[0]

        # Stage 6
        sum_stage_6 = Signal(intbv(0)[1:])
        carry_stage_6 = Signal(intbv(0)[1:])

        sum_stage_6 = carry_stage_5[0] ^ sum_stage_4[1]
        carry_stage_6 = carry_stage_5[0] and sum_stage_4[1]

        sl[6] = sum_stage_6

        # stage 7 : carry look ahead adder for propagate region additions
        p0 = sum_stage_4[2] ^ carry_stage_4[1]
        sl[7] = p0 ^ carry_stage_6
        g0 = sum_stage_4[2] and carry_stage_4[1]

        c1 = g0 or (p0 and carry_stage_6)
        p1 = sum_stage_5[1] ^ Signal(intbv(0)[1:])
        sl[8] = p1 ^ c1
        g1 = sum_stage_5[1] and Signal(intbv(0)[1:])

        c2 = g1 or (p1 and c1)
        p2 = sum_stage_5[2] ^ carry_stage_5[1]
        sl[9] = p2 ^ c2
        g2 = sum_stage_5[2] and carry_stage_5[1]

        c3 = g2 or (p2 and c2)
        p3 = sum_stage_4[4] ^ carry_stage_5[2]
        sl[10] = p3 ^ c3
        g3 = sum_stage_4[4] and carry_stage_5[2]

        c4 = g3 or (p3 and c3)
        p4 = sum_stage_4[5] ^ carry_stage_4[4]
        sl[11] = p4 ^ c4
        g4 = sum_stage_4[5] and carry_stage_4[4]

        c5 = g4 or (p4 and c4)
        p5 = sum_stage_3[7] ^ carry_stage_4[5]
        sl[12] = p5 ^ c5
        g5 = sum_stage_3[7] and carry_stage_4[5]

        c6 = g5 or (p5 and c5)
        p6 = sum_stage_2[10] ^ carry_stage_3[7]
        sl[13] = p6 ^ c6
        g6 = sum_stage_2[10] and carry_stage_3[7]

        c7 = g6 or (p6 and c6)
        p7 = partial_products[7][7] ^ carry_stage_2[10]
        sl[14] = p7 ^ c7
        g7 = partial_products[7][7] and carry_stage_2[10]

        sl[15] = g7 or (p7 and c7)

        # post-processing unit to handle out of 8 bit bound scenarios and limit the output
        isGreater = Signal(bool(0))
        isGreater = (sl[15] or sl[14] or sl[13] or sl[12] or sl[11] or sl[10] or sl[9] or sl[8] or (sl[7] and (sl[6] or sl[5] or sl[4] or sl[3] or sl[2] or sl[1] or sl[0])))

        #
        if sl[7] == 1 and (not sl[15]) and (not sl[14]) and (not sl[13]) and (not sl[12]) and (not sl[11]) and (not sl[10]) and (not sl[9]) and (not sl[8]) and (not sl[6]) and (not sl[5]) and (not sl[4]) and (not sl[3]) and (not sl[2]) and (not sl[1]) and (not sl[0]):
            if s_b_req:
                mult16.next = intbv(-128)[8:].signed()
            else:
                mult16.next = intbv(127)[8:].signed()
        else:
            if isGreater:
                if s_b_req:
                    mult16.next = intbv(-128)[8:].signed()
                else:
                    mult16.next = intbv(127)[8:].signed()
            else:
                if s_b_req:
                    for i in range(8):
                        res_c[i] = not sl[i]
                    p0 = res_c[0] ^ Signal(intbv(1)[1:])
                    res_c_r[0] = p0
                    g0 = res_c[0] and Signal(intbv(1)[1:])

                    c1 = g0
                    p1 = res_c[1] ^ Signal(intbv(0)[1:])
                    res_c_r[1] = p1 ^ c1
                    g1 = res_c[1] and Signal(intbv(0)[1:])

                    c2 = g1 or (p1 and g0)
                    p2 = res_c[2] ^ Signal(intbv(0)[1:])
                    res_c_r[2] = p2 ^ c2
                    g2 = res_c[2] and Signal(intbv(0)[1:])

                    c3 = g2 or (p2 and g1) or (p2 and p1 and g0)
                    p3 = res_c[3] ^ Signal(intbv(0)[1:])
                    res_c_r[3] = p3 ^ c3
                    g3 = res_c[3] and Signal(intbv(0)[1:])

                    c4 = g3 or (p3 and g2) or (p3 and p2 and g1) or (p3 and p2 and p1 and g0)
                    p4 = res_c[4] ^ Signal(intbv(0)[1:])
                    res_c_r[4] = p4 ^ c4
                    g4 = res_c[4] and Signal(intbv(0)[1:])

                    c5 = g4 or (p4 and c4)
                    p5 = res_c[5] ^ Signal(intbv(0)[1:])
                    res_c_r[5] = p5 ^ c5
                    g5 = res_c[5] and Signal(intbv(0)[1:])

                    c6 = g5 or (p5 and g4) or (p5 and p4 and c4)
                    p6 = res_c[6] ^ Signal(intbv(0)[1:])
                    res_c_r[6] = p6 ^ c6
                    g6 = res_c[6] and Signal(intbv(0)[1:])

                    c7 = g6 or (p6 and g5) or (p6 and p5 and g4) or (c4 and p4 and p5 and p6)
                    p7 = res_c[7] ^ Signal(intbv(0)[1:])
                    res_c_r[7] = p7 ^ c7
                    mult16.next = intbv(intbv(
                        str(int(res_c_r[7])) + "_" + str(int(res_c_r[6])) + "_" + str(int(res_c_r[5])) + "_" + str(int(res_c_r[4])) + "_" + str(
                            int(res_c_r[3])) + "_" + str(int(res_c_r[2])) + "_" + str(int(res_c_r[1])) + "_" + str(int(res_c_r[0])))[
                                        8:]).signed()
                else:
                    mult16.next = intbv(intbv(
                        str(int(sl[7])) + "_" + str(int(sl[6])) + "_" + str(int(sl[5])) + "_" + str(int(sl[4])) + "_" + str(
                            int(sl[3])) + "_" + str(int(sl[2])) + "_" + str(int(sl[1])) + "_" + str(int(sl[0])))[
                          8:]).signed()

    return multiplier_16


@block
def test_multiplier():
    clk = Signal(bool(0))
    a, b = [Signal(intbv(0)[8:].signed()) for i in range(2)]
    mult16 = Signal(intbv(0)[8:].signed())
    dff_inst = WallaceTreeMultiplier(a, b, mult16, clk)

    @always(delay(10))
    def clkgen():
        clk.next = not clk

    @always(clk.negedge)
    def stimulus():
        # test upper bounds
        # a.next = random.randint(-128, 127)
        # b.next = random.randint(-128, 127)

        # test lower bounds
        a.next = random.randint(-16, 16)
        b.next = random.randint(-16, 16)
        print(str(int(a)) + " * " + str(int(b)) + " = " + str(int(mult16)))

        if -128 < int(a * b) < 127:
            assert int(a*b) == int(mult16)
        if int(a*b) < -128:
            assert int(mult16) == -128
        if int(a*b) > 127:
            assert int(mult16) == 127

    return dff_inst, clkgen, stimulus


def simulate(timesteps):
    simInst = test_multiplier()
    simInst.config_sim(trace=True, tracebackup=False)
    simInst.run_sim(timesteps, quiet=0)


simulate(2000)
