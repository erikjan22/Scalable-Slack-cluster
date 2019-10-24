import yaml

def set_workers(file_name, workers):
    with open(file_name) as f:
        list_doc = yaml.load(f)
        parameters = list_doc['parameters']
        node_count = parameters['node_count']
        
        #return node_count

        list_doc['parameters']['node_count']['num_workers'] = workers

    with open(file_name, 'w') as f:
        yaml.dump(list_doc, f)
    
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

c = set_workers('Heat_v6_test.yml', 3)
print(c)

# Get the floating IP from the heat template 
