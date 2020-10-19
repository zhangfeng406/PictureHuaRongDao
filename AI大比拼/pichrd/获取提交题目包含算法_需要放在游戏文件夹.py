import sys
import base64
import json
import cv2
import requests
import numpy as np
import time
import copy
from tkinter import _flatten
from enum import IntEnum
from PIL import Image
from PIL import ImageChops

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
    path = '../segpic/'
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
                path22 = '../segpic/' + str(zuhao) + '_' + str(j) + ".jpg"
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
    # print("该图是第{0}张图片".format(zuhao))
    # print("题目序列是")
    # print(alist[0])
    # print(alist[1])
    # print(alist[2])
    return zuhao, alist, disnumber


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



def post(url, data_json):
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/79.0.3941.4 Safari/537.36',
        'Content-Type': 'application/json'
    }
    r = requests.post(url, headers=headers, data=data_json)
    return r.text


def get(url):
    # url = "http://47.102.118.1:8089/api/problem?stuid=031802437"
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/79.0.3941.4 Safari/537.36'
    }
    r = requests.get(url, headers=headers)
    r.raise_for_status()
    r.encoding = r.apparent_encoding
    return r.text


# 接口描述：获取今日的赛题，以列表方式展示所有的赛题，
# uuid为赛题的唯一标识符，challengercount为这个赛题被挑战了多少次，
# pubtimestamp为赛题的创建时间，author为赛题所属队伍，records为所有解出这题的队伍的数量。
def getChallenge():
    url = 'http://47.102.118.1:8089/api/challenge/list'
    datas = json.loads(get(url))
    count = 0
    for data in datas:
        print("第" + str(count) + "题")
        for key in data.keys():
            print(key + " : ", data[key])
        count += 1


# 获取赛题的解题记录，返回所有解出这题的队伍的纪录，按rank先后进行排序
# （包含step步数和以毫秒计的timeelapsed所用时间，以及记录的所属队伍的IDteamid和在这项赛题中取得的排名rank，
# owner为对应答题的队伍id。当前没有纪录时为[]。
def getRecord(uuid):
    url = 'http://47.102.118.1:8089/api/challenge/record/' + str(uuid)
    datas = json.loads(get(url))
    count = 0
    print("uuid : ", uuid)
    for data in datas:
        print("第"+str(count)+"名")
        for key in data.keys():
            print(key + " : ", data[key])


# 创建赛题，用token作为权限验证，提供队伍的IDteamid和赛题数据data。
# 创建成功返回赛题标识符uuid。data中letter表示赛题的对应字母、exclude表示当前哪个位置的图片被删去作为空格，
# challenge为游戏地图，step为强制交换的步数（0<=X<=20），swap为强制交换的图片（从左到右从上到下编号1-9）
def createQuestion(teamid, letter, exclude, challenge, step, swap, token):
    url = 'http://47.102.118.1:8089/api/challenge/create'
    datas = {
        "teamid": teamid,
        "data": {
            "letter": letter,
            "exclude": exclude,
            "challenge": challenge,
            "step": step,
            "swap": swap
        },
        "token": token
    }
    data_json = json.dumps(datas)
    ret = json.loads(post(url, data_json))
    for key in ret.keys():
        print(key + " : ", ret[key])


# 从高到低返回排行榜，展示每个队伍的获得的分数score、以及rank总分排名。
def getRank():
    url = 'http://47.102.118.1:8089/api/rank'
    datas = json.loads(get(url))
    count = 1
    for data in datas:
        print("第" + str(count) + "名")
        for key in data.keys():
            print(key + " : ", data[key])
        count+=1

# 获取指定队伍的信息，展示当前队伍的分数score、rank总分排名、还有解出的题success列表
# （每一项包含problemid赛题uuid和在这项赛题中取得的排名rank,challengeid为对应挑战的uuid），
# fail为未通过测试的列表， unsolved为未提交答案的列表。
def getTeamdetail(teamid):
    url = 'http://47.102.118.1:8089/api/teamdetail/'+str(teamid)
    datas = json.loads(get(url))
    for key in datas.keys():
        print(key + " : ", datas[key])


