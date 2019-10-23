def count_worker():
    num = 0
    f = open('../../../etc/ansible/hosts')
    for i in f:
        if i.strip() == "[sparkworker]":
            num += 1
        else:
            continue
    f.close()
    return num

c = count_worker()
print(c)

# Get the floating IP from the heat template 
