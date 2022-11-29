from myhdl import *


# Utility functions, not related to hardware implementations but are used to reduce lines of code instead of statically
# adding pre-calculated indexes.

def pooling1ins(relu1out, number):
    x = int(number / 6) * 6 * 4 + (number % 6) * 2
    pooling1in = [relu1out[x], relu1out[x + 1], relu1out[x + 12], relu1out[x + 13]]
    return pooling1in


def convo2ins(pooling1out, number):
    x = number + int(number / 4) * 2
    submat = [[Signal(0) for i in range(3)] for j in range(3)]
    submat[0][0] = pooling1out[x]
    submat[0][1] = pooling1out[x + 1]
    submat[0][2] = pooling1out[x + 2]
    submat[1][0] = pooling1out[x + 6]
    submat[1][1] = pooling1out[x + 7]
    submat[1][2] = pooling1out[x + 8]
    submat[2][0] = pooling1out[x + 12]
    submat[2][1] = pooling1out[x + 13]
    submat[2][2] = pooling1out[x + 14]
    return submat


def pooling2ins(relu2out, number):
    x = int(number / 2) * 2 * 4 + (number % 2) * 2
    pooling2in = [relu2out[x], relu2out[x + 1], relu2out[x + 4], relu2out[x + 5]]
    return pooling2in


# Hardware code starts from here

