

        
def open_file(path):
    #print("opening...")
    with open(path, "r") as f:
        code = f.read()
        #print(code)
        return code