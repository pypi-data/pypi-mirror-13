'''定义函数print_lol(),用于迭代输出列表中的所有元数据'''
import sys

def print_lol(the_list,indent=False,level=0,fn=sys.stdout):
    """This function takes one positinal argument called "the_list",
which is any Python list (of - possibly - nested lists).
Each data item in the provided list is (recursively) printed to the creen on it`s own line"""

    for each_item in the_list:
        if isinstance(each_item,list):
            print_lol(each_item,indent,level+1,fn)
        else:
            if indent:
                for tab_stop in range(level):
                    print("\t",end='',file=fn) 
            print(each_item,file=fn)

'''先定义两个空列表'''
man = []
other = []

'''将源文件sketch.txt中的每行数据，按不同的人man和other man说的话，分别存到列表man和other中'''
try:
	data = open('sketch.txt')
	for each_line in data:
		try:
			(role,line_spoken) = each_line.split(':',1)
			line_spoken = line_spoken.strip()
			if role == 'Man':
				man.append(line_spoken)
			elif role == 'Other Man':
				other.append(line_spoken)
		except ValueError:
			pass
	data.close()
	
except IOError:
        print('The datafile is Missing!')

'''创建两个文件man_data.txt和other_data.txt，将文件对象man和other中的数据经过函数print_lol()格式化后写入到两个txt文件；
程序通过with语句会对文件对象做自动close处理；程序会对报的IO异常会做屏幕输出，以便定位问题'''

try:
        with open('man_data.txt','w') as man_file,open('other_data.txt','w') as other_file:
                print_lol(man,fn=man_file)
                print_lol(other,fn=other_file)
except IOError as err:
	print('File Error :' + str(err))