@block
def CNN():
    # Input matrix

    image = [[0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
             [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
             [0, 0, -10, 2, 3, 2, 1, 5, 4, 3, 5, 2, 0, 0],
             [0, 0, 3, 2, 4, 1, 5, 4, 3, 2, 1, 3, 0, 0],
             [0, 0, 2, 2, 1, 3, 4, 2, 3, 2, 2, 3, 0, 0],
             [0, 0, 1, 1, 2, 2, 4, 3, 4, 2, 1, 3, 0, 0],
             [0, 0, 5, 4, 2, 2, 1, 2, 4, 2, 2, 1, 0, 0],
             [0, 0, 5, 2, 4, 2, 1, 0, 1, 2, 4, 2, 0, 0],
             [0, 0, 3, 3, 2, 3, 4, 1, 0, 0, 1, 2, 0, 0],
             [0, 0, 1, 1, 1, 4, 3, 4, 5, 2, 1, 3, 0, 0],
             [0, 0, 3, 1, 1, 4, 1, 5, 3, 3, 2, 1, 0, 0],
             [0, 0, 4, 4, 4, 2, 3, 4, 2, 2, 2, 5, 0, 0],
             [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
             [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0]]

    # global variables used in hardware, will be converted in ahrdware as wires.

    submat = [[[Signal(0) for i in range(3)] for j in range(3)] for k in range(12 * 12)]
    for i in range(0, 12):
        for j in range(0, 12):
            k = i * 12 + j
            submat[k][0][0] = image[i][j]
            submat[k][0][1] = image[i][j + 1]
            submat[k][0][2] = image[i][j + 2]
            submat[k][1][0] = image[i + 1][j]
            submat[k][1][1] = image[i + 1][j + 1]
            submat[k][1][2] = image[i + 1][j + 2]
            submat[k][2][0] = image[i + 2][j]
            submat[k][2][1] = image[i + 2][j + 1]
            submat[k][2][2] = image[i + 2][j + 2]

    kernel1 = [[1, 2, 1], [1, 1, 1], [1, 2, 3]]
    convo1out = [Signal(intbv(0)[8:].signed()) for i in range(12 * 12)]
    relu1out = [Signal(0) for i in range(12 * 12)]
    pooling1out = [Signal(0) for i in range(6 * 6)]
    kernel2 = [[1, 1, -2], [0, 2, -3], [2, -3, 0]]
    convo2out = [Signal(0) for i in range(4 * 4)]
    relu2out = [Signal(0) for i in range(4 * 4)]
    pooling2out = [Signal(0) for i in range(2 * 2)]
    fc1weights = [[-2, 1, 1, 1], [1, -2, 1, 1], [1, 1, -2, 1], [1, 1, 1, -2]]
    fc2weights = [[3, 1, 1, 1], [1, 2, 1, 1], [1, 1, 3, 1], [1, 1, 1, 3]]
    fc1out = [Signal(0) for i in range(4)]
    fc2out = [Signal(0) for i in range(4)]
    a = [Signal(intbv(0)[8:].signed()) for i in range(9)]
    b = [Signal(intbv(0)[8:].signed()) for i in range(9)]
    mult16 = [Signal(intbv(0)[8:].signed()) for i in range(9)]
    adders4 = [Signal(intbv(0)[8:].signed()) for i in range(4)]
    adders2 = [Signal(intbv(0)[8:].signed()) for i in range(2)]
    adder1 = Signal(intbv(0)[8:].signed())
    addrFin = Signal(intbv(0)[8:].signed())
    c, d, sum8 = [Signal(intbv(0)[8:].signed()) for i in range(3)]
    c0, c8 = [Signal(intbv(0)[1:]) for i in range(2)]
    convo1out_2 = [Signal(intbv(0)[8:].signed()) for i in range(12 * 12)]

    clk = Signal(bool(0))
    enableConvolution1 = Signal(1)
    indicingHelper = Signal(0)
    enableRelu1 = Signal(0)
    enablePooling1 = Signal(0)
    enableConvolution2 = Signal(0)
    enableRelu2 = Signal(0)
    enablePooling2 = Signal(0)
    conv2number = Signal(0)
    enableFc1 = Signal(0)
    enableFc2 = Signal(0)

    # Clock generator

    @always(delay(10))
    def clkgen():
        clk.next = not clk

    # Convolution layer 1

    @block
    def convo1_unit(submatrix, number):
        @always(clk.posedge)
        def convo1_calculation():
            if enableConvolution1 == 1:
                a[0].next = kernel1[0][0]
                b[0].next = submat[number][0][0]
                a[1].next = kernel1[0][1]
                b[1].next = submat[number][0][1]
                a[2].next = kernel1[0][2]
                b[2].next = submat[number][0][2]
                a[3].next = kernel1[1][0]
                b[3].next = submat[number][1][0]
                a[4].next = kernel1[1][1]
                b[4].next = submat[number][1][1]
                a[5].next = kernel1[1][2]
                b[5].next = submat[number][1][2]
                a[6].next = kernel1[2][0]
                b[6].next = submat[number][2][0]
                a[7].next = kernel1[2][1]
                b[7].next = submat[number][2][1]
                a[8].next = kernel1[2][2]
                b[8].next = submat[number][2][2]

        return convo1_calculation

    # Relu layer 1

    @block
    def relu1_unit(relu1in, number):
        @always(clk.posedge)
        def relu1_calculation():
            if enableRelu1 == 1:
                if relu1in > 0:
                    relu1out[number].next = relu1in
                else:
                    relu1out[number].next = 0
                if number == 0:
                    enableRelu1.next = 0
                    enablePooling1.next = 1

        return relu1_calculation

    # Pooling layer 1

    @block
    def pooling1_unit(pooling1in, number):
        @always(clk.posedge)
        def pooling1_calculation():
            if enablePooling1 == 1:
                pooling1out[number].next = max(pooling1in)
                if number == 35:
                    enablePooling1.next = 0
                    enableConvolution2.next = 1

        return pooling1_calculation

    # Convolution layer 2

    @block
    def convo2_unit(mat, number):
        @always(clk.posedge)
        def convo2_calculation():
            if enableConvolution2 == 1:
                submat = convo2ins(pooling1out, number)
                a[0].next = kernel2[0][0]
                b[0].next = submat[0][0]
                a[1].next = kernel2[0][1]
                b[1].next = submat[0][1]
                a[2].next = kernel2[0][2]
                b[2].next = submat[0][2]
                a[3].next = kernel2[1][0]
                b[3].next = submat[1][0]
                a[4].next = kernel2[1][1]
                b[4].next = submat[1][1]
                a[5].next = kernel2[1][2]
                b[5].next = submat[1][2]
                a[6].next = kernel2[2][0]
                b[6].next = submat[2][0]
                a[7].next = kernel2[2][1]
                b[7].next = submat[2][1]
                a[8].next = kernel2[2][2]
                b[8].next = submat[2][2]

        return convo2_calculation

    # Relu layer 2

    @block
    def relu2_unit(relu2in, number):
        @always(clk.posedge)
        def relu2_calculation():

            if enableRelu2 == 1:
                if relu2in > 0:
                    relu2out[number].next = relu2in
                else:
                    relu2out[number].next = 0
                if number == 0:
                    enableRelu2.next = 0
                    enablePooling2.next = 1

        return relu2_calculation

    # Pooling layer 2

    @block
    def pooling2_unit(pooling2in, number):
        @always(clk.posedge)
        def pooling2_calculation():
            if enablePooling2 == 1:
                pooling2out[number].next = max(pooling2in)
                if number == 0:
                    enablePooling2.next = 0
                    enableFc1.next = 1

        return pooling2_calculation

    # Fully connected layer 1

    @block
    def fc1_unit(fc1in, number):
        @always(clk.posedge)
        def fc1_calculation():
            if enableFc1 == 1:
                a[0].next = fc1weights[number][0]
                b[0].next = pooling2out[0]
                a[1].next = fc1weights[number][1]
                b[1].next = pooling2out[1]
                a[2].next = fc1weights[number][2]
                b[2].next = pooling2out[2]
                a[3].next = fc1weights[number][3]
                b[3].next = pooling2out[3]
                a[4].next = 0
                b[4].next = 0
                a[5].next = 0
                b[5].next = 0
                a[6].next = 0
                b[6].next = 0
                a[7].next = 0
                b[7].next = 0
                a[8].next = 0
                b[8].next = 0

        return fc1_calculation

    # Fully connected layer 2

    @block
    def fc2_unit(fc2in, number):
        @always(clk.posedge)
        def fc2_calculation():
            if enableFc2 == 1:
                a[0].next = fc2weights[number][0]
                b[0].next = fc1out[0]
                a[1].next = fc2weights[number][1]
                b[1].next = fc1out[1]
                a[2].next = fc2weights[number][2]
                b[2].next = fc1out[2]
                a[3].next = fc2weights[number][3]
                b[3].next = fc1out[3]
                a[4].next = 0
                b[4].next = 0
                a[5].next = 0
                b[5].next = 0
                a[6].next = 0
                b[6].next = 0
                a[7].next = 0
                b[7].next = 0
                a[8].next = 0
                b[8].next = 0

        return fc2_calculation

    # Wallace Tree Multiplier 8 * 8 bit

    @block
    def WallaceTreeMultiplier(a, b, number):
        @always_comb
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
            carry_stage_4[1] = (carry_stage_3[1] and sum_stage_3[2]) or (
                    carry_stage_3[1] and partial_products[0][6]) or (
                                       sum_stage_3[2] and partial_products[0][6])
            sum_stage_4[2] = carry_stage_3[2] ^ carry_stage_2[4] ^ sum_stage_3[3]
            carry_stage_4[2] = (carry_stage_3[2] and carry_stage_2[4]) or (carry_stage_3[2] and sum_stage_3[3]) or (
                    carry_stage_2[4] and sum_stage_3[3])
            sum_stage_4[3] = carry_stage_2[5] ^ sum_stage_3[4] ^ partial_products[4][4]
            carry_stage_4[3] = (carry_stage_2[5] and sum_stage_3[4]) or (
                    carry_stage_2[5] and partial_products[4][4]) or (
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
            isGreater = (sl[15] or sl[14] or sl[13] or sl[12] or sl[11] or sl[10] or sl[9] or sl[8] or (
                    sl[7] and (sl[6] or sl[5] or sl[4] or sl[3] or sl[2] or sl[1] or sl[0])))

            res_c = [Signal(intbv(0)[1:]) for i in range(8)]
            res_c_r = [Signal(intbv(0)[1:]) for i in range(8)]
            if sl[7] == 1 and (not sl[15]) and (not sl[14]) and (not sl[13]) and (not sl[12]) and (not sl[11]) and (
                    not sl[10]) and (not sl[9]) and (not sl[8]) and (not sl[6]) and (not sl[5]) and (not sl[4]) and (
                    not sl[3]) and (not sl[2]) and (not sl[1]) and (not sl[0]):
                if s_b_req:
                    mult16[number].next = intbv(-128)[8:].signed()
                else:
                    mult16[number].next = intbv(127)[8:].signed()
            else:
                if isGreater:
                    if s_b_req:
                        mult16[number].next = intbv(-128)[8:].signed()
                    else:
                        mult16[number].next = intbv(127)[8:].signed()
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
                        mult16[number].next = intbv(intbv(
                            str(int(res_c_r[7])) + "_" + str(int(res_c_r[6])) + "_" + str(int(res_c_r[5])) + "_" + str(
                                int(res_c_r[4])) + "_" + str(
                                int(res_c_r[3])) + "_" + str(int(res_c_r[2])) + "_" + str(int(res_c_r[1])) + "_" + str(
                                int(res_c_r[0])))[
                                                    8:]).signed()
                    else:
                        mult16[number].next = intbv(intbv(
                            str(int(sl[7])) + "_" + str(int(sl[6])) + "_" + str(int(sl[5])) + "_" + str(
                                int(sl[4])) + "_" + str(
                                int(sl[3])) + "_" + str(int(sl[2])) + "_" + str(int(sl[1])) + "_" + str(int(sl[0])))[
                                                    8:]).signed()

        return multiplier_16

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
        # 8 bit Carry Look Ahead adder

    @block
    def CarryLookAheadAdder(a, b, c0, c8, sum8):
        @always_comb
        def cl_adder():
            sl = [Signal(bool(0)) for i in range(8)]
            p0, p1, p2, p3, p4, p5, p6, p7 = [Signal(bool(0)) for i in range(8)]
            g0, g1, g2, g3, g4, g5, g6, g7 = [Signal(bool(0)) for i in range(8)]
            c1, c2, c3, c4, c5, c6, c7 = [Signal(bool(0)) for i in range(7)]

            o_b, o_p, o_n = [Signal(bool(0)) for i in range(3)]
            o_b = not (a(7) ^ b(7))
            o_n = a[7] and b[7]
            o_p = not o_n

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

            if o_b == 1:
                if (g7 or (p7 and c7)) and (not sl[7]) and o_n:
                    sum8.next = intbv(intbv(-128)).signed()
                elif (p7 ^ c7) and o_p == 1:
                    sum8.next = intbv(intbv(127)).signed()
                else:
                    sum8.next = intbv(intbv(
                        str(int(sl[7])) + "_" + str(int(sl[6])) + "_" + str(int(sl[5])) + "_" + str(
                            int(sl[4])) + "_" + str(
                            int(sl[3])) + "_" + str(int(sl[2])) + "_" + str(int(sl[1])) + "_" + str(int(sl[0])))[
                                      8:]).signed()
            else:
                sum8.next = intbv(intbv(
                    str(int(sl[7])) + "_" + str(int(sl[6])) + "_" + str(int(sl[5])) + "_" + str(int(sl[4])) + "_" + str(
                        int(sl[3])) + "_" + str(int(sl[2])) + "_" + str(int(sl[1])) + "_" + str(int(sl[0])))[
                                  8:]).signed()

        return cl_adder

    # 8 bit Carry Look ahead adder to add and store in registers the final addition of addition tree.

    @block
    def CarryLookAheadAdderF(a, b, c0, c8, number):
        @always_comb
        def cl_adder():
            sl = [Signal(bool(0)) for i in range(8)]
            p0, p1, p2, p3, p4, p5, p6, p7 = [Signal(bool(0)) for i in range(8)]
            g0, g1, g2, g3, g4, g5, g6, g7 = [Signal(bool(0)) for i in range(8)]
            c1, c2, c3, c4, c5, c6, c7 = [Signal(bool(0)) for i in range(7)]

            o_b, o_p, o_n = [Signal(bool(0)) for i in range(3)]
            o_b = not (a(7) ^ b(7))
            o_n = a[7] and b[7]
            o_p = not o_n

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
            # print(number)
            if o_b == 1:
                if (g7 or (p7 and c7)) and (not sl[7]) and o_n:
                    # sum8.next = intbv(intbv(-128)).signed()
                    if enableConvolution1 == 1:
                        convo1out[number].next = intbv(intbv(-128)).signed()
                    elif enableConvolution2 == 1:
                        convo2out[number].next = intbv(intbv(-128)).signed()
                    elif enableFc1 == 1:
                        fc1out[number].next = intbv(intbv(-128)).signed()
                    elif enableFc2 == 1:
                        fc2out[number].next = intbv(intbv(-128)).signed()
                elif (p7 ^ c7) and o_p == 1:
                    # sum8.next = intbv(intbv(127)).signed()
                    if enableConvolution1 == 1:
                        convo1out[number].next = intbv(intbv(127)).signed()
                    elif enableConvolution2 == 1:
                        convo2out[number].next = intbv(intbv(127)).signed()
                    elif enableFc1 == 1:
                        fc1out[number].next = intbv(intbv(127)).signed()
                    elif enableFc2 == 1:
                        fc2out[number].next = intbv(intbv(127)).signed()
                else:
                    # sum8.next = intbv(intbv(
                    #     str(int(sl[7])) + "_" + str(int(sl[6])) + "_" + str(int(sl[5])) + "_" + str(int(sl[4])) + "_" + str(
                    #         int(sl[3])) + "_" + str(int(sl[2])) + "_" + str(int(sl[1])) + "_" + str(int(sl[0])))[
                    #                   8:]).signed()
                    if enableConvolution1 == 1:
                        convo1out[number].next = intbv(intbv(
                            str(int(sl[7])) + "_" + str(int(sl[6])) + "_" + str(int(sl[5])) + "_" + str(
                                int(sl[4])) + "_" + str(
                                int(sl[3])) + "_" + str(int(sl[2])) + "_" + str(int(sl[1])) + "_" + str(int(sl[0])))[
                                                       8:]).signed()
                    elif enableConvolution2 == 1:
                        # print(number)
                        convo2out[number].next = intbv(intbv(
                            str(int(sl[7])) + "_" + str(int(sl[6])) + "_" + str(int(sl[5])) + "_" + str(
                                int(sl[4])) + "_" + str(
                                int(sl[3])) + "_" + str(int(sl[2])) + "_" + str(int(sl[1])) + "_" + str(int(sl[0])))[
                                                       8:]).signed()
                    elif enableFc1 == 1:
                        # print(number)
                        fc1out[number].next = intbv(intbv(
                            str(int(sl[7])) + "_" + str(int(sl[6])) + "_" + str(int(sl[5])) + "_" + str(
                                int(sl[4])) + "_" + str(
                                int(sl[3])) + "_" + str(int(sl[2])) + "_" + str(int(sl[1])) + "_" + str(int(sl[0])))[
                                                    8:]).signed()
                    elif enableFc2 == 1:
                        # print(number)
                        fc2out[number].next = intbv(intbv(
                            str(int(sl[7])) + "_" + str(int(sl[6])) + "_" + str(int(sl[5])) + "_" + str(
                                int(sl[4])) + "_" + str(
                                int(sl[3])) + "_" + str(int(sl[2])) + "_" + str(int(sl[1])) + "_" + str(int(sl[0])))[
                                                    8:]).signed()
            else:
                # sum8.next = intbv(intbv(
                #     str(int(sl[7])) + "_" + str(int(sl[6])) + "_" + str(int(sl[5])) + "_" + str(int(sl[4])) + "_" + str(
                #         int(sl[3])) + "_" + str(int(sl[2])) + "_" + str(int(sl[1])) + "_" + str(int(sl[0])))[8:]).signed()
                if enableConvolution1 == 1:
                    convo1out[number].next = intbv(intbv(
                        str(int(sl[7])) + "_" + str(int(sl[6])) + "_" + str(int(sl[5])) + "_" + str(
                            int(sl[4])) + "_" + str(
                            int(sl[3])) + "_" + str(int(sl[2])) + "_" + str(int(sl[1])) + "_" + str(int(sl[0])))[
                                                   8:]).signed()
                elif enableConvolution2 == 1:
                    convo2out[number].next = intbv(intbv(
                        str(int(sl[7])) + "_" + str(int(sl[6])) + "_" + str(int(sl[5])) + "_" + str(
                            int(sl[4])) + "_" + str(
                            int(sl[3])) + "_" + str(int(sl[2])) + "_" + str(int(sl[1])) + "_" + str(int(sl[0])))[
                                                   8:]).signed()
                elif enableFc1 == 1:
                    fc1out[number].next = intbv(intbv(
                        str(int(sl[7])) + "_" + str(int(sl[6])) + "_" + str(int(sl[5])) + "_" + str(
                            int(sl[4])) + "_" + str(
                            int(sl[3])) + "_" + str(int(sl[2])) + "_" + str(int(sl[1])) + "_" + str(int(sl[0])))[
                                                8:]).signed()
                elif enableFc2 == 1:
                    fc2out[number].next = intbv(intbv(
                        str(int(sl[7])) + "_" + str(int(sl[6])) + "_" + str(int(sl[5])) + "_" + str(
                            int(sl[4])) + "_" + str(
                            int(sl[3])) + "_" + str(int(sl[2])) + "_" + str(int(sl[1])) + "_" + str(int(sl[0])))[
                                                8:]).signed()

        return cl_adder

    @block
    def indicing():
        @always(clk.negedge)
        def increment():
            if enableConvolution1 == 1:
                if indicingHelper.val < 143:
                    indicingHelper.next = indicingHelper + 1
                else:
                    enableConvolution1.next = False
                    enableRelu1.next = True
                    indicingHelper.next = -1
            elif enableConvolution2 == 1:
                if indicingHelper.val >= 143:
                    indicingHelper.next = 0
                if indicingHelper.val < 15:
                    indicingHelper.next = indicingHelper + 1
                else:
                    enableConvolution2.next = False
                    enableRelu2.next = True
                    indicingHelper.next = -1
            elif enableFc1 == 1:
                if indicingHelper.val >= 3:
                    indicingHelper.next = -1
                if indicingHelper.val < 3:
                    indicingHelper.next = indicingHelper + 1
                else:
                    indicingHelper.next = -1
                    enableFc1.next = False
                    enableFc2.next = True
            elif enableFc2 == 1:
                if indicingHelper.val >= 3:
                    indicingHelper.next = -1
                if indicingHelper.val < 3:
                    indicingHelper.next = indicingHelper + 1
                else:
                    indicingHelper.next = 3
                    enableFc2.next = False

        return increment

    # Functional blocks

    multiplierunits = [WallaceTreeMultiplier(a[i], b[i], i) for i in range(9)]
    adderunits4 = [CarryLookAheadAdder(mult16[i], mult16[i + 1], c0, c8, adders4[int(i / 2)]) for i in [0, 2, 4, 6]]
    adderunits2 = [CarryLookAheadAdder(adders4[i], adders4[i + 1], c0, c8, adders2[int(i / 2)]) for i in [0, 2]]
    adderunits1 = CarryLookAheadAdder(adders2[0], adders2[1], c0, c8, adder1)
    adderFinal = CarryLookAheadAdderF(adder1, mult16[8], c0, c8, indicingHelper)
    indicer = indicing()
    convo1units = convo1_unit(submat, indicingHelper)
    relu1units = [relu1_unit(convo1out[i], i) for i in range(12 * 12)]
    pooling1units = [pooling1_unit(pooling1ins(relu1out, i), i) for i in range(6 * 6)]
    convo2units = convo2_unit(pooling1out, indicingHelper)
    relu2units = [relu2_unit(convo2out[i], i) for i in range(4 * 4)]
    pooling2units = [pooling2_unit(pooling2ins(relu2out, i), i) for i in range(2 * 2)]
    fc1units = fc1_unit(pooling2out, indicingHelper)
    fc2units = fc2_unit(fc1out, indicingHelper)
    return clkgen, convo1units, multiplierunits, adderunits4, adderunits2, adderunits1, adderFinal, indicer, relu1units, pooling1units, convo2units, relu2units, pooling2units, fc1units, fc2units


# Simulation block, generates vcd file named CNN.vcd to observe the waveforms

def simulate(timesteps):
    simInst = CNN()
    simInst.config_sim(trace=True, tracebackup=False)
    simInst.run_sim(timesteps, quiet=0)


simulate(5000)
