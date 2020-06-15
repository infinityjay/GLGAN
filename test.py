import tensorflow as tf
import numpy as np
from parameter import *
from network import *
import cv2

drawing = False # true if mouse is pressed
ix,iy = -1,-1
color = (255,255,255)
size = 1

def erase_img(args, img):

    # mouse callback function
    def erase_rect(event,x,y,flags,param):
        global ix,iy,drawing

        if event == cv2.EVENT_LBUTTONDOWN:
            drawing = True
            if drawing == True:
                # cv2.circle(img,(x,y),10,(255,255,255),-1)
                cv2.rectangle(img,(x-size,y-size),(x+size,y+size),color,)
                cv2.rectangle(mask,(x-size,y-size),(x+size,y+size),color,-1)

        elif event == cv2.EVENT_MOUSEMOVE:
            if drawing == True:
                # cv2.circle(img,(x,y),10,(255,255,255),-1)
                cv2.rectangle(img,(x-size,y-size),(x+size,y+size),color,-1)
                cv2.rectangle(mask,(x-size,y-size),(x+size,y+size),color,-1)
        elif event == cv2.EVENT_LBUTTONUP:
            drawing = False
            # cv2.circle(img,(x,y),10,(255,255,255),-1)
            cv2.rectangle(img,(x-size,y-size),(x+size,y+size),color,-1)
            cv2.rectangle(mask,(x-size,y-size),(x+size,y+size),color,-1)


    cv2.namedWindow('image')
    cv2.setMouseCallback('image',erase_rect)
    # cv2.namedWindow('mask')
    cv2.setMouseCallback('mask',erase_rect)
    mask = np.zeros(img.shape)


    while(1):
        img_show = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
        cv2.imshow('image',img_show)
        k = cv2.waitKey(1) & 0xFF
        if k == ord('q'): #press 'q' to close the mask process
            break

    test_img = cv2.resize(img, (args.input_height, args.input_width))/127.5 - 1
    test_mask = cv2.resize(mask, (args.input_height, args.input_width))/255.0
    #fill mask region to 1
    test_img = (test_img * (1-test_mask)) + test_mask

    cv2.destroyAllWindows()
    return np.tile(test_img[np.newaxis,...], [args.batch_size,1,1,1]), np.tile(test_mask[np.newaxis,...], [args.batch_size,1,1,1])




def test(args, sess, model):
    #saver  
    saver = tf.train.Saver()        
    last_ckpt = tf.train.latest_checkpoint(args.checkpoints_path)
    saver.restore(sess, last_ckpt)
    ckpt_name = str(last_ckpt)
    print("Loaded model file from " + ckpt_name)
    
    img = cv2.imread('./test_result_orig/12_orig.jpg')    #read the path of testing images
    img = cv2.cvtColor(img, cv2.COLOR_RGB2BGR)
    orig_test = cv2.resize(img, (args.input_height, args.input_width))/127.5 - 1
    # print(orig_test.shape) #(64, 64, 3)
    orig_test = np.tile(orig_test[np.newaxis,...],[args.batch_size,1,1,1]) #transfer the image from (64, 64, 3)to(64, 64, 64, 3)
    # print(orig_test.shape) #(64, 64, 64, 3)
    orig_test = orig_test.astype(np.float32)  #orig_test is the 4-D tensor filled with 1
    # print(orig_test.shape) #(64, 64, 64, 3)
    orig_w, orig_h = img.shape[0], img.shape[1]
    test_img, mask = erase_img(args, img)
    # print(test_img.shape) #(64, 64, 64, 3)
    test_img = test_img.astype(np.float32)

    print("Testing ...")
    # print(orig_test.shape)
    # print(test_img.shape)
    # print(mask.shape)
    res_img = sess.run(model.test_res_imgs, feed_dict={model.single_orig:orig_test,
                                                       model.single_test:test_img,
                                                       model.single_mask:mask})

    # save the results
    orig_test = cv2.cvtColor(orig_test[0], cv2.COLOR_BGR2RGB)
    test_img = cv2.cvtColor(test_img[0], cv2.COLOR_BGR2RGB)
    res_img = cv2.cvtColor(res_img[0], cv2.COLOR_BGR2RGB)

    cv2.imwrite("./manual_orig/" + "12_orig.jpg", (orig_test + 1) * 127.5)
    cv2.imwrite("./manual_test/" + "12_test.jpg", (test_img + 1) * 127.5)
    cv2.imwrite("./manual_res/" + "12_res.jpg", (res_img + 1) * 127.5)

    print("Done.")



def main(_):
    run_config = tf.ConfigProto()
    run_config.gpu_options.allow_growth = True
    
    with tf.Session(config=run_config) as sess:
        model = network(args)

        print('Start Testing...')
        test(args, sess, model)

main(args)
