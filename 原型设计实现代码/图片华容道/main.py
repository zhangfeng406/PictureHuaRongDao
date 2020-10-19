#coding:utf-8
import sys
import base64
import json
import cv2
import requests
import copy
from enum import IntEnum
from tkinter import _flatten
from PyQt5 import QtGui, QtCore, QtWidgets
from PyQt5.QtWidgets import QLabel, QWidget, QApplication, QGridLayout, QMessageBox, QMainWindow, QPushButton
from PyQt5.QtGui import QIcon, QPixmap
from PyQt5.QtCore import Qt
from PIL import Image
from PIL import ImageChops
# -*- coding:utf-8 -*-

uuid = ""  # 此题目的标识，提交答案时使用
ans = ""  # answer
operations = ""  # 我的操作序列
step = 0  # 第几步进行强制调换
zuhao = 0  # 组号
disnumber = 0  # 缺少的图片对应的编号
myswap = [0, 0]  # 无解时自己所进行的交换
swap = []  # 题目给的调换位置
targetSequence = []  # 目标序列
listproblem = []  # 得到的乱序图片的序列
my_step = 0
name = ""

def compareImages(path_one, path_two):  # 比对两张图片是否相同
    image_one = Image.open(path_one)
    image_two = Image.open(path_two)
    try:
        diff = ImageChops.difference(image_one, image_two)

        if diff.getbbox() is None:
            return True
        else:
            return False

    except ValueError as e:
        return "{0}\n{1}".format(e, "图片大小和box对应的宽度不一致!")


def getGroupNumber(path_one):  # 获得该组图片对应的字母序号
    path = '../切割图片/'
    for i in range(36):
        path2 = path + str(i) + '_'
        for j in range(1, 10):
            path_two = path2 + str(j) + '.jpg'
            if compareImages(path_one, path_two):
                return i


def getSequence(zuhao):
    listnow = []
    for i in range(1, 10):
        path11 = './' + "subject" + str(i) + ".jpg"
        if compareImages(path11, 'white.jpg'):
            listnow.append(0)
        else:
            for j in range(1, 10):
                path22 = '../切割图片/' + str(zuhao) + '_' + str(j) + ".jpg"
                if compareImages(path11, path22):
                    listnow.append(j)
    # 当前得到的乱序图片的序列
    disnumber = 0
    listnowsum = 0
    for i in listnow:
        listnowsum += int(i)
        disnumber = 45 - listnowsum
    # 1-9 求和为45 而找出序列的求和值 求可以找到空白块对应的哪个序号
    listnow2 = [[], [], []]  # 构造二维数组
    listnow2[0] = listnow[0:3]
    listnow2[1] = listnow[3:6]
    listnow2[2] = listnow[6:9]
    return listnow2, disnumber


def getlist():
    path1 = ''
    for i in range(1, 10):
        filename = './' + "subject" + str(i) + ".jpg"
        if not compareImages(filename, 'white.jpg'):
            if not compareImages(filename, 'black.jpg'):
                path1 = filename
                break  # 找到一张既不是全黑也不是全白的切割完的小图进行比对
    zuhao = getGroupNumber(path1)  # 获得该组图片对应的字母序号
    alist, disnumber = getSequence(zuhao)
    print("该图是第{0}张图片".format(zuhao))
    print("题目序列是")
    print(alist[0])
    print(alist[1])
    print(alist[2])
    return zuhao, alist, disnumber


# 获取题目
def getSubject():
    url = "http://47.102.118.1:8089/api/problem?stuid=031802437"
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/79.0.3941.4 Safari/537.36'
    }
    r = requests.get(url, headers=headers)
    r.raise_for_status()
    r.encoding = r.apparent_encoding
    text = json.loads(r.text)
    # 获取到的数据
    img_base64 = text["img"]
    step = text["step"]
    swap = text["swap"]
    uuid = text["uuid"]
    img = base64.b64decode(img_base64)
    # base64 编码后的题目存在本地
    with open("photo.jpg", "wb") as fp:
        fp.write(img)
    img = cv2.imread("photo.jpg", cv2.IMREAD_GRAYSCALE)
    # 切分题目图片
    for row in range(3):
        for colum in range(3):
            sub = img[row * 300:(row + 1) * 300, colum * 300:(colum + 1) * 300]
            cv2.imwrite("subject" + str(row * 3 + colum + 1) + ".jpg", sub)
    zuhao, alist, disnumber = getlist()
    return step, swap, uuid, zuhao, alist, disnumber


