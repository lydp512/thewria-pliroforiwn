import random


# Simply reads the file
def read_file():
    filename = '/path/to/file/filename.txt'
    file = open(filename, "r")
    file = file.read().split(' ')
    return file


# Converts the word to binary
def binary_converter(array):
    bin_array = []
    for word in array:
        word = int.from_bytes(word.encode(), 'big')
        bin_array.append(bin(word))
    return bin_array


# Encodes the word using cyclical coding
def encode(array):
    # Uses 1001 (9) as the checking part
    check = '0b1001'
    encoded_array = []
    for word in array:
        # adds the suffix
        enc = word + '000'
        # Modulo check, to find out what to add at the end
        enc = int(enc,2) % int(check,2)
        # Turns to binary
        enc = "{0:b}".format(enc)
        # We need 4 bits. So if it's less than that, add 0 in the beginning
        while len(enc) < 4:
            enc = '0' + enc
        # Add the suffix to the word and append into the array
        word = word + enc
        encoded_array.append(word)
    return encoded_array


# Adds noise
def induce_random_error(array, noise):
    error_array = []
    i = 0
    for word in array:
        dice_roll = random.randint(1,20)
        if dice_roll == 20:
            # Depending on how severe the noise is, the corresponding number of bits will change
            for j in range(random.randint(1,noise)):
                i = i+1
                # Turns the word into a list
                word = list(word)
                # Selects a random bit based on the length of the word. The first two bits are skipped, since it's the
                # '0b' part
                random_bit_to_change = random.randint(2,len(word)-1)
                if word[random_bit_to_change] == 1:
                    word[random_bit_to_change] = '0'
                else:
                    word[random_bit_to_change] = '1'
            # Glues the word back together
            word = ''.join(word)
        # Appends the words, with or without errors
        error_array.append(word)
    return error_array, i


# Checks for clean words
def clean_words(array):
    clean_array=[]
    dirty_array=[]
    for word in array:
        # Splits the word from the last "checking" bits
        last_bits = word[-4:]
        word = word[:-4]
        # Adds up the values to a check
        check = int(word, 2) + int(last_bits, 2)
        # If the check is devided by 9, then it's (probably) good to go
        if check%9 == 0:
            try:
                # Decodes back to string, and appends to the clean array
                word = int(word,2)
                word = word.to_bytes((word.bit_length() + 7) // 8, 'big').decode()
                clean_array.append(word)
            except:
                # Just in case the error detection was wrong AND there is an invalid byte, append NaN
                clean.append('NaN')
        else:
            # Now deals with the wrong words. If the errors add up to an invalid byte, then append with NaN
            word = int(word, 2)
            try:
                word = word.to_bytes((word.bit_length() + 7) // 8, 'big').decode()
            except:
                word = 'NaN'
            # Appends to the error array
            dirty_array.append(word)
    return clean_array, dirty_array


# Can't have the noise level to be a string or a negative number! Loop until a proper value is given!
noise_level = 'random_string'
while not noise_level.isdigit() or int(noise_level)<1:
    noise_level = input('Select how noisy the channel will be. Max is 5.')
noise_level = int(noise_level)
# Tried to be sneaky? Default noise level to 5!
if noise_level > 5:
    noise_level = 5

words = read_file()
print('Text is read!')

binary_words = binary_converter(words)
print('Text has been converted to binary!')

encoded_words_to_send = encode(binary_words)
print('Text has been encoded!')

encoded_words_to_send, false_goods = induce_random_error(encoded_words_to_send, noise_level)
print('Errors have been appended')

clean, dirty =clean_words(encoded_words_to_send)
print('The clean words are:')
print(clean)

if len(dirty)!=0:
    print('The dirty words are:')
    print(dirty)
    print('Correct percentage is: ', (len(clean)/len(encoded_words_to_send)), '%.', false_goods-len(dirty),
          ' words have been wrongly categorized as normal')