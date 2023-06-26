# -*- coding: utf-8 -*-
# Copyright (c) 2021 Tachibana Securities Co., Ltd. All rights reserved.

# 2021.07.09,   yo.
# 2023.04.14 reviced,   yo.
# Python 3.6.8 / centos7.4
# API v4r3 で動作確認
# 立花証券ｅ支店ＡＰＩ利用のサンプルコード
# ログインして属性取得、指定した項目別のマスターデータを取得、ログアウトします。
# 利用方法: コード後半にある「プログラム始点」以下の設定項目を自身の設定に変更してご利用ください。
#
# == ご注意: ========================================
#   本番環境にに接続した場合、実際に市場に注文を出せます。
#   市場で約定した場合取り消せません。
# ==================================================
#

import urllib3
import datetime
import json
import time


#--- 共通コード ------------------------------------------------------

# request項目を保存するクラス。配列として使う。
# 'p_no'、'p_sd_date'は格納せず、func_make_url_requestで生成する。
class class_req :
    def __init__(self) :
        self.str_key = ''
        self.str_value = ''
        
    def add_data(self, work_key, work_value) :
        self.str_key = work_key
        self.str_value = work_value


# 口座属性クラス
class class_def_cust_property:
    def __init__(self):
        self.sUrlRequest = ''       # request用仮想URL
        self.sUrlMaster = ''        # master用仮想URL
        self.sUrlPrice = ''         # price用仮想URL
        self.sUrlEvent = ''         # event用仮想URL
        self.sZyoutoekiKazeiC = ''  # 8.譲渡益課税区分    1：特定  3：一般  5：NISA     ログインの返信データで設定済み。 
        self.sSecondPassword = ''   # 22.第二パスワード  APIでは第２暗証番号を省略できない。 関連資料:「立花証券・e支店・API、インターフェース概要」の「3-2.ログイン、ログアウト」参照
        self.sJsonOfmt = ''         # 返り値の表示形式指定
        


# 機能: システム時刻を"p_sd_date"の書式の文字列で返す。
# 返値: "p_sd_date"の書式の文字列
# 引数1: システム時刻
# 備考:  "p_sd_date"の書式：YYYY.MM.DD-hh:mm:ss.sss
def func_p_sd_date(int_systime):
    str_psddate = ''
    str_psddate = str_psddate + str(int_systime.year) 
    str_psddate = str_psddate + '.' + ('00' + str(int_systime.month))[-2:]
    str_psddate = str_psddate + '.' + ('00' + str(int_systime.day))[-2:]
    str_psddate = str_psddate + '-' + ('00' + str(int_systime.hour))[-2:]
    str_psddate = str_psddate + ':' + ('00' + str(int_systime.minute))[-2:]
    str_psddate = str_psddate + ':' + ('00' + str(int_systime.second))[-2:]
    str_psddate = str_psddate + '.' + (('000000' + str(int_systime.microsecond))[-6:])[:3]
    return str_psddate


# JSONの値の前後にダブルクオーテーションが無い場合付ける。
def func_check_json_dquat(str_value) :
    if len(str_value) == 0 :
        str_value = '""'
        
    if not str_value[:1] == '"' :
        str_value = '"' + str_value
        
    if not str_value[-1:] == '"' :
        str_value = str_value + '"'
        
    return str_value
    
    
# 受けたテキストの１文字目と最終文字の「"」を削除
# 引数：string
# 返り値：string
def func_strip_dquot(text):
    if len(text) > 0:
        if text[0:1] == '"' :
            text = text[1:]
            
    if len(text) > 0:
        if text[-1] == '\n':
            text = text[0:-1]
        
    if len(text) > 0:
        if text[-1:] == '"':
            text = text[0:-1]
        
    return text
    


# 機能: URLエンコード文字の変換
# 引数1: 文字列
# 返値: URLエンコード文字に変換した文字列
# 
# URLに「#」「+」「/」「:」「=」などの記号を利用した場合エラーとなる場合がある。
# APIへの入力文字列（特にパスワードで記号を利用している場合）で注意が必要。
#   '#' →   '%23'
#   '+' →   '%2B'
#   '/' →   '%2F'
#   ':' →   '%3A'
#   '=' →   '%3D'
def func_replace_urlecnode( str_input ):
    str_encode = ''
    str_replace = ''
    
    for i in range(len(str_input)):
        str_char = str_input[i:i+1]

        if str_char == ' ' :
            str_replace = '%20'       #「 」 → 「%20」 半角空白
        elif str_char == '!' :
            str_replace = '%21'       #「!」 → 「%21」
        elif str_char == '"' :
            str_replace = '%22'       #「"」 → 「%22」
        elif str_char == '#' :
            str_replace = '%23'       #「#」 → 「%23」
        elif str_char == '$' :
            str_replace = '%24'       #「$」 → 「%24」
        elif str_char == '%' :
            str_replace = '%25'       #「%」 → 「%25」
        elif str_char == '&' :
            str_replace = '%26'       #「&」 → 「%26」
        elif str_char == "'" :
            str_replace = '%27'       #「'」 → 「%27」
        elif str_char == '(' :
            str_replace = '%28'       #「(」 → 「%28」
        elif str_char == ')' :
            str_replace = '%29'       #「)」 → 「%29」
        elif str_char == '*' :
            str_replace = '%2A'       #「*」 → 「%2A」
        elif str_char == '+' :
            str_replace = '%2B'       #「+」 → 「%2B」
        elif str_char == ',' :
            str_replace = '%2C'       #「,」 → 「%2C」
        elif str_char == '/' :
            str_replace = '%2F'       #「/」 → 「%2F」
        elif str_char == ':' :
            str_replace = '%3A'       #「:」 → 「%3A」
        elif str_char == ';' :
            str_replace = '%3B'       #「;」 → 「%3B」
        elif str_char == '<' :
            str_replace = '%3C'       #「<」 → 「%3C」
        elif str_char == '=' :
            str_replace = '%3D'       #「=」 → 「%3D」
        elif str_char == '>' :
            str_replace = '%3E'       #「>」 → 「%3E」
        elif str_char == '?' :
            str_replace = '%3F'       #「?」 → 「%3F」
        elif str_char == '@' :
            str_replace = '%40'       #「@」 → 「%40」
        elif str_char == '[' :
            str_replace = '%5B'       #「[」 → 「%5B」
        elif str_char == ']' :
            str_replace = '%5D'       #「]」 → 「%5D」
        elif str_char == '^' :
            str_replace = '%5E'       #「^」 → 「%5E」
        elif str_char == '`' :
            str_replace = '%60'       #「`」 → 「%60」
        elif str_char == '{' :
            str_replace = '%7B'       #「{」 → 「%7B」
        elif str_char == '|' :
            str_replace = '%7C'       #「|」 → 「%7C」
        elif str_char == '}' :
            str_replace = '%7D'       #「}」 → 「%7D」
        elif str_char == '~' :
            str_replace = '%7E'       #「~」 → 「%7E」
        else :
            str_replace = str_char

        str_encode = str_encode + str_replace
        
    return str_encode



# 機能： API問合せ文字列を作成し返す。
# 戻り値： url文字列
# 第１引数： ログインは、Trueをセット。それ以外はFalseをセット。
# 第２引数： ログインは、APIのurlをセット。それ以外はログインで返された仮想url（'sUrlRequest'等）の値をセット。
# 第３引数： 要求項目のデータセット。クラスの配列として受取る。
def func_make_url_request(auth_flg, \
                          url_target, \
                          work_class_req) :
    work_key = ''
    work_value = ''

    str_url = url_target
    if auth_flg == True :
        str_url = str_url + 'auth/'

    str_url = str_url + '?{\n\t'
    
    for i in range(len(work_class_req)) :
        work_key = func_strip_dquot(work_class_req[i].str_key)
        if len(work_key) > 0:
            if work_key[:1] == 'a' :
                work_value = work_class_req[i].str_value
            else :
                work_value = func_check_json_dquat(work_class_req[i].str_value)

            str_url = str_url + func_check_json_dquat(work_class_req[i].str_key) \
                                + ':' + work_value \
                                + ',\n\t'
               
        
    str_url = str_url[:-3] + '\n}'
    return str_url



# 機能: API問合せ。通常のrequest,price用。
# 返値: API応答（辞書型）
# 第１引数： URL文字列。
# 備考: APIに接続し、requestの文字列を送信し、応答データを辞書型で返す。
#       master取得は専用の func_api_req_muster を利用する。
def func_api_req(str_url): 
    print('送信文字列＝')
    print(str_url)  # 送信する文字列

    # APIに接続
    http = urllib3.PoolManager()
    req = http.request('GET', str_url)
    print("req.status= ", req.status )

    # 取得したデータを、json.loadsを利用できるようにstr型に変換する。日本語はshift-jis。
    bytes_reqdata = req.data
    str_shiftjis = bytes_reqdata.decode("shift-jis", errors="ignore")

    print('返信文字列＝')
    print(str_shiftjis)

    # JSON形式の文字列を辞書型で取り出す
    json_req = json.loads(str_shiftjis)

    return json_req



