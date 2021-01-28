import re
import operator

header_patterns = [[r'> ### ', r'>### '], 
                  [r'Pre-condition', r'Precondition'], 
                  [r'Test procedure']]

arg_patterns = ['to', '=', 'for']
                

constants = {'INACTIVE' : 0, 
             'ACTIVE' : 1, 
             'TRUE' : 1, 
             'FALSE' : 0,
             '1B DOWN ALLOWED' : 1}

operators = {'/' : operator.truediv,
             '*' : operator.mul,
             '+' : operator.add,
             '-' : operator.sub}

filename = 'ComponentSignalExternalFunctions.h'

commands = {}
commands['Set'] = 'Set'
commands['Check'] = 'Compare'
commands['Run'] = 'Wait'


def populate_InterfaceDict(compName):
    
    interfaceDict = {}
    compFound = False
    
    interfaceDict['compName'] = compName
    
    with open(filename, 'r') as reader:
        print(f'file {filename} opened')
        data = reader.readlines()
        for line in data:
            # Extract info from the line
            m = re.search('_GID(\d+)_', line)
            if m:
                # Extract signal ID
                sigID = m.group(1)

                # Extract function name
                funcName = re.split(' ', line)[2]
                funcName = re.split('[(]', funcName)[0]

                if '_GetValue' in line:
                    interfaceType = 'Check'
                elif '_SetValue' in line:
                    interfaceType = 'Set'
                elif '_SetStatus' in line:
                    interfaceType = 'SetStatus'
                elif '_GetStatus' in line:
                    interfaceType = 'GetStatus'

                # Add function name to dictionary
                interfaceDict[interfaceType + '_' + sigID] = funcName

            # Check if it's state machine interface
            else:
                m = re.search(f'{compName}_Comp_(\w+)()', line)
                if m: 
                    # Extract state name (eg.Wakeup, Cycl, CyclEnd)
                    stateName = m.group(1)

                    # Extract function name
                    funcName = re.split(' ', line)[2]
                    funcName = re.split('[(]', funcName)[0]

                    # Add function name to dictionary
                    interfaceDict[compName + '_' + stateName] = funcName

    return interfaceDict                    


def is_number(s):
    try:
        float(s)
        return True
    except ValueError:
        return False

def searchPattern(line):

    # for pattern in arg_patterns:
    #     m = re.search(f'{pattern} (.+?)', line)

    #     if m:
    #         return m
    # return None

    # Parse the line looking for numbers of characters used in numerical expressions
    newstr = ''.join((ch if ch in '0123456789.-' else ' ') for ch in line)
    
    listOfNumbers = []

    for i in newstr.split():
        
        # The try/except is necessary to filter out cases like | - |
        try:
            listOfNumbers.append(float(i))
        except:
            continue

    return listOfNumbers

def extractArg(type, line):
    
    # In case of a Check statement, search in the third column
    # eg: "| 1. | Set signal value of `PWM control slew` = -1 | - |"
    #        1                       2                          3

    if type == 'Check':
        m = searchPattern(line.split("|")[3])

    # In case of other statement types (Set, Run, etc), search in the second column
    else:
        m = searchPattern(line.split("|")[2])
       
    if len(m) > 0:

        if len(m) == 1:

            return m[0]
        
        else:    
            # TODO this is bullshit
            # This is a workaround for the case where there is a number found in the name of the signal
            # Return the second number
            return m[1]
            pass

            #TODO
            # Check if there is an expression
            # args = re.split('\+|\-|\/|\*|\%', arg)

            # if len(args) > 1:
            #     for char in arg:
            #         if not(char.isalnum()):
            #             op = operators[char]
            #             break

            #     try:
            #         print(f"arg1 = {args}")
            #         arg1 = float(args[0])
            #     except ValueError:
            #         arg1 = constants[args[0]]

            #     try:
            #         arg2 = float(args[1])
            #     except ValueError:
            #         arg2 = constants[args[1]]

            #     return str(op(arg1,arg2))

            # else:
            #     # Convert the extracted string to a number, if possible
            #     try:
            #         arg = float(arg)
            #     except ValueError:
            #         # Use the dictionary values
            #         arg = constants[arg]

            #     return str(arg)

    # Argument value was not found
    return None

    
    
