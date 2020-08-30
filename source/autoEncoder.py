# 대표적인 비지도(Unsupervised) 학습 방법인 Autoencoder 를 구현해봅니다.
# 이 autoEncoder에서는 MNIST를 학습 데이터로 사용합니다.

import tensorflow as tf
import numpy as np
import matplotlib.pyplot as plt
from rbm_v2 import BBRBM, GBRBM
import os

from tensorflow.examples.tutorials.mnist import input_data
mnist = input_data.read_data_sets("./mnist/data/", one_hot=True)

#########
# 옵션 설정
######

rbm_learning_rate = 0.01
rbm_training_epoch = 20
learning_rate = 0.01
training_epoch = 50
batch_size = 32

# 신경망 레이어 구성 옵션
n_hidden = [400, 160, 80, 20]     # 히든 레이어의 뉴런 갯수 (다중 뉴런으로 바꾸는 것이 좋을것 입니다.)
n_input = 28*28                     # 입력값 크기 - 이미지 픽셀수 (윈도우 사이즈 크기로 바꿔야 할것입니다.)

###
# RBM 모델 구성
###

rbmObject01 = BBRBM(n_visible=n_input, n_hidden=n_hidden[0], learning_rate=learning_rate, momentum=0.95, use_tqdm=False)
rbmObject02 = BBRBM(n_visible=n_hidden[0], n_hidden =n_hidden[1], learning_rate= learning_rate, momentum=0.95, use_tqdm= False)
rbmObject03 = BBRBM(n_visible=n_hidden[1], n_hidden =n_hidden[2], learning_rate= learning_rate, momentum=0.95, use_tqdm= False)
rbmObject04 = BBRBM(n_visible=n_hidden[2], n_hidden =n_hidden[3], learning_rate= learning_rate, momentum=0.95, use_tqdm= False)
rbmObject05 = BBRBM(n_visible=n_hidden[3], n_hidden =n_hidden[2], learning_rate= learning_rate, momentum=0.95, use_tqdm= False)
rbmObject06 = BBRBM(n_visible=n_hidden[2], n_hidden =n_hidden[1], learning_rate= learning_rate, momentum=0.95, use_tqdm= False)
rbmObject07 = BBRBM(n_visible=n_hidden[1], n_hidden =n_hidden[0], learning_rate= learning_rate, momentum=0.95, use_tqdm= False)
rbmObject08 = BBRBM(n_visible=n_hidden[0], n_hidden =n_input, learning_rate= learning_rate, momentum=0.95, use_tqdm= False)

# ensure output dir exists
if not os.path.isdir('out'):
  os.mkdir('out')

###
# RBM 훈련
###

start = False

if start:
    errs = rbmObject01.fit(mnist.train.images, n_epoches=rbm_training_epoch, batch_size=32)
    rbmObject01.save_weights('./out/RBM_data1','RBM_vr1')
    plt.plot(errs)
    plt.show()
    rbmObject02.fit(rbmObject01.transform(mnist.train.images), n_epoches=rbm_training_epoch, batch_size=32)
    rbmObject02.save_weights('./out/RBM_data2', 'RBM_vr2')
    rbmObject03.fit(
        rbmObject02.transform(rbmObject01.transform(mnist.train.images)), n_epoches=rbm_training_epoch, batch_size=32)
    rbmObject03.save_weights('./out/RBM_data3', 'RBM_vr3')
    rbmObject04.fit(
        rbmObject03.transform(rbmObject02.transform(rbmObject01.transform(mnist.train.images))),
        n_epoches=rbm_training_epoch, batch_size=32)
    rbmObject04.save_weights('./out/RBM_data4', 'RBM_vr4')
    rbmObject05.fit(
        rbmObject04.transform(rbmObject03.transform(rbmObject02.transform(rbmObject01.transform(mnist.train.images)))),
        n_epoches=rbm_training_epoch, batch_size=32)
    rbmObject05.save_weights('./out/RBM_data5', 'RBM_vr5')
    rbmObject06.fit(
        rbmObject05.transform(rbmObject04.transform(rbmObject03.transform(rbmObject02.transform(rbmObject01.transform(mnist.train.images))))),
        n_epoches=rbm_training_epoch, batch_size=32)
    rbmObject06.save_weights('./out/RBM_data6', 'RBM_vr6')
    rbmObject07.fit(
        rbmObject06.transform(rbmObject05.transform(rbmObject04.transform(
            rbmObject03.transform(rbmObject02.transform(rbmObject01.transform(mnist.train.images)))))),
        n_epoches=rbm_training_epoch, batch_size=32)
    rbmObject07.save_weights('./out/RBM_data7', 'RBM_vr7')
    rbmObject08.fit(
        rbmObject07.transform(rbmObject06.transform(rbmObject05.transform(rbmObject04.transform(
            rbmObject03.transform(rbmObject02.transform(rbmObject01.transform(mnist.train.images))))))),
        n_epoches=rbm_training_epoch, batch_size=32)
    rbmObject08.save_weights('./out/RBM_data8', 'RBM_vr8')