# ログイン関数
# 引数1: p_noカウンター
# 引数2: アクセスするurl（'auth/'以下は付けない）
# 引数3: ユーザーID
# 引数4: パスワード
# 引数5: 口座属性クラス
# 返値：辞書型データ（APIからのjson形式返信データをshift-jisのstring型に変換し、更に辞書型に変換）
def func_login(int_p_no, my_url, str_userid, str_passwd, class_cust_property):
    # 送信項目の解説は、マニュアル「立花証券・ｅ支店・ＡＰＩ（ｖ〇）、REQUEST I/F、機能毎引数項目仕様」
    # p2/46 No.1 引数名:CLMAuthLoginRequest を参照してください。
    
    req_item = [class_req()]
    str_p_sd_date = func_p_sd_date(datetime.datetime.now())     # システム時刻を所定の書式で取得

    str_key = '"p_no"'
    str_value = func_check_json_dquat(str(int_p_no))
    #req_item.append(class_req())
    req_item[-1].add_data(str_key, str_value)

    str_key = '"p_sd_date"'
    str_value = str_p_sd_date
    req_item.append(class_req())
    req_item[-1].add_data(str_key, str_value)

    str_key = '"sCLMID"'
    str_value = 'CLMAuthLoginRequest'
    req_item.append(class_req())
    req_item[-1].add_data(str_key, str_value)

    str_key = '"sUserId"'
    str_value = str_userid
    req_item.append(class_req())
    req_item[-1].add_data(str_key, str_value)
    
    str_key = '"sPassword"'
    str_value = str_passwd
    req_item.append(class_req())
    req_item[-1].add_data(str_key, str_value)
    
    # 返り値の表示形式指定
    str_key = '"sJsonOfmt"'
    str_value = class_cust_property.sJsonOfmt    # "5"は "1"（1ビット目ＯＮ）と”4”（3ビット目ＯＮ）の指定となり「ブラウザで見や易い形式」且つ「引数項目名称」で応答を返す値指定
    req_item.append(class_req())
    req_item[-1].add_data(str_key, str_value)

    # ログインとログイン後の電文が違うため、第１引数で指示。
    # ログインはTrue。それ以外はFalse。
    # このプログラムでの仕様。APIの仕様ではない。
    # URL文字列の作成
    str_url = func_make_url_request(True, \
                                     my_url, \
                                     req_item)
    # API問合せ
    json_return = func_api_req(str_url)
    # 戻り値の解説は、マニュアル「立花証券・ｅ支店・ＡＰＩ（ｖ〇）、REQUEST I/F、機能毎引数項目仕様」
    # p2/46 No.2 引数名:CLMAuthLoginAck を参照してください。

    int_p_errno = int(json_return.get('p_errno'))    # p_erronは、マニュアル「立花証券・ｅ支店・ＡＰＩ（ｖ〇ｒ〇）、REQUEST I/F、利用方法、データ仕様」を参照ください。
    if not json_return.get('sResultCode') == None :
        int_sResultCode = int(json_return.get('sResultCode'))
    else :
        int_sResultCode = -1
    # sResultCodeは、マニュアル
    # 「立花証券・ｅ支店・ＡＰＩ（ｖ〇ｒ〇）、REQUEST I/F、注文入力機能引数項目仕様」
    # (api_request_if_order_vOrO.pdf)
    # の p13/42 「6.メッセージ一覧」を参照ください。
    #
    # 時間外の場合 'sResultCode' が返らないので注意
    # 参考例
    # {
    #         "p_no":"1",
    #         "p_sd_date":"2022.11.25-08:28:04.609",
    #         "p_rv_date":"2022.11.25-08:28:04.598",
    #         "p_errno":"-62",
    #         "p_err":"システム、情報提供時間外。",
    #         "sCLMID":"CLMAuthLoginRequest"
    # }




    if int_p_errno ==  0 and int_sResultCode == 0:    # ログインエラーでない場合
        # ---------------------------------------------
        # ログインでの注意点
        # 契約締結前書面が未読の場合、
        # 「int_p_errno = 0 And int_sResultCode = 0」で、
        # sUrlRequest=""、sUrlEvent="" が返されログインできない。
        # ---------------------------------------------
        if len(json_return.get('sUrlRequest')) > 0 :
            # 口座属性クラスに取得した値をセット
            class_cust_property.sZyoutoekiKazeiC = json_return.get('sZyoutoekiKazeiC')
            class_cust_property.sUrlRequest = json_return.get('sUrlRequest')        # request用仮想URL
            class_cust_property.sUrlMaster = json_return.get('sUrlMaster')          # master用仮想URL
            class_cust_property.sUrlPrice = json_return.get('sUrlPrice')            # price用仮想URL
            class_cust_property.sUrlEvent = json_return.get('sUrlEvent')            # event用仮想URL
            bool_login = True
        else :
            print('契約締結前書面が未読です。')
            print('ブラウザーで標準Webにログインして確認してください。')
    else :  # ログインに問題があった場合
        print('p_errno:', json_return.get('p_errno'))
        print('p_err:', json_return.get('p_err'))
        print('sResultCode:', json_return.get('sResultCode'))
        print('sResultText:', json_return.get('sResultText'))
        print()
        bool_login = False

    return bool_login



# ログアウト
# 引数1: p_noカウンター
# 引数2: class_cust_property（request通番）, 口座属性クラス
# 返値：辞書型データ（APIからのjson形式返信データをshift-jisのstring型に変換し、更に辞書型に変換）
def func_logout(int_p_no, class_cust_property):
    # 送信項目の解説は、マニュアル「立花証券・ｅ支店・ＡＰＩ（ｖ〇）、REQUEST I/F、機能毎引数項目仕様」
    # p3/46 No.3 引数名:CLMAuthLogoutRequest を参照してください。
    
    req_item = [class_req()]
    str_p_sd_date = func_p_sd_date(datetime.datetime.now())     # システム時刻を所定の書式で取得

    str_key = '"p_no"'
    str_value = func_check_json_dquat(str(int_p_no))
    #req_item.append(class_req())
    req_item[-1].add_data(str_key, str_value)

    str_key = '"p_sd_date"'
    str_value = str_p_sd_date
    req_item.append(class_req())
    req_item[-1].add_data(str_key, str_value)

    str_key = '"sCLMID"'
    str_value = 'CLMAuthLogoutRequest'  # logoutを指示。
    req_item.append(class_req())
    req_item[-1].add_data(str_key, str_value)
    
    # 返り値の表示形式指定
    str_key = '"sJsonOfmt"'
    str_value = class_cust_property.sJsonOfmt    # "5"は "1"（ビット目ＯＮ）と”4”（ビット目ＯＮ）の指定となり「ブラウザで見や易い形式」且つ「引数項目名称」で応答を返す値指定
    req_item.append(class_req())
    req_item[-1].add_data(str_key, str_value)
    
    # ログインとログイン後の電文が違うため、第１引数で指示。
    # ログインはTrue。それ以外はFalse。
    # このプログラムでの仕様。APIの仕様ではない。
    # URL文字列の作成
    str_url = func_make_url_request(False, \
                                     class_cust_property.sUrlRequest, \
                                     req_item)
    # API問合せ
    json_return = func_api_req(str_url)
    # 戻り値の解説は、マニュアル「立花証券・ｅ支店・ＡＰＩ（ｖ〇）、REQUEST I/F、機能毎引数項目仕様」
    # p3/46 No.4 引数名:CLMAuthLogoutAck を参照してください。

    int_sResultCode = int(json_return.get('sResultCode'))    # p_erronは、マニュアル「立花証券・ｅ支店・ＡＰＩ（ｖ〇ｒ〇）、REQUEST I/F、利用方法、データ仕様」を参照ください。
    if int_sResultCode ==  0 :    # ログアウトエラーでない場合
        bool_logout = True
    else :  # ログアウトに問題があった場合
        bool_logout = False

    return bool_logout

#--- 以上 共通コード -------------------------------------------------





# 資料
# 'sCLMID':'CLMMfdsGetMasterData' の利用方法
# API専用ページ
# ５．マニュアル 
# １．共通説明
# （３）ブラウザからの利用方法
# 「ｅ支店・ＡＰＩ、ブラウザからの利用方法」
# 
# 「マスタ・時価」シート・・・・マスタ情報問合取得、 時価情報問合取得
# ２－２．各Ｉ／Ｆ説明																				
# （１）マスタ情報問合取得																			
# 【要求】																				
##No	項目			設定値													
##1	sCLMID			CLMMfdsGetMasterData													
##2	sTargetCLMID		取得したいマスタデータ識別子をカンマで区切りで羅列、未指定「””」時は全マスタデータ。													
#        マスタデータ識別子：			※１								
#        CLMIssueMstKabu    	銘柄マスタ_株					
#        CLMIssueSizyouMstKabu	銘柄市場マスタ_株					
#        CLMIssueMstSak	    	銘柄マスタ_先物					
#        CLMIssueMstOp	    	銘柄マスタ_ＯＰ					
#        CLMIssueMstOther   	日経平均等指数、為替、その他上記外の銘柄コードと名称					
#        CLMOrderErrReason  	取引所エラー理由コード					※３
#        CLMDateZyouhou	    	日付情報					
##3	sTargetColumn	    各マスタデータで取得したい項目名をカンマ区切りで羅列													
#       例：													
#        sIssueCode	銘柄コード					
#        sIssueName	銘柄名称					
#        sErrReasonCode	取引所エラー理由
#        sErrReasonText	取引所エラーコード
##※１、（※２を除く）マスタデータ項目仕様等については別紙「立花証券・ｅ支店・ＡＰＩ、REQUEST I/F、マスタデータ利用方法」参照。																				
##※２、マスタデータ※１には無い株価ボード、ｅ支店・ＡＰＩ独自で取り扱う時価情報配信対象の銘柄コード、銘柄名称（それ以外の項目は無い）。																				
#
# マスターデータの内容の解説は、マニュアル「立花証券・ｅ支店・ＡＰＩ、REQUEST I/F、マスタデータ利用方法」参照。