# 获取还未通过的题目，展示当前队伍还未挑战或通过的题目
# （今天之内创建的题目，不包含你自己出的以及你已经通过的题目）。字段含义可参考上面的接口说明。当前没有纪录时返回为[]。
def notPass(teamid):
    url = 'http://47.102.118.1:8089/api/team/problem/'+str(teamid)
    datas = json.loads(get(url))
    count = 1
    for data in datas:
        print("第" + str(count) + "题")
        for key in data.keys():
            print(key + " : ", data[key])
        count += 1
def solve(olst,step,swap):
    _dispatcher = {}
    def _copy_list(_l):
        ret = _l.copy()
        for idx, item in enumerate(ret):
            cp = _dispatcher.get(type(item))
            if cp is not None:
                ret[idx] = cp(item)
        return ret
    _dispatcher[list] = _copy_list

    g_dict_shifts = {0: [1, 3], 1: [0, 2, 4], 2: [1, 5],
                     3: [0, 4, 6], 4: [1, 3, 5, 7], 5: [2, 4, 8],
                     6: [3, 7], 7: [4, 6, 8], 8: [5, 7]}

    g_dict_ansleft = {0: ["d", "a"], 1: ["d", "a"], 2: ["a", "d"],
                      3: ["d", "a"], 4: ["d", "a"], 5: ["a", "d"],
                      6: ["d", "a"], 7: ["d", "a"], 8: ["a", "d"]}

    def getv(lst, qtab):  # 预测状态x对应的步数
        ss = [str(x) for x in lst]
        sk = ''.join(ss)
        lv = qtab.get(sk, -1)
        return lv

    def change(al):
        cl = []
        zeroindex = al.index(0)
        p = 1
        while p <= 8:
            for j in range(p + 1, 10):
                p1 = p - 1
                j1 = j - 1
                if (j % 2) == (p % 2):
                    t1 = al[p1]
                    t2 = al[j1]
                    al[p1] = t2
                    al[j1] = t1
                    cl.append(_copy_list(al))
                    al[p1] = t1
                    al[j1] = t2
                else:
                    if p1 == zeroindex or j1 == zeroindex:
                        continue
                    t1 = al[p1]
                    t2 = al[j1]
                    al[p1] = t2
                    al[j1] = t1
                    cl.append(_copy_list(al))
                    al[p1] = t1
                    al[j1] = t2
            p += 1
        return cl
    def change2(al):
        cl = []
        zeroin = al.index(0)
        z1 = zerofor - 1
        for i in range(9):
            if al[i] == dlist[i]:
                continue
            ti=al.index(dlist[i])
            if  i==zeroin or ti==zeroin:
                if i%2!=ti%2:
                    continue
                else:
                    t1 = al[i]
                    t2 = al[ti]
                    al[i] = t2
                    al[ti] = t1
                    cl.append(_copy_list(al))
                    al[i] = t1
                    al[ti] = t2
            else:
                t1 = al[i]
                t2 = al[ti]
                al[i] = t2
                al[ti] = t1
                cl.append(_copy_list(al))
                al[i] = t1
                al[ti] = t2
        return cl

    def swapinlist(twodlist, ain8, bin8):
        anslist = _copy_list(twodlist)
        for i in range(len(anslist)):
            anslist[i][ain8], anslist[i][bin8] = anslist[i][bin8], anslist[i][ain8]
        return anslist

    def swapsinglelist(lst, ain8, bin8):
        anslist = _copy_list(lst)
        anslist[ain8], anslist[bin8] = anslist[bin8], anslist[ain8]
        return anslist

    def swap_chr(a, i, j):
        if i > j:
            i, j = j, i
        # 得到ij交换后的数组
        b = a[:i] + a[j] + a[i + 1:j] + a[i] + a[j + 1:]
        return b

    def gen(lst):
        s1 = [str(x) for x in lst]  # 列表中的数字转成字符
        srcLayout = ''.join(s1)

        g_layouts = {}
        g_layouts [srcLayout] = -1
        g_v = {}
        g_v[srcLayout] = 0

        que_layouts = []
        que_layouts.append(srcLayout)  # 当前状态存入列表
        curv = g_v[srcLayout]

        while 1:
            curLayout = que_layouts.pop(0)  # 出队列
            curv = g_v[curLayout]
            if curv==step:
                break
            index_slide = curLayout.index("0")  # 寻找0 的位置。
            lst_shifts = g_dict_shifts[index_slide]  # 当前可进行交换的位置集合

            for nShift in lst_shifts:
                newLayout = swap_chr(curLayout, nShift, index_slide)

                if g_layouts.get(newLayout) == None:  # 判断交换后的状态是否已经查询过
                    g_v[newLayout] = curv + 1
                    g_layouts[newLayout] = curLayout
                    que_layouts.append(newLayout)  # 存入集合

        return g_v,g_layouts

        # def save_q_tab(strsave):  # 保存Query表
        #     k = list(g_dict_layouts.keys())
        #     v = list(g_dict_layouts.values())
        #     sq = "q" + strsave + ".npz"
        #     np.savez(sq, k=k, v=v)

        return
    def nosolve(srclist,destlist,step, swap):
        def rmove(lst):
            ts1 = [str(x) for x in lst]  # 列表中的数字转成字符
            tLayout = ''.join(ts1)
            return drm[tLayout]

        def lmove(lst):
            ts1 = [str(x) for x in lst]  # 列表中的数字转成字符
            tLayout = ''.join(ts1)

            lst_steps = []
            lst_steps.append(tLayout)
            while dleftlay[tLayout] != -1:  # 存入路径
                tLayout = dleftlay[tLayout]
                lst_steps.append(tLayout)
            lst_steps.reverse()

            motion = ""  # 创建移动motion字符串，即wasd操作序列
            for cc in range(len(lst_steps) - 1):
                index_a = lst_steps[cc].index("0")
                index_b = lst_steps[cc + 1].index("0")
                abs_ab = (index_a - index_b)  # 比较空格0在当前状态和下一状态的index检索，得到移动方向wasd
                if abs_ab > 0:
                    if abs_ab == 1:
                        motion += "a"
                    else:
                        motion += "w"
                else:
                    if abs_ab == -1:
                        motion += "d"
                    else:
                        motion += "s"
            # return  lst_steps, motion
            return motion

        if zerofor == 1:
            destQdict = destQdict1
            drm = rma1
        elif zerofor == 2:
            destQdict = destQdict2
            drm = rma2
        elif zerofor == 3:
            destQdict = destQdict3
            drm = rma3
        elif zerofor == 4:
            destQdict = destQdict4
            drm = rma4
        elif zerofor == 5:
            destQdict = destQdict5
            drm = rma5
        elif zerofor == 6:
            destQdict = destQdict6
            drm = rma6
        elif zerofor == 7:
            destQdict = destQdict7
            drm = rma7
        elif zerofor == 8:
            destQdict = destQdict8
            drm = rma8
        else:
            destQdict = destQdict9
            drm = rma9

        dleftv,dleftlay=gen(srclist)

        svaluelist = list(dleftv.values())
        skeylist = list(dleftv.keys())
        tstep = step

        rangelist = []
        while tstep > -1:
            for i in range(len(skeylist)):
                if svaluelist[i] == tstep:
                    rangelist.append([int(x) for x in skeylist[i]])
            tstep = tstep - 2

        swapmove = []
        strans = ""
        #不交换，无解》》无解
        if swap[0] == swap[1]:
            lst0 = rangelist
            chlst0 = []

            for i in range(len(lst0)):
                temptdlst0 = change2(lst0[i])
                for j in range(len(temptdlst0)):
                    chlst0.append(temptdlst0[j])
            tpvlst0 = []
            for i in range(len(chlst0)):
                tpvlst0.append(getv(chlst0[i], destQdict))
            vmin0 = min(tpvlst0)

            indexminlst0 = tpvlst0.index(vmin0)
            vminlaylst0 =chlst0[indexminlst0]
            tempch0 = change(vminlaylst0)

            for i in range(len(tempch0)):
                if tempch0[i] in lst0:
                    unch = tempch0[i]
                    break

            for i in range(9):
                if unch[i] != vminlaylst0[i]:
                    swapmove.append(i + 1)
            if vmin0==0:
                ansright="a"
                #print("vmin是0，ansright是a")
            else:
                ansright = rmove(vminlaylst0)
            ansleft = lmove(unch)
            templen = len(ansleft)
            indzero = unch.index(0)
            while templen < step:
                ansleft +=g_dict_ansleft[indzero][0]
                ansleft +=g_dict_ansleft[indzero][1]
                templen += 2

            strans = ansleft + ansright
        #同奇或同偶，无解》》有解
        elif (swap[0] % 2) == (swap[1] % 2):
            tsa = swap[0] - 1
            tsb = swap[1] - 1
            swapedlst = swapinlist(rangelist, tsa, tsb)
            tpvlst = []
            for i in range(len(swapedlst)):
                tpvlst.append(getv(swapedlst[i], destQdict))

            vmin = min(tpvlst)

            indexmin = tpvlst.index(vmin)
            vminlaylst = swapedlst[indexmin]
            if vmin==0:
                ansright="a"
                #print("vmin是0，ansright是a")
            else:
                ansright =rmove(vminlaylst)

            tsa = swap[0] - 1
            tsb = swap[1] - 1
            vminswapback = swapsinglelist(vminlaylst, tsa, tsb)

            ansleft = lmove(vminswapback)

            templen = len(ansleft)
            indzero = vminswapback.index(0)
            while templen < step:
                ansleft += g_dict_ansleft[indzero][0]
                ansleft += g_dict_ansleft[indzero][1]
                templen += 2


            strans = ansleft + ansright
        #一奇一偶，看交换位置上有无0
        else:
            #lst2有0，无解》》无解
            #lst1无0，无解》》有解
            lst1 = []
            lst2 = []
            tsa = swap[0] - 1
            tsb = swap[1] - 1
            cprl = _copy_list(rangelist)
            j = 0
            for i in range(len(rangelist)):
                if rangelist[i][tsa] == 0 or rangelist[i][tsb] == 0:
                    lst2.append(rangelist[i])
                    cprl.pop(i - j)
                    j += 1
            lst1 =cprl
            # lst1 强制交换，无解》》有解
            vmin1 = 100
            if len(lst1) != 0:
                swapedlst1 = swapinlist(lst1, tsa, tsb)
                tpvlst1 = []
                for i in range(len(swapedlst1)):
                    tpvlst1.append(getv(swapedlst1[i], destQdict))

                vmin1 = min(tpvlst1)

            vmin2 = 200
            #lst2 强制交换，无解》》无解
            if len(lst2) != 0:
                swapedlst2 = swapinlist(lst2, tsa, tsb)
                chlst2 = []
                for i in range(len(swapedlst2)):
                    temptdlst2 = change2(swapedlst2[i])
                    for j in range(len(temptdlst2)):
                        chlst2.append(temptdlst2[j])
                tpvlst2 = []
                for i in range(len(chlst2)):
                    tpvlst2.append(getv(chlst2[i], destQdict))

                vmin2 = min(tpvlst2)

            # lst2 vmin2
            if vmin1 > vmin2:
                #print("nosol,vmin2<vmin1")
                indexminlst2 = tpvlst2.index(vmin2)
                vminlaylst2 = chlst2[indexminlst2]
                tempch2 = change(vminlaylst2)

                for i in range(len(tempch2)):
                    if tempch2[i] in swapedlst2:
                        unch = tempch2[i]
                        break

                for i in range(9):
                    if unch[i] != vminlaylst2[i]:
                        swapmove.append(i + 1)
                tsa = swap[0] - 1
                tsb = swap[1] - 1
                vminswapback2 = swapsinglelist(unch, tsa, tsb)
                if vmin2 == 0:
                    #print("vmin是0，ansright是a")
                    ansright = "a"
                else:
                    ansright = rmove(vminlaylst2)
                ansleft = lmove(vminswapback2)
                templen = len(ansleft)
                indzero = vminswapback2.index(0)
                while templen < step:
                    ansleft += g_dict_ansleft[indzero][0]
                    ansleft += g_dict_ansleft[indzero][1]
                    templen += 2

                strans = ansleft + ansright
            elif vmin1==vmin2:
                #print("nosol,vmin1=vmin2")
                indexminlst1 = tpvlst1.index(vmin1)
                vminlaylst1 = swapedlst1[indexminlst1]
                if vmin1 == 0:
                    #print("vmin是0，ansright是a")
                    ansright = "a"
                else:
                    ansright = rmove(vminlaylst1)
                tsa = swap[0] - 1
                tsb = swap[1] - 1
                vminswapback1 = swapsinglelist(vminlaylst1, tsa, tsb)
                ansleft = lmove(vminswapback1)
                templen = len(ansleft)
                indzero = vminswapback1.index(0)
                while templen < step:
                    ansleft += g_dict_ansleft[indzero][0]
                    ansleft += g_dict_ansleft[indzero][1]
                    templen += 2
                strans = ansleft + ansright
            else:
                #print("nosol,vmin1<vmin2")
                indexminlst1 = tpvlst1.index(vmin1)
                vminlaylst1 = swapedlst1[indexminlst1]
                if vmin1 == 0:
                    #print("vmin是0，ansright是a")
                    ansright = "a"
                else:
                    ansright =rmove(vminlaylst1)
                tsa = swap[0] - 1
                tsb = swap[1] - 1
                vminswapback1 = swapsinglelist(vminlaylst1, tsa, tsb)
                ansleft = lmove(vminswapback1)
                templen = len(ansleft)
                indzero = vminswapback1.index(0)
                while templen < step:
                    ansleft += g_dict_ansleft[indzero][0]
                    ansleft += g_dict_ansleft[indzero][1]
                    templen += 2
                strans = ansleft + ansright
        return  swapmove, strans

    def yessolve(srclist,destlist, step, swap):

        def rmove(lst):
            ts1 = [str(x) for x in lst]  # 列表中的数字转成字符
            tLayout = ''.join(ts1)
            return drm[tLayout]

        def lmove(lst):
            ts1 = [str(x) for x in lst]  # 列表中的数字转成字符
            tLayout = ''.join(ts1)

            lst_steps = []
            lst_steps.append(tLayout)
            while dleftlay[tLayout] != -1:  # 存入路径
                tLayout = dleftlay[tLayout]
                lst_steps.append(tLayout)
            lst_steps.reverse()

            motion = ""  # 创建移动motion字符串，即wasd操作序列
            for cc in range(len(lst_steps) - 1):
                index_a = lst_steps[cc].index("0")
                index_b = lst_steps[cc + 1].index("0")
                abs_ab = (index_a - index_b)  # 比较空格0在当前状态和下一状态的index检索，得到移动方向wasd
                if abs_ab > 0:
                    if abs_ab == 1:
                        motion += "a"
                    else:
                        motion += "w"
                else:
                    if abs_ab == -1:
                        motion += "d"
                    else:
                        motion += "s"
            # return  lst_steps, motion
            return motion

        if zerofor == 1:
            destQdict = destQdict1
            drm = rma1
        elif zerofor == 2:
            destQdict = destQdict2
            drm = rma2
        elif zerofor == 3:
            destQdict = destQdict3
            drm = rma3
        elif zerofor == 4:
            destQdict = destQdict4
            drm = rma4
        elif zerofor == 5:
            destQdict = destQdict5
            drm = rma5
        elif zerofor == 6:
            destQdict = destQdict6
            drm = rma6
        elif zerofor == 7:
            destQdict = destQdict7
            drm = rma7
        elif zerofor == 8:
            destQdict = destQdict8
            drm = rma8
        else:
            destQdict = destQdict9
            drm = rma9

        swapmove = []
        strans = ""

        directsolve = rmove(srclist)
        if len(directsolve) <= step:
            strans = directsolve
            return swapmove, strans
        #不交换，有解》》有解
        if swap[0] == swap[1]:
            strans = directsolve
            return swapmove, strans

        dleftv,dleftlay=gen(srclist)

        svaluelist = list(dleftv.values())
        skeylist = list(dleftv.keys())
        tstep = step
        rangelist = []
        while tstep > -1:
            for i in range(len(skeylist)):
                if svaluelist[i] == tstep:
                    rangelist.append([int(x) for x in skeylist[i]])
            tstep-=2

        #同奇数或同偶数，强制交换，有解》》无解
        if (swap[0] % 2) == (swap[1] % 2):
            tsa = swap[0] - 1
            tsb = swap[1] - 1
            swapedlst = swapinlist(rangelist, tsa, tsb)

            chlst = []
            for i in range(len(swapedlst)):
                temptdlst = change2(swapedlst[i])
                for j in range(len(temptdlst)):
                    chlst.append(temptdlst[j])
            tpvlst = []
            for i in range(len(chlst)):
                tpvlst.append(getv(chlst[i], destQdict))

            vmin = min(tpvlst)

            indexminlst = tpvlst.index(vmin)
            vminlaylst = chlst[indexminlst]
            tempch = change(vminlaylst)

            for i in range(len(tempch)):
                if tempch[i] in swapedlst:
                    unch = tempch[i]
                    break

            for i in range(9):
                if unch[i] != vminlaylst[i]:
                    swapmove.append(i + 1)
            tsa = swap[0] - 1
            tsb = swap[1] - 1
            vminswapback = swapsinglelist(unch, tsa, tsb)
            if vmin == 0:
                #print("vmin是0，ansright是a")
                ansright = "a"
            else:
                ansright = rmove(vminlaylst)
            ansleft = lmove(vminswapback)
            templen = len(ansleft)
            indzero = vminswapback.index(0)
            while templen < step:
                ansleft += g_dict_ansleft[indzero][0]
                ansleft += g_dict_ansleft[indzero][1]
                templen += 2

            strans = ansleft + ansright
        #一奇一偶，看交换位置有0无0
        else:
            # lst1有0，有解》》有解
            # lst2无0，有解》》无解
            lst1 = []
            lst2 = []
            tsa = swap[0] - 1
            tsb = swap[1] - 1

            cprl = _copy_list(rangelist)
            j = 0
            for i in range(len(rangelist)):
                if rangelist[i][tsa] == 0 or rangelist[i][tsb] == 0:
                    lst1.append(rangelist[i])
                    cprl.pop(i - j)
                    j += 1
            lst2 = cprl

            # lst1 vmin1
            vmin1 = 100
            if len(lst1) != 0:
                swapedlst1 = swapinlist(lst1, tsa, tsb)
                tpvlst1 = []
                for i in range(len(swapedlst1)):
                    tpvlst1.append(getv(swapedlst1[i], destQdict))

                vmin1 = min(tpvlst1)

            # lst2 vmin2
            vmin2 = 200
            if len(lst2) != 0:
                swapedlst2 = swapinlist(lst2, tsa, tsb)
                chlst2 = []
                for i in range(len(swapedlst2)):
                    temptdlst2 = change2(swapedlst2[i])
                    for j in range(len(temptdlst2)):
                        chlst2.append(temptdlst2[j])
                tpvlst2 = []
                for i in range(len(chlst2)):
                    tpvlst2.append(getv(chlst2[i], destQdict))

                vmin2 = min(tpvlst2)

            # lst2 vmin2

            if vmin1 > vmin2:
                #print("yessol,vmin2<vmin1")
                indexminlst2 = tpvlst2.index(vmin2)
                vminlaylst2 = chlst2[indexminlst2]
                tempch2 = change(vminlaylst2)

                for i in range(len(tempch2)):
                    if tempch2[i] in swapedlst2:
                        unch = tempch2[i]
                        break

                for i in range(9):
                    if unch[i] != vminlaylst2[i]:
                        swapmove.append(i + 1)
                tsa = swap[0] - 1
                tsb = swap[1] - 1
                vminswapback2 = swapsinglelist(unch, tsa, tsb)
                if vmin2 == 0:
                    #print("vmin是0，ansright是a")
                    ansright = "a"
                else:
                    ansright =rmove(vminlaylst2)
                ansleft = lmove(vminswapback2)
                templen = len(ansleft)
                indzero = vminswapback2.index(0)
                while templen < step:
                    ansleft += g_dict_ansleft[indzero][0]
                    ansleft += g_dict_ansleft[indzero][1]
                    templen += 2

                strans = ansleft + ansright

            elif vmin1==vmin2:
                # vmin1=vmin2
                #print("yessol,vmin2=vmin1")
                indexminlst1 = tpvlst1.index(vmin1)
                vminlaylst1 = swapedlst1[indexminlst1]
                if vmin1 == 0:
                    #print("vmin是0，ansright是a")
                    ansright = "a"
                else:
                    ansright = rmove(vminlaylst1)
                tsa = swap[0] - 1
                tsb = swap[1] - 1
                vminswapback1 = swapsinglelist(vminlaylst1, tsa, tsb)
                ansleft = lmove(vminswapback1)
                templen = len(ansleft)
                indzero = vminswapback1.index(0)
                while templen < step:
                    ansleft += g_dict_ansleft[indzero][0]
                    ansleft += g_dict_ansleft[indzero][1]
                    templen += 2

                strans = ansleft + ansright
            else:
                #print("yessol,vmin1<vmin2")
                indexminlst1 = tpvlst1.index(vmin1)
                vminlaylst1 = swapedlst1[indexminlst1]
                if vmin1 == 0:
                    #print("vmin是0，ansright是a")
                    ansright = "a"
                else:
                    ansright = rmove(vminlaylst1)
                tsa = swap[0] - 1
                tsb = swap[1] - 1
                vminswapback1 = swapsinglelist(vminlaylst1, tsa, tsb)
                ansleft = lmove(vminswapback1)
                templen = len(ansleft)
                indzero = vminswapback1.index(0)
                while templen < step:
                    ansleft += g_dict_ansleft[indzero][0]
                    ansleft += g_dict_ansleft[indzero][1]
                    templen += 2

                strans = ansleft + ansright
        return  swapmove, strans

    sum = 0  # 找到0对应的1-9中的数字 zerofor
    for i in range(9):
        sum += olst[i]
    zerofor = 45 - sum

    dlist = [1, 2, 3, 4, 5, 6, 7, 8, 9]
    for i in range(9):
        if dlist[i] == zerofor:  # 1-9中把zerofor替换为0，目标与初始状态 相对应
            dlist[i] = 0
            break
    src = 0
    dest = 0
    for i in range(1, 9):
        fist = 0
        for j in range(0, i):
            if olst[j] > olst[i] and olst[i] != 0:
                fist += 1
        src += fist
    for i in range(1, 9):
        fist = 0
        for j in range(0, i):
            if dlist[j] > dlist[i] and dlist[i] != 0:
                fist += 1
        dest += fist

    if (src % 2) == (dest % 2):
        mys,ans=yessolve(olst,dlist,step,swap)
    else:
        mys,ans = nosolve(olst,dlist,step,swap)
    return mys, ans

