import csv

def printMenu():
    print("ACME WEATHER DATA APP")
    print("1) Choose weather data file")
    print("2) See data for selected day")
    print("3) Calculate average statistics for the data")
    print("4) Print a scatterplot of the average temperatures")
    print("0) Quit program")

    
def chooseFile():
    try:
        filename = input('Give name of the file: ')
        if filename == "helsinki.csv" or filename == "turku.csv" or filename == "tampere.csv":
            print("Loaded weather data from " + filename[:-4].capitalize())
            print(" ")
            return filename
        else:
            return "Wrong name"
    except ValueError:
        "Wrong name"

def chooseOption():
    try:
        option = int(input('Choose what to do: '))
        if 0 <= option <= 4:
            return option
        else:
            return "Wrong option"
    except ValueError:
        return "Wrong option"
        

def function2_dataForSelectedDay(filename):
    filename = open(filename, "r")
    givenDate = input("Give a date (dd.mm): ")
    splittedDayMonth = givenDate.split('.')
    DayMonthProgramFormat = "2019-",splittedDayMonth[1],"-",splittedDayMonth[0]
    listToStr = ''.join([str(elem) for elem in DayMonthProgramFormat])
    listToStr2 = '"' + listToStr + '"'
    
    for row2 in filename:                
        rowData2 = row2.split(';')
        if listToStr2 == rowData2[0]:
            print("The weather on", givenDate, "was on average",rowData2[2] ,"centigrade")
            print("The lowest temperature was", rowData2[3], "and the highest temperature was", rowData2[4])
            print("There was", rowData2[1], "mm rain" )
    print(" ")        

def function3_average(filename):
    filename = open(filename, "r")
    elementoflist = '"' + "DateTime" + '"'     
    total1 = 0
    total2 = 0
    total3 = 0
    countROWS = 0
    
    
    for row2 in filename:    
        rowData2 = row2.split(';')
        if elementoflist != rowData2[0]:       
            countROWS += 1
        
            #3.1 THE AVERAGE TEMPERATURE FOR THE 25 DAY PERIOD:
            meanTemperatures = rowData2[2]   
            meanTemperaturesSTRINGtoINT = float(rowData2[2])   
                    
            total1 = total1 + meanTemperaturesSTRINGtoINT     
            total1AVERAGEmeantemp = round(total1/countROWS,1)

            #3.2 THE AVERAGE LOWEST TEMPERATURE FOR THE 25 DAY PERIOD:
            meanLOWESTTemperatures = rowData2[3]   
            meanLOWESTTemperaturesSTRINGtoINT = float(rowData2[3])
                  
            total2 = total2 + meanLOWESTTemperaturesSTRINGtoINT 
            total1AVERAGElowestmeantemp = round(total2/countROWS,1)

            #3.3 THE AVERAGE HIGHEST TEMPERATURE FOR THE 25 DAY PERIOD:
            meanHIGHESTTemperatures = rowData2[4]   
            meanHIGHESTTemperaturesSTRINGtoINT = float(rowData2[4])
                    
            total3 = total3 + meanHIGHESTTemperaturesSTRINGtoINT 
            total1AVERAGEhighestmeantemp = round(total3/countROWS,1)


    print("The average temperature for the 25 day period was", round(total1/countROWS,1))
    print("The average lowest temperature was", round(total2/countROWS,1))
    print("The average highest temperature was", round(total3/countROWS,1))
    print(" ")
    
def function4_scatterplot(filename):
    filename = open(filename, "r")
    day = 5
    month = 10
    elementoflist = '"' + "DateTime" + '"'   

    for row2 in filename:
        rowData2 = row2.split(';')

        if elementoflist != rowData2[0]:       
            day += 1
            meanTemperatures = rowData2[2]   
            meanTemperaturesSTRINGtoINT = float(rowData2[2])
            roundedMeanTemperaturesSTRINGtoINT = int(round(meanTemperaturesSTRINGtoINT, 0)) 
        
            print("{:02d}".format(day) + "." + str(month), end="")
            print('   '.ljust(roundedMeanTemperaturesSTRINGtoINT*3+15),"-")
            
    print("      ", end="")
    for i in range(-5,16):
        print("{:02d} ".format(i), end="")
    print(" ")    
    print(" ")

def main():
    filename = None
    
    while True:
        printMenu()
        option = chooseOption()

        if option == "Wrong option":
            print ("Wrong option. Choose 0-4")
            continue
        
        if option == 0:
            break
            
        if option == 1:
            filename = chooseFile()

        if filename == "Wrong name":
            print ("Wrong name")
            continue
        
        if filename is not None:
            if option == 2:
                function2_dataForSelectedDay(filename)   

            elif option == 3:
                function3_average(filename)

            elif option == 4:
                function4_scatterplot(filename)
    
        else:
            print("Error: No file selected")
            continue
            
    

if __name__ == "__main__":        
    main()
 
