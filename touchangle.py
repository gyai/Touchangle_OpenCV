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

files = glob.glob("img/*.png")
img_datas = [] #先に配列作っておけば、読み込んだ画像データを配列内に追加してくれる？(上書きしないよな。。？)

for f in files: #imageフォルダ下の全画像データ分繰り返す
    '''
    #全部の画像データを取得+グレースケール化
    img = cv2.imread(f,cv2.IMREAD_GRAYSCALE) 

    # 二値化
    _, binimg = cv2.threshold(img, 0, 255, cv2.THRESH_BINARY | cv2.THRESH_OTSU)
    binimg = cv2.bitwise_not(binimg)
    '''
    img = cv2.imread(f,cv2.IMREAD_COLOR)
    # グレイスケール化
    gray1 = cv2.bitwise_and(img[:,:,0], img[:,:,1])
    gray1 = cv2.bitwise_and(gray1, img[:,:,2])

    # 二値化
    _, binimg = cv2.threshold(gray1, 0, 255, cv2.THRESH_BINARY | cv2.THRESH_OTSU)
    binimg = cv2.bitwise_not(binimg)
    # 結果画像表示
    # bimg = binimg // 2 + 128  # 結果画像の黒の部分を灰色にする。
    bimg = binimg // 4 + 255 * 3 //4
    resimg = cv2.merge((bimg,bimg,bimg)) 

    # 輪郭取得
    contours,hierarchy =  cv2.findContours(binimg,cv2.RETR_TREE,cv2.CHAIN_APPROX_SIMPLE)
    for i, cnt in enumerate(contours): # 引数にリストなどのイテラブルオブジェクトを指定する。インデックス番号, 要素の順に取得できる。
        if len(contours[i]) >= 5:
            # 楕円フィッティング
            ellipse = cv2.fitEllipse(cnt)
            print(ellipse)

            cx = int(ellipse[0][0])
            cy = int(ellipse[0][1])

            # 楕円描画
            resimg = cv2.ellipse(resimg,ellipse,(255,0,0),2)
            cv2.drawMarker(resimg, (cx,cy), (0,0,255), markerType=cv2.MARKER_CROSS, markerSize=10, thickness=1)
            cv2.putText(resimg, str(i+1), (cx+3,cy+3), cv2.FONT_HERSHEY_SIMPLEX, 0.8, (0,80,255), 1,cv2.LINE_AA)
        print(i,cnt)
        cv2.imshow('resimg',resimg)
        cv2.waitKey()




    #ここまでで、全部の画像データが白黒の二値化されて表示できるようになった




 
