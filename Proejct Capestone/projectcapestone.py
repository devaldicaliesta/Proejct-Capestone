# -*- coding: utf-8 -*-
"""ProjectCapestone.ipynb

Automatically generated by Colaboratory.

Original file is located at
    https://colab.research.google.com/drive/1XY7rOLKIsgoSCHpzKncXVGr4d--btn_s
"""

import tensorflow as tf
import matplotlib.pyplot as plt
from tensorflow.keras.preprocessing.image import ImageDataGenerator
from google.colab import files
import os
from tensorflow.keras.preprocessing.image import ImageDataGenerator
import tempfile
import keras
from tensorflow.keras.applications.inception_v3 import InceptionV3
from tensorflow.keras.applications.mobilenet import MobileNet
from tensorflow.keras import layers
from tensorflow.keras import Model
import numpy as np
from keras.preprocessing import image

! pip install kaggle
! mkdir ~/.kaggle
! cp kaggle.json ~/.kaggle/
! chmod 600 ~/.kaggle/kaggle.json

from google.colab import drive
drive.mount('/content/drive')

! kaggle datasets download -d techsash/waste-classification-data

! unzip waste-classification-data.zip

base_dir="/content/DATASET"
train_dir=os.path.join(base_dir,"TRAIN")
test_dir=os.path.join(base_dir,"TEST")

train_datagen=ImageDataGenerator(rescale=1./255,
                                 shear_range=0.1,
                                 zoom_range=0.1,
                                 horizontal_flip=True)

validation_datagen=ImageDataGenerator(rescale=1./255)

train_generator=train_datagen.flow_from_directory(train_dir,
                                                  target_size=(150,150),
                                                  batch_size=64,
                                                  class_mode='binary')

validation_generator=validation_datagen.flow_from_directory(test_dir,
                                                            target_size=(150,150),
                                                            batch_size=64,
                                                            class_mode='binary')

pretrain_1=InceptionV3(input_shape=(150,150,3),include_top=False,weights='imagenet')
for layer in pretrain_1.layers:
      layer.trainable = False
last_layer = pretrain_1.get_layer('mixed7')

pretrain_2=MobileNet(input_shape=(150,150,3),include_top=False,weights='imagenet')
for layers_1 in pretrain_2.layers:
  layers_1.trainable=False

model = tf.keras.models.Sequential([
        # YOUR CODE HERE, end with a Neuron Dense, activated by 'sigmoid'
        tf.keras.layers.Conv2D(32,(3,3),activation='relu',input_shape=(150,150,3)),
        tf.keras.layers.MaxPooling2D(2,2),
        tf.keras.layers.Conv2D(32,(3,3),activation='relu'),
        tf.keras.layers.MaxPooling2D(2,2),
        tf.keras.layers.Flatten(),
        tf.keras.layers.Dense(128,activation='relu'),
        tf.keras.layers.Dropout(0.2),
        tf.keras.layers.Dense(1, activation='sigmoid')
    ])

xx = layers.Flatten()(last_layer.output)
xx = layers.Dense(1024,activation='relu')(xx)
xx = layers.Dropout(0.2)(xx)
xx = layers.Dense(32, activation='sigmoid')(xx)
xx = layers.Dropout(0.2)(xx)
xx = layers.Dense(1, activation='sigmoid')(xx)

model_1 = Model(pretrain_1.input, xx)

model_2=tf.keras.models.Sequential([
                                    pretrain_2,
                                    tf.keras.layers.Dense(1,activation='relu'),
                                    tf.keras.layers.GlobalAveragePooling2D(),
                                    tf.keras.layers.Dense(1,activation='sigmoid')])

class myCallback(tf.keras.callbacks.Callback):
      def on_epoch_end(self,epoch,logs={}):
        if((logs.get('accuracy')>0.85) and (logs.get('val_accuracy')>0.85)):
          self.model.stop_training = True

model.compile(loss="binary_crossentropy",optimizer=tf.keras.optimizers.Adam(learning_rate=0.001),metrics=["accuracy"])
model.fit(train_generator,steps_per_epoch=25,epochs=50,validation_data=validation_generator,validation_steps=5,verbose=2,callbacks=myCallback())

model_1.compile(loss="binary_crossentropy",optimizer=tf.keras.optimizers.Adam(learning_rate=0.001),metrics=["accuracy"])
model_1.fit(train_generator,steps_per_epoch=25,epochs=50,validation_data=validation_generator,validation_steps=5,verbose=2,callbacks=myCallback())

model_2.compile(loss="binary_crossentropy",optimizer=tf.keras.optimizers.Adam(learning_rate=0.001),metrics=["accuracy"])
model_2.fit(train_generator,steps_per_epoch=25,epochs=50,validation_data=validation_generator,validation_steps=5,verbose=2,callbacks=myCallback())

uploaded = files.upload()                                                         

for fn in uploaded.keys():

  path = fn
  img = image.load_img(path, target_size=(150, 150))                             
  imgplot = plt.imshow(img)                                                       
  x = image.img_to_array(img)
  x = np.expand_dims(x, axis=0)

  images = np.vstack([x])
  classes = model.predict(images, batch_size=10)
  classes_1=model_1.predict(images,batch_size=10)
  
  if classes==0:
    classes="Organik"
  else:
    classes="Anorganik"
  
  if classes_1==0:
    classes_1="Organik"
  else:
    classes_1="Anorganik"

  print(classes)
  print(classes_1)

from google.colab import drive
drive.mount('/content/drive')
drive.mount("/content/drive", force_remount=True)

tf.saved_model.save(model,"/content/drive/MyDrive/File Program MBKM/Project Capestone/Model_Sequensial")
tf.saved_model.save(model_1,"/content/drive/MyDrive/File Program MBKM/Project Capestone/Model_InceptionV3")
tf.saved_model.save(model_2,"/content/drive/MyDrive/File Program MBKM/Project Capestone/Model_MobileNet")

# Convert the model
Model_InceptionV3 = r"/content/drive/MyDrive/File Program MBKM/Project Capestone/Model_InceptionV3"
# Convert the model
converter = tf.compat.v1.lite.TFLiteConverter.from_saved_model(Model_InceptionV3) # path to the SavedModel directory
tflite_model = converter.convert()

# Save the model.
with open('model.tflite', 'wb') as f:
  f.write(tflite_model)

# Convert the model
Model_MobileNet = r"/content/drive/MyDrive/File Program MBKM/Project Capestone/Model_MobileNet"
converter = tf.compat.v1.lite.TFLiteConverter.from_saved_model(Model_MobileNet) # path to the SavedModel directory
tflite_model = converter.convert()

# Save the model.
with open('Model_MobileNet.tflite', 'wb') as f:
  f.write(tflite_model)

# Convert the model
Model_Sequensial = r"/content/drive/MyDrive/File Program MBKM/Project Capestone/Model_Sequensial"
converter = tf.compat.v1.lite.TFLiteConverter.from_saved_model(Model_Sequensial) # path to the SavedModel directory
tflite_model = converter.convert()

# Save the model.
with open('Model_Sequensial.tflite', 'wb') as f:
  f.write(tflite_model)