def extractFuncType(line):
    
    # Check if the following keywords are found in the line, to determine the function type.
    # Note: the space is needed, to exclude false positives like "settings", "checking", etc
    if 'Set ' in line:
        return 'Set'
        
    elif 'Check ' in line:
        return 'Check'
    
    elif 'Run ' in line:
        return 'Run'

    elif '>> | >>>>' in line:
        return 'Comment'
    
    else:
        return None
    
    
def isHeaderType(htype, line):
    
    # Check all possible patterns of type htype (0,1,..)
    for pattern in header_patterns[htype]:

        # Search the required pattern
        p1 = re.search(pattern, line)
        
        if p1:
            return True
    # No pattern found, exit
    return False
    
    
def init_Test(testname):
    
    test_obj = []
    test_obj.append(testname)
    
    return test_obj
    
def extractSignalID(line):
    
    # first extract the signal name (as it appears in the requirements)
    # create a mapping of signal name - interface name
    # return mapped value of signal name
    
    # Split the line by commas
    m = re.split(r'`', line)
    
    return m[1]
    
    
def addTPTStep(testObj, line, signals, missingSignals):

    # First, add printf 
    # comment = re.split('\|', line)
    # comment = '"' + comment[1] + comment[2] + '"'

    # testObj.append(f"// {comment[1:-1]}")
    
    # print(line)

    if 'substeps' in line:
        return None

    # Extract interface function and argument
    # This will return: 'set', 'check', 'run'
    func_type = extractFuncType(line)

#     print(f"func_type = {func_type}")

    # Component cyclic run
    # TODO: add argument check for defined period   
    if func_type == 'Run':

        f_interface = commands['Run']

        if len(signals) > 0:

            # Add the function to the test body
            testObj.append(f_interface + " 0.1")

        return None

    elif func_type == 'Set':

        # Check if status or value is set
        # This will return: 'status', 'value'
        if re.search(r'status', line):
            func_type = 'SetStatus'
        if re.search(r'value', line):
            sig_type = 'value'

        sigID = extractSignalID(line).lower()

        try:
            # Get interface name from the commands dictionary
            f_interface = commands['Set']
        except:
            f_interface = 'dummyInterface'


        # Extract function argument
        f_arg = str(extractArg('Set', line))
        

        if len(signals) > 0:

            # print(f"error here: {signals[sigID]}")
            # print(f"error here: {f_interface}")
            # print(f"error here: {f_arg}")

            # Add the function to the test body
            testObj.append(f_interface + " " + signals[sigID] + " to " + f_arg)
        else:

            # Add the signal to the missingSignals list
            if sigID not in missingSignals:
                missingSignals.append(sigID)
            
        return None


    elif func_type == 'Check':

        sigID = extractSignalID(line)

#         print(f"sigID = {sigID}")

        f_arg = extractArg('Check', line)

#         print(f"f_arg = {f_arg}")

        try:
            # Get interface name from the interface dictionary
            f_interface = commands['Check']
        except:
            f_interface = 'dummyInterface'

#         print(f"f_interface = {f_interface}")

        if len(signals) > 0:

            # Add the function to the test body
            testObj.append(f"{f_interface} {sigID} == {f_arg}")

        else:
            if sigID not in missingSignals:
                missingSignals.append(sigID)
            
        return None

    elif func_type == "Comment":

        if len(signals) > 0:
            # testObj.append(line)

            # First, add printf 
            comment = re.split('\|', line)
            comment = '"' + comment[2] + '"'

            testObj.append(f"// {comment[1:-1]}")
        
        return None

    else:
        print(line)
        print(f" Incorrect function type found <<{func_type}>>. Probably incorrectly formatted test step.")

    return None

def write_TCtoFile(test_name, test_obj, output_path):

    filename = f"{output_path}/{test_name}.TPTTest"
    
#     f = open(f"{test_name}.TPTTest", "a")
    f = open(filename,"a")

    for line in test_obj:    
        f.write(line + "\n")

    print(f"Created test script {test_name}.TPTTest")

    f.close()

