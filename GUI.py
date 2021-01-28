import tkinter as tk
from tkinter import filedialog as fd
from tkinter import simpledialog as sd
import helper_functions as H
import xml.etree.ElementTree as ET
import pprint as pp


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
            print(f"file {self.filename} opened")
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
            test_name = TC[0][8:-3]
            
            test_obj = H.init_Test(test_name)
            
            # Loop through all the lines in the testcase
            for line in TC:

                # print(line)
                
                if line == '\n':
                    continue

                # Check if Preconditions part is found 
                if H.isHeaderType(1, line):
                    
                    print("preconditions found")

                    test_obj.append(f"// *** PRECONDITIONS ***")
                    # Set flags
                    test_precondFound = True
                    
                    continue
                    
                # Check if Test Description part is found 
                if H.isHeaderType(2, line):
                    
                    print("test Description found")

                    test_obj.append(f"// *** TEST PROCEDURE ***")
                    # Set flags
                    test_descrFound = True
                    test_precondFound = False
                            
                    continue

                if test_descrFound:
                    
                    # add a step of type 1 (test step) in the C body
                    H.addTPTStep(test_obj, line, self.signals, self.missingSignals)
                    
                    continue            
                    
                if test_precondFound:
                    
                    # add a step of type 0 (precondition) in the C body
                    H.addTPTStep(test_obj, line, self.signals, self.missingSignals)
                    
                    continue
            
            if len(self.signals) > 0:
                print("write here")
                H.write_TCtoFile(test_name, test_obj, self.outputPath)
                        

    def populate_signalsInterfaces(self):

        for signal in self.missingSignals:

            signInput = sd.askstring(title="Input Interface", prompt=signal)
            self.signals[signal] = signInput

        print("signals list")
        pp.pprint(self.signals)





root = tk.Tk()
root.geometry('300x300')
app = Application(master=root)
app.mainloop()
