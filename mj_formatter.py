import pandas as pd


class mailjet:
    def __init__(self, mainlistFile, exclusionFile, outputFile):        
        self.mainlistFile  = mainlistFile
        self.exclusionFile = exclusionFile
        self.outputFile   =  outputFile

    def readData(self, file, emailHeader='email',statusHeader='unsubscribed'):
        """
        Read Data from customer
        References:
        https://stackoverflow.com/questions/41303246/error-tokenizing-data-c-error-out-of-memory-pandas-python-large-file-csv
        https://stackoverflow.com/questions/18039057/python-pandas-error-tokenizing-data
        """          
        mylist = []
        keepCols = [emailHeader]
        if statusHeader != '':
            keepCols.append(statusHeader)

        for chunk in  pd.read_csv(file, sep=',', chunksize=20000,error_bad_lines=False, usecols=keepCols):
            mylist.append(chunk)
        big_data = pd.concat(mylist, axis= 0)
        
        df = pd.DataFrame(big_data)
        
        del mylist
        del big_data
        return df
    
    def formatData(self):
        ''' 
        Read the data from given files
        '''
        excludedDf =  self.readData(self.exclusionFile,statusHeader='')
        mainlistDf =  self.readData(self.mainlistFile)
        
        # Extract sub and unsub
        sub = pd.DataFrame(mainlistDf[mainlistDf['unsubscribed']=='f']['email'])
        unsub = pd.DataFrame(mainlistDf[mainlistDf['unsubscribed']=='t']['email'])
        del mainlistDf

        # Remove duplicated excluded users in the mainlist
        temp = excludedDf.merge(sub,how="outer",indicator=True)
        global_exclude = pd.DataFrame(temp[temp["_merge"]!='right_only'])        
        mj_sub = pd.DataFrame(temp[temp["_merge"]=='right_only'])

        global_exclude['status'] = 'excluded'
        mj_sub['status'] = 'sub'        
        unsub['status'] = 'unsub'
        
        print("1) Formatting Mailjet Data")
        print("Sub, Unsub, Exlcuded: %s, %s, %s" % (len(mj_sub),len(unsub),len(global_exclude)))
        print("Total Data in Mailjet: ", len(mj_sub)+len(unsub)+len(global_exclude))
        print("")
        merged  = mj_sub.append(unsub).append(global_exclude)
        merged.drop(columns=['_merge'], inplace=True)        
        merged.to_csv(self.outputFile,index=False)
        del merged
        