#########
# 오토인코더 신경망 모델 구성
######

# Small epsilon value for the BN transform
epsilon = 1e-3

sess = tf.Session()

# Y 가 없습니다. 입력값을 Y로 사용하기 때문입니다.
Original_X = tf.placeholder(tf.float32, [None, n_input])
noise = tf.random_normal(tf.shape(Original_X), mean=0.0, stddev=0.2, dtype=tf.float32)
Noised_X = Original_X + noise
# 인코더 레이어와 디코더 레이어의 가중치와 편향 변수를 설정합니다.
# 다음과 같이 이어지는 레이어를 구성하기 위한 값들 입니다.
# input -> encode -> decode -> output

# 첫번째 encoder layer
W_encode01 = tf.Variable(tf.random_normal([n_input, n_hidden[0]]), name="W_encode01")
b_encode01 = tf.Variable(tf.random_normal([n_hidden[0]]))

# sigmoid 함수를 이용해 신경망 레이어를 구성합니다.
# sigmoid(X * W + b)
# 인코더 레이어 구성
# batch_nomarlization 적용
preHidden01 = tf.matmul(Noised_X, W_encode01)
batch_mean1, batch_var1 = tf.nn.moments(preHidden01,[0])
scale1 = tf.Variable(tf.ones([n_hidden[0]]))
hidden01 = tf.nn.sigmoid(tf.nn.batch_normalization(preHidden01,batch_mean1,batch_var1,b_encode01,scale1,epsilon))


# 두번째 encoder layer
W_encode02 = tf.Variable(tf.random_normal([n_hidden[0], n_hidden[1]]))
b_encode02 = tf.Variable(tf.random_normal([n_hidden[1]]))

# batch_nomarlization 적용
preHidden02 = tf.matmul(hidden01, W_encode02)
batch_mean2, batch_var2 = tf.nn.moments(preHidden02,[0])
scale2 = tf.Variable(tf.ones([n_hidden[1]]))
hidden02 = tf.nn.sigmoid(tf.nn.batch_normalization(preHidden02,batch_mean2,batch_var2,b_encode02,scale2,epsilon))

# 세번째 encoder layer
W_encode03 = tf.Variable(tf.random_normal([n_hidden[1], n_hidden[2]]))
b_encode03 = tf.Variable(tf.random_normal([n_hidden[2]]))

# batch_nomarlization 적용
preHidden03 = tf.matmul(hidden02, W_encode03)
batch_mean3, batch_var3 = tf.nn.moments(preHidden03,[0])
scale3 = tf.Variable(tf.ones([n_hidden[2]]))
hidden03 = tf.nn.sigmoid(tf.nn.batch_normalization(preHidden03,batch_mean3,batch_var3,b_encode03,scale3,epsilon))

# 네번째 encoder layer (encoder의 최종 결과물)
W_encode04 = tf.Variable(tf.random_normal([n_hidden[2], n_hidden[3]]))
b_encode04 = tf.Variable(tf.random_normal([n_hidden[3]]))

# batch_nomarlization 적용
preHidden04 = tf.matmul(hidden03, W_encode04)
batch_mean4, batch_var4 = tf.nn.moments(preHidden04,[0])
scale4 = tf.Variable(tf.ones([n_hidden[3]]))
hidden04 = tf.nn.sigmoid(tf.nn.batch_normalization(preHidden04,batch_mean4,batch_var4,b_encode04,scale4,epsilon))

# encode 의 아웃풋 크기를 입력값보다 작은 크기로 만들어 정보를 압축하여 특성을 뽑아내고,
# decode 의 출력을 입력값과 동일한 크기를 갖도록하여 입력과 똑같은 아웃풋을 만들어 내도록 합니다.
# 히든 레이어의 구성과 특성치을 뽑아내는 알고리즘을 변경하여 다양한 오토인코더를 만들 수 있습니다.

# 첫번째 decoder layer (이는 네번째 encoder layer를 사용한것임.)
W_decode01 = tf.Variable(tf.random_normal([n_hidden[3], n_hidden[2]]))
b_decode01 = tf.Variable(tf.random_normal([n_hidden[2]]))

# 디코더 레이어 구성
preHidden05 = tf.matmul(hidden04, W_decode01)
batch_mean5, batch_var5 = tf.nn.moments(preHidden05,[0])
scale5 = tf.Variable(tf.ones([n_hidden[2]]))
hidden05 = tf.nn.sigmoid(tf.nn.batch_normalization(preHidden05,batch_mean5,batch_var5,b_decode01,scale5,epsilon))

# 두번째 decoder layer
W_decode02 = tf.Variable(tf.random_normal([n_hidden[2], n_hidden[1]]))
b_decode02 = tf.Variable(tf.random_normal([n_hidden[1]]))

# batch_nomarlization 적용
preHidden06 = tf.matmul(hidden05, W_decode02)
batch_mean6, batch_var6 = tf.nn.moments(preHidden06,[0])
scale6 = tf.Variable(tf.ones([n_hidden[1]]))
hidden06 = tf.nn.sigmoid(tf.nn.batch_normalization(preHidden06,batch_mean6,batch_var6,b_decode02,scale6,epsilon))