# 提交赛题答案的接口，用token作为权限验证，提供队伍的IDteamid，以及答案operations。
# 接口会对操作合法性进行验证，成功时返回步数step和以毫秒计算的timeelapsed以及排名rank字段。
def submit(uuid, operation, myswap):
    url = 'http://47.102.118.1:8089/api/challenge/submit'
    datas = {
        "uuid": uuid,
        "teamid": 9,
        "token": "46d12dca-2c6b-4a0a-9fdd-92b1404e23a9",
        "answer": {
            "operations": operation,
            "swap": myswap
        }
    }
    data_json = json.dumps(datas)
    ret = json.loads(post(url, data_json))
    for key in ret.keys():
        print(key + " : ", ret[key])
# 挑战赛题的接口，用token作为权限验证，提供队伍的IDteamid，
# 返回赛题的图片数据img（以base64编码）、答题倒计时expire(秒)、
# 以及今日剩余挑战次数chanceleft、uuid为此次挑战的uuid（在/api/challenge/submit接口中使用)，一个uuid只能答一次题。
def challenge(uuid):
    url = 'http://47.102.118.1:8089/api/challenge/start/'+str(uuid)
    inputdata = {
        "teamid":9,
        "token":"46d12dca-2c6b-4a0a-9fdd-92b1404e23a9"
    }
    data_json = json.dumps(inputdata)
    ret = json.loads(post(url, data_json))
    uuid = ret["uuid"]
    data = ret["data"]
    chanceleft = ret["chanceleft"]
    img_base64 = data["img"]
    step = data["step"]
    swap = data["swap"]
    img = base64.b64decode(img_base64)
    with open("photo.jpg","wb") as fp:
        fp.write(img)
    img = cv2.imread("photo.jpg", cv2.IMREAD_GRAYSCALE)
    # 切分题目图片
    for row in range(3):
        for colum in range(3):
            sub = img[row * 300:(row + 1) * 300, colum * 300:(colum + 1) * 300]
            cv2.imwrite("subject" + str(row * 3 + colum + 1) + ".jpg", sub)
    zuhao, alist, disnumber = getlist()

    fllst = list(_flatten(alist))
    print("orilst",fllst)
    print("step",step)
    print("swap", swap)
    print("chanceleft",chanceleft)
    myswap,operations=solve(fllst,step,swap)
    print("operations",operations)
    print("myswap", myswap)
    submit(uuid,operations,myswap)
