# coding: utf-8

from smartbot import Utils

import re
import os
import tempfile
import subprocess
import requests
from lxml import etree
from lxml import html
from urllib import (quote, quote_plus)

class ExternalAPI:
    bingAppId = None

    @staticmethod
    def getBingAppId():
        if not ExternalAPI.bingAppId:
            headers = { 'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_10_5) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/47.0.2526.73 Safari/537.36' }
            response = requests.get('http://www.bing.com/translator/dynamic/226010/js/LandingPage.js?loc=pt&phenabled=&rttenabled=&v=226010', headers=headers)
            match = re.match('.*rttAppId:"([^"]+)".*', response.text)
            ExternalAPI.bingAppId = match.groups()[0] if match else None
        return ExternalAPI.bingAppId

    @staticmethod
    def translate(text, fromLanguage='en', toLanguage=None):
        if not toLanguage:
            toLanguage = 'pt' if fromLanguage == 'en' else 'en'
        bingAppId = ExternalAPI.getBingAppId()
        text = text.encode('utf-8')
        headers = { 'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_10_5) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/47.0.2526.73 Safari/537.36' }
        text = re.sub('\s+', ' ', text, re.UNICODE)
        translateUrl = 'http://api.microsofttranslator.com/v2/ajax.svc/TranslateArray2?appId=%22' + bingAppId + '%22&texts=%5B%22' + quote_plus(text) + '%22%5D&from=%22' + fromLanguage + '%22&to=%22' + toLanguage + '%22&options=%7B%7D&oncomplete=onComplete_19&onerror=onError_19&_=1450313639189'
        response = requests.get(translateUrl, headers=headers)
        match = re.match('.*TranslatedText":"(.*)","TranslatedTextSentenceLengths.*', response.text, re.UNICODE)
        result = unicode(match.groups()[0]) if match else None
        return result

    @staticmethod
    def textToSpeech(text, language='pt', encode='mp3'):
        headers = { 'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_10_5) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/47.0.2526.73 Safari/537.36' }
        baseName = tempfile.mkstemp()[1]
        mp3Name = baseName + '.mp3'
        fd = file(mp3Name, 'ab')
	text = text.encode('utf-8')
        words = re.split('\s+', text, re.UNICODE)
        words = filter(lambda word: word.strip(), words)
        if len(words) < 50:
            bingAppId = ExternalAPI.getBingAppId()
            bingLanguage = 'pt-BR' if language == 'pt' else 'en-US'
            ttsUrl = 'http://api.microsofttranslator.com/v2/http.svc/speak?appId=' + bingAppId + '&language=' + bingLanguage + '&format=audio/mp3&options=MinSize|male&text=' + quote(text)
            response = requests.get(ttsUrl, headers=headers)
            fd.write(response.content)
        else:
            for wordPos in range(0, len(words), 40):
                piece = ' '.join(words[wordPos:wordPos+40])
                pieceFileName = ExternalAPI.textToSpeech(piece, language, encode)
                pieceFile = file(pieceFileName, 'rb')
                fd.write(pieceFile.read())
                pieceFile.close()
        fd.close()
        if encode == 'mp3':
            return mp3Name
        elif encode == 'ogg':
            oggName = baseName + '.ogg'
            subprocess.call(('ffmpeg -v -8 -i %s -acodec libvorbis %s' % (mp3Name, oggName)).split(' '))
            return oggName
        else:
            return None

    @staticmethod
    def searchJoke(query=None):
        if query:
            tree = Utils.crawlUrl('http://www.piadasnet.com/index.php?pesquisaCampo=%s&btpesquisa=OK&pesquisaInicio=0' % quote(query.encode('utf-8')))
        else:
            tree = Utils.crawlUrl('http://www.piadasnet.com/')
        jokeTags = tree.xpath('//p[contains(@class, "piada")]')
        return map(lambda t: t.text_content(), jokeTags)

    @staticmethod
    def searchGoogleImage(query):
        query = query.encode('utf-8')
        tree = Utils.crawlUrl('https://www.google.com.br/search?site=&tbm=isch&q=%s&oq=%s&tbs=isz:l' % (quote(query), quote(query)))
        imageTags = tree.xpath('//img[contains(@src, "gstatic")]')
        imageSources = map(lambda img: img.attrib.get('src'), imageTags)
        return imageSources

    @staticmethod
    def searchBingImage(query):
        tree = Utils.crawlUrl('http://www.bing.com/images/search?q=%s' % quote(query.encode('utf-8')))
        imageTags = tree.xpath('//img[contains(@src, "bing.net")]')
        imageSources = map(lambda img: img.attrib.get('src'), imageTags)
        return imageSources

    @staticmethod
    def getNasaIOD():
        tree = Utils.crawlUrl('http://apod.nasa.gov')
        imageTags = tree.xpath('//img[contains(@src,"image")]')
        pTags = tree.xpath('//p')
        if imageTags and len(pTags) >= 3:
            result = { 'imageSource': 'http://apod.nasa.gov/%s' % imageTags[0].attrib['src'], 'explanation': pTags[2].text_content() }
            return result
        else:
            return None

    @staticmethod
    def wolframQuery(query, appId=None):
        query = query.encode('utf-8')
        response = requests.get('http://api.wolframalpha.com/v2/query?input=%s&appid=%s' % (quote(query), appId))
        try:
            tree = etree.fromstring(response.content)
            results = []
            results += tree.xpath('//pod[contains(@title, "Solution")]/subpod/plaintext')
            results += tree.xpath('//pod[contains(@title, "Result")]/subpod/plaintext')
            results += tree.xpath('//pod[contains(@scanner, "Data")]/subpod/plaintext')
            if len(results) >= 0 and results[0].text and results[0].text.strip():
                return results[0].text.decode('utf-8')
            else:
                return None
        except:
            return None

    @staticmethod
    def eviQuery(query):
        query = query.encode('utf-8')
        query = re.sub('(\?|&)', ' ', query)
        query = re.sub('\s+', '_', query.strip().lower())
        headers = { 'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_10_5) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/47.0.2526.73 Safari/537.36' }
        response = requests.get('https://www.evi.com/q/%s' % quote(query), headers=headers)
        tree = html.fromstring(response.text)
        results = tree.xpath('//*[contains(@class, "tk_text") or contains(@class, "tk_common")]')
        results = map(lambda tag: tag.text_content(), results)
        results = filter(lambda text: text.strip(), results)
        try:
            if len(results) >= 1 and results[0] and results[0].strip():
                result = results[0].strip()
                if result != 'Sorry, I don\'t yet have an answer to that question.':
                    return result.decode('utf-8')
                else:
                    return None
            else:
                return None
        except:
            return None
