#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import tkinter
from tkinter import Tk, Text, Scrollbar, Menu, messagebox, filedialog, BooleanVar, Checkbutton, Label, Entry, StringVar, Grid, Frame
import os, subprocess, json, string

class Editor():
    def __init__(self, root):
        self.root = root        
        self.TITLE = "Simple IO"
        self.file_path = None
        self.set_title()
        
        self.fontSize = 12

        self.windowWidth = 100
        self.windowHeight = 25

        frame = Frame(root)
        # Scroll Bar [X and Y]
        self.xscrollbar = Scrollbar(root, orient="horizontal")
        self.yscrollbar = Scrollbar(root, orient="vertical")

        # Textbox
        self.editor = Text(frame, yscrollcommand=self.yscrollbar.set, xscrollcommand=self.xscrollbar.set,bg="#1d3557", fg="#f1faee")
        self.editor.pack(side="left", fill="both", expand=1)
        self.editor.config( wrap = "none",              # use word wrapping
               undo = True, # Tk 8.4 
               width = self.windowWidth,                # Window Width
               height = self.windowHeight,              # Window Height
               font=("Consolas", self.fontSize) )      # Font and Font Size        
        self.editor.focus()

        # Scroll Bar packing
        self.xscrollbar.pack(side="bottom", fill="x")
        self.xscrollbar.config(command=self.editor.xview)
        self.yscrollbar.pack(side="right", fill="y")
        self.yscrollbar.config(command=self.editor.yview) 

        # ## Status Bar ## #
        # Vars
        self.statusText = ("Font Size: " + str(self.fontSize))
        self.status = Label(root, text=self.statusText, relief=tkinter.SUNKEN,  anchor='w')
        self.status.pack(side=tkinter.BOTTOM, fill=tkinter.X)

        frame.pack(fill="both", expand=1)

        #instead of closing the window, execute a function. Call file_quit
        root.protocol("WM_DELETE_WINDOW", self.file_quit) 




        #create a top level menu
        self.menubar = Menu(root)

        #Menu item: File
        filemenu = Menu(self.menubar, tearoff=0)# tearoff = 0 => can't be seperated from window
        filemenu.add_command(label="New", command=self.file_new, accelerator="Ctrl+N")
        filemenu.add_command(label="Open", command=self.file_open, accelerator="Ctrl+O")
        filemenu.add_command(label="Save", command=self.file_save, accelerator="Ctrl+S")
        filemenu.add_command(label="Save As", command=self.file_save_as, accelerator="Ctrl+Alt+S")
        filemenu.add_separator() # Adds a lines between the above elements
        filemenu.add_command(label="Exit", command=self.file_quit, accelerator="Ctrl+Q")
        self.menubar.add_cascade(label="File", menu=filemenu)        
            
        # Menu item: View
        viewMenu = Menu(self.menubar, tearoff=0)
        viewMenu.add_command(label="Zoom In", command=self.zoom_In, accelerator="Ctrl+")
        viewMenu.add_command(label="Zoom Out", command=self.zoom_Out, accelerator="Ctrl-")
        self.menubar.add_cascade(label="View", menu=viewMenu)


        # Menu item: Color Scheme
        colorMenu = Menu(self.menubar, tearoff=0)
        colorMenu.add_command(label="Plain Text")
        colorMenu.add_command(label="Monokai")
        self.menubar.add_cascade(label="Color Scheme", menu=colorMenu)

        # display the menu
        root.config(menu=self.menubar)



    # If user trys to quit while there is unsaved content
    def save_if_modified(self, event=None):
        if self.editor.edit_modified(): #modified
            response = messagebox.askyesnocancel("Save?", "This document has been modified. Do you want to save changes?") #yes = True, no = False, cancel = None
            if response: #yes/save
                result = self.file_save()
                if result == "saved": #saved
                    return True
                else: #save cancelled
                    return None
            else:
                return response #None = cancel/abort, False = no/discard
        else: #not modified
            return True
    


