import dataloader2
import sys
import termcolor as tc

if len(sys.argv) != 2:
    print('%d arguments' % len(sys.argv))
    sys.exit(-1)
testDataSet = dataloader2.read_data_sets(sys.argv[1])
print

#train
print tc.colored('train:', 'yellow')
print('%d data points' % (testDataSet.train.num_examples))
print('features:')
for features in testDataSet.train.features:
    print('\t %s: %s' % (features, (testDataSet.train.features[features].shape),))
print('labels:')
for labels in testDataSet.train.labels:
     print('\t %s: %s' % (labels, (testDataSet.train.labels[labels].shape),))

#dev
print tc.colored('\ndev:', 'yellow')
print('%d data points' % (testDataSet.dev.num_examples))
print('features:')
for features in testDataSet.dev.features:
    print('\t %s: %s' % (features, (testDataSet.dev.features[features].shape),))
print('labels:')
for labels in testDataSet.dev.labels:
     print('\t %s: %s' % (labels, (testDataSet.dev.labels[labels].shape),))

#test
print tc.colored('\ntest:', 'yellow')
print('%d data points' % (testDataSet.test.num_examples))
print('features:')
for features in testDataSet.test.features:
    print('\t %s: %s' % (features, (testDataSet.test.features[features].shape),))
print('labels:')
for labels in testDataSet.train.labels:
     print('\t %s: %s' % (labels, (testDataSet.dev.labels[labels].shape),))
