
"""这是一个嵌套函数"""
def print_qiantao(every,level):
    """这是一个递归函数，用于显示出一个数组重嵌套的多个数组重的每个元素"""
    for everyone in every:
        if isinstance(everyone,list):
            print_qiantao(everyone,level+1)
        else:
            for tab_stop in range(level):
                print("\t",end='')
            print(everyone)
