#quicksort




#low = start index, high = end index
def quicksort(arr, low, high):
    if low < high:
        pi = partition(arr,low, high)
        quicksort(arr,low, pi-1)
        quicksort(arr,pi+1, high)
        


#takes last ele as pivot and places the pivot in its correct position in the sorted array
def partition(arr,low, high):
    pivot = arr[high]
    
    i = low-1
    
    for j in range(low,high):
        if arr[j]['Date'] == pivot['Date']:
            if arr[j]['Time'] < pivot['Time']:
                i +=1
                arr[i],arr[j] = arr[j],arr[i]
        elif arr[j]['Date'] < pivot['Date']:
            i+=1
            arr[i],arr[j] = arr[j],arr[i]
        else:
            pass
        # if a[j] < pivot:
        #     i+=1
        #     a[i],a[j] = a[j], a[i]
    arr[i+1],arr[high] = arr[high],arr[i+1]
    return (i+1)


if __name__ == '__main__':
    array = [
        {'MessageID': 1, 'MESSAGE': b'\xeb;\xbeX\x8f\xa9\x17', 'Date': '12/11/2021', 'Time': '23:39', 'UserID': 1, 'RoomID': 1, 'USERNAME': 'admin', 'ROOM': '#General'},
        {'MessageID': 2, 'MESSAGE': b"\xa0\xd4P|J/\xce\xd7", 'Date': '12/11/2021', 'Time': '23:38', 'UserID': 1, 'RoomID': 1, 'USERNAME': 'admin', 'ROOM': '#General'},
        {'MessageID': 3, 'MESSAGE': b'\x86\xb7\xbe3\x96\xe3\x12', 'Date': '13/11/2021', 'Time': '22:58', 'UserID': 2, 'RoomID': 1, 'USERNAME': 'test', 'ROOM': '#General'}, 
        {'MessageID': 4, 'MESSAGE': b"\xa9\x8d\x8d\x92\xdb\xc2\xdb", 'Date': '13/11/2021', 'Time': '22:59', 'UserID': 3, 'RoomID': 1, 'USERNAME': 'testuser', 'ROOM': '#General'}, 
        {'MessageID': 5, 'MESSAGE': b'fX\x98u)\xd8\xe5\xb2\xa6\x98', 'Date': '13/11/2021', 'Time': '23:42', 'UserID': 3, 'RoomID': 1, 'USERNAME': 'testuser', 'ROOM': '#General'}
       ]

    quicksort(array,0,len(array)-1)
    for each in array:
        print(each)
    