# 機能: 銘柄マスタ_株（CLMIssueMstKabu）用 sTargetColumn作成 
# 引数: 無し
# 返値: 取得フィールド名 string型
def func_make_column_CLMIssueMstKabu():
    str_column = 'sIssueCode'
    str_column = str_column + ',' + 'sIssueName'
    str_column = str_column + ',' + 'sIssueNameRyaku'
    str_column = str_column + ',' + 'sIssueNameKana'
    str_column = str_column + ',' + 'sIssueNameEizi'
    str_column = str_column + ',' + 'sTokuteiF'
    str_column = str_column + ',' + 'sHikazeiC'
    str_column = str_column + ',' + 'sZyouzyouHakkouKabusu'
    str_column = str_column + ',' + 'sKenriotiFlag'
    str_column = str_column + ',' + 'sKenritukiSaisyuDay'
    str_column = str_column + ',' + 'sZyouzyouNyusatuC'
    str_column = str_column + ',' + 'sNyusatuKaizyoDay'
    str_column = str_column + ',' + 'sNyusatuDay'
    str_column = str_column + ',' + 'sBaibaiTani'
    str_column = str_column + ',' + 'sBaibaiTaniYoku'
    str_column = str_column + ',' + 'sBaibaiTeisiC'
    str_column = str_column + ',' + 'sHakkouKaisiDay'
    str_column = str_column + ',' + 'sHakkouSaisyuDay'
    str_column = str_column + ',' + 'sKessanC'
    str_column = str_column + ',' + 'sKessanDay'
    str_column = str_column + ',' + 'sZyouzyouOutouDay'
    str_column = str_column + ',' + 'sNiruiKizituC'
    str_column = str_column + ',' + 'sOogutiKabusu'
    str_column = str_column + ',' + 'sOogutiKingaku'
    str_column = str_column + ',' + 'sBadenpyouOutputYNC'
    str_column = str_column + ',' + 'sHosyoukinDaiyouKakeme'
    str_column = str_column + ',' + 'sDaiyouHyoukaTanka'
    str_column = str_column + ',' + 'sKikoSankaC'
    str_column = str_column + ',' + 'sKarikessaiC'
    str_column = str_column + ',' + 'sYusenSizyou'              # 優先市場
    str_column = str_column + ',' + 'sMukigenC'
    str_column = str_column + ',' + 'sGyousyuCode'
    str_column = str_column + ',' + 'sGyousyuName'
    str_column = str_column + ',' + 'sSorC'
    str_column = str_column + ',' + 'sCreateDate'
    str_column = str_column + ',' + 'sUpdateDate'
    str_column = str_column + ',' + 'sUpdateNumber'
    return str_column


# 機能: 銘柄マスタ_株（CLMIssueMstKabu）用 列名を漢字に変換 
# 引数: 列名
# 返値: 漢字名 string型
def func_column_kanji_CLMIssueMstKabu(str_column_name):
    if str_column_name == "sIssueCode" : str_name_kanji = "銘柄コード"
    elif str_column_name == "sIssueName" : str_name_kanji = "銘柄名"
    elif str_column_name == "sIssueNameRyaku" : str_name_kanji = "銘柄名略称"
    elif str_column_name == "sIssueNameKana" : str_name_kanji = "銘柄名（カナ）"
    elif str_column_name == "sIssueNameEizi" : str_name_kanji = "銘柄名（英語表記）"
    elif str_column_name == "sTokuteiF" : str_name_kanji = "特定口座対象Ｃ"
    elif str_column_name == "sHikazeiC" : str_name_kanji = "非課税口座受付可否"
    elif str_column_name == "sZyouzyouHakkouKabusu" : str_name_kanji = "上場発行株数"
    elif str_column_name == "sKenriotiFlag" : str_name_kanji = "権利落ちフラグ"
    elif str_column_name == "sKenritukiSaisyuDay" : str_name_kanji = "権利付最終日"
    elif str_column_name == "sZyouzyouNyusatuC" : str_name_kanji = "上場・入札Ｃ"
    elif str_column_name == "sNyusatuKaizyoDay" : str_name_kanji = "入札解除日"
    elif str_column_name == "sNyusatuDay" : str_name_kanji = "入札日"
    elif str_column_name == "sBaibaiTani" : str_name_kanji = "売買単位"
    elif str_column_name == "sBaibaiTaniYoku" : str_name_kanji = "売買単位(翌営業日)"
    elif str_column_name == "sBaibaiTeisiC" : str_name_kanji = "売買停止Ｃ"
    elif str_column_name == "sHakkouKaisiDay" : str_name_kanji = "発行開始日"
    elif str_column_name == "sHakkouSaisyuDay" : str_name_kanji = "発行最終日"
    elif str_column_name == "sKessanC" : str_name_kanji = "決算Ｃ"
    elif str_column_name == "sKessanDay" : str_name_kanji = "決算日"
    elif str_column_name == "sZyouzyouOutouDay" : str_name_kanji = "上場応答日"
    elif str_column_name == "sNiruiKizituC" : str_name_kanji = "二類期日Ｃ"
    elif str_column_name == "sOogutiKabusu" : str_name_kanji = "大口株数"
    elif str_column_name == "sOogutiKingaku" : str_name_kanji = "大口金額"
    elif str_column_name == "sBadenpyouOutputYNC" : str_name_kanji = "場伝票出力有無Ｃ"
    elif str_column_name == "sHosyoukinDaiyouKakeme" : str_name_kanji = "保証金代用掛目"
    elif str_column_name == "sDaiyouHyoukaTanka" : str_name_kanji = "代用証券評価単価"
    elif str_column_name == "sKikoSankaC" : str_name_kanji = "機構参加Ｃ"
    elif str_column_name == "sKarikessaiC" : str_name_kanji = "仮決済Ｃ"
    elif str_column_name == "sYusenSizyou" : str_name_kanji = "優先市場"
    elif str_column_name == "sMukigenC" : str_name_kanji = "無期限対象Ｃ"
    elif str_column_name == "sGyousyuCode" : str_name_kanji = "業種コード"
    elif str_column_name == "sGyousyuName" : str_name_kanji = "業種コード名"
    elif str_column_name == "sSorC" : str_name_kanji = "ＳＯＲ対象銘柄Ｃ"
    elif str_column_name == "sCreateDate" : str_name_kanji = "新規作成日時"
    elif str_column_name == "sUpdateDate" : str_name_kanji = "最終更新日時"
    elif str_column_name == "sUpdateNumber" : str_name_kanji = "最終更新通番"
    else :
        str_name_kanji = str_column_name
    return str_name_kanji


def func_make_column_CLMIssueSizyouMstKabu():
    str_column = 'sIssueCode'
    str_column = str_column + ',' + 'sZyouzyouSizyou'
    str_column = str_column + ',' + 'sSystemC'
    str_column = str_column + ',' + 'sNehabaMin'
    str_column = str_column + ',' + 'sNehabaMax'
    str_column = str_column + ',' + 'sIssueKubunC'
    str_column = str_column + ',' + 'sNehabaSizyouC'
    str_column = str_column + ',' + 'sSinyouC'
    str_column = str_column + ',' + 'sSinkiZyouzyouDay'
    str_column = str_column + ',' + 'sNehabaKigenDay'
    str_column = str_column + ',' + 'sNehabaKiseiC'
    str_column = str_column + ',' + 'sNehabaKiseiTi'
    str_column = str_column + ',' + 'sNehabaCheckKahiC'
    str_column = str_column + ',' + 'sIssueBubetuC'
    str_column = str_column + ',' + 'sZenzituOwarine'
    str_column = str_column + ',' + 'sNehabaSansyutuSizyouC'
    str_column = str_column + ',' + 'sIssueKisei1C'
    str_column = str_column + ',' + 'sIssueKisei2C'
    str_column = str_column + ',' + 'sZyouzyouKubun'
    str_column = str_column + ',' + 'sZyouzyouHaisiDay'
    str_column = str_column + ',' + 'sSizyoubetuBaibaiTani'
    str_column = str_column + ',' + 'sSizyoubetuBaibaiTaniYoku'
    str_column = str_column + ',' + 'sYobineTaniNumber'
    str_column = str_column + ',' + 'sYobineTaniNumberYoku'
    str_column = str_column + ',' + 'sZyouhouSource'
    str_column = str_column + ',' + 'sZyouhouCode'
    str_column = str_column + ',' + 'sKouboPrice'
    str_column = str_column + ',' + 'sCreateDate'
    str_column = str_column + ',' + 'sUpdateDate'
    str_column = str_column + ',' + 'sUpdateNumber'
    return str_column


