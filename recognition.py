import pickle
import cv2
import face_recognition
import numpy as np
import multiprocessing
import pandas as pd
from datetime import datetime,date
import pyrebase
class Attendance:
    def __init__(self):
        self.dt=str(date.today())+".csv"
        self.firebaseConfig={"apiKey": "AIzaSyCDCLzEPBswgUVIXl7R4ZGF6C6kxQj7k3I","authDomain": "asperatest-e23d9.firebaseapp.com","databaseURL":"gs://asperatest-e23d9.appspot.com","projectId": "asperatest-e23d9","storageBucket": "asperatest-e23d9.appspot.com","messagingSenderId": "78725734753","appId": "1:78725734753:web:a203760f05203d1f58e520","measurementId": "G-115D8FQY6X"}
        self.firebase=pyrebase.initialize_app(self.firebaseConfig)
        self.storage = self.firebase.storage()
    def check_duplicate(self,dt,storage,name):
        try :
            url=storage.child("Attendence/"+dt).get_url(None)
            dup_df=pd.read_csv(url)
            dup=dup_df["NAME"].tolist()
            if name not in dup:

                return True
            else:
                pass
        except:
            return False
    def store(self,dt,storage,name,df,t):
        if self.check_duplicate(self.dt,self.storage,name):
            df.loc[len(df)]=[name,t]
            df.to_csv("/home/visgenix/Documents/"+dt,index=False)
            storage.child("Attendence/"+dt).put("/home/visgenix/Documents/"+dt)
        elif self.check_duplicate(dt,storage,name)==False:
            df.loc[len(df)]=[name,t]
            df.to_csv("/home/visgenix/Documents/"+dt,index=False)
            storage.child("Attendence/"+dt).put("/home/visgenix/Documents/"+dt)

    def __call__(self,Queue):

        while True:
            name,t=Queue.get()
            try:
                df=pd.read_csv("/home/visgenix/Documents/"+self.dt)
                self.store(self.dt,self.storage,name,df,t)
            except:
                df=pd.DataFrame(columns=["NAME","TIME"])
                self.store(self.dt,self.storage,name,df,t)




def main():
    notes=[]
    data=pickle.loads(open("/home/visgenix/Documents/emb.sav","rb").read())
    cap=cv2.VideoCapture("/dev/video0",cv2.CAP_V4L2)
    def variance_of_laplacian(image):
        return cv2.Laplacian(image, cv2.CV_64F).var()
    def gettime():
        now=datetime.now()
        current_time=now.strftime("%H:%M")
        return current_time

    def exc(name,notes):
        if name not in notes:
            val=(name,gettime())
            Queue.put(val)
            notes.append(name)
    while True:
        _,imgs=cap.read()
        thr = variance_of_laplacian(imgs)
        if thr>50:
            img=cv2.resize(imgs,(0,0),None,0.25,0.25)
            img=cv2.cvtColor(img,cv2.COLOR_BGR2RGB)

            boxes=face_recognition.face_locations(img)
            encodesframe=face_recognition.face_encodings(img,boxes)
            for encode,faceloc in zip(encodesframe,boxes):
                matches=face_recognition.compare_faces(data["encodngs"],encode)
                facedis=face_recognition.face_distance(data["encodngs"],encode)
                matchIndex=np.argmin(facedis)
                a=facedis[facedis<0.40]
                if matches[matchIndex] and len(a)!=0:
                    name=data["names"][matchIndex].upper()
                    exc(name,notes)
                    y1,x2,y2,x1=faceloc
                    y1,x2,y2,x1=y1*4,x2*4,y2*4,x1*4
                    cv2.rectangle(imgs,(x1,y1),(x2,y2),(144,230,172),2)
                    cv2.rectangle(imgs,(x1,y2-35),(x2,y2),(144,230,172),cv2.FILLED)
                    cv2.putText(imgs,name,(x1+6,y2-6),cv2.FONT_HERSHEY_DUPLEX,0.7,(0,0,0),2)

                else:
                    name="UNKNOWN"
                    y1,x2,y2,x1=faceloc
                    y1,x2,y2,x1=y1*4,x2*4,y2*4,x1*4
                    cv2.rectangle(imgs,(x1,y1),(x2,y2),(144,230,172),2)
                    cv2.rectangle(imgs,(x1,y2-35),(x2,y2),(144,230,172),cv2.FILLED)
                    cv2.putText(imgs,name,(x1+6,y2-6),cv2.FONT_HERSHEY_DUPLEX,0.7,(0,0,0),2)
        cv2.namedWindow("win",cv2.WINDOW_AUTOSIZE)
        cv2.imshow("win",imgs)
        if cv2.waitKey(1)&0xff==13:
            p.terminate()
            break

    cap.release()
    cv2.destroyAllWindows()




if __name__=="__main__":
    Queue=multiprocessing.Queue()
    p=multiprocessing.Process(target=Attendance(),args=(Queue,))
    p.start()

    main()