from datetime import datetime
from os import listdir
import os
import re
import json
import shutil
import pandas as pd
from application_logging.logger import App_Logger





class Prediction_Data_validation:
    """
               This class shall be used for handling all the validation done on the Raw Prediction Data!!.

    """

    def __init__(self,path, logging_db):
        self.Batch_Directory = path
        self.schema_path = 'schema_prediction.json'
        self.logging_db = logging_db
        self.logger = App_Logger()


    def valuesFromSchema(self):
        """
                                Method Name: valuesFromSchema
                                Description: This method extracts all the relevant information from the pre-defined "Schema" file.
                                Output: LengthOfDateStampInFile, LengthOfTimeStampInFile, column_names, Number of Columns
                                On Failure: Exception
        """
        collection='valuesfromSchemaValidationLog'
        try:
            with open(self.schema_path, 'r') as f:
                dic = json.load(f)
                f.close()
            pattern = dic['SampleFileName']
            LengthOfDateStampInFile = dic['LengthOfDateStampInFile']
            LengthOfTimeStampInFile = dic['LengthOfTimeStampInFile']
            column_names = dic['ColName']
            NumberofColumns = dic['NumberofColumns']

            message ="LengthOfDateStampInFile:: %s" %LengthOfDateStampInFile + "\t" + "LengthOfTimeStampInFile:: %s" % LengthOfTimeStampInFile +"\t " + "NumberofColumns:: %s" % NumberofColumns + "\n"

            self.logger.log(self.logging_db, collection, 'INFO', message)



        except Exception as e:
            self.logger.log(self.logging_db, collection, 'ERROR', str(e))
            raise e

        return LengthOfDateStampInFile, LengthOfTimeStampInFile, column_names, NumberofColumns


    def manualRegexCreation(self):

        """
                                      Method Name: manualRegexCreation
                                      Description: This method contains a manually defined regex based on the "FileName" given in "Schema" file.
                                                  This Regex is used to validate the filename of the prediction data.
                                      Output: Regex pattern
                                      On Failure: None
        """
        regex = "['Store_Sales']+['\_'']+[\d_]+[\d]+\.csv"
        return regex

    def createDirectoryForGoodBadRawData(self):

        """
                                        Method Name: createDirectoryForGoodBadRawData
                                        Description: This method creates directories to store the Good Data and Bad Data
                                                      after validating the prediction data.

                                        Output: None
                                        On Failure: Exception
        """
        collection='GeneralLog'
        try:
            path = os.path.join("Prediction_Raw_Files_Validated/", "Good_Raw/")
            if not os.path.isdir(path):
                os.makedirs(path)
            path = os.path.join("Prediction_Raw_Files_Validated/", "Bad_Raw/")
            if not os.path.isdir(path):
                os.makedirs(path)

        except Exception as e:
            self.logger.log(self.logging_db, collection, 'ERROR', "Error while creating Directory %s:" % e)
            raise e

    def deleteExistingGoodDataPredictionFolder(self):
        """
                                            Method Name: deleteExistingGoodDataTrainingFolder
                                            Description: This method deletes the directory made to store the Good Data
                                                          after loading the data in the table. Once the good files are
                                                          loaded in the DB,deleting the directory ensures space optimization.
                                            Output: None
                                            On Failure: Exception
        """
        collection='GeneralLog'
        try:
            path = 'Prediction_Raw_Files_Validated/'

            if os.path.isdir(path + 'Good_Raw/'):
                shutil.rmtree(path + 'Good_Raw/')
                self.logger.log(self.logging_db, collection, 'INFO',"GoodRaw directory deleted successfully!!!")
        except Exception as e:
            self.logger.log(self.logging_db, collection, 'ERROR', "Error while Deleting Directory : %s" %e)
            raise e
    def deleteExistingBadDataPredictionFolder(self):

        """
                                            Method Name: deleteExistingBadDataTrainingFolder
                                            Description: This method deletes the directory made to store the bad Data.
                                            Output: None
                                            On Failure: Exception
        """
        collection='GeneralLog'
        try:
            path = 'Prediction_Raw_Files_Validated/'
            if os.path.isdir(path + 'Bad_Raw/'):
                shutil.rmtree(path + 'Bad_Raw/')
                self.logger.log(self.logging_db, collection, 'INFO', "BadRaw directory deleted before starting validation!!!")
        except Exception as e:
            self.logger.log(self.logging_db, collection, 'ERROR', "Error while Deleting Directory : %s" %e)
            raise e

    def moveBadFilesToArchiveBad(self):


        """
                                            Method Name: moveBadFilesToArchiveBad
                                            Description: This method deletes the directory made  to store the Bad Data
                                                          after moving the data in an archive folder. We archive the bad
                                                          files to send them back to the client for invalid data issue.
                                            Output: None
                                            On Failure: Exception
        """
        now = datetime.now()
        date = now.date()
        time = now.strftime("%H%M%S")

        collection = 'GeneralLog'
        try:
            path= "PredictionArchivedBadData"
            if not os.path.isdir(path):
                os.makedirs(path)
            source = 'Prediction_Raw_Files_Validated/Bad_Raw/'

            if len(os.listdir(source))>0:
                dest = 'PredictionArchivedBadData/BadData_' + str(date)+"_"+str(time)
                if not os.path.isdir(dest):
                    os.makedirs(dest)
                files = os.listdir(source)
                for f in files:
                    if f not in os.listdir(dest):
                        shutil.move(source + f, dest)
                self.logger.log(self.logging_db, collection, 'INFO', "Bad files moved to archive")

            path = 'Prediction_Raw_Files_Validated/'
            if os.path.isdir(path + 'Bad_Raw/'):
                shutil.rmtree(path + 'Bad_Raw/')
            self.logger.log(self.logging_db, collection, 'INFO', "Bad Raw Data Folder Deleted successfully!!")
        except Exception as e:
            self.logger.log(self.logging_db, collection, 'ERROR', "Error while moving bad files to archive:: %s" % e)
            raise e


    def validationFileNameRaw(self,regex,LengthOfDateStampInFile,LengthOfTimeStampInFile):
            """
                Method Name: validationFileNameRaw
                Description: This function validates the name of the prediction csv file as per given name in the schema!
                             Regex pattern is used to do the validation.If name format do not match the file is moved
                             to Bad Raw Data folder else in Good raw data.
                Output: None
                On Failure: Exception


            """
            # delete the directories for good and bad data in case last run was unsuccessful and folders were not deleted.
            self.deleteExistingBadDataPredictionFolder()
            self.deleteExistingGoodDataPredictionFolder()
            self.createDirectoryForGoodBadRawData()
            onlyfiles = [f for f in listdir(self.Batch_Directory)]

            collection='nameValidationLog'
            try:
                for filename in onlyfiles:
                    if (re.match(regex, filename)):
                        splitAtDot = re.split('.csv', filename)
                        splitAtDot = (re.split('_', splitAtDot[0]))
                        if len(splitAtDot[2]) == LengthOfDateStampInFile:
                            if len(splitAtDot[3]) == LengthOfTimeStampInFile:
                                shutil.copy(self.Batch_Directory+ "/" + filename, "Prediction_Raw_Files_Validated/Good_Raw")
                                self.logger.log(self.logging_db, collection, 'INFO', "Valid File name!! File moved to GoodRaw Folder :: %s" % filename)

                            else:
                                shutil.copy(self.Batch_Directory+ "/" + filename, "Prediction_Raw_Files_Validated/Bad_Raw")
                                self.logger.log(self.logging_db, collection, 'INFO',"Invalid File Name!! File moved to Bad Raw Folder :: %s" % filename)
                        else:
                            shutil.copy(self.Batch_Directory+ "/" + filename, "Prediction_Raw_Files_Validated/Bad_Raw")
                            self.logger.log(self.logging_db, collection, 'INFO',"Invalid File Name!! File moved to Bad Raw Folder :: %s" % filename)
                    else:
                        shutil.copy(self.Batch_Directory+ "/" + filename, "Prediction_Raw_Files_Validated/Bad_Raw")
                        self.logger.log(self.logging_db, collection, 'INFO', "Invalid File Name!! File moved to Bad Raw Folder :: %s" % filename)


            except Exception as e:
                self.logger.log(self.logging_db, collection, 'ERROR', "Error occured while validating FileName %s" % e)

                raise e




    def validateColumnLength(self,NumberofColumns):
        """
                    Method Name: validateColumnLength
                    Description: This function validates the number of columns in the csv files.
                                 It is should be same as given in the schema file.
                                 If not same file is not suitable for processing and thus is moved to Bad Raw Data folder.
                                 If the column number matches, file is kept in Good Raw Data for processing.
                                The csv file is missing the first column name, this function changes the missing name to "Wafer".
                    Output: None
                    On Failure: Exception

        """
        collection='columnValidationLog'
        try:
            self.logger.log(self.logging_db, collection, 'INFO', "Column Length Validation Started!!")
            for file in listdir('Prediction_Raw_Files_Validated/Good_Raw/'):
                csv = pd.read_csv("Prediction_Raw_Files_Validated/Good_Raw/" + file)
                if csv.shape[1] == NumberofColumns:
                    pass
                else:
                    shutil.move("Prediction_Raw_Files_Validated/Good_Raw/" + file, "Prediction_Raw_Files_Validated/Bad_Raw")
                    self.logger.log(self.logging_db, collection, 'INFO', "Invalid Column Length for the file!! File moved to Bad Raw Folder :: %s" % file)

            self.logger.log(self.logging_db, collection, 'INFO', "Column Length Validation Completed!!")

        except Exception as e:
            self.logger.log(self.logging_db, collection, 'ERROR', "Error Occured:: %s" % e)
            raise e



    def validateMissingValuesInWholeColumn(self):
        """
                                  Method Name: validateMissingValuesInWholeColumn
                                  Description: This function validates if any column in the csv file has all values missing.
                                               If all the values are missing, the file is not suitable for processing.
                                               SUch files are moved to bad raw data.
                                  Output: None
                                  On Failure: Exception
        """
        collection='missingValuesInColumn'
        try:
            self.logger.log(self.logging_db, collection, 'INFO', "Missing Values Validation Started!!")

            for file in listdir('Prediction_Raw_Files_Validated/Good_Raw/'):
                csv = pd.read_csv("Prediction_Raw_Files_Validated/Good_Raw/" + file)
                for column in csv:
                    if (len(csv[column]) - csv[column].count()) == len(csv[column]):
                        shutil.move("Prediction_Raw_Files_Validated/Good_Raw/" + file,
                                    "Prediction_Raw_Files_Validated/Bad_Raw")
                        self.logger.log(self.logging_db, collection, 'INFO',"Invalid Column Length for the file!! File moved to Bad Raw Folder :: %s" % file)
                        break

        except Exception as e:
            self.logger.log(self.logging_db, collection, 'INFO', "Error Occured:: %s" % e)
            raise e













