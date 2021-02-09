import tkinter as tk
from tkinter import filedialog as fd
from tkinter import simpledialog as sd
import helper_functions as H
import xml.etree.ElementTree as ET
import pprint as pp
import json
import os.path


class Application(tk.Frame):
    def __init__(self, master=None):

        super().__init__(master)
        self.master = master
        self.signals = {}
        self.missingSignals = []

        self.pack()
        self.create_widgets()


    def create_widgets(self):
        
        self.field_selOutputPath = tk.Entry()        
        self.read_outputPath()
        self.but_selTestSpec = tk.Button(text="Select Test Specification file (*.md)", command=self.read_testSpec, height=3, width=35, justify='center', relief='raised' )
        self.but_selTestSpec.pack()


    def read_testSpec(self):

        self.filename = fd.askopenfilename()

        # Extract testcases from file and store them in an array
        self.parse_testSpec()

        # First call: for extracting missing signals
        self.parse_testSteps()

        # Ask user to populate signal-interface list
        self.populate_signalsInterfaces()

        # Second call: for creating the test objects
        self.parse_testSteps()

        response = tk.messagebox.showinfo(title="Done", message="Testcase generation completed. Check output path")



    def read_outputPath(self):
        
        self.outputPath = sd.askstring(title="Output Path", prompt="Enter output path")
        

        if self.outputPath is not None:
            tk.messagebox.showinfo(title="Output Path", message="Output Path saved")
        else:
            tk.messagebox.showerror(title="Output Path", message="Output path not valid. Please retry")



    def parse_testSpec(self):     

        with open(self.filename, 'r') as reader:
            print(f"DEBUG: file {self.filename} opened")
            testFound = -1
            data = reader.readlines()
            self.TC_list = []
            for line in data:
                # print(line)
                isFound = H.isHeaderType(0, line)
                if isFound:
                    # print("test found")
                    testFound = testFound + 1
                    self.TC_list.append([line])
                else:
                    # print("test step")
                    if testFound > -1:
                        self.TC_list[testFound].append(line)
            # pp.pprint(self.TC_list)

    
    def parse_testSteps(self):

        for TC in self.TC_list:
    
            # Initialize flags
            test_precondFound = False
            test_descrFound = False
            test_bodyObj_pre = None
            test_bodyObj_descr = None

            
            # Extract the name of the testcase from the first line
            test_name = H.extract_TestName(TC[0])
            
            test_obj = H.init_Test(test_name)
            
            # Loop through all the lines in the testcase
            for line in TC:

#                 print(line)
                
                if line == '\n':
                    continue

                # Check if Preconditions part is found 
                if H.isHeaderType(1, line):
                    
#                     print("DEBUG: preconditions found")

                    test_obj.append(f"// *** PRECONDITIONS ***")
                    # Set flags
                    test_precondFound = True
                    
                    continue
                    
                # Check if Test Description part is found 
                if H.isHeaderType(2, line):
                    
#                     print("DEBUG: test Description found")

                    test_obj.append(f"// *** TEST PROCEDURE ***")
                    # Set flags
                    test_descrFound = True
                    test_precondFound = False
                            
                    continue

                if test_descrFound:
                    
                    H.addTPTStep(test_obj, line, self.signals, self.missingSignals)
                    
                    continue            
                    
                if test_precondFound:
                    
                    H.addTPTStep(test_obj, line, self.signals, self.missingSignals)
                    
                    continue
            
            if len(self.signals) > 0:
#                 print("DEBUG: Write to file")
                H.write_TCtoFile(test_name, test_obj, self.outputPath)
                        

    def populate_signalsInterfaces(self):

        # TODO: 
        # 1.add handling for adding signals to already existing files
        # 2.add handling for taking file name and path from user input
        
        # Check if the file already exists
        if os.path.isfile("signals.json"):
            
            # Load the file and extract the signal dictionary
            with open('signals.json', 'r') as json_file:
                self.signals = json.load(json_file)
                print(f"DEBUG: loaded signals: {self.signals}")
        else:
        
            # Ask the user to input each signal
            for signal in self.missingSignals:

                signInput = sd.askstring(title="Input Interface", prompt=signal)
                self.signals[signal] = signInput

            print("DEBUG: signals list")
            pp.pprint(self.signals)

            # Dump the signal dictionary to a file
            with open('signals.json', 'w') as file:
                 file.write(json.dumps(self.signals)) # use `json.loads` to do the reverse
                
            print("DEBUG: Dumped signals to file signals.json.")






root = tk.Tk()
root.geometry('300x300')
app = Application(master=root)
app.mainloop()
