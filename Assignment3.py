from math import sqrt
import random

# generate fixed size message which is 1's and 0's
def generate_message(size):
    message = []
    for i in range(size):
        message.append(random.choice([0, 1]))
    return message

def noisy_channel(message, p):
    noisy_message = []
    for block in message:
        noisy_block = []
        for bit in block:
            if random.random() < p:
                noisy_block.append(1 - bit)
            else:
                noisy_block.append(bit)
        noisy_message.append(noisy_block)

    return noisy_message

def add_parity_bits(message, d):
    # split the message into blocks of size d-1 (data bits) + 1 (parity bit)
    blocks = [message[i:i+d-1] for i in range(0, len(message), d-1)] 
    for block in blocks:
        parity = sum(block) % 2
        block.append(parity)
    return blocks

def add_parity_matrix(message, d):
    # create parity matrix of (sqrt(d)*sqrt(d))
    dim = int(sqrt(d))
    # ensure that the message is a multiple of (dim-1)^2 by padding zeros if necessary
    padded_message = message + [0] * ((dim-1)**2 - len(message) % (dim-1)**2)
    # split the message into blocks of size dim-1 (data bits) and add row and column parity bits to each block (error correction code), so each block represents a matrix of sqrt(d)*sqrt(d)
    blocks = [padded_message[i:i+dim-1] for i in range(0, len(padded_message), dim-1)]
    for block in blocks:
        row_parity = sum(block) % 2
        block.append(row_parity)
    # we have matrix of (dim-1)*dim now we need to add parity bits to columns
    result = []
    for i in range(0, len(blocks), dim-1):
        matrix = blocks[i:i+dim-1]
        col_parity = [sum(matrix[k][j] for k in range(dim-1)) % 2 for j in range(len(matrix[0]))]
        matrix.append(col_parity)
        result.extend(matrix)
    return result

# check if the parity bit is correct
def check_parity(message):
    return sum(message[:-1]) % 2 == message[-1]


# check if there is a single error in a given matrix and correct it if possible
def check_and_correct_matrix(matrix):
    # print("Matrix to check: ", matrix) # for debugging
    dim = len(matrix)
    row_errors=[]
    col_errors=[]
    for r in range(dim):
        if sum(matrix[r][:-1]) % 2 != matrix[r][-1]:
            for c in range(dim):
                if sum([matrix[i][c] for i in range(dim-1)]) % 2 != matrix[-1][c]:
                    row_errors.append(r)
                    col_errors.append(c)

    if len(row_errors) == 0 and len(col_errors) == 0:
        return True # no errors
    elif len(row_errors) == 1 and len(col_errors) == 1:
        r = row_errors[0]
        c = col_errors[0]
        matrix[r][c] = 1 - matrix[r][c]
        return True # single error corrected
    return False # multiple errors detected 
    


# check if the message is correct
def check_message(message, method, d):
    if method == "parity_bit":
        for block in message:
            if not check_parity(block):
                return False
    elif method == "parity_matrix":
        dim = int(sqrt(d))
        for i in range(0, len(message), dim):
            matrix = message[i:i+dim]
            if not check_and_correct_matrix(matrix):
                return False
    return True

def simulation(d, p, method):
    MESSAGE_LENGTH = 500
    total_transmissions = 0

    #generate message
    message = generate_message(MESSAGE_LENGTH)

    #encode the message
    if method == "parity_bit":
        message = add_parity_bits(message, d)
    elif method == "parity_matrix":
        message = add_parity_matrix(message, d)
            
    while True:
        total_transmissions += 1

        #add noise to the message, i.e., flip each bit with probability p
        noisy_message = noisy_channel(message, p)

        #decoding - detect errors and correct them if possible(only matrix method can correct errors)
        if check_message(noisy_message, method, d):
            break
    
        # else - message is incorrect, retransmit the message
        p-=0.00001 # decrease the probability of error in each retransmission to avoid infinite loop
    efficiency = 1/total_transmissions # efficiency = successful transmissions / total transmissions
    return efficiency

                    
                
        
def main():

    
    p_values = [0.0001, 0.001, 0.01, 0.05]
    d_values = [9, 16, 25] 
    results = []
    for d in d_values:
        for p in p_values:
            # Try parity bit method
            efficiency_parity_bit = simulation(d, p, 'parity_bit')
            results.append((d, 'parity_bit', p, efficiency_parity_bit))

            # Try parity matrix method (d should be perfect square)
            efficiency_parity_matrix = simulation(d, p, 'parity_matrix')
            results.append((d, 'parity_matrix', p, efficiency_parity_matrix))
    
    # Print results
    print("Results:")
    print("d\t\tCoding Method\t\t\tP\t\tEfficiency Factor")
    for result in results:
        print(f"{result[0]}\t\t{result[1]}\t\t{result[2]}\t\t{result[3]}")

if __name__ == "__main__":
    main()