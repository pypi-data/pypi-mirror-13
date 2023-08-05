
#定义数组list



def jiazu(dai):#自定义函数
        for mei_dai in dai:#如果目标标识符在dai中，那么继续执行
            if isinstance(mei_dai,list):#如果目标标识符是一个数组（list），那么继续执行自定义函数jiazu
                jiazu(mei_dai)#执行自定义函数（嵌套）
            else:
                print(mei_dai)#否者，不是个数组（list）那么这行打印目标标识符（就是数组中的具体值）
