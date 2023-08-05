#!/usr/bin/env python

##   dt_example_involving_csv_cleanup.py

##  This scripts illustrates the constructor options introduced in Version 3.2.4
##  in November 2015.  These options are:
##
##       csv_cleanup_needed
##  and
##
##       first_field_in_first_record
##
##  The comma separated values in some large econometrics datasets include
##  double-quoted strings with commas.  To deal with such CSV files, Version
##  3.2.4 incorporates a new function named 'cleanup_csv()'.  This function is
##  invoked when you set the construction option 'csv_cleanup_needed' to 1 as
##  shown below.

##  You may also want to note that I have used the constructor option
##
##            number_of_histogram_bins
##
##  In general, the larger a dataset, the smaller the smallest difference between any
##  two values for a numeric variable in relation to the overall range of values for
##  that variable. In such cases, the value used for the number of bins used for
##  estimating the probabilities could become much too large and slow down the
##  calculation of the decision tree.  You can get around that problem by explicitly
##  giving a value to the 'number_of_histogram_bins' parameter, as shown in the
##  following example.


import DecisionTree

#training_datafile = "try10.csv"
training_datafile = "try100.csv"
#training_datafile = "try1000.csv"
#training_datafile = "try20000.csv"
#training_datafile = "/home/kak/DecisionTree_data/Indraneel/NETS_IN2012_confidential.csv"

dt = DecisionTree.DecisionTree( training_datafile = training_datafile,
                                csv_class_column_index = 14,
                                csv_columns_for_features = [166,167,176,177,178],
                                entropy_threshold = 0.01,
                                max_depth_desired = 8,
                                symbolic_to_numeric_cardinality_threshold = 10,
                                number_of_histogram_bins = 100,
                              )
dt.get_training_data()
dt.calculate_first_order_probabilities()
dt.calculate_class_priors()
#   UNCOMMENT THE FOLLOWING LINE if you would like to see the training
#   data that was read from the disk file:
#dt.show_training_data()

root_node = dt.construct_decision_tree_classifier()

#   UNCOMMENT THE FOLLOWING LINE if you would like to see the decision
#   tree displayed in your terminal window:
print("\n\nThe Decision Tree:\n")
root_node.display_decision_tree("     ")

test_sample  = ['SALES90 = 1000000.0',
                'SALES91 = 500000.0',
                'SALES00 = 100000.0',
                'SALES01 = 20000.0',
                'SALES02 = 0.0']

# The rest of the script is for displaying the results:

classification = dt.classify(root_node, test_sample)

solution_path = classification['solution_path']
del classification['solution_path']
which_classes = list( classification.keys() )
which_classes = sorted(which_classes, key=lambda x: classification[x], reverse=True)
print("\nClassification:\n")
print("     "  + str.ljust("class name", 30) + "probability")    
print("     ----------                    -----------")
for which_class in which_classes:
    if which_class is not 'solution_path':
        print("     "  + str.ljust(which_class, 30) +  str(classification[which_class]))

print("\nSolution path in the decision tree: " + str(solution_path))
print("\nNumber of nodes created: " + str(root_node.how_many_nodes()))

