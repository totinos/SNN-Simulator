import sys
import numpy as np
from optparse import OptionParser


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


# Wrapper function for the add_noise function (operates on a set of shapes)
def noisify_set(shape_set, num_noise_bits):
    noisy_shape_set = []
    for shape in shape_set:
        noisy_shape = add_noise(shape, num_noise_bits)
        noisy_shape_set.append(noisy_shape)
    return noisy_shape_set


# Assumes base_shapes and base_labels will have the same length
def generate_random_shape_set(base_shapes, base_labels, num_shapes):
    base_len = len(base_shapes)
    shape_set = []*num_shapes
    label_set = []*num_shapes
    for i in range(num_shapes):
        shape_index = np.random.randint(base_len)
        new_shape = np.copy(base_shapes[shape_index])
        label_set.append(base_labels[shape_index])
        shape_set.append(new_shape)
    return shape_set, label_set


def generate_single_shape_set(shape, label, num_shapes):
    shape_set = []*num_shapes
    label_set = []*num_shapes
    for i in range(num_shapes):
        new_shape = np.copy(shape)
        label_set.append(label)
        shape_set.append(new_shape)
    return shape_set, label_set

def merge_shape_set(shapes_1, labels_1, shapes_2, labels_2):
    len1 = len(shapes_1)
    len2 = len(shapes_2)

    if len1 == 0 and len2 != 0:
        return shapes_2, labels_2
    elif len2 == 0:
        return shapes_1, labels_1

    total_len = len1 + len2
    idx1, idx2 = 0, 0
    shape_set = []
    label_set = []
    for i in range(total_len):

        # Determine which set to get shape from
        if idx1 >= len1:
            shape = 1
        elif idx2 >= len2:
            shape = 0
        else:
            shape = np.random.randint(2)

        # Append shape from appropriate set
        if shape == 0:
            shape_set.append(shapes_1[idx1])
            label_set.append(labels_1[idx1])
            idx1 += 1
        else:
            shape_set.append(shapes_2[idx2])
            label_set.append(labels_2[idx2])
            idx2 += 1
    return shape_set, label_set

    

# TODO --> UNTESTED
def flip_shape_set_vertically(shape_set):
    flipped_set = []
    for shape in shape_set:
        flipped_shape = np.flip(shape, 1)
        flipped_set.append(flipped_shape)
    return flipped_set



# Assumes that the shapes being read were printed without padded zeros
# Assumes that the dim of the shapes is 5x5
def read_shapes(directory):

    label_set = []
    shape_set = []

    fname = "{}/shape_labels.txt".format(directory)
    with open(fname, "r") as f:
        lines = f.readlines()
    for line in lines:
        line = line.replace('\n', '')
        label_set.append(line)

    num_shapes = len(label_set)
    for shape_index in range(num_shapes):
        fname = "{}/shape_{:03d}.txt".format(directory, shape_index)
        with open(fname, "r") as f:
            lines = f.readlines()
        shape = np.zeros((rows, cols), dtype="int32")
        for i in range(len(lines)):
            line = lines[i].split(" ")
            for j in range(len(line)):
                shape[i][j] = line[j]
        shape_set.append(shape)

    return shape_set, label_set


def write_shapes(directory="shapes", shape_set=[], label_set=[], include_zeros=False, cycle_gap=10):

    fname = "{}/shape_labels.txt".format(directory)
    with open(fname, "w") as f:
        for label in label_set:
            f.write("{}\n".format(label))

    for shape_index in range(len(shape_set)):
        fname = "{}/shape_{:03d}.txt".format(directory, shape_index)
        with open(fname, "w") as f:

            # Write the shapes to their respective files
            for i in range(rows):
                for j in range(cols):
                    if j != 0:
                        f.write(" ")
                    f.write("{}".format(shape_set[shape_index][i][j]))
                    if include_zeros == True:
                        f.write(" 0")

                # Print some zeros to appease the simulator
                if include_zeros == True:
                    for j in range(cycle_gap):
                        f.write(" 0")
                if i != (rows-1):
                    f.write("\n")
    return


