"""定义一个递归函数"""
def printList(l,tabs):
    tabs += "\t";
    print(len(tabs));
    for cl in l:
        if isinstance(cl,list):
            printList(cl,tabs);
        else:
            print(tabs  + cl);


