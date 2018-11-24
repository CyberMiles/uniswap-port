import os
import re
import json
import shutil
import requests
import fileinput
import subprocess
import configparser
from zipfile import ZipFile

class UP: 
    def __init__(self):
        self.scriptExecutionLocation = os.getcwd()
        print("Starting to port Uniswap, please wait.")
        # GENERAL CLASS VARIABLES - START
        self.addressJsData = {}
        self.stringForAddressJsFile = ''
        # GENERAL CLASS VARIABLES - END

        # READ CONFIGURATION (uniswap.ini) INTO CLASS VARIABLES - START
        print("Reading configuration file, uniswap.ini")
        config = configparser.ConfigParser()
        config.read('uniswap.ini')

        print("Configuration is as follows ...")

        self.urls = {}
        for key in config['urls']:
            stringKey = str(key)
            self.urls[stringKey] = config['urls'][key]
        print("\nURLs:")
        for (ufaKey, ufaValue) in self.urls.items():
            print(ufaKey + ": " + ufaValue)

        self.blockchain = {}
        for key in config['blockchain']:
            stringKey = str(key)
            self.blockchain[stringKey] = config['blockchain'][key]
        print("\nBlockchain:")
        for (ufaKey, ufaValue) in self.blockchain.items():
            print(ufaKey + ": " + ufaValue)

        self.uniswapFactoryAddress = config['uniswapFactoryAddress']['factoryAddress']
        print("factoryAddress: " + self.uniswapFactoryAddress)

        self.uniswapTokenAddresses = {}
        for key in config['uniswapTokenAddresses']:
            stringKey = str(key)
            upperStringKey = stringKey.upper()
            self.uniswapTokenAddresses[upperStringKey] = config['uniswapTokenAddresses'][upperStringKey]
        print("\nUniswapTokenAddresses:")
        for (ufaKey, ufaValue) in self.uniswapTokenAddresses.items():
            print(ufaKey + ": " + ufaValue)

        self.uniswapExchangeAddresses = {}
        for key in config['uniswapExchangeAddresses']:
            stringKey = str(key)
            upperStringKey = stringKey.upper()
            self.uniswapExchangeAddresses[upperStringKey] = config['uniswapExchangeAddresses'][upperStringKey]
        print("\nUniswapExchangeAddresses:")
        for (ufaKey, ufaValue) in self.uniswapExchangeAddresses.items():
            print(ufaKey + ": " + ufaValue)

        self.quotedTextReplacements = {}
        for key in config['quotedTextReplacements']:
            stringKey = str(key)
            upperStringKey = stringKey.upper()
            self.quotedTextReplacements[stringKey] = config['quotedTextReplacements'][stringKey]
            valueToConvert = config['quotedTextReplacements'][stringKey]
            self.quotedTextReplacements[stringKey.capitalize()] = str(valueToConvert).capitalize()
            self.quotedTextReplacements[stringKey.upper()] = str(valueToConvert).upper()
            self.quotedTextReplacements[key] = config['quotedTextReplacements'][key]
        print("\nQuotedTextReplacements:")
        for (ufaKey, ufaValue) in self.quotedTextReplacements.items():
            print(ufaKey + ": " + ufaValue)

        self.unquotedTextReplacements = {}
        for key in config['unquotedTextReplacements']:
            stringKey = str(key)
            self.unquotedTextReplacements[stringKey] = config['unquotedTextReplacements'][stringKey]
        print("\nUnquotedTextReplacements:")
        for (ufaKey, ufaValue) in self.unquotedTextReplacements.items():
            print(ufaKey + ": " + ufaValue)

        self.paths = {}
        for key in config['paths']:
            stringKey = str(key)
            self.paths[stringKey] = config['paths'][key]
        print("\nPaths:")
        for (ufaKey, ufaValue) in self.paths.items():
            print(ufaKey + ": " + ufaValue)
            
        self.ignoreThisTextInThisFile = {}
        for key in config['ignoreThisTextInThisFile']:
            stringKey = str(key)
            self.ignoreThisTextInThisFile[stringKey] = config['ignoreThisTextInThisFile'][key]
        print("\nIgnoreThisTextInThisFile:")
        for (ufaKey, ufaValue) in self.ignoreThisTextInThisFile.items():
            print(ufaKey + ": " + ufaValue)
    # READ CONFIGURATION (uniswap.ini) INTO CLASS VARIABLES - END

    # CLASS METHODS - START
    def cleanUp(self):
        if (os.path.isdir(self.paths['uniswap_zip_download_location'])):
            print('Removing ' + self.paths['uniswap_zip_download_location'] + ' now because we want a clean slate!')
            shutil.rmtree(self.paths['uniswap_zip_download_location'])
        if (os.path.isdir(self.paths['uniswap_base_dir'])):
            print('Removing ' + self.paths['uniswap_base_dir'] + ' now because we want a clean slate!')
            shutil.rmtree(self.paths['uniswap_base_dir'])

    def housekeeping(self):
        print('Operating out of path: ' + os.getcwd())
        print('Changing directories...')
        os.chdir(self.paths['home_dir'])
        print('Operating out of path: ' + os.getcwd())

    def fetchUniswapSourceCode(self):
        print('Operating out of path: ' + os.getcwd())
        print('Fetching Uniswap source code from ' + self.urls['uniswap_source_code'])
        r = requests.get(self.urls['uniswap_source_code'])
        with open(self.paths['uniswap_zip_download_location'], 'wb') as f:
            f.write(r.content)

    def unpackUniswapSourceCode(self):
        print('Operating out of path: ' + os.getcwd())
        print('Unpacking Uniswap source code...')
        with ZipFile(self.paths['uniswap_zip_download_location'], 'r') as zip: 
            zip.extractall()
        os.remove(self.paths['uniswap_zip_download_location'])

    def buildAddress(self, items, addressType):
        print('Operating out of path: ' + os.getcwd())
        print("Creating " + addressType + " configuration...")
        self.addressJsData[addressType] = {}
        addresses = []
        address = []
        for (k, v) in items:
            address.append(k)
            address.append(v)
            addresses.append(address)
            address = []
        self.addressJsData[addressType]['addresses'] = addresses

    def runBuildAddresses(self):
        print('Operating out of path: ' + os.getcwd())
        self.addressJsData['factoryAddress'] = self.uniswapFactoryAddress
        self.buildAddress(self.uniswapExchangeAddresses.items(), 'exchangeAddresses')
        self.buildAddress(self.uniswapTokenAddresses.items(), 'tokenAddresses')

    def pairExchangeAndTokenAddresses(self):
        print('Operating out of path: ' + os.getcwd())
        print("Creating exchange and token pairing configuration...")
        fromToken = {}
        for (k1, v1) in self.uniswapTokenAddresses.items():
            for (k2, v2) in self.uniswapExchangeAddresses.items():
                if k1 == k2:
                    fromToken[v1] = v2
        self.addressJsData['exchangeAddresses']['fromToken'] = fromToken

    def createStringForAddressJsFile(self):
        print('Operating out of path: ' + os.getcwd())
        print('Creating final string for address.js file...')
        self.stringForAddressJsFile = self.stringForAddressJsFile + 'const ' + self.blockchain['test_net'].upper() + ' = ' + json.dumps(self.addressJsData, indent=4) + ";\n"
        print(self.stringForAddressJsFile)

    def writeStringForAddressFile(self):
        print('Operating out of path: ' + os.getcwd())
        print('Writing final string to address.js file at: ' + self.paths['uniswap_addresses_js_file'])
        # This can be done with sed (as demonstrated in the following 2 lines) but I think the formatting of the output file is important so I will do it with Python fileinput
        #sedReplacementString = '1s/^/' + self.stringForAddressJsFile + '/'
        #subprocess.call(['sed', '-ir', sedReplacementString, os.path.join(self.paths['uniswap_source_code_dir'], 'ducks', 'addresses.js')])
        temp_data_1 = os.path.join(os.getcwd(), 'temp_data_1.js')
        temp_data_2 = os.path.join(os.getcwd(), 'temp_data_2.js')
        with open(temp_data_1, 'w') as tempOutFile:
            tempOutFile.write(self.stringForAddressJsFile)
        with open(temp_data_2, 'w') as fout, fileinput.input(files=(temp_data_1, self.paths['uniswap_addresses_js_file'])) as fin:
            for line in fin:
                fout.write(line)
        os.remove(temp_data_1)
        os.remove(self.paths['uniswap_addresses_js_file'])
        os.rename(temp_data_2, self.paths['uniswap_addresses_js_file'])

    def textReplacementFunction(self, configData, quotes, ignore = False):
        # This function will replace any text 
        print('Operating out of path: ' + os.getcwd())
        print('Performing text replacement in each individual file...')
        for (root, dirs, files) in os.walk(self.paths['uniswap_source_code_dir']):
            for name in files:
                print("Processing: " + os.path.join(root, name))
                for (key, value) in configData:
                    if(ignore != False and str(key) in ignore):
                        if(ignore[str(key)] == str(os.path.join(root, name))):
                           print("Skipping the replacement of " + str(key) + " in the file " + str(os.path.join(root, name)))
                           # fall out of this iteration of the configData for loop and continue on with the rest of the configData
                           continue
                    if(quotes == 2):
                        sedCommand = 's/\"' + key + '\"/\"' + value + '\"/g'
                    elif(quotes == 1):
                        sedCommand = 's/\'' + key + '\'/\'' + value + '\'/g'
                    elif(quotes == 0):
                        sedCommand = 's/' + key + '/' + value + '/g'
                    subprocess.call(['sed', '-ir', sedCommand, os.path.join(root, name)])
                    
    def performTextReplacements(self):
        # Call the text replacement function 0 = no quotes, 1 = single quotes and 2 = double quotes
        self.textReplacementFunction(self.quotedTextReplacements.items(), 2)
        # Deliberately ignore the text 'ethereum' which is surrounded in single quotes 
        # See https://github.com/CyberMiles/uniswap-port/issues/3 for more details
        self.textReplacementFunction(self.quotedTextReplacements.items(), 1, self.ignoreThisTextInThisFile.items())
        self.textReplacementFunction(self.unquotedTextReplacements.items(), 0)
        
        
    def performImageCopying(self):
        print('Operating out of path: ' + os.getcwd())
        print('Changing directories to ' + self.scriptExecutionLocation)
        os.chdir(self.scriptExecutionLocation)
        print('Copying image files...')
        for (root, dirs, files) in os.walk('./images'):
            for name in files:
                print('Copying: ' + os.path.join(root,name) + " to " + self.paths['uniswap_image_dir'])
                shutil.copy2(os.path.join(root, name), self.paths['uniswap_image_dir'])
    
    def caseSensitiveReplace(self, string, old, new):
        # Attribution https://stackoverflow.com/a/17729686/5500769 user:341329
        def repl(match):
            current = match.group()
            result = ''
            all_upper=True
            for i,c in enumerate(current):
                if i >= len(new):
                    break
                if c.isupper():
                    result += new[i].upper()
                else:
                    result += new[i].lower()
                    all_upper=False
            if all_upper:
                result += new[i+1:].upper()
            else:
                result += new[i+1:].lower()
            return result
        regex = re.compile(re.escape(old), re.I)
        return regex.sub(repl, string)

    def editPackageJson(self):
        print('Editing core package file to create npm start command')
        with open(self.paths['uniswap_package_json_file'], 'r') as pjf:
            self.packageJsonDict = json.load(pjf)
            tempDicts = {}
        for (key, value) in self.packageJsonDict['scripts'].items():
            if 'rinkeby' in str(key):
                newKey1 = self.caseSensitiveReplace(key, self.blockchain['uniswap_test_net'], self.blockchain['test_net'])
                newValue1 = self.caseSensitiveReplace(value, self.blockchain['uniswap_test_net'], self.blockchain['test_net'])
                newValue2 = self.caseSensitiveReplace(newValue1, self.blockchain['uniswap_test_net_id'], self.blockchain['test_net_id'])
                print(newKey1)
                print(newValue2)
                tempDicts[newKey1] = [newValue2]
        for (key, value) in tempDicts.items():
            self.packageJsonDict['scripts'][key] = value
        with open(self.paths['uniswap_package_json_file'], 'w') as pjfW:
            pjfW.write(json.dumps(self.packageJsonDict, indent=4))

    def printMessage(self):
        print("Porting complete")
        #print("To investigate filenames containing the string \"ethereum\" please use the following find command")
        #print("find " + self.paths['uniswap_base_dir'] + " -name \"*ethereum*\" -print")
        
        #print("To investigate instances of the string \"ethereum\" in any and all files, please use the following grep command")
        #print("grep -rnw " + "\'" + self.paths['uniswap_base_dir'] + "\'"+ " -e \'ethereum\'")
        
        print("\nPlease install yarn by following the instructions at the following URL")
        print('''https://yarnpkg.com/lang/en/docs/install/#debian-stable''')
        
        print("\nPlease install node by following the instructions at the following URL")
        print("https://github.com/nodesource/distributions/blob/master/README.md#debinstall")
        
        print("\nTo run Uniswap, type the following commands")
        print("cd " + self.paths['uniswap_base_dir']) 
        print("npm install")
        print("yarn start:" + self.blockchain['test_net'] + " --loglevel verbose")
    # CLASS METHODS - END

# DRIVER - START
uniswapPort = UP()
uniswapPort.cleanUp()
uniswapPort.housekeeping()
uniswapPort.fetchUniswapSourceCode()
uniswapPort.unpackUniswapSourceCode()
uniswapPort.runBuildAddresses()
uniswapPort.pairExchangeAndTokenAddresses()
uniswapPort.createStringForAddressJsFile()
uniswapPort.writeStringForAddressFile()
uniswapPort.performTextReplacements()
uniswapPort.performImageCopying()
uniswapPort.editPackageJson()
uniswapPort.printMessage()
# DRIVER - END