# 機能: 銘柄市場マスタ_株（CLMIssueSizyouMstKabu）用 列名を漢字に変換 
# 引数: 列名
# 返値: 漢字名 string型
def func_column_kanji_CLMIssueSizyouMstKabu(str_column_name):
    if str_column_name == "sIssueCode" : str_name_kanji = "銘柄コード"
    elif str_column_name == "sZyouzyouSizyou" : str_name_kanji = "上場市場"
    elif str_column_name == "sSystemC" : str_name_kanji = "システムＣ"
    elif str_column_name == "sNehabaMin" : str_name_kanji = "値幅下限"
    elif str_column_name == "sNehabaMax" : str_name_kanji = "値幅上限"
    elif str_column_name == "sIssueKubunC" : str_name_kanji = "銘柄区分Ｃ"
    elif str_column_name == "sNehabaSizyouC" : str_name_kanji = "値幅市場Ｃ"
    elif str_column_name == "sSinyouC" : str_name_kanji = "信用Ｃ"
    elif str_column_name == "sSinkiZyouzyouDay" : str_name_kanji = "新規上場日"
    elif str_column_name == "sNehabaKigenDay" : str_name_kanji = "値幅期限日"
    elif str_column_name == "sNehabaKiseiC" : str_name_kanji = "値幅規制Ｃ"
    elif str_column_name == "sNehabaKiseiTi" : str_name_kanji = "値幅規制値"
    elif str_column_name == "sNehabaCheckKahiC" : str_name_kanji = "値幅チェック可否Ｃ"
    elif str_column_name == "sIssueBubetuC" : str_name_kanji = "銘柄部別Ｃ"
    elif str_column_name == "sZenzituOwarine" : str_name_kanji = "前日終値"
    elif str_column_name == "sNehabaSansyutuSizyouC" : str_name_kanji = "値幅算出市場Ｃ"
    elif str_column_name == "sIssueKisei1C" : str_name_kanji = "銘柄規制１Ｃ"
    elif str_column_name == "sIssueKisei2C" : str_name_kanji = "銘柄規制２Ｃ"
    elif str_column_name == "sZyouzyouKubun" : str_name_kanji = "上場区分"
    elif str_column_name == "sZyouzyouHaisiDay" : str_name_kanji = "上場廃止日"
    elif str_column_name == "sSizyoubetuBaibaiTani" : str_name_kanji = "市場別売買単位"
    elif str_column_name == "sSizyoubetuBaibaiTaniYoku" : str_name_kanji = "市場別売買単位(翌営業日)"
    elif str_column_name == "sYobineTaniNumber" : str_name_kanji = "呼値の単位番号"
    elif str_column_name == "sYobineTaniNumberYoku" : str_name_kanji = "呼値の単位番号(翌営業日)"
    elif str_column_name == "sZyouhouSource" : str_name_kanji = "情報系ソース"
    elif str_column_name == "sZyouhouCode" : str_name_kanji = "情報系コード"
    elif str_column_name == "sKouboPrice" : str_name_kanji = "公募価格"
    elif str_column_name == "sCreateDate" : str_name_kanji = "新規作成日時"
    elif str_column_name == "sUpdateDate" : str_name_kanji = "最終更新日時"
    elif str_column_name == "sUpdateNumber" : str_name_kanji = "最終更新通番"
    else :
        str_name_kanji = str_column_name
    return str_name_kanji



def func_make_column_CLMIssueMstSak():
    str_column = 'sIssueCode'
    str_column = str_column + ',' + 'sIssueName'
    str_column = str_column + ',' + 'sIssueNameEizi'
    str_column = str_column + ',' + 'sSakOpSyouhin'
    str_column = str_column + ',' + 'sGensisanKubun'
    str_column = str_column + ',' + 'sGensisanCode'
    str_column = str_column + ',' + 'sGengetu'
    str_column = str_column + ',' + 'sZyouzyouSizyou'
    str_column = str_column + ',' + 'sTorihikiStartDay'
    str_column = str_column + ',' + 'sLastBaibaiDay'
    str_column = str_column + ',' + 'sTaniSuryou'
    str_column = str_column + ',' + 'sYobineTaniNumber'
    str_column = str_column + ',' + 'sZyouhouSource'
    str_column = str_column + ',' + 'sZyouhouCode'
    str_column = str_column + ',' + 'sNehabaMin'
    str_column = str_column + ',' + 'sNehabaMax'
    str_column = str_column + ',' + 'sIssueKisei1C'
    str_column = str_column + ',' + 'sBaibaiTeisiC'
    str_column = str_column + ',' + 'sZenzituOwarine'
    str_column = str_column + ',' + 'sBaDenpyouOutputUmuC'
    str_column = str_column + ',' + 'sCreateDate'
    str_column = str_column + ',' + 'sUpdateDate'
    str_column = str_column + ',' + 'sUpdateNumber'
    return str_column


# 機能: 先物（CLMIssueMstSak）用 列名を漢字に変換 
# 引数: 列名
# 返値: 漢字名 string型
def func_column_kanji_CLMIssueMstSak(str_column_name):
    if str_column_name == "sIssueCode" : str_name_kanji = "銘柄コード"
    elif str_column_name == "sIssueName" : str_name_kanji = "銘柄名"
    elif str_column_name == "sIssueNameEizi" : str_name_kanji = "銘柄名（英語表記）"
    elif str_column_name == "sSakOpSyouhin" : str_name_kanji = "先物OP商品"
    elif str_column_name == "sGensisanKubun" : str_name_kanji = "原資産区分"
    elif str_column_name == "sGensisanCode" : str_name_kanji = "原資産コード"
    elif str_column_name == "sGengetu" : str_name_kanji = "限月"
    elif str_column_name == "sZyouzyouSizyou" : str_name_kanji = "上場市場"
    elif str_column_name == "sTorihikiStartDay" : str_name_kanji = "取引開始日"
    elif str_column_name == "sLastBaibaiDay" : str_name_kanji = "最終売買日"
    elif str_column_name == "sTaniSuryou" : str_name_kanji = "単位数量"
    elif str_column_name == "sYobineTaniNumber" : str_name_kanji = "呼値の単位番号"
    elif str_column_name == "sZyouhouSource" : str_name_kanji = "情報系ソース"
    elif str_column_name == "sZyouhouCode" : str_name_kanji = "情報系コード"
    elif str_column_name == "sNehabaMin" : str_name_kanji = "値幅下限"
    elif str_column_name == "sNehabaMax" : str_name_kanji = "値幅上限"
    elif str_column_name == "sIssueKisei1C" : str_name_kanji = "銘柄規制１Ｃ"
    elif str_column_name == "sBaibaiTeisiC" : str_name_kanji = "売買停止Ｃ"
    elif str_column_name == "sZenzituOwarine" : str_name_kanji = "前日終値"
    elif str_column_name == "sBaDenpyouOutputUmuC" : str_name_kanji = "場伝票出力有無Ｃ"
    elif str_column_name == "sCreateDate" : str_name_kanji = "新規作成日時"
    elif str_column_name == "sUpdateDate" : str_name_kanji = "最終更新日時"
    elif str_column_name == "sUpdateNumber" : str_name_kanji = "最終更新通番"
    else :
        str_name_kanji = str_column_name
    return str_name_kanji




def func_make_column_CLMIssueMstOp():
    str_column = 'sIssueCode'                       # 銘柄コード
    str_column = str_column + ',' + 'sIssueName'    # 銘柄名
    str_column = str_column + ',' + 'sIssueNameEizi'
    str_column = str_column + ',' + 'sSakOpSyouhin'
    str_column = str_column + ',' + 'sGensisanKubun'    # 原資産区分
    str_column = str_column + ',' + 'sGensisanCode'     # 原資産コード
    str_column = str_column + ',' + 'sGengetu'          # 限月
    str_column = str_column + ',' + 'sZyouzyouSizyou'   # 上場市場
    str_column = str_column + ',' + 'sKousiPrice'       # 行使価格
    str_column = str_column + ',' + 'sPutCall'          # プット・コール
    str_column = str_column + ',' + 'sTorihikiStartDay' # 取引開始日
    str_column = str_column + ',' + 'sLastBaibaiDay'    # 直近売買日
    str_column = str_column + ',' + 'sKenrikousiLastDay'    # 直近権利行使日
    str_column = str_column + ',' + 'sTaniSuryou'       # 単位数量
    str_column = str_column + ',' + 'sYobineTaniNumber' # 呼値単位数
    str_column = str_column + ',' + 'sZyouhouSource'    # 情報ソース
    str_column = str_column + ',' + 'sZyouhouCode'      # 情報コード
    str_column = str_column + ',' + 'sNehabaMin'        # 値幅_最小
    str_column = str_column + ',' + 'sNehabaMax'        # 値幅_最大
    str_column = str_column + ',' + 'sIssueKisei1C'
    str_column = str_column + ',' + 'sZenzituOwarine'   # 前日終値
    str_column = str_column + ',' + 'sZenzituRironPrice'    # 前日理論価格
    str_column = str_column + ',' + 'sBaDenpyouOutputUmuC'  # 場伝票出力有無
    str_column = str_column + ',' + 'sCreateDate'       # 作成日
    str_column = str_column + ',' + 'sUpdateDate'       # 更新日
    str_column = str_column + ',' + 'sUpdateNumber'     # 更新番号
    str_column = str_column + ',' + 'sATMFlag'
    return str_column