# 提交数据
def submit(uuid, operations, swap):
    # json.dumps()用于将字典形式的数据转化为字符串 json.loads()用于将字符串形式的数据转化为字典
    url = " http://47.102.118.1:8089/api/answer"
    data_json = json.dumps({"uuid": uuid, "answer": {"operations": operations, "swap": swap}})
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/79.0.3941.4 Safari/537.36',
        'Content-Type': 'application/json'
    }
    response = requests.post(url, headers=headers, data=data_json)
    ret = json.loads(response.text)
    answer = ret['answer']
    score = ret['score']
    time = ret['time']
    print('answer:', answer)
    print('score:', score)
    print('time:', time)


def solvePuzzle(twoDimensionalList):
    print("twoDim")
    print(twoDimensionalList[0])
    print(twoDimensionalList[1])
    print(twoDimensionalList[2])
    flattenlist = list(_flatten(twoDimensionalList))  # 使用tkinter的_flatten函数 转成一维
    s1 = [str(x) for x in flattenlist]  # 列表中的数字转成字符
    srcLayout = ''.join(s1)  # 得到初始状态字符串srcLayout

    sum = 0  # 找到0对应的1-9中的数字 zeroFor
    for i in range(9):
        sum = sum + flattenlist[i]
    zeroFor = 45 - sum

    tempList = [1, 2, 3, 4, 5, 6, 7, 8, 9]
    for i in range(9):
        if tempList[i] == zeroFor:  # 1-9中把zerofor替换为0，目标与初始状态 相对应
            tempList[i] = 0
            break
    d1 = [str(x) for x in tempList]
    destLayout = ''.join(d1)  # 得到目标状态字符串destLayout

    def checkSrcDest():
        print("src ", srcLayout)
        print("dest", destLayout)

    # 注释掉下面这行调用，将不打印显示src,dest字符串
    checkSrcDest()

    # 原始算法开始
    g_dict_layouts = {}
    # 每个位置可交换的位置集合
    g_dict_shifts = {0: [1, 3], 1: [0, 2, 4], 2: [1, 5],
                     3: [0, 4, 6], 4: [1, 3, 5, 7], 5: [2, 4, 8],
                     6: [3, 7], 7: [4, 6, 8], 8: [5, 7]}

    def swap_chr(a, i, j):
        if i > j:
            i, j = j, i
        # 得到ij交换后的数组
        b = a[:i] + a[j] + a[i + 1:j] + a[i] + a[j + 1:]
        return b

    # 初始化字典
    g_dict_layouts[srcLayout] = -1
    stack_layouts = []
    stack_layouts.append(srcLayout)  # 当前状态存入列表

    # bFound = False
    while len(stack_layouts) > 0:
        curLayout = stack_layouts.pop(0)  # 出队列
        if curLayout == destLayout:  # 判断当前状态是否为目标状态
            break

        index_slide = curLayout.index("0")  # 寻找0 的位置。
        lst_shifts = g_dict_shifts[index_slide]  # 当前可进行交换的位置集合
        for nShift in lst_shifts:
            newLayout = swap_chr(curLayout, nShift, index_slide)

            if g_dict_layouts.get(newLayout) == None:  # 判断交换后的状态是否已经查询过
                g_dict_layouts[newLayout] = curLayout
                stack_layouts.append(newLayout)  # 存入集合

    lst_steps = []
    lst_steps.append(curLayout)
    while g_dict_layouts[curLayout] != -1:  # 存入路径
        curLayout = g_dict_layouts[curLayout]
        lst_steps.append(curLayout)
    lst_steps.reverse()
    # 原始算法结束

    motion = ""  # 创建移动motion字符串，即wasd操作序列
    for cc in range(len(lst_steps) - 1):
        index_a = lst_steps[cc].index("0")
        index_b = lst_steps[cc + 1].index("0")
        abs_ab = (index_a - index_b)  # 比较空格0在当前状态和下一状态的index检索，得到移动方向wasd
        if abs_ab > 0:
            if abs_ab == 1:
                motion = motion + "a"
            else:
                motion = motion + "w"
        else:
            if abs_ab == -1:
                motion = motion + "d"
            else:
                motion = motion + "s"
    # return  lst_steps, motion
    return motion


