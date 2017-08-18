def readFile(file_path):
    with open(file_path) as f :
        read_data = f.read()
        array = read_data.splitlines()
        listOfLists = []
        listOfObjects = []
        for item in array:
            arrays = item.split(",")
            listOfLists.append(arrays)
        for item in listOfLists:
            objects = {}
            objects["Day"] = item[0]
            objects["Date"] = item[1]
            objects["Product"] = item[2]
            objects["Number_Sold"] = item[3]
            objects["Price"] = item[4]

            listOfObjects.append(objects)

    return listOfObjects
# print readFile('../static/files/Week1.csv')