if __name__ == '__main__':

    #############################################
    #                                           #
    #  Check the command line arguments         #
    #                                           #
    #############################################
    #if len(sys.argv) == 3:
    #    infile = str(sys.argv[1])
    #    #outfile = str(sys.argv[2])
    #    cycle_gap = int(sys.argv[2])
    #else:
    #    print('Usage: python input_data_gen.py <input file> <cycle_gap>')
    #    exit(1)

    
    parser = OptionParser()
    parser.add_option("--file", dest="infile", help="Input shape file", metavar="INPUT_FILE")
    parser.add_option("--shape", dest="gen_shape", help="Shape to generate ('T', 'S', 'C', or 'ALL')", metavar="SHAPE");
    parser.add_option("--num_noise_bits", dest="num_noise_bits", help="Number of noise bits to insert", metavar="NUM_NOISE_BITS");
    (options, args) = parser.parse_args()
    if not options.infile:
        parser.error("Filename not given")


    #############################################
    #                                           #
    #  Read the file into a list of lines       #
    #                                           #
    #############################################
    with open(options.infile, 'r') as f:
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

    # num_noise_bits = 3
    # # print("length:", len(shapes))
    # starting_len = len(shapes)
    # # print(shapes)
    # # print_shapes(shapes)

    # for i in range(97):
    #     shape_index = np.random.randint(starting_len)
    #     # print("index of shape:", shape_index)
    #     new_shape = add_noise(shapes[shape_index], num_noise_bits)
    #     labels.append(labels[shape_index])
    #     # print(new_shape)
    #     shapes.append(new_shape)
    #     # print_shapes(shapes)
    # print_shapes(shapes)
        

    # ss1, ls1 = generate_single_shape_set(shapes[0], 'T', 100)
    # ss2, ls2 = generate_single_shape_set(shapes[1], 'S', 100)
    # ss3, ls3 = generate_single_shape_set(shapes[2], 'C', 100)
    # ss4, ls4 = merge_shape_set(ss1, ls1, ss2, ls2)
    # ss5, ls5 = merge_shape_set(ss3, ls3, ss4, ls4)
    # print_shapes(ss5)
    # write_shapes("mixed", ss5, ls5)

    # new_shapes, new_labels = read_shapes("mixed")
    # noisy_shapes = noisify_set(new_shapes, 0)
    # print_shapes(noisy_shapes)
    # write_shapes("noisy_shapes", noisy_shapes, new_labels, include_zeros=True)
    # exit()


    # TODO --> Fix this assumption:
    # ASSUMES THE FIRST SHAPE WILL BE A TRIANGLE
    # shape_set, label_set = generate_single_shape_set(shapes[2], 'C', 100)
    # write_shapes("crosses", shape_set, label_set)
    
    # new_shapes, new_labels = read_shapes("crosses")
    # noisy_shapes = noisify_set(new_shapes, 6)
    # print_shapes(noisy_shapes)
    # write_shapes("noisy_shapes", noisy_shapes, new_labels, include_zeros=True)

    # shape_set, label_set = generate_random_shape_set(shapes, labels, 100)
    # write_shapes("shapes", shape_set, label_set)
    # new_shapes, new_labels = read_shapes("shapes")

    # noisy_shapes = noisify_set(new_shapes, 2)
    # write_shapes("noisy_shapes", noisy_shapes, new_labels, include_zeros=True)
    # ns, nl = read_shapes("noisy_shapes")
    # print_shapes(ns)
    # print(nl)

    if options.gen_shape == 'T':
        gen_shape = "triangles"
    elif options.gen_shape == 'S':
        gen_shape = "squares"
    elif options.gen_shape == 'C':
        gen_shape = "crosses"
    elif options.gen_shape == "ALL":
        gen_shape = "mixed"

    new_shapes, new_labels = read_shapes(gen_shape)
    noisy_shapes = noisify_set(new_shapes, int(options.num_noise_bits))
    print_shapes(noisy_shapes)
    write_shapes("noisy_shapes", noisy_shapes, new_labels, include_zeros=True)

    exit()