# FILE MENU FUNCTIONS
##############################################################################################

    # NEW FILE
    def file_new(self, event=None):
        result = self.save_if_modified()
        if result != None: #None => Aborted or Save cancelled, False => Discarded, True = Saved or Not modified
            self.editor.delete(1.0, "end")
            self.editor.edit_modified(False)
            self.editor.edit_reset()
            self.file_path = None
            self.set_title()
    # OPEN FILE
    def file_open(self, event=None, filepath=None):
        result = self.save_if_modified()
        if result != None: #None => Aborted or Save cancelled, False => Discarded, True = Saved or Not modified
            if filepath == None:
                filepath = filedialog.askopenfilename()
            if filepath != None  and filepath != '':
                with open(filepath, encoding="utf-8") as f:
                    fileContents = f.read()# Get all the text from file.           
                # Set current text to file contents
                self.editor.delete(1.0, "end")
                self.editor.insert(1.0, fileContents)
                self.editor.edit_modified(False)
                self.file_path = filepath
    # SAVE FILE
    def file_save(self, event=None):
        if self.file_path == None:
            result = self.file_save_as()
        else:
            result = self.file_save_as(filepath=self.file_path)
        return result
    # SAVE AS
    def file_save_as(self, event=None, filepath=None):
        if filepath == None:
            filepath = filedialog.asksaveasfilename(filetypes=(('Text files', '*.txt'), ('Python files', '*.py *.pyw'), ('All files', '*.*'))) #defaultextension='.txt'
        try:
            with open(filepath, 'wb') as f:
                text = self.editor.get(1.0, "end-1c")
                f.write(bytes(text, 'UTF-8'))
                self.editor.edit_modified(False)
                self.file_path = filepath
                self.set_title()
                return "saved"
        except FileNotFoundError:
            print('FileNotFoundError')
            return "cancelled"
    # QUIT
    def file_quit(self, event=None):
        result = self.save_if_modified()
        if result != None: #None => Aborted or Save cancelled, False => Discarded, True = Saved or Not modified
            self.root.destroy() #sys.exit(0)
    # Show the file name on the top of the window
    def set_title(self, event=None):
        if self.file_path != None:
            title = os.path.basename(self.file_path)
        else:
            title = "Untitled"
        self.root.title(title + " - " + self.TITLE)
    def undo(self, event=None):
        self.editor.edit_undo()
        
    def redo(self, event=None):
        self.editor.edit_redo()   


# VIEW MENU FUNCTIONS
###############################################################################################
    def zoom_Out(self, event=None):
        if self.fontSize > 9:
            self.fontSize -= 1
            self.editor.config(font=("Helvetica", self.fontSize))
            self.updateStatusBar()

    def zoom_In(self, event=None):
        if self.fontSize < 50:
            self.fontSize += 1
            self.editor.config(font=("Helvetica", self.fontSize))
            self.updateStatusBar()
###############################################################################################
    def updateStatusBar(self, event=None):
        self.status.config(text=("Font Size: " + str(self.fontSize)))



    def main(self, event=None):
        # Key bindings          
        self.editor.bind("<Control-o>", self.file_open) # Open File
        self.editor.bind("<Control-O>", self.file_open) # ^
        self.editor.bind("<Control-S>", self.file_save) # Save File
        self.editor.bind("<Control-s>", self.file_save) # ^
        self.editor.bind("<Control-q>", self.file_quit) # Quit Application
        self.editor.bind("<Control-Q>", self.file_quit) # ^
        self.editor.bind("<Control-y>", self.redo)  # Redo Action
        self.editor.bind("<Control-Y>", self.redo)  # ^
        self.editor.bind("<Control-Z>", self.undo)  # Undo Action
        self.editor.bind("<Control-z>", self.undo)  # ^
        self.editor.bind("<Control-minus>", self.zoom_Out)
        self.editor.bind("<Control-plus>", self.zoom_In)

        
if __name__ == "__main__":
    root = Tk()
    editor = Editor(root)       # new editor instance
    editor.main()               # Main function
    root.mainloop()             # Run the loop
