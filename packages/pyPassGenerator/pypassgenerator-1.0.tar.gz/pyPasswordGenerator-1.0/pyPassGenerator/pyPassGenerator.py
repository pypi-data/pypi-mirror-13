from random import randrange
from re import compile

def verifyLetter(letter, passphrase):
    for i in range(len(passphrase)):
        if passphrase[i] == letter:
            return False
    return True

def makeVocabulary(mixVocabulary):
        vocals = "aeiou"
        consonants = "bcdfghjklmnpqrstvwxyz"
        numbers = "0123456789"
        specials = "#.,*/^+-_@[]()?' "

        vocabulary = ""
        mixVocabulary = str(mixVocabulary)
        pattern = compile("(@.+|[avVcCns]+)")

        if not pattern.match(mixVocabulary):
            print("You have passed mixVocabulary parameter like a empty parameter. This's understanded how 'a'")
            return (vocals + consonants + numbers + vocals.upper() + specials + consonants.upper())

        if mixVocabulary[0] == "@": vocabulary = mixVocabulary[1:]

        if len(vocabulary) == 0:
            vocabulary += vocals if mixVocabulary.count("a") or mixVocabulary.count("v") else ""
            vocabulary += vocals.upper() if mixVocabulary.count("a") or mixVocabulary.count("V") else ""
            vocabulary += consonants if mixVocabulary.count("a") or mixVocabulary.count("c") else ""
            vocabulary += consonants.upper() if mixVocabulary.count("a") or mixVocabulary.count("C") else ""
            vocabulary += numbers if mixVocabulary.count("a") or mixVocabulary.count("n") else ""
            vocabulary += specials if mixVocabulary.count("a") or mixVocabulary.count("s") else ""
            # vocabulary += vocals + consonants + numbers + vocals.upper() + specials + consonants.upper()

        return vocabulary

def generatePass(size,  mixVocabulary="a", repeatCharacters=True):
    passphrase = ""
    vocabulary = makeVocabulary(mixVocabulary)

    i = 0
    while i < size:
        if len(passphrase) == len(vocabulary) and not repeatCharacters:
            print("You have reached the limit of characters without repeat", len(vocabulary))
            return passphrase

        letter = vocabulary[randrange(len(vocabulary))]
        letterVerified = True if repeatCharacters else verifyLetter(letter, passphrase)

        if letterVerified:
            passphrase += letter
            i += 1

    return passphrase

if __name__ == '__main__':
    print(generatePass(25, "@123ToNiV"))
