from tkinter import Tk, BOTH, IntVar, LEFT
from tkinter.ttk import Frame, Label, Scale, Style
hsv_min = []
hsv_max = []
 
class Example(Frame):
 
    def __init__(self):
        super().__init__()
 
    def initUI(self, i):
        scale = Scale(self, from_=0, to=100, command=self.onScale)
        if i < 3:
            scale.pack(side=LEFT, padx=15, pady = 15 *(i % 3))
        else:
            scale.pack(side=LEFT, padx=50, pady = 15 *(i % 3))
        self.var = IntVar()
        self.label = Label(self, text=0, textvariable=self.var)
        self.label.pack(side=LEFT)
    def onScale(self, val):
        v = int(float(val))
        print(v)
        self.var.set(v)
        return v
 
 
def main():
    root = Tk()
    for i in range(6):
        ex = Example()
        ex.initUI(i)
        if i < 3:
            hsv_min.append(ex)
        else:
            hsv_max.append(ex)
    root.geometry("500x500+300+300")
    print(hsv_min)
    print(hsv_max)
    root.mainloop()
 
 
if __name__ == '__main__':
    main()