# 機能: OP（CLMIssueMstOp）用 列名を漢字に変換 
# 引数: 列名
# 返値: 漢字名 string型
def func_column_kanji_CLMIssueMstOp(str_column_name):
    if str_column_name == "sIssueCode" : str_name_kanji = "銘柄コード"
    elif str_column_name == "sIssueName" : str_name_kanji = "銘柄名"
    elif str_column_name == "sIssueNameEizi" : str_name_kanji = "銘柄名（英語表記）"
    elif str_column_name == "sSakOpSyouhin" : str_name_kanji = "先物OP商品"
    elif str_column_name == "sGensisanKubun" : str_name_kanji = "原資産区分"
    elif str_column_name == "sGensisanCode" : str_name_kanji = "原資産コード"
    elif str_column_name == "sGengetu" : str_name_kanji = "限月"
    elif str_column_name == "sZyouzyouSizyou" : str_name_kanji = "上場市場"
    elif str_column_name == "sKousiPrice" : str_name_kanji = "行使価格"
    elif str_column_name == "sPutCall" : str_name_kanji = "プット・コール"
    elif str_column_name == "sTorihikiStartDay" : str_name_kanji = "取引開始日"
    elif str_column_name == "sLastBaibaiDay" : str_name_kanji = "最終売買日"
    elif str_column_name == "sKenrikousiLastDay" : str_name_kanji = "権利行使最終日"
    elif str_column_name == "sTaniSuryou" : str_name_kanji = "単位数量"
    elif str_column_name == "sYobineTaniNumber" : str_name_kanji = "呼値の単位番号"
    elif str_column_name == "sZyouhouSource" : str_name_kanji = "情報系ソース"
    elif str_column_name == "sZyouhouCode" : str_name_kanji = "情報系コード"
    elif str_column_name == "sNehabaMin" : str_name_kanji = "値幅下限"
    elif str_column_name == "sNehabaMax" : str_name_kanji = "値幅上限"
    elif str_column_name == "sIssueKisei1C" : str_name_kanji = "銘柄規制１Ｃ"
    elif str_column_name == "sZenzituOwarine" : str_name_kanji = "前日終値"
    elif str_column_name == "sZenzituRironPrice" : str_name_kanji = "前日理論価格"
    elif str_column_name == "sBaDenpyouOutputUmuC" : str_name_kanji = "場伝票出力有無Ｃ"
    elif str_column_name == "sCreateDate" : str_name_kanji = "新規作成日時"
    elif str_column_name == "sUpdateDate" : str_name_kanji = "最終更新日時"
    elif str_column_name == "sUpdateNumber" : str_name_kanji = "最終更新通番"
    elif str_column_name == "sATMFlag" : str_name_kanji = "アット・ザ・マネーF"
    else :
        str_name_kanji = str_column_name
    return str_name_kanji




# 指数・為替
def func_make_column_CLMIssueMstOther():
    str_column = 'sIssueCode'
    str_column = str_column + ',' + 'sIssueName'
    return str_column


# 機能: 指数・為替（CLMIssueMstOther）用 列名を漢字に変換 
# 引数: 列名
# 返値: 漢字名 string型
def func_column_kanji_CLMIssueMstOther(str_column_name):
    if str_column_name == "sIssueCode" : str_name_kanji = "銘柄コード"
    elif str_column_name == "sIssueName" : str_name_kanji = "銘柄名"
    else :
        str_name_kanji = str_column_name
    return str_name_kanji




def func_make_column_CLMDaiyouKakeme():
    str_column = 'sSystemKouzaKubun'
    str_column = str_column + ',' + 'sIssueCode'
    str_column = str_column + ',' + 'sTekiyouDay'
    str_column = str_column + ',' + 'sHosyokinDaiyoKakeme'
    str_column = str_column + ',' + 'sDeleteDay'
    str_column = str_column + ',' + 'sCreateDate'
    str_column = str_column + ',' + 'sUpdateNumber'
    str_column = str_column + ',' + 'sUpdateDate'
    return str_column

# 機能: 代用掛目（CLMDaiyouKakeme）用 列名を漢字に変換 
# 引数: 列名
# 返値: 漢字名 string型
def func_column_kanji_CLMDaiyouKakeme(str_column_name):
    if str_column_name == "sSystemKouzaKubun" : str_name_kanji = "システム口座区分"
    elif str_column_name == "sIssueCode" : str_name_kanji = "銘柄コード"
    elif str_column_name == "sTekiyouDay" : str_name_kanji = "適用日"
    elif str_column_name == "sHosyokinDaiyoKakeme" : str_name_kanji = "保証金代用掛目"
    elif str_column_name == "sDeleteDay" : str_name_kanji = "削除日"
    elif str_column_name == "sCreateDate" : str_name_kanji = "作成日"
    elif str_column_name == "sUpdateNumber" : str_name_kanji = "更新番号"
    elif str_column_name == "sUpdateDate" : str_name_kanji = "更新日"
    else :
        str_name_kanji = str_column_name
    return str_name_kanji




def func_make_column_CLMHosyoukinMst():
    str_column = 'sSystemKouzaKubun'
    str_column = str_column + ',' + 'sIssueCode'
    str_column = str_column + ',' + 'sZyouzyouSizyou'
    str_column = str_column + ',' + 'sHenkouDay'
    str_column = str_column + ',' + 'sDaiyoHosyokinRitu'
    str_column = str_column + ',' + 'sGenkinHosyokinRitu'
    str_column = str_column + ',' + 'sCreateDate'
    str_column = str_column + ',' + 'sUpdateNumber'
    str_column = str_column + ',' + 'sUpdateDate'
    return str_column

# 機能: 保証金（CLMHosyoukinMst）用 列名を漢字に変換 
# 引数: 列名
# 返値: 漢字名 string型
def func_column_kanji_CLMHosyoukinMst(str_column_name):
    if str_column_name == "sSystemKouzaKubun" : str_name_kanji = "システム口座区分"
    elif str_column_name == "sIssueCode" : str_name_kanji = "銘柄コード"
    elif str_column_name == "sZyouzyouSizyou" : str_name_kanji = "上場市場"
    elif str_column_name == "sHenkouDay" : str_name_kanji = "変更日"
    elif str_column_name == "sDaiyoHosyokinRitu" : str_name_kanji = "代用保証金率"
    elif str_column_name == "sGenkinHosyokinRitu" : str_name_kanji = "現金保証金率"
    elif str_column_name == "sCreateDate" : str_name_kanji = "作成日"
    elif str_column_name == "sUpdateNumber" : str_name_kanji = "更新番号"
    elif str_column_name == "sUpdateDate" : str_name_kanji = "更新日"
    else :
        str_name_kanji = str_column_name
    return str_name_kanji



def func_make_column_CLMDateZyouhou():
    str_column = 'sDayKey'
    str_column = str_column + ',' + 'sMaeEigyouDay_1'
    str_column = str_column + ',' + 'sMaeEigyouDay_2'
    str_column = str_column + ',' + 'sMaeEigyouDay_3'
    str_column = str_column + ',' + 'sTheDay'
    str_column = str_column + ',' + 'sYokuEigyouDay_1'
    str_column = str_column + ',' + 'sYokuEigyouDay_2'
    str_column = str_column + ',' + 'sYokuEigyouDay_3'
    str_column = str_column + ',' + 'sYokuEigyouDay_4'
    str_column = str_column + ',' + 'sYokuEigyouDay_5'
    str_column = str_column + ',' + 'sYokuEigyouDay_6'
    str_column = str_column + ',' + 'sYokuEigyouDay_7'
    str_column = str_column + ',' + 'sYokuEigyouDay_8'
    str_column = str_column + ',' + 'sYokuEigyouDay_9'
    str_column = str_column + ',' + 'sYokuEigyouDay_10'
    str_column = str_column + ',' + 'sKabuUkewatasiDay'
    str_column = str_column + ',' + 'sKabuKariUkewatasiDay'
    str_column = str_column + ',' + 'sBondUkewatasiDay'
    return str_column

# 機能: 日付情報（CLMDateZyouhou）用 列名を漢字に変換 
# 引数: 列名
# 返値: 漢字名 string型
def func_column_kanji_CLMDateZyouhou(str_column_name):
    if str_column_name == "sDayKey" : str_name_kanji = "日付ＫＥＹ"
    elif str_column_name == "sMaeEigyouDay_1" : str_name_kanji = "３営業日前"
    elif str_column_name == "sMaeEigyouDay_2" : str_name_kanji = "２営業日前"
    elif str_column_name == "sMaeEigyouDay_3" : str_name_kanji = "１営業日前"
    elif str_column_name == "sTheDay" : str_name_kanji = "当日日付"
    elif str_column_name == "sYokuEigyouDay_1" : str_name_kanji = "翌１営業日"
    elif str_column_name == "sYokuEigyouDay_2" : str_name_kanji = "翌２営業日"
    elif str_column_name == "sYokuEigyouDay_3" : str_name_kanji = "翌３営業日"
    elif str_column_name == "sYokuEigyouDay_4" : str_name_kanji = "翌４営業日"
    elif str_column_name == "sYokuEigyouDay_5" : str_name_kanji = "翌５営業日"
    elif str_column_name == "sYokuEigyouDay_6" : str_name_kanji = "翌６営業日"
    elif str_column_name == "sYokuEigyouDay_7" : str_name_kanji = "翌７営業日"
    elif str_column_name == "sYokuEigyouDay_8" : str_name_kanji = "翌８営業日"
    elif str_column_name == "sYokuEigyouDay_9" : str_name_kanji = "翌９営業日"
    elif str_column_name == "sYokuEigyouDay_10" : str_name_kanji = "翌１０営業日"
    elif str_column_name == "sKabuUkewatasiDay" : str_name_kanji = "株式受渡日"
    elif str_column_name == "sKabuKariUkewatasiDay" : str_name_kanji = "株式仮決受渡日"
    elif str_column_name == "sBondUkewatasiDay" : str_name_kanji = "債券受渡日"
    else :
        str_name_kanji = str_column_name
    return str_name_kanji



def func_make_column_CLMOrderErrReason():
    str_column = 'sErrReasonCode'
    str_column = str_column + ',' + 'sErrReasonText'
    return str_column

