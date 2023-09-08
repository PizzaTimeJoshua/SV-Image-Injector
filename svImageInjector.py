from PIL import Image
from tkinter import filedialog
import tkinter
import etcpak
import texture2ddecoder
import sys
from io import StringIO
from PIL import UnidentifiedImageError


#Default Width Height and Block Size 
width = 960
height = 544
blockSize = 0x97E00
filePath = ""

def compressImageToData(img : Image.Image):
    raw = img.tobytes()
    #Verify Width and Height
    if (width,height) != (img.width,img.height):
        print(f"Size not correct. Expected width: {width}, height: {height}.\nInstead obtained {img.width}, {img.height}.")
        return False
    #Compress data to DXT1 Format
    data = etcpak.compress_to_dxt1(raw,img.width,img.height)
    #Fill with empty bytes to fit Data Block Size
    data = b''.join([data,b'\x00' * (blockSize-len(data))])
    return data

def saveCompressedData(data, path):
    with open(path, "wb") as file:
        file.write(data)
    return

def uncompressDataToImage(data,width,height):
    image = Image.frombytes("RGBA", (width,height) , texture2ddecoder.decode_bc1(data, width, height),"raw", "BGRA")
    return image

def updatePicture():
    pictureType = filePictureVar.get()
    global width
    global height
    global blockSize
    if pictureType == "Profile Picture":    
        width = 960
        height = 544
        blockSize = 0x97E00
    else:
        width = 224
        height = 224
        blockSize = 0xF200
        

def selectFile():
    global filePath
    filePath = filedialog.askopenfilename(filetypes=[("Binary and Image Files","*.bin; *.png; *.jpg; *.jpeg"),("All Files", "*.*")])
    if filePath=="":
        print("File Selection Cancelled")
        return
    shortPath = filePath.split('/')
    shortPath = shortPath[len(shortPath)-1]

    #If an image is selected, auto Radio Button to 'Image to BIN'
    pathExt = filePath.split('.')
    pathExt = pathExt[len(pathExt)-1]
    imageExts = ["png","jpg","jpeg"]
    if any(word in pathExt for word in imageExts):
        fileTypeVar.set("Image to BIN")
        fileTypeSelector2.configure(state=tkinter.ACTIVE)
        print("Image File detected. Auto Selecting 'Image to BIN'")
    #If an binary file is selected, auto Radio Button to 'BIN to Image'
    binExts = ["bin","tex","dxt1"]
    if any(word in pathExt for word in binExts):
        fileTypeVar.set("BIN to Image")
        fileTypeSelector2.configure(state=tkinter.ACTIVE)
        print("Binary File detected. Auto Selecting 'BIN to Image'")
        

    fileLoadText.config(state=tkinter.NORMAL)
    fileLoadText.delete(1.0,tkinter.END)
    fileLoadText.insert(tkinter.END,"Selected File:")
    fileLoadText.insert(2.0,f"\n{shortPath}")
    fileLoadText.config(state=tkinter.DISABLED)

def convertSave():
    convertionType = fileTypeVar.get()
    if filePath == "":
        print("No File Selected")
        return
    try:
        if convertionType == "BIN to Image":
            with open(filePath, "rb") as file:
                data = file.read()
            if len(data)!=blockSize:
                print(f"Warning: File size is {len(data)} bytes\nExpected size is {blockSize} bytes")
            img = uncompressDataToImage(data,width,height)
            savePath = filedialog.asksaveasfilename(defaultextension=".png",filetypes=[("PNG Image","*.png"),("All Files","*.*")],initialfile="output.png")
            if savePath=="":
                print("File Selection Cancelled")
                return
            img.save(savePath)
            print("Image Successfully Exported")
        else:
            image = Image.open(filePath).convert("RGBA")
            data = compressImageToData(image)
            if data==False:
                return
            savePath = filedialog.asksaveasfilename(defaultextension=".png",filetypes=[("Binary Image","*.bin"),("All Files","*.*")],initialfile="output.bin")
            if savePath=="":
                print("File Selection Cancelled")
                return
            saveCompressedData(data,savePath)
            print("Image Successfully Compressed")
    except FileNotFoundError:
        print("Error: Could not find file.")
    except UnidentifiedImageError:
        print("Error: Image File Invalid")
            
    

app = tkinter.Tk()
app.title("SV Image Injector")
app.geometry("505x200")
app.resizable(width=False,height=False)

fileLoadButton = tkinter.Button(master=app,text="Select File",width=10,height=1,command= selectFile)
fileLoadButton.grid(column=0,row=0,padx=(10,10),pady=(10,10))

fileLoadText = tkinter.Text(master=app,width=30,height=2)
fileLoadText.grid(column=0,row=1,padx=(10,10),pady=(10,10),columnspan=2)
fileLoadText.insert(tkinter.END,"Selected File:")
fileLoadText.delete(2.0,tkinter.END)
fileLoadText.insert(2.0,"\n[NONE]")
fileLoadText.config(state=tkinter.DISABLED)

fileConvertButton = tkinter.Button(master=app,text="Convert and Save",width=15,height=1,command= convertSave)
fileConvertButton.grid(column=1,row=0,padx=(10,10),pady=(10,10))

fileTypeVar = tkinter.StringVar(app,"BIN to Image")
fileTypeSelector = tkinter.Radiobutton(app, text="BIN to Image", variable=fileTypeVar, value="BIN to Image")
fileTypeSelector2 = tkinter.Radiobutton(app, text="Image to BIN", variable=fileTypeVar, value="Image to BIN")
fileTypeSelector.grid(column=2,row=0,padx=(10,10),pady=(10,10))
fileTypeSelector2.grid(column=3,row=0,padx=(10,10),pady=(10,10))


filePictureVar = tkinter.StringVar(app,"Profile Picture")
filePictureSelector = tkinter.Radiobutton(app, text="Profile Picture", variable=filePictureVar, value="Profile Picture", command=updatePicture)
filePictureSelector2 = tkinter.Radiobutton(app, text="Icon Picture", variable=filePictureVar, value="Icon Picture", command=updatePicture)
filePictureSelector.grid(column=2,row=1,padx=(10,10),pady=(10,10))
filePictureSelector2.grid(column=3,row=1,padx=(10,10),pady=(10,10))


#Captures Console Messages
console_output = StringIO()
sys.stdout = console_output
debugText = tkinter.Text(master=app,width=60,height=4)
debugText.grid(column=0,row=2,padx=(10,10),pady=(10,10),columnspan=4)
debugText.insert(tkinter.END,"Console Messages:")
debugText.config(state=tkinter.DISABLED)

def updateConsoleDisplay():
    consoleInfo = console_output.getvalue()
    lines = consoleInfo.split('\n')
    info =  '\n'.join(lines[-4:])

    debugText.config(state=tkinter.NORMAL)
    debugText.delete(1.0,tkinter.END)
    debugText.insert(tkinter.END,"Console Messages:")
    debugText.insert(tkinter.END,f"\n{info}")
    debugText.config(state=tkinter.DISABLED)
    
    app.after(200,updateConsoleDisplay)

updateConsoleDisplay()

app.mainloop()
sys.stdout = sys.__stdout__
print(console_output.getvalue())