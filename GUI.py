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
        self.pack()
        self.create_widgets()

    def create_widgets(self):
        
        self.field_selOutputPath = tk.Entry()
        # self.but_confirmPath = tk.Button(text="Confirm path", command=self.read_outputPath)
        self.read_outputPath()

        self.but_selTestSpec = tk.Button(text="Select Test Specification file (*.md)", command=self.read_testSpec)


        self.but_selTestSpec.pack()
        # self.field_selOutputPath.pack()
        # self.but_confirmPath.pack()

    def read_testSpec(self):

        self.filename = fd.askopenfilename()
        self.parse_testSpec(self.filename)
        
        self.signals = {}
        self.missingSignals = []

        # Call the function with empty argument
        self.parse_testSteps(self.signals, self.missingSignals)

        # print("Following signals must be defined")
        # pp.pprint(self.missingSignals)

        self.populate_signalsInterfaces(self.missingSignals)

        # Ask user to populate signal-interface list

        # Call the function with non-empty argument
        self.parse_testSteps(self.signals, self.missingSignals)


    def read_outputPath(self):

        # self.outputPath = self.field_selOutputPath.get()
        
        self.outputPath = sd.askstring(title="Output Path", prompt="Enter output path")
        

        if self.outputPath is not None:
            tk.messagebox.showinfo(title="Output Path", message="Output Path saved")
        else:
            tk.messagebox.showerror(title="Output Path", message="Output path not valid. Please retry")



        
        # print(f"outputPath = {self.outputPath}")

    def parse_testSpec(self, filename):     

        with open(filename, 'r') as reader:
            print(f"file {filename} opened")
            testFound = -1
            data = reader.readlines()
            self.TC_list = []
            for line in data:
                isFound = H.isHeaderType(0, line)
                if isFound:
                    testFound = testFound + 1
                    self.TC_list.append([line])
                else:
                    if testFound > -1:
                        self.TC_list[testFound].append(line)
            # pp.pprint(self.TC_list)
	
    def parse_testSteps(self, signals, missingSignals):

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
                    
                    # Set flags
                    test_precondFound = True
                    
                    continue
                    
                # Check if Test Description part is found 
                if H.isHeaderType(2, line):
                    
                    # Set flags
                    test_descrFound = True
                    test_precondFound = False
                            
                    continue

                if test_descrFound:
                    
                    # add a step of type 1 (test step) in the C body
                    H.addTPTStep(1, test_obj, line, signals, missingSignals)
                    
                    continue            
                    
                if test_precondFound:
                    
                    # add a step of type 0 (precondition) in the C body
                    H.addTPTStep(0, test_obj, line, signals, missingSignals)
                    
                    continue

            H.write_TCtoFile(test_name, test_obj, self.outputPath)
                        

    def populate_signalsInterfaces(self, missingSignals):

        for signal in missingSignals:

            signInput = sd.askstring(title="Input Interface", prompt=signal)
            self.signals[signal] = signInput

        pp.pprint(self.signals)

    # H.write_TCtoFile(test_name, test_obj)




root = tk.Tk()
root.geometry('500x500')
app = Application(master=root)
app.mainloop()
