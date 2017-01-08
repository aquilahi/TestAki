# -*- coding: utf-8 -*-
#############################################################################
#このモジュールでは､bloombergのニュースサイトから､一定のニュースを取得する｡このバージョンでは､日本語版のページを対象とする｡
#取得対象を絞るため､起動引数として文字列を与え､その文字列を本文に含むニュースを取得対象とする｡
#検索対象は､トップページから､1階層下のページまでとする｡
#############################################################################

#必要なモジュールをインポートする
from urllib.request import urlopen
from urllib import request
from bs4 import BeautifulSoup
import re
import datetime as dt
import codecs
import sys

#ファイルから読み込む想定のpropertyのkeyになる文字列を定義する
ARGS_FILE_PATH = "ArgumentFilePath" #argsファイルのパス
NEWS_LANG = "lang" #読み込むニュースの言語
OUTPUT_PATH = "outputPath" #出力ファイルの置き場所
TARGET_WORD = "target"
ENCODING = "utf-8"

#本文生成処理の中で使う文字列を定義する
NEWS_TITLE = "newsTitle"
NEWS_BODY = "newsBody" 
###引数で受け取ったURLのHTMLについてのBeautifulSoupオブジェクトを返す関数###
###arg:URL to build BeautifulSoup object###
def get_bs_obj(url):
    html = urlopen(url)
    return BeautifulSoup(html, "html.parser")

###受け取ったオブジェクトに含まれるニュース本文を取得します｡###
def get_print_body(bsObj,target):
    divs = bsObj.find("div", class_="article-body__content").findAll("p")

    #この記事が出力対象であるか｡
    toPrint = False

    #出力用の文字列を初期化する
    body = ""

    for d in divs:
        text = d.get_text()
        if target in text:
            toPrint = True

        body = body + "\n" + text


    if toPrint:
        return body
    else:
        print("This word is not included in this article:" + bsObj.find("title").get_text())
        return ""


#ファイルへの書き込みを行う関数
#どのような形式で書き出すかを定義する
def write_output_file(textData, fileObj):
    fileObj.write("TITLE:" + textData[NEWS_TITLE] + "\n")
    fileObj.write("ARTICLE:" + textData[NEWS_BODY] + "\n")
    fileObj.write("---------------------------------------------------------------------------------\n")
    return fileObj


###ファイルの中身を､dist形式で取得します｡###
###ファイルはkey:value形式で記述されていることが前提です｡###
def get_file_contents(filepath):

    #return value
    contents = {}
    for line in codecs.open(filepath,"r",ENCODING):
        #コメント行は無視
        if re.match("^#", line):
            continue

        #key,value形式で記述されている想定
        #TODO 想定外の記述に対応する
        keyValue = line.split(",")
        contents[keyValue[0]] = keyValue[1].replace('\n','').replace('\r','')
 
    return contents

#bloombergのトップページにアクセスする(今回はデフォルトで日本語版のページにする
#arg: properties 実行時に必要な属性情報を保持したdictionary
def main(properties):
        #検索対象ワードやニュース取得先などは､外部ファイルから読み込む
        args = get_file_contents(properties[ARGS_FILE_PATH])


        newsLang = args[NEWS_LANG]
        topPageUrl = ""

        #ニュースの言語を選択する｡それによって､情報を取りにいくURLを変える
        #propertyファイルにURLを定義してもよいが､このモジュールではbloombergしか対応しないので､言語だけを選択出来るようにした｡
        #URL変わったら､コード直すというのもかっこ悪いけど｡｡｡
        #改行コードかなにかが含まれてしまうようなので､前方一致としている｡
        if newsLang.startswith("Japanese"):
            topPageUrl = "https://www.bloomberg.co.jp"
        elif newsLang.startswith("English"): #TODO 動作未確認です!!!
            topPageUrl = "https://www.bloomberg.com/asia"
        else:
            #想定外の言語が指定された場合は､どうせ動かないので停止する
            print("Unexpected Argument:" + newsLang)
            sys.exit()

        bsObjTop = get_bs_obj(topPageUrl)

        ###個別のニュースページへのリンクを取得する｡###
        articleLinks = [] #個々のページのリンクを格納するためのリスト

        articleTags = bsObjTop.findAll("article")
        for t in articleTags:
            link = t.find("a").attrs["href"]
            articleLinks.append(link)

        #ループして､各ニュースページにそれぞれアクセスする
        target = args[TARGET_WORD]

        #検索結果を出力するファイル
        #ファイル名は､#日付#.txtにしてある
        file = codecs.open(args[OUTPUT_PATH] + str(dt.date.today()) + ".txt", "w", ENCODING)#出力対象のファイル
        for link in articleLinks:
            targetUrl = topPageUrl + link
            bsObj = get_bs_obj(targetUrl)
            #出力する文字列を取得する
            printBody = get_print_body(bsObj, target)
            #何も返ってこなければ､この記事は無視
            if len(printBody) != 0:
                file = write_output_file({NEWS_TITLE:bsObj.find("title").get_text(), NEWS_BODY:printBody}, file)

        file.close()

        #処理終了がわかりにくいので､出力してみただけです｡
        print("----Successfully finished-----")

#main関数
if __name__ == '__main__':
    #起動直後にpropertyファイルを読み込んで､実行に必要な属性情報を取得する
    properties = get_file_contents(".\\property\\property.txt")
    #実際の処理は､以下の関数以降で行う
    main(properties)