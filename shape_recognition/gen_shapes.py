import sys
import numpy as np


# Assumes that the shape is 2D and that there are more than one element in each dim
def print_shapes(shapes=[]):
    print("================")
    print("ARRAY OF SHAPES:")
    print("================")
    print()
    for index in range(len(shapes)):
        shape = shapes[index]
        rows = len(shape)
        cols = len(shape[0])
        for i in range(rows):

            # Print the index of the shape in the array
            if i == 2:
                print("{:03d} -- ".format(index), end="")
            else:
                print("       ", end="")

            # Print the row/col values
            for j in range(cols):
                print("{} ".format(shape[i][j]), end="")
            print()
        print()
    print("================")
    return


# Assumes that the shape is 2-dimensional and that there are more than one element in each dim
def add_noise(shape, num_noise_bits):
    new_shape = shape.copy()
    rows = len(new_shape)
    cols = len(new_shape[0])
    bits_changed = np.zeros((rows, cols), dtype='int32')
    for bit in range(num_noise_bits):

        # Choose a random bit that has not yet been flipped
        while True:
            index = np.random.randint(rows*cols)
            if bits_changed[index//rows][index%rows] == 0:
                bits_changed[index//rows][index%rows] = 1
                break

        # Flip the binary pixel to add "noise"
        if new_shape[index//rows][index%rows] == 1:
            new_shape[index//rows][index%rows] = 0
        else:
            new_shape[index//rows][index%rows] = 1

    return new_shape


if __name__ == '__main__':

    #############################################
    #                                           #
    #  Check the command line arguments         #
    #                                           #
    #############################################
    if len(sys.argv) == 3:
        infile = str(sys.argv[1])
        #outfile = str(sys.argv[2])
        cycle_gap = int(sys.argv[2])
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
            # shapes = [np.zeros((rows, cols), dtype='int32')]*num_images

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
            shape = np.zeros((rows, cols), dtype='int32')
            for i in range(len(line)):
                for j in range(len(line[i])):
                    shape[i][j] = int(line[i][j])
                    # shapes[shape_index][i][j] = int(line[i][j])
            print(shape)
            labels.append(label_char)
            shapes.append(shape)
            # print(shapes[shape_index])
            shape_index += 1

    #############################################
    #                                           #
    #  Shuffle the order of images and labels   #
    #                                           #
    #############################################

    # TODO --> this...


    #############################################
    #                                           #
    #  Add some shapes with noisy bits          #
    #                                           #
    #############################################


    # TODO --> Make the noise additions more modular/user friendly

    num_noise_bits = 1
    # print("length:", len(shapes))
    starting_len = len(shapes)
    # print(shapes)
    # print_shapes(shapes)

    for i in range(96):
        shape_index = np.random.randint(starting_len)
        # print("index of shape:", shape_index)
        new_shape = add_noise(shapes[shape_index], num_noise_bits)
        labels.append(labels[shape_index])
        # print(new_shape)
        shapes.append(new_shape)
        # print_shapes(shapes)
    print_shapes(shapes)
        



    #############################################
    #                                           #
    #  Reverse the order of input spikes to     #
    #  reflect visual representation in time -  #
    #  Insert the desired cycle gap as well     #
    #                                           #
    #############################################
    #fires = np.zeros((num_images, rows, cols+cycle_gap), dtype='int')
    # print(fires.shape)
    shapes = np.flip(shapes, 2)
    #fires[:, :, :shapes.shape[2]] = shapes

    # print(shapes)

    #############################################
    #                                           #
    #  Write the shapes to output files         #
    #                                           #
    #############################################

    label_outfile = "shape_labels.txt"
    with open(label_outfile, "w") as labels_of:

        # Put each of the shapes in a separate output file
        for shape_index in range(len(shapes)):

            # Format the name of each output shape file
            fout = "shapes/shape_{:03d}.txt".format(shape_index)
            with open(fout, "w") as of:

                # Write the shape (with columns of zeros inserted) to a file
                for i in range(rows):
                    for j in range(cols):
                        if j == 0:
                            of.write("{} 0".format(shapes[shape_index][i][j]))
                        else:
                            of.write(" {} 0".format(shapes[shape_index][i][j]))

                    # Print some zeros after the shape so the simulator doesn't get mad
                    for j in range(cycle_gap):
                        of.write(" 0")
                    if i != (rows-1):
                        of.write("\n")

            labels_of.write("{}\n".format(labels[shape_index]))
        # print(fout)
    exit()

    with open(outfile, 'w') as of:
        
        # Output all of the first rows first
        for j in range(rows):
            for i in range(len(fires)):
                for k in range(len(fires[i][j])):
                    of.write('{} '.format(fires[i][j][k]))
            #         print(fires[i][j][k], end='')
            #     print(' ', end='')
            # print('')
            of.write('\n')


    # print(shapes[3])
    # print(fires)
    # print()
    # print(labels)