# 计算不在原位的个数
def notInPlace(alist):
    cost = 0
    for row in range(3):
        for column in range(3):
            if alist[row][column] == 0:
                pass
                # 值是否对应
            elif alist[row][column] != row * 3 + column + 1:
                cost += 1
    return cost


# 计算逆序数之和
def inverseNum(nums):
    count = 0
    for i in range(len(nums)):
        if nums[i] != 0:
            for j in range(i):
                if nums[j] > nums[i]:
                    count += 1
    return count


# 根据逆序数之和判断所给八数码是否可解
def isSolvable(src, target1):
    src = src[0] + src[1] + src[2]
    target1 = target1[0] + target1[1] + target1[2]
    N1 = inverseNum(src)
    N2 = inverseNum(target1)
    if N1 % 2 == N2 % 2:  # 奇偶性相同则有解
        return True
    else:
        return False


# 赋值
def assignment(a, b, c, d, e, f):
    global step
    global swap
    global uuid
    global zuhao
    global listproblem
    global disnumber
    step = a
    swap = b.copy()  # copy() 对于父对象深拷贝 对子对象浅拷贝
    uuid = c
    zuhao = d
    listproblem = e
    disnumber = f


# 方向
class Direction(IntEnum):
    # 用枚举类表示方向
    UP = 0
    DOWN = 1
    LEFT = 2
    RIGHT = 3


