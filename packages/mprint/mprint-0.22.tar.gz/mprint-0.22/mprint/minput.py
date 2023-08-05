# Add imput functionalities

# Import mprint
from mprint.mprint import mprint, colorTable, formatTable

# Fixing raw_input and input problems in Python 3
try:
    input = raw_input
except NameError:
    pass


# Question
def mquestion(text, yes=True):
    yesno = "y/N"
    if yes:
        yesno = "Y/n"

    mprint("%s <bold>[%s]</bold> " % (text, yesno))
    result = input()
    if (result == "" and yes) or result.lower().startswith("y"):
        return True
    elif (result == "" and yes is False) or result.lower().startswith("n"):
        return False
    else:
        raise ValueError("Invalid value returned from input: %s" % result)


# Press any key
def mpause(text="Press enter to continue..."):
    mprint(text)
    input()


# Text input
def minput(text=""):
    mprint("<default>%s<bold>" % text)
    result = input()
    mprint("<default>")
    return result


# Deprecated is_number function
def is_number(number=""):
    import warnings
    warnings.warn("Use mis_number instead.")
    return mis_number(number)


# Function to detect if a variable is a number
def mis_number(number):
    try:
        float(number)
        return True
    except ValueError:
        return False


# Numeric input
def mnum_input(text=""):
    mprint("<default>%s<bold>" % text)
    result = input()
    mprint("<default>")
    if mis_number(result):
        return float(result)
    else:
        raise ValueError("Input is not numeric")


# Email input
def memail_input(text=""):
    mprint("<default>%s<bold>" % text)
    result = input()
    mprint("<default>")
    if "@" in result and "." in result:
        return result
    else:
        raise ValueError("Input is not email")
