import re
import operator

header_patterns = [r'> ### ', r'Pre-condition', r'Test procedure']


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


def extractArg(type, line):
    
    if type == 'Set':
        m = re.search('to (.+?) ', line)
    elif type == 'Check':
        m = re.search('` = (.+?) ', line)
       
    if m:
        arg = m.group(1)
        
        if is_number(arg):
            return arg
        else:        
            # Check if there is an expression
            args = re.split('\+|\-|\/|\*|\%', arg)

            if len(args) > 1:
                for char in arg:
                    if not(char.isalnum()):
                        op = operators[char]
                        break

                try:
                    print(f"arg1 = {args}")
                    arg1 = float(args[0])
                except ValueError:
                    arg1 = constants[args[0]]

                try:
                    arg2 = float(args[1])
                except ValueError:
                    arg2 = constants[args[1]]

                return str(op(arg1,arg2))

            else:
                # Convert the extracted string to a number, if possible
                try:
                    arg = float(arg)
                except ValueError:
                    # Use the dictionary values
                    arg = constants[arg]

                return str(arg)

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
    
    else:
        return None
    
    
def isHeaderType(htype, line):
    
    # Search the required pattern
    p1 = re.search(header_patterns[htype], line)
    
    if p1:
        return True
    else:
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
    
    
def addTPTStep(stype, testObj, line, signals, missingSignals):

# First, add printf 
    comment = re.split('\|', line)
    comment = '"' + comment[1] + comment[2] + '"'

    testObj.append(f"// {comment[1:-1]}")
    
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

        # Call the needed function
        testObj.append(f_interface + " 0.1")

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
        f_arg = extractArg('Set', line)
        
        try:
            # Call the needed function
            testObj.append(f_interface + " " + signals[sigID] + " to " + f_arg)
        except:
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

        try:
            # Call the needed function
            testObj.append(f"{f_interface} {sigID} == {f_arg}")
        except:
            if sigID not in missingSignals:
                missingSignals.append(sigID)
                return None

    else:
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