# 图片华容道主体
class pictureHuaRongDaoAI(QWidget):

    def __init__(self):
        super().__init__()
        self.numbers = list(range(1, 10))
        self.blocks = []
        self.zero_row = 0
        self.zero_column = 0
        self.gltMain = QGridLayout()
        self.disnum = 0  # 空白格位置
        self.cost = 0
        self.mylist = []
        self.goal = []
        self.initUI()
        self.ans = ""
        self.count = 0
        self.myStep = 0

    def initUI(self):
        # 设置方块间隔
        self.gltMain.setSpacing(10)
        self.onInit()
        # 设置布局
        self.setLayout(self.gltMain)
        # 设置宽和高
        self.setFixedSize(950, 950)
        # self.center()
        # 设置标题和图标
        s = "每开始新的一局要点击键Z开始哦！ 点击Q键可以实现AI演示！点击R建回到主界面"
        self.setWindowTitle(s)
        # 设置背景颜色
        self.setStyleSheet("background-color:white;")
        self.show()

    # 初始化布局
    def onInit(self):
        # 产生顺序数组
        global ans
        global my_step
        global name
        name = ""
        ans = ""
        my_step = 0
        self.ans = ""
        self.count = 0
        self.disnum = disnumber  # 缺的数字
        self.numbers = list(range(1, 10))
        self.numbers[self.disnum - 1] = 0  # 标记空白格对应的位置
        self.blocks = copy.deepcopy(listproblem)
        # 将数字添加到二维数组
        for row in range(3):
            for column in range(3):
                if self.blocks[row][column] == 0:
                    self.zero_row = row
                    self.zero_column = column
                    # 找到空白格的位置
        self.mylist = self.blocks.copy()
        self.updatePanel()
        # self.ourAI()

    # 检测按键
    def keyPressEvent(self, event):
        # if self.myStep == step:
        #     if QMessageBox.Ok == QMessageBox.information(self, '步数提醒', '你已经走了'+str(step)+'步啦！我们将进行强制交换哦！'):
        #         self.change(swap)
        #         self.updatePanel()
        global my_step
        key = event.key()
        if key == Qt.Key_Up or key == Qt.Key_W:
            self.move(Direction.UP)  # 空白格向上
            my_step += 1
        if key == Qt.Key_Down or key == Qt.Key_S:
            self.move(Direction.DOWN)  # 空白格向下
            my_step += 1
        if key == Qt.Key_Left or key == Qt.Key_A:
            self.move(Direction.LEFT)  # 空白格向左
            my_step += 1
        if key == Qt.Key_Right or key == Qt.Key_D:
            self.move(Direction.RIGHT)  # 空白格向右
            my_step += 1
        if key == Qt.Key_Z:
            self.ourAI()    # 按Z开始游戏
        if key == Qt.Key_Q: # AI 演示
            self.nextStep()
            if QMessageBox.Ok == QMessageBox.information(self, 'AI演示', '您选择了AI代跑 点击E键即可代跑一步'):
                self.count = 0
        if key == Qt.Key_E: # 提示下一步
            next_step = operations[self.count]
            my_step += 1
            if next_step == 'w':
                self.move(Direction.UP)
            elif next_step == 's':
                self.move(Direction.DOWN)
            elif next_step == 'a':
                self.move(Direction.LEFT)
            elif next_step == 'd':
                self.move(Direction.RIGHT)
            self.updatePanel()
            self.count += 1
        if key == Qt.Key_R: # 键入R回到主界面
            self.close()
            self.f = homePage()
            self.f.show()
        self.updatePanel()
        # self.myStep = self.myStep + 1
        if self.checkResult():
            if QMessageBox.Ok == QMessageBox.information(self, '挑战结果', '恭喜您完成挑战！'):
                dict = {name : my_step}
                print(dict)
                with open("score.txt", "a") as f:
                    f.write(name+":"+str(my_step)+'\n')
                self.onInit()  # 结束重开一局

    # 方块移动算法
    def move(self, direction):
        if (direction == Direction.UP):  # 上
            if self.zero_row != 0:
                self.blocks[self.zero_row][self.zero_column] = self.blocks[self.zero_row - 1][self.zero_column]
                self.blocks[self.zero_row - 1][self.zero_column] = 0
                self.zero_row -= 1
        if (direction == Direction.DOWN):  # 下
            if self.zero_row != 2:
                self.blocks[self.zero_row][self.zero_column] = self.blocks[self.zero_row + 1][self.zero_column]
                self.blocks[self.zero_row + 1][self.zero_column] = 0
                self.zero_row += 1

        if (direction == Direction.LEFT):  # 左
            if self.zero_column != 0:
                self.blocks[self.zero_row][self.zero_column] = self.blocks[self.zero_row][self.zero_column - 1]
                self.blocks[self.zero_row][self.zero_column - 1] = 0
                self.zero_column -= 1
        if (direction == Direction.RIGHT):  # 右
            if self.zero_column != 2:
                self.blocks[self.zero_row][self.zero_column] = self.blocks[self.zero_row][self.zero_column + 1]
                self.blocks[self.zero_row][self.zero_column + 1] = 0
                self.zero_column += 1

    # 更新一下显示面板上的图案
    # 这里用到了类block
    def updatePanel(self):
        for row in range(3):
            for column in range(3):
                self.gltMain.addWidget(Block(self.blocks[row][column]), row, column)
        self.setLayout(self.gltMain)

    # 检测是否完成
    def checkResult(self):
        for row in range(3):
            for column in range(3):
                if row == self.zero_row and column == self.zero_column:
                    pass
                # 值是否对应
                elif self.blocks[row][column] != row * 3 + column + 1:
                    return False
        return True

    # 强制调换 x的格式 [a,b]
    def change(self, x):
        global myswap
        row1 = int((x[0] - 1) / 3)
        col1 = (x[0] - 1) % 3  # 交换元素一的坐标
        row2 = int((x[1] - 1) / 3)
        col2 = (x[1] - 1) % 3  # 交换元素二的坐标
        print('第{0}步 强制交换{1}：'.format(step, swap))
        # print('强制交换前', self.blocks)
        self.blocks[row1][col1], self.blocks[row2][col2] = self.blocks[row2][col2], self.blocks[row1][col1]
        print('强制交换后',self.blocks)
        self.goal = []
        for row in range(3):
            self.goal.append([])  # 二维数组
            for column in range(3):
                # number 中存的 1-9
                self.goal[row].append(self.numbers[row * 3 + column])
                # goal 为目标序列
        if isSolvable(self.blocks, self.goal):  # 判断是否有解
            return
        else:
            mini = 10
            flag1 = 0
            flag2 = 0
            for i in range(9):
                for j in range(i, 9):  # 遍历 0-9 取两个进行交换 并判断交换后是否有解
                    #  若有解 判断不在原位的个数是否小于10，若小于10则交换
                    list1 = copy.deepcopy(self.blocks)
                    row1 = int(i / 3)
                    col1 = i % 3
                    row2 = int(j / 3)
                    col2 = j % 3
                    list1[row1][col1], list1[row2][col2] = list1[row2][col2], list1[row1][col1]
                    if isSolvable(list1, self.goal):
                        thiscost = notInPlace(list1)
                        if mini > thiscost:  # 不断比较 找到一个开销最小的，即找到一个使不在原位的个数最少的交换方式
                            mini = thiscost
                            flag1 = i
                            flag2 = j
            row1 = int(flag1 / 3)
            col1 = flag1 % 3
            row2 = int(flag2 / 3)
            col2 = flag2 % 3
            # print('用户交换前', self.blocks)
            self.blocks[row1][col1], self.blocks[row2][col2] = self.blocks[row2][col2], self.blocks[row1][col1]
            print('无解，进行用户交换{0}：'.format([flag1 + 1, flag2 + 1]))
            # print('用户交换后', self.blocks)
            myswap = [flag1 + 1, flag2 + 1]
            return

    def ourAI(self):
        self.goal = []
        for row in range(3):
            self.goal.append([])  # 二维数组
            for column in range(3):
                # number 中存的 1-9
                self.goal[row].append(self.numbers[row * 3 + column])
                # goal 为目标序列
        global targetSequence
        targetSequence = self.goal.copy()  # 深拷贝
        currentSequence = self.mylist
        # stat
        global operations
        print("currentSequence")
        print(currentSequence[0])
        print(currentSequence[1])
        print(currentSequence[2])
        if not isSolvable(currentSequence, targetSequence):
            print('一开始无解，随机移动到step步再进行解题')
            anscopy = ""
            print(self.zero_row, self.zero_column)
            for i in range(step):
                if self.zero_row == 0:
                    anscopy += 's'
                    self.move(Direction.DOWN)
                else:
                    anscopy += 'w'
                    self.move(Direction.UP)

            self.change(swap)
            currentSequence = self.mylist  # mylist 就是题目给的乱序的图片序列
            ans = solvePuzzle(currentSequence)
            print("anscopy=", anscopy)
            print("ans=", ans)
            anscopy = anscopy + ans  # anscopy是强制调换前的操作序列，ans是调换完的操作序列

            operations = anscopy  # 把自己的操作序列赋给operation
        else:
            ans = solvePuzzle(currentSequence)
            if len(ans) <= step:
                operations = ans
            else:
                anscopy = ans[0:step]
                for i in range(step):
                    mm = ans[i]
                    if mm == 'w':
                        self.move(Direction.UP)
                    elif mm == 's':
                        self.move(Direction.DOWN)
                    elif mm == 'a':
                        self.move(Direction.LEFT)
                    elif mm == 'd':
                        self.move(Direction.RIGHT)
                self.change(swap)
                currentSequence = self.mylist
                ans = solvePuzzle(currentSequence)
                anscopy = anscopy + ans
                operations = anscopy

        print('uuid=', uuid)
        print('operations=', operations)
        print('myswap=', myswap)
        # submit(uuid, operations, myswap)

    def nextStep(self):
        global operations
        currentSequence = self.blocks.copy()    # 当前的序列
        operations = solvePuzzle(currentSequence)

    def center(self):  # 实现窗体在屏幕中央
        screen = QtWidgets.QDesktopWidget().screenGeometry()  # QDesktopWidget为一个类，调用screenGeometry函数获得屏幕的尺寸
        size = self.geometry()  # 同上
        self.move((screen.width() - size.width()) / 2, (screen.height() - size.height()) / 2)  # 调用move移动到指定位置



