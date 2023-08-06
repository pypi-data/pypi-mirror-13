def get_data(file):
    with open(file) as myfile:
        Data = {}
        for line in myfile.readlines()[1:]: # 
            line = line.split('\t')
            #print line[2]
            Data[line[0]] = [int(line[3]), str(line[2]), str(line[-1])]
    return Data

def top_x(x, Data):
    Data = sorted(Data.items(), key=operator.itemgetter(1), reverse=True)
    for i in range(x):
        print Data[i][0]#, Data[i][1][1]

def range_x_citations(Data, Range):
    #Data = sorted(Data.items(), key=operator.itemgetter(1), reverse=True)
    results = [Data[x][0] for x in range(len(Data)) if (Data[x][1][0] >= Range[0] and Data[x][1][0] < Range[1])]
    return results
    
def range_x_year(Data, Range):
    #Exception Handling
    results = [Data[x][0] for x in range(len(Data)) if (Data[x][1][1] >= Range[0] and Data[x][1][1] <= Range[1])]
    return results

def gen(x):
  i = 1
  while True:
    yield x+i*2
    i += 1
    
def gen_max(x, maximum):
  i = 1
  while x < maximum:
    x = x+i*2
    yield x
    i += 1
  print "test"
  raise StopIteration()

  if __name__ = "__main__":
  	