# 機能: エラー理由（CLMOrderErrReason）用 列名を漢字に変換 
# 引数: 列名
# 返値: 漢字名 string型
def func_column_kanji_CLMOrderErrReason(str_column_name):
    if str_column_name == "sErrReasonCode" : str_name_kanji = "エラーコード"
    elif str_column_name == "sErrReasonText" : str_name_kanji = "エラーメッセージ"
    else :
        str_name_kanji = str_column_name
    return str_name_kanji



def func_make_column_CLMSystemStatus():
    str_column = 'sSystemStatusKey'
    str_column = str_column + ',' + 'sLoginKyokaKubun'
    str_column = str_column + ',' + 'sSystemStatus'
    str_column = str_column + ',' + 'sCreateTime'
    str_column = str_column + ',' + 'sUpdateTime'
    str_column = str_column + ',' + 'sUpdateNumber'
    str_column = str_column + ',' + 'sDeleteFlag'
    str_column = str_column + ',' + 'sDeleteTime'
    return str_column

# 機能: システムステイタス（CLMSystemStatus）用 列名を漢字に変換 
# 引数: 列名
# 返値: 漢字名 string型
def func_column_kanji_CLMSystemStatus(str_column_name):
    if str_column_name == "sSystemStatusKey" : str_name_kanji = "システムステイタスキー"
    elif str_column_name == "sLoginKyokaKubun" : str_name_kanji = "ログイン許可区分"
    elif str_column_name == "sSystemStatus" : str_name_kanji = "システムステイタスキー"
    elif str_column_name == "sCreateTime" : str_name_kanji = "作成日時"
    elif str_column_name == "sUpdateTime" : str_name_kanji = "更新日時"
    elif str_column_name == "sUpdateNumber" : str_name_kanji = "更新番号"
    elif str_column_name == "sDeleteFlag" : str_name_kanji = "削除フラグ"
    elif str_column_name == "sDeleteTime" : str_name_kanji = "削除日時"
    else :
        str_name_kanji = str_column_name
    return str_name_kanji



def func_make_column_CLMYobine():
    str_column = 'sYobineTaniNumber'
    str_column = str_column + ',' + 'sTekiyouDay'
    str_column = str_column + ',' + 'sKizunPrice_1'
    str_column = str_column + ',' + 'sKizunPrice_2'
    str_column = str_column + ',' + 'sKizunPrice_3'
    str_column = str_column + ',' + 'sKizunPrice_4'
    str_column = str_column + ',' + 'sKizunPrice_5'
    str_column = str_column + ',' + 'sKizunPrice_6'
    str_column = str_column + ',' + 'sKizunPrice_7'
    str_column = str_column + ',' + 'sKizunPrice_8'
    str_column = str_column + ',' + 'sKizunPrice_9'
    str_column = str_column + ',' + 'sKizunPrice_10'
    str_column = str_column + ',' + 'sKizunPrice_11'
    str_column = str_column + ',' + 'sKizunPrice_12'
    str_column = str_column + ',' + 'sKizunPrice_13'
    str_column = str_column + ',' + 'sKizunPrice_14'
    str_column = str_column + ',' + 'sKizunPrice_15'
    str_column = str_column + ',' + 'sKizunPrice_16'
    str_column = str_column + ',' + 'sKizunPrice_17'
    str_column = str_column + ',' + 'sKizunPrice_18'
    str_column = str_column + ',' + 'sKizunPrice_19'
    str_column = str_column + ',' + 'sKizunPrice_20'
    str_column = str_column + ',' + 'sYobineTanka_1'
    str_column = str_column + ',' + 'sYobineTanka_2'
    str_column = str_column + ',' + 'sYobineTanka_3'
    str_column = str_column + ',' + 'sYobineTanka_4'
    str_column = str_column + ',' + 'sYobineTanka_5'
    str_column = str_column + ',' + 'sYobineTanka_6'
    str_column = str_column + ',' + 'sYobineTanka_7'
    str_column = str_column + ',' + 'sYobineTanka_8'
    str_column = str_column + ',' + 'sYobineTanka_9'
    str_column = str_column + ',' + 'sYobineTanka_10'
    str_column = str_column + ',' + 'sYobineTanka_11'
    str_column = str_column + ',' + 'sYobineTanka_12'
    str_column = str_column + ',' + 'sYobineTanka_13'
    str_column = str_column + ',' + 'sYobineTanka_14'
    str_column = str_column + ',' + 'sYobineTanka_15'
    str_column = str_column + ',' + 'sYobineTanka_16'
    str_column = str_column + ',' + 'sYobineTanka_17'
    str_column = str_column + ',' + 'sYobineTanka_18'
    str_column = str_column + ',' + 'sYobineTanka_19'
    str_column = str_column + ',' + 'sYobineTanka_20'
    str_column = str_column + ',' + 'sDecimal_1'
    str_column = str_column + ',' + 'sDecimal_2'
    str_column = str_column + ',' + 'sDecimal_3'
    str_column = str_column + ',' + 'sDecimal_4'
    str_column = str_column + ',' + 'sDecimal_5'
    str_column = str_column + ',' + 'sDecimal_6'
    str_column = str_column + ',' + 'sDecimal_7'
    str_column = str_column + ',' + 'sDecimal_8'
    str_column = str_column + ',' + 'sDecimal_9'
    str_column = str_column + ',' + 'sDecimal_10'
    str_column = str_column + ',' + 'sDecimal_11'
    str_column = str_column + ',' + 'sDecimal_12'
    str_column = str_column + ',' + 'sDecimal_13'
    str_column = str_column + ',' + 'sDecimal_14'
    str_column = str_column + ',' + 'sDecimal_15'
    str_column = str_column + ',' + 'sDecimal_16'
    str_column = str_column + ',' + 'sDecimal_17'
    str_column = str_column + ',' + 'sDecimal_18'
    str_column = str_column + ',' + 'sDecimal_19'
    str_column = str_column + ',' + 'sDecimal_20'
    str_column = str_column + ',' + 'sCreateDate'
    str_column = str_column + ',' + 'sUpdateDate'
    return str_column


# 機能: 呼値（CLMYobine）用 列名を漢字に変換 
# 引数: 列名
# 返値: 漢字名 string型
def func_column_kanji_CLMYobine(str_column_name):
    if str_column_name == "sYobineTaniNumber" : str_name_kanji = "呼値単位番号"
    elif str_column_name == "sTekiyouDay" : str_name_kanji = "適用日"
    elif str_column_name == "sKizunPrice_1" : str_name_kanji = "基準値段_1"
    elif str_column_name == "sKizunPrice_2" : str_name_kanji = "基準値段_2"
    elif str_column_name == "sKizunPrice_3" : str_name_kanji = "基準値段_3"
    elif str_column_name == "sKizunPrice_4" : str_name_kanji = "基準値段_4"
    elif str_column_name == "sKizunPrice_5" : str_name_kanji = "基準値段_5"
    elif str_column_name == "sKizunPrice_6" : str_name_kanji = "基準値段_6"
    elif str_column_name == "sKizunPrice_7" : str_name_kanji = "基準値段_7"
    elif str_column_name == "sKizunPrice_8" : str_name_kanji = "基準値段_8"
    elif str_column_name == "sKizunPrice_9" : str_name_kanji = "基準値段_9"
    elif str_column_name == "sKizunPrice_10" : str_name_kanji = "基準値段_10"
    elif str_column_name == "sKizunPrice_11" : str_name_kanji = "基準値段_11"
    elif str_column_name == "sKizunPrice_12" : str_name_kanji = "基準値段_12"
    elif str_column_name == "sKizunPrice_13" : str_name_kanji = "基準値段_13"
    elif str_column_name == "sKizunPrice_14" : str_name_kanji = "基準値段_14"
    elif str_column_name == "sKizunPrice_15" : str_name_kanji = "基準値段_15"
    elif str_column_name == "sKizunPrice_16" : str_name_kanji = "基準値段_16"
    elif str_column_name == "sKizunPrice_17" : str_name_kanji = "基準値段_17"
    elif str_column_name == "sKizunPrice_18" : str_name_kanji = "基準値段_18"
    elif str_column_name == "sKizunPrice_19" : str_name_kanji = "基準値段_19"
    elif str_column_name == "sKizunPrice_20" : str_name_kanji = "基準値段_20"
    elif str_column_name == "sYobineTanka_1" : str_name_kanji = "呼値単価_1"
    elif str_column_name == "sYobineTanka_2" : str_name_kanji = "呼値単価_2"
    elif str_column_name == "sYobineTanka_3" : str_name_kanji = "呼値単価_3"
    elif str_column_name == "sYobineTanka_4" : str_name_kanji = "呼値単価_4"
    elif str_column_name == "sYobineTanka_5" : str_name_kanji = "呼値単価_5"
    elif str_column_name == "sYobineTanka_6" : str_name_kanji = "呼値単価_6"
    elif str_column_name == "sYobineTanka_7" : str_name_kanji = "呼値単価_7"
    elif str_column_name == "sYobineTanka_8" : str_name_kanji = "呼値単価_8"
    elif str_column_name == "sYobineTanka_9" : str_name_kanji = "呼値単価_9"
    elif str_column_name == "sYobineTanka_10" : str_name_kanji = "呼値単価_10"
    elif str_column_name == "sYobineTanka_11" : str_name_kanji = "呼値単価_11"
    elif str_column_name == "sYobineTanka_12" : str_name_kanji = "呼値単価_12"
    elif str_column_name == "sYobineTanka_13" : str_name_kanji = "呼値単価_13"
    elif str_column_name == "sYobineTanka_14" : str_name_kanji = "呼値単価_14"
    elif str_column_name == "sYobineTanka_15" : str_name_kanji = "呼値単価_15"
    elif str_column_name == "sYobineTanka_16" : str_name_kanji = "呼値単価_16"
    elif str_column_name == "sYobineTanka_17" : str_name_kanji = "呼値単価_17"
    elif str_column_name == "sYobineTanka_18" : str_name_kanji = "呼値単価_18"
    elif str_column_name == "sYobineTanka_19" : str_name_kanji = "呼値単価_19"
    elif str_column_name == "sYobineTanka_20" : str_name_kanji = "呼値単価_20"
    elif str_column_name == "sDecimal_1" : str_name_kanji = "小数点以下桁数_1"
    elif str_column_name == "sDecimal_2" : str_name_kanji = "小数点以下桁数_2"
    elif str_column_name == "sDecimal_3" : str_name_kanji = "小数点以下桁数_3"
    elif str_column_name == "sDecimal_4" : str_name_kanji = "小数点以下桁数_4"
    elif str_column_name == "sDecimal_5" : str_name_kanji = "小数点以下桁数_5"
    elif str_column_name == "sDecimal_6" : str_name_kanji = "小数点以下桁数_6"
    elif str_column_name == "sDecimal_7" : str_name_kanji = "小数点以下桁数_7"
    elif str_column_name == "sDecimal_8" : str_name_kanji = "小数点以下桁数_8"
    elif str_column_name == "sDecimal_9" : str_name_kanji = "小数点以下桁数_9"
    elif str_column_name == "sDecimal_10" : str_name_kanji = "小数点以下桁数_10"
    elif str_column_name == "sDecimal_11" : str_name_kanji = "小数点以下桁数_11"
    elif str_column_name == "sDecimal_12" : str_name_kanji = "小数点以下桁数_12"
    elif str_column_name == "sDecimal_13" : str_name_kanji = "小数点以下桁数_13"
    elif str_column_name == "sDecimal_14" : str_name_kanji = "小数点以下桁数_14"
    elif str_column_name == "sDecimal_15" : str_name_kanji = "小数点以下桁数_15"
    elif str_column_name == "sDecimal_16" : str_name_kanji = "小数点以下桁数_16"
    elif str_column_name == "sDecimal_17" : str_name_kanji = "小数点以下桁数_17"
    elif str_column_name == "sDecimal_18" : str_name_kanji = "小数点以下桁数_18"
    elif str_column_name == "sDecimal_19" : str_name_kanji = "小数点以下桁数_19"
    elif str_column_name == "sDecimal_20" : str_name_kanji = "小数点以下桁数_20"
    elif str_column_name == "sCreateDate" : str_name_kanji = "作成日"
    elif str_column_name == "sUpdateDate" : str_name_kanji = "更新日"
    else :
        str_name_kanji = str_column_name
    return str_name_kanji