class homePage(QMainWindow):
    def __init__(self):
        super(homePage, self).__init__()
        self.init_ui()

    def init_ui(self):
        self.resize(950, 950)
        self.setWindowTitle('PictureHuaRongDao')

        # 设置背景
        window_pale = QtGui.QPalette()
        window_pale.setBrush(self.backgroundRole(), QtGui.QBrush(QtGui.QPixmap("background.jpg")))
        self.setPalette(window_pale)
        self.setWindowOpacity(0.9)  # 设置窗口透明度
        # self.setWindowFlag(QtCore.Qt.FramelessWindowHint)  # 隐藏边框
        self.center()
        # self.label = QLabel(self)
        # self.label.setGeometry(325, 200, 400, 200)  # 前两个 是坐标 后两个是长宽
        # self.label.setText("图片华容道")
        # self.setStyleSheet("QLabel{color:rgb(0,0,0,255);font-size:50px;font-weight:bold;font-family:Arial;}")
        self.btn1 = QPushButton('游戏界面', self)
        self.btn1.setStyleSheet("QPushButton{font-family:'黑体';font-size:32px;color:pink;}QPushButton{background-color:white}QPushButton:hover{background-color:skyblue}")
        self.btn1.setGeometry(350, 300, 250, 80)
        self.btn1.clicked.connect(self.goToGamePage)
        self.btn2 = QPushButton('游戏规则', self)
        self.btn2.setStyleSheet("QPushButton{font-family:'黑体';font-size:32px;color:pink;}QPushButton{background-color:white}QPushButton:hover{background-color:skyblue}")
        self.btn2.setGeometry(350, 400, 250, 80)
        self.btn2.clicked.connect(self.goToRule)
        self.btn3 = QPushButton('往次得分', self)
        self.btn3.setStyleSheet("QPushButton{font-family:'黑体';font-size:32px;color:pink;}QPushButton{background-color:white}QPushButton:hover{background-color:skyblue}")
        self.btn3.setGeometry(350, 500, 250, 80)
        self.btn3.clicked.connect(self.goToScore)

    def goToGamePage(self):
        self.close()
        self.s = gamePage()
        self.s.show()

    def goToRule(self):
        self.close()
        self.s = rulePage()
        self.s.show()

    def goToScore(self):
        self.close()
        self.s = scorePage()
        self.s.show()

    def center(self):  # 实现窗体在屏幕中央
        screen = QtWidgets.QDesktopWidget().screenGeometry()  # QDesktopWidget为一个类，调用screenGeometry函数获得屏幕的尺寸
        size = self.geometry()  # 同上
        self.move((screen.width() - size.width()) / 2, (screen.height() - size.height()) / 2)  # 调用move移动到指定位置


