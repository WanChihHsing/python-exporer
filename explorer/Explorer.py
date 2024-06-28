# 列表，相当于java的list
py_list = [1, 2, 3, 4, 5]

for py in py_list:
    print(py)

# 列表推导式
py_list = [i for i in range(10)]

for py in py_list:
    print(py)

# 列表推导式
py_list = [i for i in range(10) if i % 2 == 0]

for py in py_list:
    print(py)

# 字典，相当于java的map
py_dict = {
    'name': '张三',
    'age': 18
}

print(py_dict)

# 字典推导式
py_dict = {i: i * 2 for i in range(10)}

print(py_dict)

# 集合，相当于java的set
py_set = {1, 2, 3, 4, 5}

print(py_set)

# 集合推导式
py_set = {i for i in range(10)}

print(py_set)

# 元组，相当于java的数组
py_tuple = (1, 2, 3, 4, 5)

print(py_tuple)

# 元组推导式
py_tuple = tuple(i for i in range(10))

print(py_tuple)

# 切片

py_list = [1, 2, 3, 4, 5]

print(py_list[0:2])

print(py_list[0:5:2])

print(py_list[::2])

print(py_list[::-1])

# 切片

py_tuple = (1, 2, 3, 4, 5)

print(py_tuple[0:2])

print(py_tuple[0:5:2])

print(py_tuple[::2])

print(py_tuple[::-1])

# 切片

py_str = 'hello world'

print(py_str[0:2])

print(py_str[0:5:2])