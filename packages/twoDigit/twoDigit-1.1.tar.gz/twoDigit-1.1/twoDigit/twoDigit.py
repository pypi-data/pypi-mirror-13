e = [0, 0, 0]

space = [
e,e,e,e,e,e,e,e,
e,e,e,e,e,e,e,e,
]

def numToMatrix(num,col=[255,255,255]):
    if len(str(num)) > 2:
        print('Number bigger than 2 digits')
    r = col
    num_1_2 = [e,e,r,e,e,e,r,e]
    num_1_1 = [e,r,r,r,r,r,r,e]
    num_1_0 = [e,e,e,e,e,e,r,e]

    num_2_2 = [e,r,e,e,e,r,r,e]
    num_2_1 = [e,r,e,e,r,e,r,e]
    num_2_0 = [e,r,r,r,e,e,r,e]

    num_3_2 = [e,r,e,e,r,e,r,e]
    num_3_1 = [e,r,e,e,r,e,r,e]
    num_3_0 = [e,r,r,r,r,r,r,e]

    num_4_2 = [e,r,r,r,r,e,e,e]
    num_4_1 = [e,e,e,e,r,e,e,e]
    num_4_0 = [e,r,r,r,r,r,r,e]

    num_5_2 = [e,r,r,r,r,e,r,e]
    num_5_1 = [e,r,e,e,r,e,r,e]
    num_5_0 = [e,r,e,e,r,r,e,e]

    num_6_2 = [e,r,r,r,r,r,r,e]
    num_6_1 = [e,r,e,e,r,e,r,e]
    num_6_0 = [e,r,e,e,r,r,r,e]

    num_7_2 = [e,r,e,e,e,e,e,e]
    num_7_1 = [e,r,e,e,e,e,e,e]
    num_7_0 = [e,r,r,r,r,r,r,e]

    num_8_2 = [e,r,r,r,r,r,r,e]
    num_8_1 = [e,r,e,e,r,e,r,e]
    num_8_0 = [e,r,r,r,r,r,r,e]

    num_9_2 = [e,r,r,r,r,e,r,e]
    num_9_1 = [e,r,e,e,r,e,r,e]
    num_9_0 = [e,r,r,r,r,r,r,e]

    num_0_2 = [e,r,r,r,r,r,r,e]
    num_0_1 = [e,r,e,e,e,e,r,e]
    num_0_0 = [e,r,r,r,r,r,r,e]

# combine columns to make digits

    sing_0 = num_0_0 + num_0_1 + num_0_2
    sing_1 = num_1_0 + num_1_1 + num_1_2
    sing_2 = num_2_0 + num_2_1 + num_2_2
    sing_3 = num_3_0 + num_3_1 + num_3_2
    sing_4 = num_4_0 + num_4_1 + num_4_2
    sing_5 = num_5_0 + num_5_1 + num_5_2
    sing_6 = num_6_0 + num_6_1 + num_6_2
    sing_7 = num_7_0 + num_7_1 + num_7_2
    sing_8 = num_8_0 + num_8_1 + num_8_2
    sing_9 = num_9_0 + num_9_1 + num_9_2

# map digits onto appropriate strings
    output = []
    for dig in str(num):
        if dig == '1':
            output.append(sing_1)
        if dig == '2':
            output.append(sing_2)
        if dig == '3':
            output.append(sing_3)
        if dig == '4':
            output.append(sing_4)
        if dig == '5':
            output.append(sing_5)
        if dig == '6':
            output.append(sing_6)
        if dig == '7':
            output.append(sing_7)
        if dig == '8':
            output.append(sing_8)
        if dig == '9':
            output.append(sing_9)
        if dig == '0':
           output.append(sing_0)

    image = output[1] + space + output[0] # build image from two digits plus spacer
    return(image)