class gamePage(QWidget):
    def __init__(self):
        super(gamePage, self).__init__()
        self.init_ui()

    def init_ui(self):
        self.resize(950, 950)
        self.setWindowTitle('游戏界面')
        # 设置背景
        window_pale = QtGui.QPalette()
        window_pale.setBrush(self.backgroundRole(), QtGui.QBrush(QtGui.QPixmap("background.jpg")))
        self.setPalette(window_pale)
        self.center()
        # self.label1 = QLabel(self)
        # self.label1.setGeometry(350, 50, 250, 80)
        # self.label1.setText("游戏界面")
        # self.label1.setStyleSheet("QLabel{color:rgb(0,0,0,255);font-size:50px;font-weight:bold;font-family:Arial;}")
        # self.btn1 = QPushButton('开始游戏', self)
        # self.btn1.setGeometry(350, 300, 250, 80)
        # self.btn1.clicked.connect(self.startGame)

        self.btn2 = QPushButton('返回主界面', self)
        self.btn2.setStyleSheet("QPushButton{font-family:'黑体';font-size:32px;color:pink;}QPushButton{background-color:white}QPushButton:hover{background-color:skyblue}")
        self.btn2.setGeometry(350, 500, 250, 80)
        self.btn2.clicked.connect(self.goToHomePage)

        # 添加文本标签
        self.label = QtWidgets.QLabel(self)
        # 设置标签的左边距，上边距，宽，高
        self.label.setGeometry(QtCore.QRect(350, 200, 250, 60))
        # 设置文本标签的字体和大小，粗细等
        self.label.setFont(QtGui.QFont("黑体", 20))
        self.label.setText("请玩家输入名字")
        # 添加设置一个文本框
        self.text = QtWidgets.QLineEdit(self)
        # 调整文本框的位置大小
        self.text.setGeometry(QtCore.QRect(350, 300, 250, 60))

        # 添加提交按钮和单击事件
        self.btn = QtWidgets.QPushButton(self)
        # 设置按钮的位置大小
        self.btn.setStyleSheet("QPushButton{font-family:'黑体';font-size:32px;color:pink;}QPushButton{background-color:white}QPushButton:hover{background-color:skyblue}")
        self.btn.setGeometry(QtCore.QRect(350, 400, 250, 80))
        # 设置按钮的位置，x坐标,y坐标
        # self.btn.move(150, 140)
        self.btn.setText("开始游戏")
        # 为按钮添加单击事件
        self.btn.clicked.connect(self.startGame)

    def startGame(self):
        global name
        self.hide()
        self.f = pictureHuaRongDaoAI()
        self.f.show()
        name = self.text.text()

    def goToHomePage(self):
        self.hide()
        self.f = homePage()
        self.f.show()

    def center(self):  # 实现窗体在屏幕中央
        screen = QtWidgets.QDesktopWidget().screenGeometry()  # QDesktopWidget为一个类，调用screenGeometry函数获得屏幕的尺寸
        size = self.geometry()  # 同上
        self.move((screen.width() - size.width()) / 2, (screen.height() - size.height()) / 2)  # 调用move移动到指定位置


