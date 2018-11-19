import os
import json
import requests
import subprocess
import configparser
import shutil
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

        self.networkName = config['blockchain']['networkName']
        print("networkName: " + self.networkName)

        self.networkId = config['blockchain']['networkId']
        print("networkId: " + self.networkId)

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

        self.multicaseTextReplacements = {}
        for key in config['multicaseTextReplacements']:
            stringKey = str(key)
            upperStringKey = stringKey.upper()
            self.multicaseTextReplacements[stringKey] = config['multicaseTextReplacements'][stringKey]
            valueToConvert = config['multicaseTextReplacements'][stringKey]
            self.multicaseTextReplacements[stringKey.capitalize()] = str(valueToConvert).capitalize()
            self.multicaseTextReplacements[stringKey.upper()] = str(valueToConvert).upper()
            self.multicaseTextReplacements[key] = config['multicaseTextReplacements'][key]
        print("\nMulticaseTextReplacements:")
        for (ufaKey, ufaValue) in self.multicaseTextReplacements.items():
            print(ufaKey + ": " + ufaValue)

        self.lowerCaseTextReplacements = {}
        for key in config['lowerCaseTextReplacements']:
            stringKey = str(key)
            self.lowerCaseTextReplacements[stringKey] = config['lowerCaseTextReplacements'][stringKey]
        print("\nLowerCaseTextReplacements:")
        for (ufaKey, ufaValue) in self.lowerCaseTextReplacements.items():
            print(ufaKey + ": " + ufaValue)

        self.paths = {}
        for key in config['paths']:
            stringKey = str(key)
            self.paths[stringKey] = config['paths'][key]
        print("\nPaths:")
        for (ufaKey, ufaValue) in self.paths.items():
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
        self.addressJsData[addressType]['address'] = addresses

    def runBuildAddresses(self):
        print('Operating out of path: ' + os.getcwd())
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
        self.stringForAddressJsFile = self.stringForAddressJsFile + 'const ' + self.networkName.upper() + ' = ' + json.dumps(self.addressJsData, indent=4) + ";\n"
        print(self.stringForAddressJsFile)

    def writeStringForAddressFile(self):
        print('Operating out of path: ' + os.getcwd())
        print('Writing final string to address.js file...')
        print("****")
        #'1s/^/const TRAVIS
        #'1s/^/dddddddoooooooggggggg\n/' asdf.txt)
        sedReplacementString = '\'1s/^/' + self.stringForAddressJsFile + '\'/'
        print('The sed sedReplacementString is ' + sedReplacementString)
        subprocess.call(['sed', '-ir', sedReplacementString, os.path.join(self.paths['uniswap_source_code_dir'], 'ducks', 'addresses.js')])
    
    def performTextReplacements(self):
        print('Operating out of path: ' + os.getcwd())
        print('Performing text replacement in each individual file...')
        for (root, dirs, files) in os.walk(self.paths['uniswap_source_code_dir']):
            for name in files:
                print("Processing: " + os.path.join(root, name))
                for (key, value) in self.multicaseTextReplacements.items():
                    sedCommandSingleQuotes = 's/\'' + key + '\'/\'' + value + '\'/g'
                    sedCommandDoubleQuotes = 's/\"' + key + '\"/\"' + value + '\"/g'
                    #print(sedCommandSingleQuotes)
                    #print(sedCommandDoubleQuotes)
                    subprocess.call(['sed', '-ir', sedCommandSingleQuotes, os.path.join(root, name)])
                    subprocess.call(['sed', '-ir', sedCommandDoubleQuotes, os.path.join(root, name)])

    def performImageCopying(self):
        print('Operating out of path: ' + os.getcwd())
        print('Changing directories to ' + self.scriptExecutionLocation)
        os.chdir(self.scriptExecutionLocation)
        print('Copying image files...')
        for (root, dirs, files) in os.walk('./images'):
            for name in files:
                print('Copying: ' + os.path.join(root,name) + " to " + self.paths['uniswap_image_dir'])
                shutil.copy2(os.path.join(root, name), self.paths['uniswap_image_dir'])
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
# DRIVER - END

