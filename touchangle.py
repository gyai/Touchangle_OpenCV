#画像を読み込んで、OpenCV使って静電容量画像の指の輪郭を取得、
#長軸短軸の長さパラメータを取得して、縦横の比率をリストにぶち込む
#それぞれの比率から、タスク毎に「指ベッタリ」か「指の側面」かを判別。
#ではターゲット右下位置の側面だった率はどれくらい？を知りたい。

# 1.全体での初期側面率
# 2.エラー多かった右下3ターゲットタスクのみの初期側面率
# ↓は余裕あれば↓
# 3.エラー全体での側面率
# 4.右下3タゲでのエラー全体からの側面率
# #

#右下位置の画像はどうやって識別する？また、エラー時の右下タスクだけを抜き出すのはどうやる？
#-> 右下タゲのタスク番号は控えた。
# 1.全体の画像を取り込む→右下ターゲットも後々やりやすいように、被験者セクション毎に収納場所（参照場所は分けたい）
# →全部画像処理かけて長短の比率出す(この時、セクション情報とタスク番号はわかるようにしたい)→それを一つずつintリストに入れる→割合計算
# 2.各セクションの該当タスクだけ画像処理以降の処理をする。
# #


import cv2
import re
import glob
import numpy as np
import math

files = sorted(glob.glob("img/*.png"))
tskdata = np.array([])
jyoutaiarray =np.array([])
for f in files: #imageフォルダ下の全画像データ分繰り返す
    
    #全部の画像データを取得+グレースケール化
    img = cv2.imread(f,cv2.IMREAD_GRAYSCALE) 

    # 二値化
    _, binimg = cv2.threshold(img, 0, 255, cv2.THRESH_BINARY | cv2.THRESH_OTSU)
    binimg = cv2.bitwise_not(binimg)

    # 結果画像表示
    # bimg = binimg // 2 + 128  # 結果画像の黒の部分を灰色にする。
    bimg = binimg // 4 + 255 * 3 //4
    resimg = cv2.merge((bimg,bimg,bimg)) 

    # 輪郭取得
    contours,hierarchy =  cv2.findContours(binimg,cv2.RETR_TREE,cv2.CHAIN_APPROX_SIMPLE)

    for i, cnt in enumerate(contours): # 引数にリストなどのイテラブルオブジェクトを指定する。インデックス番号, 要素の順に取得できる。
        if len(contours[i]) >= 5: #楕円抽出するためには輪郭（頂点？）が5つ以上必要なので、fitEllipse()がエラーを吐いてしまうことあり。エラー回避はこれで良いのか怪しい。
            # 楕円フィッティング
            ellipse = cv2.fitEllipse(cnt)
            '''
            ellipseの中身　　((cx, cy), (h, w), deg) 例)print(ellipse) -> ((7.5, 17.0), (4.073996067047119, 5.374904155731201), 116.52420043945312)
            cx - 中心X
            cy - 中心Y
            h - 楕円縦方向の長さ
            w - 楕円横方向の長さ　→　長短逆っぽい？
            deg - 傾き角度
            '''

            # taskdata[繰り返し番号]に(被験者-セクション、task番号、ベッタリか側面か、楕円の長軸短軸の比率)　後から「タスク番号」や「被験者セクション」などで検索かけられるようにしたい
            taskname = f[4:13]
            tyoujiku = ellipse[1][1]
            tannjiku = ellipse[1][0]
            jyotai = tannjiku/tyoujiku # 今は比率を表示している。この後指の状態を基準決めて判別する
            tskdata = np.append(tskdata, taskname)
            tskdata = np.append(tskdata, str(jyotai))
            jyoutaiarray = np.append(jyoutaiarray, jyotai)  
            ## tskdataに[task番号,比率,task番号,比率,~~~]で格納されてる ##

            # 楕円描画
            resimg = cv2.ellipse(resimg,ellipse,(255,0,0),1) # cv2.ellipse(img, box, color, thickness=1, lineType=cv2.LINE_8)


   # cv2.imshow(taskname,resimg)
   # cv2.waitKey()
   # np.where(配列名　条件)
#print(tskdata.dtype) # U32型 ['1_1task01' '0.7803787641266638' '1_1task02' ... '0.7158853693844002''5_5task35' '0.7476881623229324']
#print(jyoutaiarray.dtype)# float64型 [0.78037876 0.78037876 0.9725435  0.61803402 1.         0.81649663 ... 0.64947324 0.64826668 0.67539631 0.65465368 0.71588537 0.74768816]


# ほしい情報は、全体の側面率と右下エラーターゲットだけでの側面率

# 関数:全体の側面率(allpercent))
def allper(percent):
    bosuu = len(jyoutaiarray)
    sokumen = 0
    bettari = 0
    for a in jyoutaiarray: 
        if a <= percent:# jyoutaiが基準(percent)より小さいとき＝側面
            sokumen += 1
        else:
            bettari += 1
    allpercent_sokumen = (sokumen/bosuu)*100
    allpercent_bettari = (bettari/bosuu)*100
    print("全体側面比率",allpercent_sokumen)
    print("全体腹比率",allpercent_bettari)

# 関数:errorターゲットの側面率(tarpercent)
def tarper(per):
    tar_array = np.array([])
    textarr = np.array(["2_1task16",
    "2_3task12",
    "2_5task25",
    "3_1task28",
    "3_3task01",
    "3_5task08",
    "4_1task13",
    "4_3task22",
    "4_5task34",
    "1_1task25",
    "1_3task28",
    "1_5task15",
    "5_1task31",
    "5_3task26",
    "5_5task07",
    "2_1task06",
    "2_3task06",
    "2_5task11",
    "3_1task32",
    "3_3task29",
    "3_5task10",
    "4_1task27",
    "4_3task32",
    "4_5task07",
    "1_1task32",
    "1_3task34",
    "1_5task29",
    "5_1task17",
    "5_3task17",
    "5_5task21",
    "2_1task23",
    "2_3task10",
    "2_5task19",
    "3_1task12",
    "3_3task26",
    "3_5task16",
    "4_1task18",
    "4_3task24",
    "4_5task25",
    "1_1task17",
    "1_3task24",
    "1_5task12",
    "5_1task28",
    "5_3task29",
    "5_5task02"])

    for t in textarr: # 右下ターゲット番号格納配列分ループ→tar_arrayに該当ターゲットの比率を配列で取得
        index = np.where(tskdata == t) # 全体データからターゲット合致indexを取得
        tarnum = float(tskdata[index[0]+1]) #ターゲットの比率を取得(tarnum)
        tar_array = np.append(tar_array,tarnum)
        

    bosuu = len(tar_array)
    sokumen = 0
    bettari = 0
    for tar in tar_array: 
        if tar <= per:# jyoutaiが基準(percent)より小さいとき＝側面
            sokumen += 1
        else:
            bettari += 1
    tarpercent_sokumen = (sokumen/bosuu)*100
    tarpercent_bettari = (bettari/bosuu)*100
    print("ターゲット側面比率",tarpercent_sokumen)
    print("ターゲット腹比率",tarpercent_bettari)
    

allper(0.5)
tarper(0.5)


'''





'''
 