class scorePage(QWidget):
    def __init__(self):
        super(scorePage, self).__init__()
        self.init_ui()
    def init_ui(self):
        self.resize(950, 950)
        self.setWindowTitle('得分界面')
        # 设置背景
        window_pale = QtGui.QPalette()
        window_pale.setBrush(self.backgroundRole(), QtGui.QBrush(QtGui.QPixmap("background.jpg")))
        self.setPalette(window_pale)
        self.center()
        ourScore = ""
        for line in open("score.txt"):
            ourScore += line
        self.label = QtWidgets.QLabel(self)
        # 设置标签的左边距，上边距，宽，高
        self.label.setGeometry(QtCore.QRect(350, 200, 250, 500))
        # 设置文本标签的字体和大小，粗细等
        self.label.setFont(QtGui.QFont("黑体", 20))
        self.label.setText(ourScore)
        self.btn2 = QPushButton('返回主界面', self)
        self.btn2.setStyleSheet("QPushButton{font-family:'黑体';font-size:32px;color:pink;}QPushButton{background-color:white}QPushButton:hover{background-color:skyblue}")
        self.btn2.setGeometry(350, 800, 250, 80)
        self.btn2.clicked.connect(self.goToHomePage)


    def goToHomePage(self):
        self.hide()
        self.f = homePage()
        self.f.show()

    def center(self):  # 实现窗体在屏幕中央
        screen = QtWidgets.QDesktopWidget().screenGeometry()  # QDesktopWidget为一个类，调用screenGeometry函数获得屏幕的尺寸
        size = self.geometry()  # 同上
        self.move((screen.width() - size.width()) / 2, (screen.height() - size.height()) / 2)  # 调用move移动到指定位置

    # def replace(self):
    #     ourScore = ""
    #     for line in open("score.txt"):
    #         ourScore += line
    #     self.label = QtWidgets.QLabel(self)
    #     # 设置标签的左边距，上边距，宽，高
    #     self.label.setGeometry(QtCore.QRect(350, 200, 250, 60))
    #     # 设置文本标签的字体和大小，粗细等
    #     self.label.setFont(QtGui.QFont("黑体", 20))
    #     self.label.setText(ourScore)