# 세번째 decoder layer
W_decode03 = tf.Variable(tf.random_normal([n_hidden[1], n_hidden[0]]))
b_decode03 = tf.Variable(tf.random_normal([n_hidden[0]]))

# batch_nomarlization 적용
preHidden07 = tf.matmul(hidden06, W_decode03)
batch_mean7, batch_var7 = tf.nn.moments(preHidden07,[0])
scale7 = tf.Variable(tf.ones([n_hidden[0]]))
hidden07 = tf.nn.sigmoid(tf.nn.batch_normalization(preHidden07,batch_mean7,batch_var7,b_decode03,scale7,epsilon))

# 네번째 decoder layer (복구한 data 출력)
W_decode04 = tf.Variable(tf.random_normal([n_hidden[0], n_input]))
b_decode04 = tf.Variable(tf.random_normal([n_input]))

# batch_nomarlization 적용
preHidden08 = tf.matmul(hidden07, W_decode04)
batch_mean8, batch_var8 = tf.nn.moments(preHidden08,[0])
scale8 = tf.Variable(tf.ones(n_input))
restoredData = tf.nn.sigmoid(tf.nn.batch_normalization(preHidden08,batch_mean8,batch_var8,b_decode04,scale8,epsilon))

saver = tf.train.Saver({'RBM_vr1' + '_w': W_encode01,
                        'RBM_vr1' + '_h': b_encode01})
saver.restore(sess, './out/RBM_data1')
saver = tf.train.Saver({'RBM_vr2' + '_w': W_encode02,
                        'RBM_vr2' + '_h': b_encode02})
saver.restore(sess, './out/RBM_data2')
saver = tf.train.Saver({'RBM_vr3' + '_w': W_encode03,
                        'RBM_vr3' + '_h': b_encode03})
saver.restore(sess, './out/RBM_data3')
saver = tf.train.Saver({'RBM_vr4' + '_w': W_encode04,
                        'RBM_vr4' + '_h': b_encode04})
saver.restore(sess, './out/RBM_data4')
saver = tf.train.Saver({'RBM_vr5' + '_w': W_decode01,
                        'RBM_vr5' + '_h': b_decode01})
saver.restore(sess, './out/RBM_data5')
saver = tf.train.Saver({'RBM_vr6' + '_w': W_decode02,
                        'RBM_vr6' + '_h': b_decode02})
saver.restore(sess, './out/RBM_data6')
saver = tf.train.Saver({'RBM_vr7' + '_w': W_decode03,
                        'RBM_vr7' + '_h': b_decode03})
saver.restore(sess, './out/RBM_data7')
saver = tf.train.Saver({'RBM_vr8' + '_w': W_decode04,
                        'RBM_vr8' + '_h': b_decode04})
saver.restore(sess, './out/RBM_data8')


# 디코더는 인풋과 최대한 같은 결과를 내야 하므로, 디코딩한 결과를 평가하기 위해
# 입력 값인 X 값을 평가를 위한 실측 결과 값으로하여 decoder 와의 차이를 손실값으로 설정합니다.

''' 
tf.reduce_mean :  Computes the mean of elements across dimensions of a tensor. 
x = tf.constant([[1., 1.], [2., 2.]])
tf.reduce_mean(x)  # 1.5
tf.reduce_mean(x, 0)  # [1.5, 1.5]
tf.reduce_mean(x, 1)  # [1.,  2.]
'''
cost = tf.reduce_mean(tf.pow(Original_X - restoredData, 2))
optimizer = tf.train.RMSPropOptimizer(learning_rate).minimize(cost)

#########
# 신경망 모델 학습
######
init = tf.global_variables_initializer()
sess.run(init)

total_batch = int(mnist.train.num_examples/batch_size)

for epoch in range(training_epoch):
    total_cost = 0

    for i in range(total_batch):
        batch_xs, batch_ys = mnist.train.next_batch(batch_size)
        batch_xs.astype('float32')
        _, cost_val = sess.run([optimizer, cost],
                               feed_dict={Original_X: batch_xs})
        total_cost += cost_val

    print('Epoch:', '%04d' % (epoch + 1),
          'Avg. cost =', '{:.4f}'.format(total_cost / total_batch))

print('최적화 완료!')

#########
# 결과 확인
# 입력값(위쪽)과 모델이 생성한 값(아래쪽)을 시각적으로 비교해봅니다.
######
sample_size = 10

samples = sess.run(restoredData,
                   feed_dict={Original_X: mnist.test.images[:sample_size]})

fig, ax = plt.subplots(2, sample_size, figsize=(sample_size, 2))

for i in range(sample_size):
    ax[0][i].set_axis_off()
    ax[1][i].set_axis_off()
    ax[0][i].imshow(np.reshape(mnist.test.images[i], (28, 28)))
    ax[1][i].imshow(np.reshape(samples[i], (28, 28)))

plt.show()