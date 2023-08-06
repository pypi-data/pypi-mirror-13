'''
Created on Feb 1, 2016

@author: rcbyron
'''
import logging, time, cv2

log = logging.getLogger('Camera Logger')
log.setLevel(logging.INFO) # log all escalated at and above INFO
fh = logging.FileHandler('log.csv')
fh.setLevel(logging.INFO) # ensure all messages are logged to file
log.addHandler(fh)

cap = cv2.VideoCapture(0)

# define the codec and create VideoWriter object
fourcc = cv2.VideoWriter_fourcc(*'DIVX')
out = cv2.VideoWriter('output.avi',fourcc, 20.0, (640,480))

start_time = time.time()
while(cap.isOpened()):
    ret, frame = cap.read()
    if ret==True:
        frame = cv2.flip(frame,0)

        # write the flipped frame
        out.write(frame)
        meta = str(time.time()-start_time)+', '+str(frame).replace('\n', '').replace('\r', '')[:50]
        log.debug(meta)

        cv2.imshow('Record Test', frame)
        if cv2.waitKey(1) & 0xFF == ord('q'):
            break
    else:
        break

# release everything if job is finished
cap.release()
out.release()
cv2.destroyAllWindows()