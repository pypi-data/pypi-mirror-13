'''
 # 说明：多层嵌套，利用递归找出来。提供了一个名为printMovieList()的函数，这函数的作用是打印列表，其中有可能包含（也可能不包含）嵌套列表。
 # 创建人：Tavis  第二版。增加level参数来控制缩进，不用重复再创建一个函数。
 # 创建时间：2015/12/26 12:03
'''
# coding=UTF-8

movies = ["The Holy Grail", 1975, "Terry Jones", 91,
          ["Graham Chapman", ["Michael Palin", "John Cleese", "Eric Idle", "Terry Jones"]]]  # 多层嵌套的列表


# 打印出来还是有列表存在，无法满足打印出所有列表中的单元元素
# for eachMovie in movies:
#     print(eachMovie)


def printMovieList(theList, level):
    """
    创建一个函数，利用递归来实现找出多层嵌套。所指定的列表中的每个数据项会（递归地）输出到屏幕上，各数据项各占一行。level用来在遇到嵌套列表时插入制表符。
    :param theList,level:
    :return:
    """
    for eachItem in theList:
        # 判断子项是否还是list，若还是list，则循环调用该函数
        if isinstance(eachItem, list):
            printMovieList(eachItem,level+1)#增加level参数的目的就是为了能控制嵌套输出。每次处理一个嵌套列表时，都需要将level的值增1.
        else:
            for tabStop in range(level):  # 使用level的值来控制使用多少个制表符。
                print('\t', end='')  # 每一层缩进显示一个Tab制表符。

# printMovieList(movies)
