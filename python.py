import cv2
import dlib
import time
import math

car_detect = cv2.CascadeClassifier('cascade2.xml')
input = cv2.VideoCapture('4K camera example for Traffic Monitoring (Road).mp4')

def estimate_speed(location1, location2, delta_time):
    distance = math.sqrt(math.pow(location2[0] - location1[0], 2) + math.pow(location2[1] - location1[1], 2))
    ppm = 8.8
    meter = distance / ppm
    fps = 18
    speed = meter * fps * 3.6
    return speed


WIDTH = 1280
HEIGHT = 720

def do_operation():
    number_of_cars = 0
    detected_car = {}
    location1 = {}
    location2 = {}
    speed = [None] * 1000
    addList = []

    while True:
        timeStart = time.time()
        ret, frame = input.read()

        frame = cv2.resize(frame, (WIDTH, HEIGHT))
        frame = frame.copy()

        gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
        detectedCar = car_detect.detectMultiScale(gray, 1.1, 13)


        for i in detected_car.keys():
            q = detected_car[i].update(frame)
            if q < 7:
                addList.append(i)


        for i in addList:
            detected_car.pop(i, None)
            location1.pop(i, None)
            location2.pop(i, None)


        for (x, y, z, w) in detectedCar:
            x = int(x)
            y = int(y)
            z = int(z)
            w = int(w)

            x_bar = x + 0.5 * z
            y_bar = y + 0.5 * w

            matchCarID = None

            for carID in detected_car.keys():


                trackedPosition = detected_car[carID].get_position()
                print("position ", str(carID), " ", trackedPosition)

                t_x = int(trackedPosition.left())
                t_y = int(trackedPosition.top())
                t_w = int(trackedPosition.width())
                t_h = int(trackedPosition.height())

                t_x_bar = t_x + 0.5 * t_w
                t_y_bar = t_y + 0.5 * t_h

                if ((t_x <= x_bar <= (t_x + t_w)) and (t_y <= y_bar <= (t_y + t_h)) and (
                        x <= t_x_bar <= (x + w)) and (y <= t_y_bar <= (y + w))):
                    matchCarID = carID


            if matchCarID is None:
                print("adding car{}".format(str(number_of_cars)))
                car = dlib.correlation_tracker()
                car.start_track(frame, dlib.rectangle(x, y, x + z, y + w))
                detected_car[number_of_cars] = car
                location1[number_of_cars] = [x, y, z, w]
                number_of_cars += 1


        for i in detected_car.keys():
            position = detected_car[i].get_position()
            x = int(position.left())
            y = int(position.top())
            z = int(position.width())
            w = int(position.height())
            location2[i] = [x, y, z, w]
            cv2.rectangle(frame, (x, y), (x + z, y + w), (255, 0, 0), 2)



        endTime = time.time()




        for i in location1.keys():
            [x1, y1, w1, h1] = location1[i]
            [x2, y2, w2, h2] = location2[i]
            location1[i] = [x2, y2, w2, h2]


            if [x1, y1, w1, h1] != [x2, y2, w2, h2]:
                print("y1" , y1)

                if (speed[i] == None or speed[i] == 0) and y1 >= 275   and y1 <= 285:
                    speed[i] = estimate_speed([x1, y1, w1, h1], [x2, y2, w2, h2], (endTime - timeStart))

                if speed[i] != None and y1 >= 180:
                    cv2.putText(frame, str(int(speed[i])) + " km/hr", (int(x1 + w1 / 2), int(y1 - 5)),
                                cv2.FONT_HERSHEY_SIMPLEX, 0.75, (0, 0, 0), 2)

        cv2.imshow('image', frame)
        cv2.waitKey(50)
    cv2.destroyAllWindows()







do_operation()
