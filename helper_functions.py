import re
import operator

header_patterns = [[r'>### '], 
                  [r'Pre-condition', r'Precondition'], 
                  [r'Test procedure']]

arg_patterns = ['to', '=', 'for']
                

constants = {'INACTIVE' : '0', 
             'ACTIVE' : '1', 
             'TRUE' : '1', 
             'FALSE' : '0',
             '1B DOWN ALLOWED' : '1'}

operators = {'/' : operator.truediv,
             '*' : operator.mul,
             '+' : operator.add,
             '-' : operator.sub}

filename = 'ComponentSignalExternalFunctions.h'

commands = {}
commands['Set'] = 'Set'
commands['Check'] = 'Compare'
commands['Run'] = 'Wait'
commands['Ramp'] = 'Ramp'
commands['Run_until'] = 'Wait_until'
commands['Comment'] = 'Comment'


def populate_InterfaceDict(compName):
    
    interfaceDict = {}
    compFound = False
    
    interfaceDict['compName'] = compName
    
    with open(filename, 'r') as reader:
        print(f'DEBUG: file {filename} opened')
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

def searchConstants(line):

    for c, v in constants.items():
        # print(f"DEBUG: searching for constant: {c} in {line}")
        if c.lower() in line:
            return v

    return None

def extractArg(type, line):
    
    # In case of a Check statement, search in the third column
    # eg: "| 1. | Set signal value of `PWM control slew` = -1 | - |"
    #        1                       2                          3

    if type == 'Check':
        m = searchPattern(line)

    # For Ramp, two arguments need to be extracted: "value" and "gradient"
    elif type == 'Ramp':

        m = searchPattern(line)

        if len(m) > 0:
            
            # Correct number of arguments found, return the tuple (value, gradient)
            if len(m) == 2:
                return (m[0], m[1])
            # Incorrect number of arguments found
            else:
                print(f"ERROR: Incorrect no. of arguments found for Ramp at line: {line}.")
                return None
            
        else: 
            # Error: Arguments not found
            print(f"ERROR: No arguments found for Ramp at line: {line}.")
            return None 
        
    # In case of other statement types (Set, Run, Run_until, etc), search in the second column
    else:
        m = searchPattern(line)
       
    if len(m) > 0:
        return m
    else:

        # Check is there is any constant 
        c = searchConstants(line)

        if c: 
            return c
        
        # No argument was found
        # This is a problem for Set, but OK for Run and some cases of Check (sig1 = sig2)
        return None
            

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
    # Note: the space is needed, to exclude false positives like "settings", "checking", etc.
    # Note2: Check comment first, since keywords might be present in a comment.
    if '>> | >>>>' in line:
        return 'Comment'
    
    elif 'Set ' in line:
        return 'Set'
        
    elif 'Check ' in line:
        return 'Check'
    
    elif 'Run ' in line:
        if 'until' in line:
            return 'Run_until'
        else:
            return 'Run'
    
    elif 'Ramp' in line:
        return 'Ramp'
    

    
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
    
    extracted_signals = []

    # Split the line by commas
    m = re.split(r'`', line)
    
    # Copy the list to a new list
    line_no_signals = m.copy()

    # Extract signal list and 
    # prepare a list that contains no signal names ( to be used when extracting numeric values)
    for i in range(len(m)):
        if i%2 != 0:
            extracted_signals.append(m[i])
            line_no_signals.remove(m[i])

    # Return a tuple containing the signal names list and a line with signal names removed
    return (extracted_signals, line_no_signals)

def extract_TestName(line):
    '''
    Note: The test name must be in format: >### **test_name**
    In this case, the function will return 'test_name'
    '''
#     print(f"DEBUG: test name line: {line}")
    m = re.split(r'\*\*',line)

    return m[1]
    