class rulePage(QWidget):
    def __init__(self):
        super(rulePage, self).__init__()
        self.init_ui()
    def init_ui(self):
        self.resize(950, 950)
        self.setWindowTitle('游戏规则')
        # 设置背景
        window_pale = QtGui.QPalette()
        window_pale.setBrush(self.backgroundRole(), QtGui.QBrush(QtGui.QPixmap("background.jpg")))
        self.setPalette(window_pale)
        self.center()
        rule = "    玩家可以通过 WSAD 键使空白块上下左右移动，最终使乱序图能恢复原状。\n" \
               "玩家点击游戏界面，进入游戏登录界面，这时你可以为自己取个网名，\n" \
               "输入名字后登陆游戏，点击Q键开始游戏，这时玩家就可以开始玩游戏啦，\n当玩家不知道下一步怎么解时，" \
               "可以点击Z键开启AI解题功能，每按一次E键，\n我们内置的AI算法会为玩家移动一步，" \
               "直至完成游戏，完成游戏后，\n玩家的步数会被记录，最后显示在往次得分面板，供玩家查阅。"
        self.setWindowOpacity(0.9)  # 设置窗口透明度
        self.setWindowFlag(QtCore.Qt.FramelessWindowHint)  # 隐藏边框
        # self.setAttribute(QtCore.Qt.WA_TranslucentBackground)  # 设置窗口背景透明
        self.label = QtWidgets.QLabel(self)
        # 设置标签的左边距，上边距，宽，高
        self.label.setGeometry(QtCore.QRect(10, 10, 900, 900))
        # 设置文本标签的字体和大小，粗细等
        self.label.setFont(QtGui.QFont("黑体", 15))
        self.label.setText(rule)
        self.btn = QPushButton('返回主界面', self)
        self.btn.setStyleSheet("QPushButton{font-family:'黑体';font-size:32px;color:pink;}QPushButton{background-color:white}QPushButton:hover{background-color:skyblue}")
        self.btn.setGeometry(350, 800, 250, 80)
        self.btn.clicked.connect(self.goToHomePage)
        # self.btn.setStyleSheet("QPushButton{color:White;font-family:微软雅黑;border: 2px solid DarkGray;background:rgb(255, 255, 255, 60);}QPushButton:hover{border: 1px solid Gray;background:rgb(255, 255, 255, 90);}QPushButton:pressed{border: 2px solid DarkGray;background:rgb(255, 255, 255, 30);}")

    def goToHomePage(self):
        self.hide()
        self.f = homePage()
        self.f.show()

    def center(self):  # 实现窗体在屏幕中央
        screen = QtWidgets.QDesktopWidget().screenGeometry()  # QDesktopWidget为一个类，调用screenGeometry函数获得屏幕的尺寸
        size = self.geometry()  # 同上
        self.move((screen.width() - size.width()) / 2, (screen.height() - size.height()) / 2)  # 调用move移动到指定位置


class Block(QLabel):

    def __init__(self, number):
        super().__init__()
        self.imgPath = ["../切割图片/" + str(zuhao) + "_" + str(i) + ".jpg" for i in range(1, 10)]
        self.number = number
        self.setFixedSize(300, 300)  # 控制窗体大小
        if self.number > 0:
            # 导入图片
            imgName = self.imgPath[number - 1]
            pix = QPixmap(imgName)
            lb1 = QLabel(self)
            lb1.setPixmap(pix)

        if self.number == 0:
            self.setStyleSheet("background-color:white;")



if __name__ == '__main__':
    step, swap, uuid, groupNumber, listProblem, disNumber = getSubject()
    assignment(step, swap, uuid, groupNumber, listProblem, disNumber)
    app = QApplication(sys.argv)
    ex = homePage()
    ex.show()
    sys.exit(app.exec_())