#函数结束

if __name__ == '__main__':
    # token = "46d12dca-2c6b-4a0a-9fdd-92b1404e23a9"
    # teamid = 9
    # #创建赛题
    # letter = 's'
    # exclude = 5
    # challenge = [
    #     [1, 2, 3],
    #     [0, 4, 6],
    #     [7, 8, 9]]
    # step = 1
    # swap = [1,2]
    # createQuestion(teamid, letter, exclude, challenge, step, swap, token)

    #获取今日的赛题
    #getChallenge()

    #获取赛题的解题记录
    # uuid = "faffa1cf-b298-452b-b469-d48f8ddf57a0"
    # getRecord(uuid)

    #从高到低返回排行榜
    # getRank()

    # 获取指定队伍的信息
    # getTeamdetail(teamid)

    # 获取还未通过的题目

    #notPass(teamid)

    dq1 = "q023456789.npz"
    destQ1 = np.load(dq1)
    destk1 = destQ1['k']
    destv1 = destQ1['v']
    destQdict1 = dict(zip(destk1, destv1))

    dq2 = "q103456789.npz"
    destQ2 = np.load(dq2)
    destk2 = destQ2['k']
    destv2 = destQ2['v']
    destQdict2 = dict(zip(destk2, destv2))

    dq3 = "q120456789.npz"
    destQ3 = np.load(dq3)
    destk3 = destQ3['k']
    destv3 = destQ3['v']
    destQdict3 = dict(zip(destk3, destv3))

    dq4 = "q123056789.npz"
    destQ4 = np.load(dq4)
    destk4 = destQ4['k']
    destv4 = destQ4['v']
    destQdict4 = dict(zip(destk4, destv4))

    dq5 = "q123406789.npz"
    destQ5 = np.load(dq5)
    destk5 = destQ5['k']
    destv5 = destQ5['v']
    destQdict5 = dict(zip(destk5, destv5))

    dq6 = "q123450789.npz"
    destQ6 = np.load(dq6)
    destk6 = destQ6['k']
    destv6 = destQ6['v']
    destQdict6 = dict(zip(destk6, destv6))

    dq7 = "q123456089.npz"
    destQ7 = np.load(dq7)
    destk7 = destQ7['k']
    destv7 = destQ7['v']
    destQdict7 = dict(zip(destk7, destv7))

    dq8 = "q123456709.npz"
    destQ8 = np.load(dq8)
    destk8 = destQ8['k']
    destv8 = destQ8['v']
    destQdict8 = dict(zip(destk8, destv8))

    dq9 = "q123456780.npz"
    destQ9 = np.load(dq9)
    destk9 = destQ9['k']
    destv9 = destQ9['v']
    destQdict9 = dict(zip(destk9, destv9))

    r1 = "n1.npz"
    rm1 = np.load(r1)
    rk1 = rm1['k']
    rv1 = rm1['v']
    rma1 = dict(zip(rk1, rv1))

    r2 = "n2.npz"
    rm2 = np.load(r2)
    rk2 = rm2['k']
    rv2 = rm2['v']
    rma2 = dict(zip(rk2, rv2))

    r3 = "n3.npz"
    rm3 = np.load(r3)
    rk3 = rm3['k']
    rv3 = rm3['v']
    rma3 = dict(zip(rk3, rv3))

    r4 = "n4.npz"
    rm4 = np.load(r4)
    rk4 = rm4['k']
    rv4 = rm4['v']
    rma4 = dict(zip(rk4, rv4))

    r5 = "n5.npz"
    rm5 = np.load(r5)
    rk5 = rm5['k']
    rv5 = rm5['v']
    rma5 = dict(zip(rk5, rv5))

    r6 = "n6.npz"
    rm6 = np.load(r6)
    rk6 = rm6['k']
    rv6 = rm6['v']
    rma6 = dict(zip(rk6, rv6))

    r7 = "n7.npz"
    rm7 = np.load(r7)
    rk7 = rm7['k']
    rv7 = rm7['v']
    rma7 = dict(zip(rk7, rv7))

    r8 = "n8.npz"
    rm8 = np.load(r8)
    rk8 = rm8['k']
    rv8 = rm8['v']
    rma8 = dict(zip(rk8, rv8))

    r9 = "n9.npz"
    rm9 = np.load(r9)
    rk9 = rm9['k']
    rv9 = rm9['v']
    rma9 = dict(zip(rk9, rv9))

    uuid ="09f6c2fd-670a-48ad-8e15-9d16aca564fb"
    challenge(uuid)
