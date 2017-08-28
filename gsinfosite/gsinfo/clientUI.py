# !/usr/bin/python
# coding: utf-8
from Tkinter import *
from PIL import Image, ImageTk

# def delectPic(root):
#     Label(root, textvariable='').pack()
#     for i in range(1, 5):
#         root.update_idletasks()

def main():
    top=Tk()
    top.geometry('850x450')#设置大小

    top.title(u'图片展示')
    top.iconbitmap('G:\\items\\webserver\\gsinfosite\\apps\\gsinfo\\logo.ico')

    s1=r'G:\\items\\webserver\\gsinfosite\\apps\\gsinfo\\gg.jpg' # jpg图片文件名 和 路径。
    im1=Image.open(s1)
    img1 = im1.resize((256,256))
    s2=r'G:\\items\\webserver\\gsinfosite\\apps\\gsinfo\\1-02-217-2002-A.png' # jpg图片文件名 和 路径。
    im2=Image.open(s2)
    img2 = im2.resize((256,256))
    bm1 = ImageTk.PhotoImage(img1)
    bm2 = ImageTk.PhotoImage(img2)
    label1 = Label(image=bm1)
    label2 = Label(image=bm2)

    label1.image = bm1
    label2.image = bm2
    label1.grid(row=0, column=0, columnspan=2, rowspan=2, sticky=W+E+N+S, padx=5, pady=5)
    label2.grid(row=0, column=2, columnspan=2, rowspan=2, sticky=W+E+N+S, padx=5, pady=5)
    deleteButton = Button(top, text="删除", pady=10, width=10, borderwidth=2, bg="#F3E9CC")
    deleteButton.grid(row=1, column=1)

    mainloop()

main()
# def resize(ev=None):
#     label.config(font='Helvetica -%d bold'%scale.get())
#
# top=Tk()
# top.geometry('750x450')#设置大小
# label=Label(top,text='Hello World!',font='Helvetica -12 bold')
# label.pack(fill=Y,expand=1)
# #进度条控件
# scale=Scale(top,from_=10,to=40,orient=HORIZONTAL,command=resize)#10-40
# scale.set(12)#初始位置
# scale.pack(fill=X,expand=1)
#
# quit=Button(top,text="QUIT",command=top.quit,activeforeground='white',activebackground='red')#Button
#
# quit.pack()
#
# mainloop()


# root = Tk()
#
# text = Text(root, undo=True, autoseparators=False)
# text.pack(expand=YES, fill=BOTH)
#
# text.insert(INSERT, "you can you up no can no bb")
#
#
# def callback(event):
#     # 每当有字符插入的时候，就自动插入一个分割符，主要是防止每次撤销的时候会全部撤销
#     text.edit_separator()
#
#
# text.bind("<Key>", callback)
#
#
# def show1():
#     x = text.get("1.0", END)
#     if len(x) == 1:  # 如果还剩余一个字符的话，不能撤销
#         return
#     text.edit_undo()
#
#
# maxx = text.get("1.0", END)
#
#
# def show2():
#     # 点击恢复的时候如果没有值可以被恢复的话，则会出现Bug，
#     # 所以要判断可以恢复的最大值，大于这个最大值的时候，则不执行恢复，防止bud
#     if len(maxx) == len(text.get("1.0", END)):
#         return
#     text.edit_redo()
#
#
# Button(root, text="撤销", command=show1).pack()
# Button(root, text="恢复", command=show2).pack()
#
# root.mainloop()


# def change():
#     label.configure(image=bm2)
# top = Tk()
# s1=r'G:\\items\\webserver\\gsinfosite\\apps\\gsinfo\\gg.jpg' # jpg图片文件名 和 路径。
# im1=Image.open(s1)
# s2=r'G:\\items\\webserver\\gsinfosite\\apps\\gsinfo\\1-02-217-2002-A.png' # jpg图片文件名 和 路径。
# im2=Image.open(s2)
# bm = ImageTk.PhotoImage(im1)
# bm2 = ImageTk.PhotoImage(im2)
#
# label = Label(top, image=bm)
# Frame()
# label.pack()
# button = Button(top, text="changepicture", command=change)
# button.pack()
# top.mainloop()




# #导入tk模块
# top = Tk()
# top.geometry('750x450')#设置大小
# #初始化Tk
# top.title('label test')
# #标题显示为label test
# label = Label(top, text='this is my first label')
# #创建一个label，它属于top窗口，文本显示内容为.....
# label.pack()
# s=r'G:\\items\\webserver\\gsinfosite\\apps\\gsinfo\\gg.jpg' # jpg图片文件名 和 路径。
# im=Image.open(s)
# bm = ImageTk.PhotoImage(im)
# label2 = Label(top, image=bm)
# label2.bm = bm
# label2.pack()
# top.mainloop()
# #进入消息循环