def addTPTStep(testObj, line, signals, missingSignals):

    sigID = ''
    func_type = ''
    f_interface = ''
    f_arg = ''
    sig_type = ''
    f_grad = ''
    
    if 'substeps' in line:
        return None

    # Extract interface function and argument
    # This will return: 'set', 'check', 'run'
    func_type = extractFuncType(line)

    try:
        # Get function name from the commands dictionary
        f_interface = commands[func_type]
    except:
        print(f"ERROR: Interface type not found for line {line}.")
        f_interface = 'dummyInterface'
    
    # Component cyclic run
    if func_type == 'Run':

        line = line.split("|")[2].lower()
        
        # Extract the argument (default or defined period)
        f_arg = extractArg(func_type, line)

        if len(signals) > 0:

            if f_arg is not None:

                # Add the function to the test body
                testObj.append(f"{f_interface} {f_arg[0]}ms")

            else:

                # Add the function to the test body
                testObj.append(f"{f_interface} 40ms")

        return None
    
    elif func_type == 'Run_until':
        
        line = line.split("|")[2].lower()
         
        (sigID, line_no_signals) = extractSignalID(line)

        line_no_signals = "".join(line_no_signals)

        f_arg = extractArg(func_type, line_no_signals)

        # Check if the signals list was already populated.
        if len(signals) > 0:

            # Add the function to the test body
            testObj.append(f"Wait until {signals[sigID[0]]} == {f_arg[0]}")
                
        else:

            # Add the signal to the missingSignals list
            # Note: only add the first signal from the list of signals
            if sigID[0] not in missingSignals:
                missingSignals.append(sigID[0])
                            
    
    # SET step handling
    elif func_type == 'Set':

        line = line.split("|")[2].lower()
        
        # Check if status or value is set
        # This will return: 'status', 'value'
        if re.search(r'status', line):
            sig_type = ' status'

        # Extract signal name. If it's a status, the tag will be added to the name. If it's value, empty tag is added.
        # eg. sigID = 'remote control mode status'
        (sigID, line_no_signals) = extractSignalID(line)
        sigID[0] = sigID[0] + sig_type

        line_no_signals = "".join(line_no_signals)

        # Extract function argument
        f_arg = extractArg(func_type, line_no_signals)

        # Check if the signals list was already populated.
        if len(signals) > 0:

            # Add the function to the test body
            testObj.append(f"{f_interface} {signals[sigID[0]]} to {f_arg[0]}")
                
        else:

            # Add the signal to the missingSignals list
            # Note: only add the first signal from the list of signals
            if sigID[0] not in missingSignals:
                missingSignals.append(sigID[0])
            
        return None

    # CHECK step handling
    elif func_type == 'Check':

        # Initialize statement string
        statement = ""

        line = line.split("|")[3].lower()
        
        (sigID, line_no_signals) = extractSignalID(line)

        # Transforms the list to a string, that can be searched (needed for extractArg) 
        line_no_signals = "".join(line_no_signals)

        f_arg = extractArg(func_type, line_no_signals)

        if len(signals) > 0:

            # Statement form: "Check sig1 = sig2"
            if len(sigID) == 2:
                statement = f"{f_interface} {signals[sigID[0]]} == {signals[sigID[1]]}"

                # Check if tolerance is specified
                if "+/-" in line:
                    statement = f"{statement} +/- {f_arg[0]}" 

            # Statement form: "Check sig1 = val"
            elif len(sigID) == 1:
                statement = f"{f_interface} {signals[sigID[0]]} == {f_arg[0]}"

                # Check if tolerance is specified
                if "+/-" in line:
                    statement = f"{statement} +/- {f_arg[1]}" 

            else:
                print(line)
                print(f"ERROR: Incorrect statement found. Probably incorrectly formatted test step.")


            testObj.append(statement)

        else:
            if sigID[0] not in missingSignals:
                missingSignals.append(sigID[0])
            
        return None
    
    # RAMP step handling
    elif func_type == "Ramp":

            line = line.split("|")[2].lower()

            (sigID, line_no_signals) = extractSignalID(line)

            line_no_signals = "".join(line_no_signals)

            (f_arg, f_grad) = extractArg(func_type, line_no_signals)
                
            # Check if the signals list was already populated.
            if len(signals) > 0:

                # Add the function to the test body
                testObj.append(f"{f_interface} {signals[sigID[0]]} to {f_arg} with {f_grad}/s")
                
            else:

                # Add the signal to the missingSignals list
                if sigID[0] not in missingSignals:
                    missingSignals.append(sigID[0])
                
                
        
    # COMMENT step handling
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
        print(f"ERROR: Incorrect function type found <<{func_type}>>. Probably incorrectly formatted test step.")

    return None

def write_TCtoFile(test_name, test_obj, output_path):

    test_obj = sortTest(test_obj)

    filename = f"{output_path}/{test_name}.TPTTest"
    
    f = open(filename,"w")

    for line in test_obj:    
        f.write(line + "\n")

    print(f"DEBUG: Created test script {test_name}.TPTTest")

    f.close()

def sortTest(test_obj):
    ''' This is necessary because in TPT, the Wait step must come after the Compare step, while in Emulator, it's the other way around.
        So this function makes sure that the Wait will always be placed after the Compare'''

    i = 0 

    # Search through all elements in the test list
    while i < len(test_obj):
        
        if 'Wait' in test_obj[i]:

            slice_test_obj=test_obj[i+1:]

            # Find the last 'Check' from the next chunck of 'Checks'
            j = 1
            
            while j < len(slice_test_obj):
                          
                if 'Compare' in slice_test_obj[j]:

                    j += 1
                    continue
                
                else:
                    
                    break

            # Insert initialy found 'Wait' step at position i+j and remove it from position i
            test_obj.insert(i+j, test_obj.pop(i))

            # Continue search from position i+j (ie. from where the 'Wait' was inserted)
            i = i+j+1
        
        else:
            i += 1
            
    return test_obj
