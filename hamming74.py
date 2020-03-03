import random


# Simply reads the file
def read_file():
    filename = '/path/to/file/filename.txt'
    file = open(filename, "r")
    file = file.read().split(' ')
    return file


# Converts to binary
def binary_converter(array):
    bin_array = []
    for word in array:
        # First encodes to integer
        word = int.from_bytes(word.encode(), 'big')
        # Then to binary
        binary_not_chopped = bin(word)
        # "Chops" the words into 4-bit parts, in order for the Hamming code to work
        # Also disregards the '0b' part. It's the same in every number. Of course, it's appended back in, when decoding
        binary_not_chopped = binary_not_chopped[2:]
        binary_chopped = []
        # Appends the "chopped" parts into a list
        # The end result is a list of lists, with every sublist being a chopped word
        for i in range((len(binary_not_chopped)//4)+1):
            binary_chopped.append(binary_not_chopped[i*4:i*4+4])
        bin_array.append(binary_chopped)
    return bin_array


# Applies the hamming(7,4) encoding.
def encode(array):
    # Since the chopped words are not of same length, it's essential to keep track of how long each number is
    # This helps with the "gluing" later.
    word_length = []
    encoded_words = []
    # First loops through each word
    for word in array:
        # Then through the chopped up parts of the sublist
        length_per_word = []
        part_of_words = []
        for part in word:
            # As long as the number of bits is 4, it's all good. Simply append that it's 4 bits, and it's done
            if len(part) == 4:
                length_per_word.append(4)
            # Otherwise, append the number of bits, but also append a 0 at the beginning of the word
            else:
                length_per_word.append(len(part))
                for i in range(4, len(part), -1):
                    part = '0' + part
            # Regularly append the Hamming bits
            bit_0 = int(part[3]) + int(part[2]) + int(part[0])
            bit_1 = int(part[3]) + int(part[1]) + int(part[0])
            bit_3 = int(part[2]) + int(part[1]) + int(part[0])
            if bit_0 % 2==1:
                bit_0='1'
            else:
                bit_0='0'
            if bit_1 % 2==1:
                bit_1='1'
            else:
                bit_1='0'
            if bit_3 % 2==1:
                bit_3='1'
            else:
                bit_3='0'
            part = part[:-1] + bit_3 + part[3:] + bit_1 + bit_0
            part_of_words.append(part)
        # Append the encoded words in the new arrays, as well as the length of the original bits
        encoded_words.append(part_of_words)
        word_length.append(length_per_word)
    return encoded_words, word_length


# Apply noise
def induce_random_error(array, noise):
    error_array = []
    # i is for counting the number of errors
    i = 0
    for word in array:
        # Loop through each chopped word, and append noise randomly
        for j in range(len(word)):
            # Rolls for critical
            dice_roll = random.randint(1,20)
            if dice_roll == 20:
                # The higher the noise, the more the errors
                number_of_times = random.randint(1, noise)
                for x in range(number_of_times):
                    i = i+1
                    word[j] = list(word[j])
                    random_bit_to_change = random.randint(2,len(word[j])-1)
                    if word[j][random_bit_to_change] == 1:
                        word[j][random_bit_to_change] = '0'
                    else:
                        word[j][random_bit_to_change] = '1'
                    word[j] = ''.join(word[j])
        # Appends the new words (with noise or not), and its' done!
        error_array.append(word)
    return error_array, i


# The cleaning process starts here
def clean_words(array, word_length):
    clean_array = []
    j = 0
    for word in array:
        new_word = []
        # Loops through each chopped word
        for part in word:
            # Checks for errors. If the recieved bits are the same as the supposedly correct bits, then it's all good
            recieved_bits = [int(part[6]), int(part[5]), int(part[3])]
            bit_0 = int(part[4]) + int(part[2]) + int(part[0])
            bit_1 = int(part[4]) + int(part[1]) + int(part[0])
            bit_3 = int(part[2]) + int(part[1]) + int(part[0])
            check_bits = [bit_0%2, bit_1%2, bit_3%2]
            wrong_bits = []
            # Checking starts here
            for i in range(3):
                if recieved_bits[i]!=check_bits[i]:
                    wrong_bits.append(i)
            # If no bits are wrong, it means that the word passed correctly. If only a bit is wrong, it means that it
            # was the Hamming bit that was altered, so it doesn't matter to check further
            if len(wrong_bits)>1:
                # Corrects the mistakes
                part = mistake(part,wrong_bits)
            # Appends the now clean part
            new_word.append(part)
        # Glues them back together
        new_word = glue_word(new_word,word_length[j])
        new_word = int(new_word, 2)
        # Converts back to string. If there was an unreachable error, append with 'NaN'.
        try:
            new_word = new_word.to_bytes((new_word.bit_length()+7)//8, 'big').decode()
        except:
            new_word = 'NaN'
        clean_array.append(new_word)
        j = j+1
    return clean_array


# Corrects the mistakes
def mistake(part,wrong_bits):
    # If the wrong bits are the two last ones, it means that the error is the last bit of the original word. Change it.
    if wrong_bits == [0, 1]:
        if part[4]=='0':
            part[4]=='1'
        else:
            part[4]=='0'
    # Similarly, if the last and the first Hamming bits are wrong, then the error is at the second bit of the
    # original word
    elif wrong_bits == [0, 2]:
        if part[2]=='0':
            part[2]=='1'
        else:
            part[2]=='0'
    # Then we check for the third bit...
    elif wrong_bits==[1, 2]:
        if part[1]=='0':
            part[1]=='1'
        else:
            part[1]=='0'
    # If all of them are wrong, then the wrong bit is the first one.
    else:
        if part[0]=='0':
            part[0]=='1'
        else:
            part[0]=='0'
    return part


# Glues the chopped word back together
def glue_word(word,word_length):
    new_word = []
    # Remember, not all words are created the same. Some have less bits in the end.
    # Therefore, we check the word_length array, to make up for it, and disregard the first x bits
    for i in range(len(word)):
        if word_length[i]==4:
            new_word.append(word[i][:3] + word[i][4])
        elif word_length[i]==3:
            new_word.append(word[i][1:3] + word[i][4])
        elif word_length[i]==2:
            new_word.append(word[i][2] + word[i][4])
        elif word_length[i]==1:
            new_word.append(word[i][4])
        else:
            new_word.append('')
    # Glue the new array in one string
    new_word = ''.join(new_word)
    # Don't forget to add the prefix!
    new_word = '0b' + new_word
    return new_word


# A simple function to find the number of persistent errors
def find_wrong(clean, starting):
    wrong = []
    for i in range(len(clean)):
        if clean[i]!=starting[i]:
            wrong.append(clean[i])
    return wrong


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

encoded_words_to_send, length_of_parts = encode(binary_words)
print('Text has been encoded!')

encoded_words_to_send, false_goods = induce_random_error(encoded_words_to_send,noise_level)
print('Errors have been appended')

clean = clean_words(encoded_words_to_send, length_of_parts)
wrong_words = find_wrong(clean,words)
print('The total number of errors that were induced was ',false_goods, '. While the number of errors left is ',
      len(wrong_words))