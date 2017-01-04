# -*- coding: utf-8 -*-
#############################################################################
#このモジュールでは､bloombergのニュースサイトから､一定のニュースを取得する｡このバージョンでは､日本語版のページを対象とする｡
#取得対象を絞るため､起動引数として文字列を与え､その文字列を本文に含むニュースを取得対象とする｡
#検索対象は､トップページから､1階層下のページまでとする｡
#############################################################################

#必要なモジュールをインポートする
from urllib.request import urlopen
from bs4 import BeautifulSoup
import re
import datetime as dt
import codecs

#TODO 起動引数か何かで､日本語版と英語版のどちらから情報を取得するかを選べるようにしたい
#トップページのURL
topPageUrl = "https://www.bloomberg.co.jp"

###引数で受け取ったURLのHTMLについてのBeautifulSoupオブジェクトを返す関数###
def getBsObj(url):
    html = urlopen(url)
    return BeautifulSoup(html, "html.parser")

def getPrintBody(bsObj):
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

#bloombergのトップページにアクセスする(今回はデフォルトで日本語版のページにする
def main():
    try:
        bsObjTop = getBsObj(topPageUrl)

        ###個別のニュースページへのリンクを取得する｡###
        articleLinks = [] #個々のページのリンクを格納するためのリスト

        articleTags = bsObjTop.findAll("article")
        for t in articleTags:
            link = t.find("a").attrs["href"]
            articleLinks.append(link)

        #ループして､各ニュースページにそれぞれアクセスする
        #検索対象の文字列 TODO 検索対象の文字列は､外から与えたい
        target = "トランプ"

        file = codecs.open("C:\\Temp\\work\\python_webscraping\\bloomberg\\" + str(dt.date.today()) +".txt", "w", "utf-8")#出力対象のファイル
        for link in articleLinks:
            targetUrl = topPageUrl + link
            bsObj = getBsObj(targetUrl)
            #出力する文字列を取得する
            printBody = getPrintBody(bsObj)
            #何も返ってこなければ､この記事は無視
            if len(printBody) != 0:
                file.write("Title:" + bsObj.find("title").get_text() + "\n")
                file.write("body:"+printBody+ "\n")
                file.write("---------------------------------------------------------------------------------\n")

        #TODO ファイル名はどんな感じにしたらちょうどよいだろうか｡
        #ファイル名の指定には､スラが入るので気を着けること

        #処理終了がわかりにくいので､出力してみただけです｡
        print("Done!!!")
    except requests.TimeoutError as err:
        print("Error happens:Timeout -> " + err.message)

    finally:
        file.close()

#main関数
if __name__ == '__main__':
    main()
#CHECK 起動引数の与え方
#引数に受け取った文字列を､ニュース本文は含む場合は､取得対象のニュースとして判断する｡

#テキストファイルに､タイトルと本文を出力する｡
#TODO ファイルの出力先は､外部から指定したい｡ プロパティファイルか何かに定義しておくのがよいだろうか｡(まぁとりあえずハードコードでいいや)