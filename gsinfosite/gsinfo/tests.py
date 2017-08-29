import os


def printer():
    filename = r'C:\Users\Administrator\Desktop\test.docx'
    printername = "/D:\\192.168.16.26\HP LaserJet M1530 MFP Series PCL 6"
    cmd = "print " + printername + " " + filename
    print "print cmd:", cmd
    if not os.system(cmd):
        print "printing..."
    else:
        print "some error occurs."


if __name__ == "__main__":
    printer()