try:
    import tkinter
except:
    import Tkinter as tkinter

class TimedDialog:
    def __init__(self):
        pass

    def selected(self, value):
        self.response = value
        self.top.destroy()

    def button_input(self, title, message, buttons, default, timeout=None, dimensions=None):
        self.response = default
        self.top = tkinter.Tk()
        self.top.title(title)

        if dimensions is not None:
            self.top.minsize(width=dimensions[0], height=dimensions[1])
            self.top.maxsize(width=dimensions[0], height=dimensions[1])

        labelString = tkinter.StringVar()
        labelString.set(message)
        label = tkinter.Label(self.top, textvariable=labelString, relief=tkinter.RAISED)
        label.pack(ipadx=100, ipady=10)

        for key in buttons.keys():
            button = tkinter.Button(self.top, text=buttons[key], command=lambda key=key: self.selected(key))
            button.pack(fill='both', pady=5, padx=10)

        if timeout != None:
            self.top.after(timeout, lambda: self.top.destroy())

        self.top.mainloop()
        return self.response
