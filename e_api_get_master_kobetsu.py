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


# 指数・為替
def func_make_column_CLMIssueMstOther():
    str_column = 'sIssueCode'
    str_column = str_column + ',' + 'sIssueName'
    return str_column


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


def func_make_column_CLMOrderErrReason():
    str_column = 'sErrReasonCode'
    str_column = str_column + ',' + 'sErrReasonText'
    return str_column


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
        
    elif str_sTargetCLMID == 'CLMYobine' :
        str_sTargetColumn = func_make_column_CLMYobine()
            
    return str_sTargetColumn



# 機能： 項目別マスターダウンロード
# 引数1：int_p_no
# 引数2：str_sTargetCLMID
# 引数3：str_sTargetColumn
# 引数4：class_cust_property
# 返値: 辞書型データ（APIからのjson形式返信データをshift-jisのstring型に変換し、更に辞書型に変換）
# 補足: 項目別のマスターデータ取得は、通常のAPI呼び出し。
#       マスターダウンロード専用（＝ストリーミング形式）の接続は使わない。
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
        
    try :
            
        with open(str_master_filename, 'w') as fout:
            int_num_of_articles = len(list_return[0].keys())
            iter_keys = iter(list_return[0].keys())
                
            # タイトル行
            str_text = ''
            for i in range(int_num_of_articles) :
                str_text = str_text + next(iter_keys) + ','
            str_text = str_text[:-1] + '\n'
            fout.write(str_text)        # タイトル行をファイルに書き込む
                
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
                
                # 先物、OPで過去の限月を削除する
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
