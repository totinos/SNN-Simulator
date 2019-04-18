#!/bin/sh

# To keep track of the shapes and accuracy
count=0
num_correctly_identified=0
epochs=10

dir_name="../shape_recognition/noisy_shapes"
label_file="$dir_name/shape_labels.txt"
num_iterations=$epochs

num_shapes=0


while [ "$epochs" -ne 0 ]; do


    # Read each label and test the shape with the network
    while read line; do

        # Generate a new shape file name to test
        suffix="` printf -- '%03d' "$count" `"
        fname="$dir_name/shape_$suffix.txt"

        # Look at the last line of the file to see if a triangle was identified
        python sim_dev.py ../shape_recognition/net2.txt $fname > f
        result=`tail -1 f`
        rm -rf f

        if [ $result -eq "1" ]
        then
            # The classifier is correct if it was a triangle
            if [ $line == "T" ]
            then
                num_correctly_identified=`echo "$num_correctly_identified" + 1 | bc`
            else
                echo "Incorrectly classified: $count"
            fi
            
        else

            # The classifier is correct if it wasn't a triangle
            if [ $line != "T" ]
            then
                #((++num_correctly_identified))
                num_correctly_identified=`echo "$num_correctly_identified" + 1 | bc`
            else
                echo "Incorrectly classified: $count"
            fi
        fi

        # Increment the count variable
        count=`echo "$count" + 1 | bc`

    done < $label_file

    # Reset the shape counter and move to the next epoch
    echo ""
    num_shapes=$count
    count=0
    epochs=`echo "$epochs" - 1 | bc`
done

# Calculate the accuracy and print it to the screen
accuracy=`echo "$num_correctly_identified / $num_iterations" | bc -l`
echo "ACCURACY: $accuracy%"

say "DONE"
