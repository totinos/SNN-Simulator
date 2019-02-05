import sys
import numpy as np

if __name__ == '__main__':

    #############################################
    #                                           #
    #  Check the command line arguments         #
    #                                           #
    #############################################
    if len(sys.argv) == 4:
        infile = str(sys.argv[1])
        outfile = str(sys.argv[2])
        cycle_gap = int(sys.argv[3])
    else:
        print('Usage: python input_data_gen.py <input file> <cycle_gap>')
        exit(1)

    #############################################
    #                                           #
    #  Read the file into a list of lines       #
    #                                           #
    #############################################
    with open(infile, 'r') as f:
        lines = f.readlines()

    # Number of rows and columns of each image
    rows = 5
    cols = 5

    # To store images and labels
    labels = []
    shapes = []

    # Variables to help with parsing
    label_char = ''
    num_images = 0
    shape_index = 0

    #############################################
    #                                           #
    #  Parse the file and extract the data      #
    #                                           #
    #############################################
    for line in lines:

        # The first line gives the total number of images
        if line == lines[0]:
            num_images = int(lines[0])
            print('num_images:', num_images)
            shapes = np.zeros((num_images, rows, cols))

        # The line contains label information
        elif line[0] == '#':
            num_shapes = int(line[2:]) # IS THIS USEFUL AT ALL?
            if line[1] == 'T':
                label_char = 'T'
            elif line[1] == 'S':
                label_char = 'S'
            elif line[1] == 'D':
                label_char = 'D'
            elif line[1] == 'C':
                label_char = 'C'

        # The line contains shape information
        else:
            line = line.replace('\n', '')
            line = line.split(' ')
            for i in range(len(line)):
                for j in range(len(line[i])):
                    shapes[shape_index][i][j] = int(line[i][j])
            labels.append(label_char)
            shape_index += 1

    #############################################
    #                                           #
    #  Shuffle the order of images and labels   #
    #                                           #
    #############################################

    # TODO --> this...

    #############################################
    #                                           #
    #  Reverse the order of input spikes to     #
    #  reflect visual representation in time -  #
    #  Insert the desired cycle gap as well     #
    #                                           #
    #############################################
    # Reverse the order of input spikes and insert cycle gap
    fires = np.zeros((num_images, rows, cols*cycle_gap), dtype='int')
    print(fires.shape)
    shapes = np.flip(shapes, 2)
    for i in range(len(shapes)):
        for j in range(len(shapes[i])):
            for k in range(len(shapes[i][j])):
                # print('i, j, k:', i, j, k)
                fires[i][j][k*cycle_gap] = shapes[i][j][k]

    #############################################
    #                                           #
    #  Write the reformatted data to a file     #
    #                                           #
    #############################################
    with open(outfile, 'w') as of:
        
        # Output all of the first rows first
        for j in range(rows):
            for i in range(len(fires)):
                for k in range(len(fires[i][j])):
                    of.write('{} '.format(fires[i][j][k]))
                    print(fires[i][j][k], end='')
                print(' ', end='')
            print('')
            of.write('\n')


    # print(shapes)
    # print(fires)
    # print()
    # print(labels)
    