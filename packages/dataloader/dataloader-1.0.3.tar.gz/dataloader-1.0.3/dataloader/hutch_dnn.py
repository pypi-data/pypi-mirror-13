import tensorflow as tf
import argparse
import dataloader.dataloader


parser = argparse.ArgumentParser()
parser.add_argument("-data_dir", metavar ="DATA_DIR", type=str)
parser.add_argument("-nlayers", type=int, metavar="NUM_HIDDEN_LAYERS")
parser.add_argument("-epochs", metavar="EPOCHS", type=int)
parser.add_argument("-learnrate", type=float, metavar="LEARNRATE")
parser.add_argument("-decay", nargs=3, type=float,
                    metavar=("GLOBAL_STEP",
                             "DECAY_STEPS",
                             "DECAY_RATE"))
parser.add_argument("-nunbreakits", type=int, metavar="NUM_HIDDEN_UNITS")
parser.add_argument("-keepprob", type=float, metavar="KEEP_PROB")
parser.add_argument("-mb", type=int, metavar="MINIBATCH_SIZE")

model_class = parser.add_mutually_exclusive_group()
model_class.add_argument("-class", "--classification", action="store_true")
model_class.add_argument("-reg"  , "--regression", action="store_true")

act_func = parser.add_mutually_exclusive_group()
act_func.add_argument("-sig", "--sigmoid", action="store_true")
act_func.add_argument("-tanh", "--tanh", action="store_true")
act_func.add_argument("-relu", "--relu", action="store_true")
act_func.add_argument("-relu6", "--relu6", action="store_true")
act_func.add_argument("-softplus", "--softplus", action="store_true")

optimizer = parser.add_mutually_exclusive_group()
optimizer.add_argument("-adam", "--adam", action="store_true")
optimizer.add_argument("-ada", "--ada", action="store_true")
optimizer.add_argument("-grad", "--grad", action="store_true")
optimizer.add_argument("-mom", "--mom", action="store_true")

args = parser.parse_args()

data = dataloader.read_data_sets(DATA_DIR)

### Build TensorFlow Graph ###
x = tf.placeholder("float", [None, input_dim], name='X')
w = []
b = []
h = []

fkeys = data.features.train.keys()
lkeys = data.labels.train.keys()
output_dim = data.train.labels[lkeys[0]].shape[1]
input_dim = data.train.features[fkeys[0]].shape[1]
w.append(tf.Variable(tf.truncated_normal([input_dim, NUM_HIDDEN_UNITS], stddev=.5)))
b.append(tf.Variable(tf.constant(.1, shape=[L[0]])))
h.append(tf.tanh(tf.matmul(x,w[0])+b[0]))
for i in xrange(1, args.NUM_HIDDEN_LAYERS):
	w.append(tf.Variable(tf.truncated_normal([NUM_HIDDEN_UNITS, NUM_HIDDEN_UNITS], stddev=.5)))
	b.append(tf.Variable(tf.constant(.1, shape=[NUM_HIDDEN_UNITS])))
	h.append(tf.tanh(tf.matmul(h[i-1],w[i])+b[i]))

u = tf.Variable(tf.truncated_normal([NUM_HIDDEN_UNITS, output_dim], stddev=.1))
q = tf.Variable(tf.constant(.1,shape=[output_dim]), name='Q')
y = tf.nn.softmax(tf.matmul(h[num_hlayers-1],u)+q, name='Y')

y_= tf.placeholder("float", [None, output_dim], name='Y_')
cross_entropy = -tf.reduce_sum(y_*tf.log(y), name='Loss')
tf.scalar_summary('Loss', cross_entropy)

train_step = tf.train.GradientDescentOptimizer(.01).minimize(cross_entropy)
correct_predictions = tf.equal(tf.argmax(y,1),tf.argmax(y_, 1))
accuracy = tf.reduce_mean(tf.cast(correct_predictions, "float"), name='acc')
tf.scalar_summary('Accuracy', accuracy)

init = tf.initialize_all_variables()
session = tf.Session()
session.run(init)
merged_summary_op = tf.merge_all_summaries()
summary_writer = tf.train.SummaryWriter('/tmp/mnist_logs',session.graph.as_graph_def())


epoch_counter = 0
while(epoch_counter < EPOCHS):
    newbatch = data.train.next_batch(MINIBATCH_SIZE)
    batch_x, batch_y = newbatch.features[fkeys[0]], newbatch.labels[
        lkeys[0]]
    session.run(train_step, feed_dict={x: batch_x.todense(), y_: batch_y})
    # summary_str = session.run(merged_summary_op, feed_dict={x: mnist.train.images, y_: mnist.train.labels})
    # summary_writer.add_summary(summary_str, i)
    print "Objective: ", i, " ", session.run(objective,
                                             feed_dict={y_: data.dev.labels[lkeys[0]],
                                                        x: data.dev.features[fkeys[0]].todense()})
    if (data.index_in_epoch + MINIBATCH_SIZE > data.num_examples):
        epoch_counter += 1
