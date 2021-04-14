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

files = sorted(glob.glob("img/*.png"))

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
            w - 楕円横方向の長さ
            deg - 傾き角度
            '''

            # taskdata[繰り返し番号]に(被験者-セクション、task番号、ベッタリか側面か、楕円の長軸短軸の比率)　後から「タスク番号」や「被験者セクション」などで検索かけられるようにしたい
            tskdata = {''}       

            # 楕円描画
            resimg = cv2.ellipse(resimg,ellipse,(255,0,0),1) # cv2.ellipse(img, box, color, thickness=1, lineType=cv2.LINE_8)

            cx = int(ellipse[0][0])
            cy = int(ellipse[0][1])
    cv2.imshow('resimg',resimg)
    cv2.waitKey()





 
