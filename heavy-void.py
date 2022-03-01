
def get_value_int(disk,pos,size, name = None, debugg = False):
    # get the value in base10 from the disk (little endian) 
    disk.read(1)
    disk.seek(pos)
    data = disk.read(size)
    int_value = int.from_bytes(data, 'little')
    if debugg:
        if name is None:
            print(f'value at position {pos}: {" ".join("{:02X}".format(c) for c in data)} ')
        else:
            print(f'value {name} at position {pos}: {" ".join("{:02X}".format(c) for c in data)} ')
    return int_value

    


def get_size_sector(disk, debugg = False):
    int_value = get_value_int(disk, 11, 2, 'size sector')
    if debugg:
        print(f'size segment: {int_value}')
    return int_value

def get_size_cluster(disk, debugg = False):
    int_value = get_value_int(disk, 13, 1, 'size cluster') 
    size_sector = get_size_sector(disk)
    size_cluster = size_sector * int_value
    if debugg:
        print(f'size cluster: {size_cluster}')
    return size_cluster

def get_loc_start_fat(disk, debbug = False):
    int_value = get_value_int(disk, 14, 2, ' loc end fat')
    loc_end_fat = int_value * get_size_sector(disk)
    if debbug:
        print(f'location end fat: {loc_end_fat}')
    return loc_end_fat

def get_n_of_fat(disk, debugg = False):
    int_value = get_value_int(disk, 16, 1, 'n of fat')
    if debugg:
        print(f'number of fat: {int_value}')
    return int_value

def get_size_fat(disk, debugg = False):
    int_value = get_value_int(disk, 36, 4, 'size fat')
    size_fat = int_value * get_size_sector(disk)
    if debugg:
        print(f'size fat: {size_fat}')
    return size_fat

def get_loc_fat1(disk, debugg = False):
    loc_fat1 =  get_loc_start_fat(disk)
    if debugg:
        print(f'location fat1: {loc_fat1} (sector: {loc_fat1//get_size_sector(disk)}, cluster: {loc_fat1//get_size_cluster(disk)})')
    return loc_fat1

def get_loc_fat2(disk, debugg = False):
    loc_fat2 =  get_loc_start_fat(disk) + (get_size_fat(disk))
    if debugg:
        print(f'location fat2: {loc_fat2} (sector: {loc_fat2//get_size_sector(disk)}, cluster: {loc_fat2//get_size_cluster(disk)})')
    return loc_fat2

def get_loc_root_directory(disk, debbug = False):
    loc_root_dir =  get_loc_start_fat(disk) + (2*get_size_fat(disk))
    if debbug:
        print(f'location root directory: {loc_root_dir} (sector: {loc_root_dir//get_size_sector(disk)}, cluster: {loc_root_dir//get_size_cluster(disk)})')
    return loc_root_dir

def fill_with_void(path, secure = False, both_FAT = False, debbug = False):
    #fill the disk with bad cluster

    with open(path, 'rb') as disk:
        loc_fat1 = get_loc_fat1(disk, debugg=debbug)
        size_fat = get_size_fat(disk, debugg=debbug)
        size_sector = get_size_sector(disk, debugg=debbug)
      
    if secure:
        stop = True
    if both_FAT:
        n_sector_in_fat  =   size_fat//size_sector*2
    else:
        n_sector_in_fat  =   size_fat//size_sector

    for i in range(n_sector_in_fat): #try with 3:
    #iterate in all the fat's sectors
        with open(path, 'rb') as disk:
            disk.read(1)
            disk.seek(i*size_sector + loc_fat1)
            data = disk.read(size_sector)
        data = bytearray(data)
        for n in range(len(data)//4):
            part_data = data[n*4:(n+1)*4]

            if int.from_bytes(part_data, 'little') == 0:
                data[n*4:(n+1)*4] = 0xf7, 0xff, 0xff, 0x0f
            elif secure:
                if int.from_bytes(part_data, 'little') == 268435440:
                    #security if go too far
                    if stop:
                        stop= False
                        if debbug:
                            print('FAT1 finded')
                    else:
                        stop = True
                        if debbug:
                            print('FAT2 reached')
                        break
                if not stop:
                    break
        with open(path, 'wb') as disk:
            disk.seek(i*size_sector + loc_fat1)
            disk.write(data)
        if debbug:
            with open(path, 'rb') as disk:
                disk.read(1)
                disk.seek(i*size_sector + loc_fat1)
                data = disk.read(size_sector)
                hex_data = " ".join("{:02X}".format(c) for c in data)
            print(hex_data)
        print(f' Filling: {i*100//n_sector_in_fat + 1}%\033[A')
    print()


def quick_clean_void(path, debugg = False):
    #copy the untouched FAT2 in the FAT1
    with open(path, 'rb') as disk:
        loc_fat1 = get_loc_fat1(disk, debugg=debugg)
        size_fat = get_size_fat(disk, debugg=debugg)
        size_sector = get_size_sector(disk, debugg=debugg)


    n_sector_in_fat  =   size_fat//size_sector
    for i in range(n_sector_in_fat):
        with open(path, 'rb') as disk:
            disk.read(1)
            disk.seek(i*size_sector + loc_fat1 + size_fat)
            data = disk.read(size_sector)
        
        with open(path, 'wb') as disk:
                disk.seek(i*size_sector + loc_fat1)
                disk.write(data)
        print(f' Cleaning: {i*100//n_sector_in_fat + 1}%\033[A')
    print()

def clean_void(path, debugg = False):
    #remove all corrupted cluster from the FAT1 and FAT2
    with open(path, 'rb') as disk:
        loc_fat1 = get_loc_fat1(disk, debugg=debugg)
        size_fat = get_size_fat(disk, debugg=debugg)
        size_sector = get_size_sector(disk, debugg=debugg)

    
    test = 0
    n_sector_in_fat  =   size_fat//size_sector*2
    for i in range(n_sector_in_fat):
        with open(path, 'rb') as disk:
            disk.read(1)
            disk.seek(i*size_sector + loc_fat1)
            data = disk.read(size_sector)
        data = bytearray(data)
        for n in range(len(data)//4):
            part_data = data[n*4:(n+1)*4]
            if int.from_bytes(part_data, 'little') == 268435447:
                data[n*4:(n+1)*4] = 0x0, 0x0, 0x0, 0x0
                test += 1
        with open(path, 'wb') as disk:
                disk.seek(i*size_sector + loc_fat1)
                disk.write(data)
        print(test)
        print(f' Cleaning: {i*100//n_sector_in_fat + 1}%\033[A\033[A')
    print()
    print()
if __name__ == '__main__':
    #/dev/sdb1
    path = "/dev/sdc1"
    fill_with_void(path)
    #quick_clean_void(path)
    