# 機能: 取得するマスターデータの種類により取得項目作成関数に分岐する。
# 引数1: マスターデータ種類
# 返値: 取得項目文字列
# 補足:  'CLMIssueMstKabu'         # 株式 銘柄マスタ
#       'CLMIssueSizyouMstKabu'   # 株式 銘柄市場マスタ
#       'CLMIssueMstSak'          # 先物
#       'CLMIssueMstOp'           # ＯＰ
#       'CLMIssueMstOther'        # 指数、為替、その他
#       'CLMOrderErrReason'       # 取引所エラー理由コード
#       'CLMDateZyouhou'          # 日付情報
#        呼び値は、個別ダウンロードでは指定不可
def func_make_sTargetColumn(str_sTargetCLMID):
    str_sTargetColumn = ''
    if str_sTargetCLMID == 'CLMIssueMstKabu' :
        str_sTargetColumn = func_make_column_CLMIssueMstKabu()
        
    elif str_sTargetCLMID == 'CLMIssueSizyouMstKabu' :
        str_sTargetColumn = func_make_column_CLMIssueSizyouMstKabu()
        
    elif str_sTargetCLMID == 'CLMIssueMstSak' :
        str_sTargetColumn = func_make_column_CLMIssueMstSak()
        
    elif str_sTargetCLMID == 'CLMIssueMstOp' :
        str_sTargetColumn = func_make_column_CLMIssueMstOp()
        
    elif str_sTargetCLMID == 'CLMIssueMstOther' :
        str_sTargetColumn = func_make_column_CLMIssueMstOther()
        
    elif str_sTargetCLMID == 'CLMDaiyouKakeme' :
        str_sTargetColumn = func_make_column_CLMDaiyouKakeme()
        
    elif str_sTargetCLMID == 'CLMHosyoukinMst' :
        str_sTargetColumn = func_make_column_CLMHosyoukinMst()
        
    elif str_sTargetCLMID == 'CLMDateZyouhou' :
        str_sTargetColumn = func_make_column_CLMDateZyouhou()
        
    elif str_sTargetCLMID == 'CLMOrderErrReason' :
        str_sTargetColumn = func_make_column_CLMOrderErrReason()
        
    elif str_sTargetCLMID == 'CLMSystemStatus' :
        str_sTargetColumn = func_make_column_CLMSystemStatus()
        
    elif str_sTargetCLMID == 'CLMYobine' :              # 呼び値は、個別ダウンロードでは指定不可。
        str_sTargetColumn = func_make_column_CLMYobine()
            
    return str_sTargetColumn


# 機能: 取得するマスターデータの種類により取得項目名の漢字名変換関数に分岐する。
# 引数1: マスターデータ種類
# 返値: 取得項目文字列
# 補足:  'CLMIssueMstKabu'         # 株式 銘柄マスタ
#       'CLMIssueSizyouMstKabu'   # 株式 銘柄市場マスタ
#       'CLMIssueMstSak'          # 先物
#       'CLMIssueMstOp'           # ＯＰ
#       'CLMIssueMstOther'        # 指数、為替、その他
#       'CLMOrderErrReason'       # 取引所エラー理由コード
#       'CLMDateZyouhou'          # 日付情報
#        呼び値は、個別ダウンロードでは指定不可
def func_column_kanji(str_sTargetCLMID, str_clumn_name):
    str_column_kanji = ''
    if str_sTargetCLMID == 'CLMIssueMstKabu' :
        str_column_kanji = func_column_kanji_CLMIssueMstKabu(str_clumn_name)
        
    elif str_sTargetCLMID == 'CLMIssueSizyouMstKabu' :
        str_column_kanji = func_column_kanji_CLMIssueSizyouMstKabu(str_clumn_name)
        
    elif str_sTargetCLMID == 'CLMIssueMstSak' :
        str_column_kanji = func_column_kanji_CLMIssueMstSak(str_clumn_name)
        
    elif str_sTargetCLMID == 'CLMIssueMstOp' :
        str_column_kanji = func_column_kanji_CLMIssueMstOp(str_clumn_name)
        
    elif str_sTargetCLMID == 'CLMIssueMstOther' :
        str_column_kanji = func_column_kanji_CLMIssueMstOther(str_clumn_name)
        
    elif str_sTargetCLMID == 'CLMDaiyouKakeme' :
        str_column_kanji = func_column_kanji_CLMDaiyouKakeme(str_clumn_name)
        
    elif str_sTargetCLMID == 'CLMHosyoukinMst' :
        str_column_kanji = func_column_kanji_CLMHosyoukinMst(str_clumn_name)
        
    elif str_sTargetCLMID == 'CLMDateZyouhou' :
        str_column_kanji = func_column_kanji_CLMDateZyouhou(str_clumn_name)
        
    elif str_sTargetCLMID == 'CLMOrderErrReason' :
        str_column_kanji = func_column_kanji_CLMOrderErrReason(str_clumn_name)
        
    elif str_sTargetCLMID == 'CLMSystemStatus' :
        str_column_kanji = func_column_kanji_CLMSystemStatus(str_clumn_name)
        
    elif str_sTargetCLMID == 'CLMYobine' :              # 呼び値は、個別ダウンロードでは指定不可。
        str_column_kanji = func_column_kanji_CLMYobine(str_clumn_name)
            
    return str_column_kanji




