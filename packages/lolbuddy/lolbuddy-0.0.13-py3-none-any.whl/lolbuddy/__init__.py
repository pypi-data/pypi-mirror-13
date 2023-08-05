#!/usr/bin/env python3
import json
from requests_futures.sessions import FuturesSession
import sys

def main():
    #apiKey = input('API key not found, please enter it: ')
    #location = input('League of Legends not found in the default location, please enter its current location: ')

    session = FuturesSession()

    apiKey = '90e995640c7be38963c1b70e7c2af77e'
    url = 'http://api.champion.gg/champion?api_key=' + apiKey

    '''
    infoRequest = session.get(url) #start request

    champions = json.loads(infoRequest.result().content.decode('utf-8')) #finish request
    totalChampions = len(champions)
    championsComplete = 0
    print('There are currently {0} champions. Getting individual champion data...\n'.format(totalChampions))

    championInfo = []

    def incrementChamps(sess, resp):
        nonlocal championsComplete
        championsComplete += 1

    for champion in champions:
        url = 'http://api.champion.gg/champion/' + champion['key'] + '?&api_key=' + apiKey
        championData = session.get(url, background_callback=incrementChamps)
        championInfo.append(championData)


    while championsComplete < totalChampions:
        print ('({0}/{1}) champions complete...'.format(championsComplete, totalChampions), end='\r')
        sys.stdout.flush()

    print('\n\nALL DONE!')
    '''
    print('ASDFASDFADSF IT WORKS!!!!!!');

if __name__ == '__main__':
    main()
