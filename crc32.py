# TODO:
#       Add support for <10 and >99 .rXX files.
#       Multithreading? That'd be cool but also fuck that.

# Completed:
#       Make .sfv formatting less particular:
#           -read/store whole file at once. Search filenames as substrings to find correctCRC
#       Automatically scan current directory for files to check.

import binascii
import os

#Scan current directory and return the full filename of the highest .rXX file.
def get_last_file():
    files = [f for f in os.listdir('.') if os.path.isfile(f)]   #Create list of files in the current directory.
    maxNum = 0
    
    #Search list of files for highest .rXX file.
    for f in files:     		#For every file in the current directory
        try:
            if int(f[-2:]) > maxNum:    #If the last 2 characters of the file extension are a number greater than maxNum
                maxNum = int(f[-2:])        #Update maxNum to the new highest number
                filename = f                #Update filename to the new highest .rXX file
        except:                         #If the last 2 characters of the file extension are not numbers
            maxNum=maxNum                   #Do nothing
			
    return filename     		#Return filename of highest .rXX file

#Calculate and return CRC32 checksum of a file.
def calculate_CRC32(filename):
    buf = open(filename,'rb').read()
    buf = (binascii.crc32(buf) & 0xFFFFFFFF)
    return "%08X" % buf

#Passed a filename, searches the .sfv file for a line containing the filename and returns the CRC32 checksum at the end of the line.
def read_correct_CRC32(filename):
    beginIndex = checksumFileContents.find(filename)	#Find starting index in the .sfv file of the current .rXX file
    endIndex = beginIndex + len(filename) + 9		#last character of line is 9 characters after the end of the filename
    line = checksumFileContents[beginIndex:endIndex]	#Set line to a string of the line beginning with the current filename
    line = line.split(' ')				#Split line into a list consisting of a filename and the file's checksum
    line = line[1]				        #Set line to the second string generated by the split, this is the CRC32 checksum
    return line						#Return the CRC32 checksum

#Passed a current number, completion number, and width. Computes and prints a progress bar.
def progress_bar(curNum, completeNum, width): 
    percentComplete = (curNum / completeNum) * width
    numDashes = int(percentComplete)
    numSpaces = width - numDashes
    print("|", end='')
    x=0
    while x<numDashes:
        print('=', end='')
        x+=1
    y=0
    while y<numSpaces:
        print(' ', end='')
        y+=1
    print("| " + str(curNum) + '/' + str(completeNum), end='\r')
    if curNum == completeNum:
        print()


def main():
    lastFilename = get_last_file()
    numFiles = int(lastFilename[-2:]) + 1	        #Convert the last 2 characters of the last .rXX file to int and add 1 to determine the number of .rXX files to verify
	
    unformattedFilename = lastFilename[:-4]		#Remove the file extension (.rXX) from the end of the filename
    checksumFile = open(unformattedFilename + '.sfv')	#Open the checksum file for the detected .rXX files
    global checksumFileContents
    checksumFileContents = checksumFile.read()	        #Store the entirety of the checksum file contents as a string in checksumFileContents
    
    fileErrors = []
    crcList = []
    correctCRCList = []
    x=0
    while x < numFiles:													#For every .rXX file in the directory
        formattedFilename = unformattedFilename + ".r" + "%02d" % x		#Append the proper extension for the current file to unformattedFilename
        crc = calculate_CRC32(formattedFilename).lower()			#Calculate the CRC32 checksum for the current file, convert to lowercase
        correctCRC = read_correct_CRC32(formattedFilename).lower()		#Obtain the correct CRC32 checksum for the current file, convert to lowercase
        if crc != correctCRC:											#If the calculated and correct checksums don't match
            fileErrors.append(x)											#Append current num to fileErrors[]
            crcList.append(crc)												#Append calculated checksum to crcList[]
            correctCRCList.append(correctCRC)								#Append correct checksum to correctCRCList[]
        progress_bar(x+1, numFiles, 40)									#Print out a progress bar for the current num out of the number of .rXX files in the directory, with width 40 chars
        x+=1

    crc = calculate_CRC32(unformattedFilename + '.rar').lower()			#Calculate checksum for the .rar file
    correctCRC = read_correct_CRC32(unformattedFilename + '.rar').lower()		#Obtain correct checksum for the .rar file
    rarError = False
    if crc != correctCRC:												#If the .rar file calculated and correct checksums don't match
        rarError = True													#Set rarError flag to true

    if len(fileErrors) == 0 and rarError == False:						#If all files checksums are correct
        print("\nAll files passed.")										#Print pass message
    else:																#If any file's checksums didn't match
        print()
        print(str(len(fileErrors) + int(rarError) ) + " file(s) failed.\n")	#Print the number of file failures
        i=0
        for num in fileErrors:											#For every file that failed
            print("ERROR for .r" + "%02d" % num)							#Print the extension num of the failed file (.rXX)
            print('Expected value: \t' + correctCRCList[i])					#Print the value obtained from the .sfv
            print('Received value: \t' + crcList[i] + '\n')					#Print the value calculated by calculate_CRC32()
            i+=1
        if rarError:													#If .rar file checksum failed
            print("ERROR for .rar")											#Print error for .rar
            print('Expected value: \t' + correctCRC)						#Print value obtained from the .sfv
            print('Received value: \t' + crc + '\n')						#Print the value calculated by calculate_CRC32()
    
    
main()
input("Press Enter to continue...")	#Pause at end of execution
