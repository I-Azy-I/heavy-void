
def get_value_int(disk,pos,size, name = None):
    disk.read(1)
    disk.seek(pos)
    data = disk.read(size)
    int_value = int.from_bytes(data, 'little')
    
    if name is None:
        print(f'value at position {pos}: {" ".join("{:02X}".format(c) for c in data)} ')
    else:
        print(f'value {name} at position {pos}: {" ".join("{:02X}".format(c) for c in data)} ')

    return int_value

    


def get_size_sector(disk):
    int_value = get_value_int(disk, 11, 2, 'size sector')
    print(f'size segment: {int_value}')
    return int_value

def get_size_cluster(disk):
    int_value = get_value_int(disk, 13, 1, 'size cluster') 
    size_sector = get_size_sector(disk)
    size_cluster = size_sector * int_value
    print(f'size cluster: {size_cluster}')
    return size_cluster

def get_loc_start_fat(disk):
    int_value = get_value_int(disk, 14, 2, ' loc end fat')
    loc_end_fat = int_value * get_size_sector(disk)
    print(f'location end fat: {loc_end_fat}')
    return loc_end_fat

def get_n_of_fat(disk):
    int_value = get_value_int(disk, 16, 1, 'n of fat')
    print(f'number of fat: {int_value}')
    return int_value

def get_size_fat(disk):
    int_value = get_value_int(disk, 36, 4, 'size fat')
    size_fat = int_value * get_size_sector(disk)
    print(f'size fat: {size_fat}')
    return size_fat

def get_loc_fat1(disk):
    loc_fat1 =  get_loc_start_fat(disk)
    print(f'location fat1: {loc_fat1} (sector: {loc_fat1//get_size_sector(disk)}, cluster: {loc_fat1//get_size_cluster(disk)})')
    return loc_fat1

def get_loc_fat2(disk):
    loc_fat2 =  get_loc_start_fat(disk) + (get_size_fat(disk))
    print(f'location fat2: {loc_fat2} (sector: {loc_fat2//get_size_sector(disk)}, cluster: {loc_fat2//get_size_cluster(disk)})')
    return loc_fat2

def get_loc_root_directory(disk):
    loc_root_dir =  get_loc_start_fat(disk) + (2*get_size_fat(disk))
    print(f'location root directory: {loc_root_dir} (sector: {loc_root_dir//get_size_sector(disk)}, cluster: {loc_root_dir//get_size_cluster(disk)})')
    return loc_root_dir

def fill_with_void(path):

    with open(path, 'rb') as disk:
        loc_fat1 = get_loc_fat1(disk)
        size_fat = get_size_fat(disk)
        size_sector = get_size_sector(disk)
      
        
    
    

    #for i in range((size_fat/4 - 4) #try with 3:
    print(size_fat)
    stop = True
    for i in range(1):
        with open(path, 'rb') as disk:
            disk.read(1)
            disk.seek((i+1)*loc_fat1)
            data = disk.read(size_sector)
        data = bytearray(data)
        for n in range(len(data)//4):
            part_data = data[n*4:(n+1)*4]
            if int.from_bytes(part_data, 'little') == 0:
                data[n*4:(n+1)*4] = 0xff, 0xff, 0xff, 0x0f
            elif int.from_bytes(part_data, 'little') == 16777208:
                if stop:
                    stop= False
                    print('FAT1 finded')
                else:
                    stop = True
                    print('FAT2 reached')
                    break
            if not stop:
                break
        with open(path, 'wb') as disk:
            disk.seek((i+1)*loc_fat1)
            disk.write(data)
        with open(path, 'rb') as disk:
            disk.read(1)
            disk.seek((i+1)*loc_fat1)
            data = disk.read(size_sector)
            hex_data = " ".join("{:02X}".format(c) for c in data)
        print(hex_data)
	

if __name__ == '__main__':
    path = "/dev/sdb1"
    fill_with_void(path)
#with open(path, 'rb') as disk:
    #size_sector = get_size_sector(disk)
    #size_cluster = get_size_cluster(disk)
    #loc_end_fat = get_loc_start_fat(disk)
    #n_of_fat = get_n_of_fat(disk)
    #size_fat = get_size_fat(disk)
    #loc_fat1 = get_loc_fat1(disk)
    #loc_fat2 = get_loc_fat2(disk)
    #loc_root_dir = get_loc_root_directory(disk)
#
    #disk.read(1)
    #print(loc_fat1)
    #disk.seek(loc_fat1)
    #data = disk.read(16)
    #hex_data = " ".join("{:02X}".format(c) for c in data)
    #print(hex_data)
   ## int_value = int.from_bytes(data, 'little')
   # print(int_value)
   # print(int(data.decode('hex'), 16))
    
    #data = bytearray(disk.read(512))
    #while (data := disk.read(16)):
    #    hex_data = " ".join("{:02X}".format(c) for c in data)
    #    print(hex_data) 
    #    i += 1
    #    if i == 32
    #        print('==='*16)
    #    if i == 64:
    #        break