# 機能： 項目別マスターダウンロード
# 引数1：int_p_no
# 引数2：str_sTargetCLMID
# 引数3：str_sTargetColumn
# 引数4：class_cust_property
# 返値: 辞書型データ（APIからのjson形式返信データをshift-jisのstring型に変換し、更に辞書型に変換）
# 補足: 項目別のマスターデータ取得は、通常のAPI呼び出し。
#       マスターダウンロード専用（＝ストリーミング形式）の接続は使わない。
#        呼び値は、個別ダウンロードでは指定不可.
#
# 資料:
# 'sCLMID':'CLMMfdsGetMasterData' の利用方法
# API専用ページ
# ５．マニュアル 
# １．共通説明
# （３）ブラウザからの利用方法
# 「ｅ支店・ＡＰＩ、ブラウザからの利用方法」
# 
# 「マスタ・時価」シート・・・・マスタ情報問合取得、 時価情報問合取得
# ２－２．各Ｉ／Ｆ説明																				
# （１）マスタ情報問合取得																			
#
# マスターデータの解説は、マニュアル「立花証券・ｅ支店・ＡＰＩ、REQUEST I/F、マスタデータ利用方法」参照。
def func_get_master_kobetsu(int_p_no, str_sTargetCLMID, str_sTargetColumn, class_cust_property):
    # 送信項目の解説は、マニュアル、（2）インタフェース概要の「立花証券・ｅ支店・ＡＰＩ、インタフェース概要」
    # p7/10 sd 5.マスタダウンロード を参照してください。

    req_item = [class_req()]
    str_p_sd_date = func_p_sd_date(datetime.datetime.now())     # システム時刻を所定の書式で取得
    
    str_key = '"p_no"'
    str_value = func_check_json_dquat(str(int_p_no))
    #req_item.append(class_req())
    req_item[-1].add_data(str_key, str_value)

    str_key = '"p_sd_date"'
    str_value = str_p_sd_date
    req_item.append(class_req())
    req_item[-1].add_data(str_key, str_value)
    
    str_key = 'sCLMID'
    str_value = 'CLMMfdsGetMasterData'  # 。
    req_item.append(class_req())
    req_item[-1].add_data(str_key, str_value)


    str_key = 'sTargetCLMID'
    str_value = str_sTargetCLMID  # 。
    req_item.append(class_req())
    req_item[-1].add_data(str_key, str_value)

    str_key = 'sTargetColumn'
    str_value = str_sTargetColumn  # 。
    req_item.append(class_req())
    req_item[-1].add_data(str_key, str_value)

    
    # 返り値の表示形式指定
    str_key = '"sJsonOfmt"'
    str_value = class_cust_property.sJsonOfmt
    req_item.append(class_req())
    req_item[-1].add_data(str_key, str_value)

    # URL文字列の作成
    str_url = func_make_url_request(False, \
                                     class_cust_property.sUrlMaster, \
                                     req_item)

    # API問合せ
    json_return = func_api_req(str_url)
    # 項目別のマスターデータ取得は、通常のAPI呼び出し。
    # マスターダウンロード専用（＝ストリーミング形式）の呼び出しは使わない。

    return json_return



# 機能: 限月が、当月以後（限月<=当月）ならば、True、当月より前（限月<当月）ならばFalseを返す。
# 
def func_judge_past_gengetsu(list_data):
    bool_judge = True
    
    # システム時刻の取得
    dt_systime = datetime.datetime.now()
    # 当月のyyyymmを取得
    str_tougetsu = str(dt_systime.year) + ('00' + str(dt_systime.month))[-2:]

    if int(list_data.get('sGengetu')) >= int(str_tougetsu) :
        bool_judge = True
    else :
        bool_judge = False

    return bool_judge


# 機能: csv形式でファイルに書き込む
# 返値: 
# 引数1:
# 引数2:
# 備考: 1行目は、タイトル行
#     2行目以降は、データ行 
def func_write_master_kobetsu(str_sTargetCLMID, \
                              json_return, \
                              str_master_filename):
##                              str_sTargetColumn, \
    
    # 返り値からsTargetCLMID内のデータレコードのみ抜き出す
    list_return = json_return.get(str_sTargetCLMID)
    
    if not list_return == None:
        try :
                
            with open(str_master_filename, 'w') as fout:
                int_num_of_articles = len(list_return[0].keys())
                iter_keys = iter(list_return[0].keys())
                    
                # タイトル行
                str_text = ''
                str_kanji = ''
                for i in range(int_num_of_articles) :
                    work_key = next(iter_keys)
                    work_kanji = func_column_kanji(str_sTargetCLMID, work_key)
                    
##                    str_text = str_text + next(iter_keys) + ','
                    str_text = str_text + work_key + ','
                    str_kanji = str_kanji + work_kanji + ','
                str_text = str_text[:-1] + '\n'
                fout.write(str_text)        # タイトル行をファイルに書き込む
                
                str_kanji = str_kanji[:-1] + '\n'
                fout.write(str_kanji)        # タイトル行をファイルに書き込む
                
                for i in range(len(list_return)):
                    # デフォルトでTrueをセット。
                    # 条件に合わない場合（非上場銘柄、過去の限月）は、以降でFalseをセット。
                    bool_judge = True


                    # 株式
                    # 銘柄マスタ_株       優先市場が 非上場:9 を除外
                    if my_sTargetCLMID == 'CLMIssueMstKabu' :
                        if list_return[i].get('sYusenSizyou') == '9' :
                            bool_judge = False

                    # 銘柄市場マスタ_株     上場市場が 非上場:9 を除外
                    if my_sTargetCLMID == 'CLMIssueSizyouMstKabu' :
                        if list_return[i].get('sZyouzyouSizyou') == '9' :
                            bool_judge = False
                    
                    # 先物、OP     過去の限月を削除する
                    if my_sTargetCLMID == 'CLMIssueMstSak' \
                       or my_sTargetCLMID == 'CLMIssueMstOp' :
                        bool_judge = func_judge_past_gengetsu(list_return[i])

                    if bool_judge :
                        iter_values = iter(list_return[i].values())
                    
                        str_text = ''
                        for n in range(int_num_of_articles) :
                            str_text = str_text +  next(iter_values) + ','
                        str_text = str_text[:-1] + '\n'
                        fout.write(str_text)        # データを1行ファイルに書き込む
                
        except IOError as e:
            print('File can not write!!!')
            print(type(e))
    else :
        str_txt = str_sTargetCLMID + ' は、取得できません。'
        print('エラー：')
        print(str_txt)



    




    
# ======================================================================================================
# ==== プログラム始点 =================================================================================
# ======================================================================================================
# 必要な設定項目
# 接続先:  my_url 
# ユーザーID:   my_userid 
# パスワード:    my_passwd （ログイン時に使うパスワード）
# 第2パスワード: my_2pwd （発注時に使うパスワード）
# マスター項目: my_sTargetCLMID （コメントアウト'##'を外して指定。）
# 出力ファイル名: my_master_filename


# --- 利用時に変数を設定してください -------------------------------------------------------

# 接続先 設定 --------------
# デモ環境（新バージョンになった場合、適宜変更）
my_url = 'https://demo-kabuka.e-shiten.jp/e_api_v4r3/'

# 本番環境（新バージョンになった場合、適宜変更）
# ＊＊！！実際に市場に注文が出るので注意！！＊＊
# my_url = 'https://kabuka.e-shiten.jp/e_api_v4r3/'


# ＩＤパスワード設定 ---------
my_userid = 'MY_USERID' # 自分のuseridに書き換える
my_passwd = 'MY_PASSWD' # 自分のpasswordに書き換える
my_2pwd = 'MY_2PASSWD'  # 自分の第２passwordに書き換える


# コマンド用パラメーター -------------------    
#

# 取得するマスター項目の選択（コメント'##'を外して指定。選択は1つのみ。）
my_sTargetCLMID = 'CLMIssueMstKabu'         # 株式 銘柄マスタ
##my_sTargetCLMID = 'CLMIssueSizyouMstKabu'   # 株式 銘柄市場マスタ
##my_sTargetCLMID = 'CLMIssueMstSak'          # 先物
##my_sTargetCLMID = 'CLMIssueMstOp'           # ＯＰ
##my_sTargetCLMID = 'CLMIssueMstOther'        # 指数、為替、その他
##my_sTargetCLMID = 'CLMOrderErrReason'       # 取引所エラー理由コード
##my_sTargetCLMID = 'CLMDateZyouhou'          # 日付情報
# （呼値  呼び値は、個別ダウンロードでは指定不可。）

# 出力ファイル名の設定
my_master_filename = 'master_' + my_sTargetCLMID +'.csv'





# --- 以上設定項目 -------------------------------------------------------------------------


class_cust_property = class_def_cust_property()     # 口座属性クラス

# ID、パスワード、第２パスワードのURLエンコードをチェックして変換
my_userid = func_replace_urlecnode(my_userid)
my_passwd = func_replace_urlecnode(my_passwd)
class_cust_property.sSecondPassword = func_replace_urlecnode(my_2pwd)

# 返り値の表示形式指定
class_cust_property.sJsonOfmt = '5'
# "5"は "1"（1ビット目ＯＮ）と”4”（3ビット目ＯＮ）の指定となり
# ブラウザで見や易い形式」且つ「引数項目名称」で応答を返す値指定

print('-- login -----------------------------------------------------')
# 送信項目、戻り値の解説は、マニュアル「立花証券・ｅ支店・ＡＰＩ（ｖ〇）、REQUEST I/F、機能毎引数項目仕様」
# p2/46 No.1 引数名:CLMAuthLoginRequest を参照してください。
int_p_no = 1
# ログイン処理
bool_login = func_login(int_p_no, my_url, my_userid, my_passwd,  class_cust_property)


# ログインOKの場合
if bool_login :
    
    print()
    print('-- マスター 取得 -------------------------------------------------------------')

    # 取得項目名を作成
    my_sTargetColumn = func_make_sTargetColumn(my_sTargetCLMID)
    
    int_p_no = int_p_no + 1

    json_return = func_get_master_kobetsu(int_p_no, my_sTargetCLMID, my_sTargetColumn, class_cust_property)
    # マスターデータの解説は、マニュアル「立花証券・ｅ支店・ＡＰＩ、REQUEST I/F、マスタデータ利用方法」参照。
    # カレントディレクトリに「str_master_filename」で指定した名前でファイルを作成する。

    # csv形式でファイルへの書き出し
    func_write_master_kobetsu(my_sTargetCLMID, json_return, my_master_filename)
    
    
    print()
    print('-- logout -------------------------------------------------------------')
    # 送信項目の解説は、マニュアル「立花証券・ｅ支店・ＡＰＩ（ｖ〇）、REQUEST I/F、機能毎引数項目仕様」
    # p3/46 No.3 引数名:CLMAuthLogoutRequest を参照してください。
    int_p_no = int_p_no + 1
    bool_logout = func_logout(int_p_no, class_cust_property)
   
else :
    print('ログインに失敗しました')
