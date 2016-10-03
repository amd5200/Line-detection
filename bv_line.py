#!/usr/bin/env python
# coding: utf -8                   #加上這行才能key中文 要import urllib2
import urllib2
# -*- coding: cp936 -*-
######################
#
# 背景建模，線檢測
# 現役羅技webcam 要先開Cheese程式 使解析度640X480
#
######################
 
 
import sys
from math import sin, cos, sqrt, pi
import cv2.cv as cv
import time



 
if __name__ == '__main__':
 
    pBkImg = None
    pFrImg = None
    pFrameadd = None                     # line
 
    pBkMat = None
    pFrMat = None
    pFrameMat = None
    
 
    nFrmNum = 0
 
    #創建視窗
    cv.NamedWindow("video", 4)
    #cv.NamedWindow("background",4)
    #cv.NamedWindow("foreground",4)
    cv.NamedWindow("line",4)                                    #line
    cv.NamedWindow("add",4)                                     #
    #使視窗有序排列
    cv.MoveWindow("video", 690, 290)
    #cv.MoveWindow("background", 360, 0)
    #cv.MoveWindow("foreground", 690, 0)
    cv.MoveWindow("line", 30, 290)                                #line
    cv.MoveWindow("add", 360, 290)                                #

    #创建一个矩形，来让我们在图片上写文字，参数依次定义了文字类型，高，宽，字体厚度等。
    font=cv.InitFont(cv.CV_FONT_HERSHEY_SIMPLEX, 1, 1, 0, 3, 4)
 
    #打開攝像頭
    pCapture = cv.CreateCameraCapture(1)
    #pCapture = cv.CreateCameraCapture(2)
    
    #設定解析度
    width = 320 #leave None for auto-detection
    height = 240 #leave None for auto-detection
    #width = 240 #leave None for auto-detection
    #height = 180 #leave None for auto-detection
    cv.SetCaptureProperty(pCapture,cv.CV_CAP_PROP_FRAME_WIDTH,width)
    cv.SetCaptureProperty(pCapture,cv.CV_CAP_PROP_FRAME_HEIGHT,height)

    if not pCapture:
        print("Can not open camera.")
        sys.exit(1)
    #打開視頻文件
 #   pCapture = cvCaptureFromFile(sys.argv[1]) if not pCapture:
 #   print("Can not open video file.") sys.exit(1)
 
    #逐幀讀取視頻
    while True:
 
        pFrame = cv.QueryFrame( pCapture )
        if not pFrame:
            print("Can not open frame.")
            sys.exit(1)
 
        nFrmNum = nFrmNum+1
 
        print(nFrmNum)
 
        #如果是第一幀，需要申請記憶體，並初始化
        if nFrmNum == 1:
            
            pBkImg = cv.CreateImage(cv.GetSize(pFrame), cv.IPL_DEPTH_8U,1)
            pFrImg = cv.CreateImage(cv.GetSize(pFrame), cv.IPL_DEPTH_8U,1)

            pFrameadd = cv.CreateImage(cv.GetSize(pFrame), cv.IPL_DEPTH_8U,1)             #line
            dst = cv.CreateImage( cv.GetSize(pFrImg), 8, 1 )                              #
            dstadd = cv.CreateImage( cv.GetSize(pFrImg), 8, 1 )                           #
            color_dst = cv.CreateImage( cv.GetSize(pFrImg), 8, 3 )                        #
            color_dstadd = cv.CreateImage( cv.GetSize(pFrImg), 8, 3 )                     #
            storage = cv.CreateMemStorage(0)                                              #
            lines = 0                                                                     #
 
            pBkMat = cv.CreateMat(pFrame.height, pFrame.width, cv.CV_32FC1)
            pFrMat = cv.CreateMat(pFrame.height, pFrame.width, cv.CV_32FC1)
            pFrameMat = cv.CreateMat(pFrame.height, pFrame.width, cv.CV_32FC1)
 
            #轉化成單通道圖像再處理
            cv.CvtColor(pFrame, pBkImg, cv.CV_BGR2GRAY)
            cv.CvtColor(pFrame, pFrImg, cv.CV_BGR2GRAY)

            cv.CvtColor(pFrame, pFrameadd, cv.CV_BGR2GRAY)                           #line
            cv.CvtColor( dst, color_dst, cv.CV_GRAY2BGR )                            #
            cv.CvtColor( dstadd, color_dstadd, cv.CV_GRAY2BGR )                      #
 
            cv.Convert(pFrImg, pFrameMat)
            cv.Convert(pFrImg, pFrMat)
            cv.Convert(pFrImg, pBkMat)
        else:
 
            cv.CvtColor(pFrame, pFrImg, cv.CV_BGR2GRAY)

            cv.CvtColor(pFrame, pFrameadd, cv.CV_BGR2GRAY)                           #line

            cv.Convert(pFrImg, pFrameMat)

            cv.CvtColor( dst, color_dst, cv.CV_GRAY2BGR )
            cv.CvtColor(pFrameadd, color_dstadd, cv.CV_GRAY2BGR )                      # 保持原畫面
 
            #高斯濾波先，以平滑圖像
            #cv.Smooth(pFrameMat, pFrameMat, cv.CV_GAUSSIAN, 3, 0, 0)
 
            #當前幀跟背景圖相減
            #cv.AbsDiff(pFrameMat, pBkMat, pFrMat)

            #邊緣偵測
            cv.Canny( pFrImg, dst, 150, 200, 3 )                                        #邊緣偵測
            cv.Canny( pFrameadd, dstadd, 150, 200, 3 )                                  #邊緣偵測
 
            #二值化前景圖
