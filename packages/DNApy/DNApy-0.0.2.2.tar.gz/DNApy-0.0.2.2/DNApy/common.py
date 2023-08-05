

revcompl = lambda x: ''.join([{'A': 'T', 'C': 'G', 'G': 'C', 'T': 'A', 'N': 'N', 'V':'B','H':'D','D':'H','B':'V','M':'K','K':'M','W':'W','S':'S','R':'Y','Y':'R'}[B] for B in x][::-1])

def regex_mapper(s):

    D = {'A': 'A', 'C': 'C', 'G': 'G', 'T': 'T', 'R': '[AG]', 'Y': '[CT]', 'N': '[ATGC]', 'S': '[GC]', 'W': '[AT]',
         'K': '[GT]', 'M': '[AC]',
         'B': '[CGT]', 'D': '[AGT]',
         'H': '[ACT]', 'V': '[ACG]', '^': ''}

    outputString = ""

    for nucleotide in s.upper():
        outputString += D[nucleotide]
    return outputString


def testIfSameLetter(letter1, letter2):
    """

    :param letter1: the first IUPAC letter
    :param letter2: the second IUPAC letter
    :return: A boolean whether they letters are the same
    """
    lettersL = (letter1.upper(), letter2.upper())
    mappedL = [regex_mapper(letter) for letter in lettersL]
    mapped_nobracketsL = []

    for i in mappedL: # this iterates only 2 times as there are only 2 elements
        if len(i) > 1: # not including the brackets
            mapped_nobracketsL.append(i[1:-1])
        else:
            mapped_nobracketsL.append(i)

    # testing if both IUPAC codes have atleast one common nucleotide
    # i.e. a non-zero Jaccard Index.
    for i in mapped_nobracketsL[0]:
        for j in mapped_nobracketsL[1]:
            if i == j:
                return True
    return False


def damerau_levenshtein_distance(s1, s2):

    d = {}
    lenstr1 = len(s1)
    lenstr2 = len(s2)
    for i in xrange(lenstr1 + 1):
        d[(i, 0)] = i
    for j in xrange(lenstr2 + 1):
        d[(0, j)] = j

    for i in xrange(1, lenstr1):
        for j in xrange(1, lenstr2):
            if testIfSameLetter(s2[j], s1[i]):
                cost = 0
            else:
                cost = 1
            d[(i, j)] = min(
                d[(i - 1, j)] + 1,  # deletion
                d[(i, j - 1)] + 1,  # insertion
                d[(i - 1, j - 1)] + cost,  # substitution
            )
            if i > 1 and j > 1 and testIfSameLetter(s1[i], s2[j - 1]) and testIfSameLetter(s1[i - 1], s2[j]):
                d[(i, j)] = min(d[(i, j)], d[(i - 2, j - 2)] + cost)  # transposition

    return d[(lenstr1 - 1, lenstr2 - 1)]