#           cv.Threshold(pFrMat, pFrImg, 60, 255.0, cv.CV_THRESH_BINARY)
            cv.Threshold(pFrImg, pFrImg, 200, 255.0, cv.CV_THRESH_BINARY)                   #前景圖+劃線
 
            #進行形態學濾波，去掉噪音
            #cv.Erode(pFrImg, pFrImg, None, 1)
            #cv.Dilate(pFrImg, pFrImg, None, 1)
            
            #劃線
#######################################################################################################
            lines = cv.HoughLines2(dst, storage, cv.CV_HOUGH_PROBABILISTIC, 1, pi / 100, 50, 50, 5)     #線的偵測參數
            lines = cv.HoughLines2(dstadd, storage, cv.CV_HOUGH_PROBABILISTIC, 1, pi / 100, 50, 50, 5)

            #将文字框加入到图片中，(5,30)定义了文字框左顶点在窗口中的位置，最后参数定义文字颜色
            TestStr = "Line Detection"
            cv.PutText(pFrame, TestStr , (5,30), font, (0,255,0))

            for line in lines:
                cv.Line(pFrame, line[0], line[1], cv.CV_RGB(255, 0, 0), 3, 8)                     #線的顏色 red
                cv.Line(color_dst, line[0], line[1], cv.CV_RGB(255, 255, 0), 3, 8)                    #線的顏色 yellow    
                cv.Line(color_dstadd, line[0], line[1], cv.CV_RGB(0, 255, 255), 3, 8)               #線的顏色 green


######################################################################################################## 
            #更新背景
            #cv.RunningAvg(pFrameMat, pBkMat, 0.003, None)
            #將背景轉化為圖像格式，用以顯示
            #cv.Convert(pBkMat, pBkImg)
 
            #顯示圖像
#            cvFlip(pFrame, None, 1)
#            cvFlip(pBkImg, None, 1)
#            cvFlip(pFrImg, None, 1)
            cv.ShowImage("video", pFrame)
            #cv.ShowImage("background", pBkImg)
            #cv.ShowImage("foreground", pFrImg)
            cv.ShowImage("line", color_dst)                                 #line
	    cv.ShowImage("add", color_dstadd)                               #

 
            #如果有按鍵事件，則跳出迴圈 此等待也為cvShowImage函數提供時間完成顯示 等待時間可以根據CPU速度調整
            if cv.WaitKey(2) >= 0 :
                break
 
 
 
 
    #銷毀視窗
    '''
    cv.DestroyWindow("video")
    cv.DestroyWindow("background")
    cv.DestroyWindow("foreground")
    '''
    cv.DestroyAllWindows()
 
    #釋放圖像和矩陣
    '''
    cv.ReleaseImage(pFrImg)
    cv.ReleaseImage(pBkImg)
 
    cv.ReleaseMat(pFrameMat)
    cv.ReleaseMat(pFrMat)
    cv.ReleaseMat(pBkMat)
    
 
    cv.ReleaseCapture(pCapture)
    '''
 
    sys.exit(0)
