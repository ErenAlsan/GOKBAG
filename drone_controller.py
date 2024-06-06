import os
import time
import math
import cv2
import numpy as np
from PIL import Image, ImageTk
import customtkinter
from tkinter import Label
from djitellopy import Tello
from utilities.yolo_model import YOLOModel
import utilities.keypressmodule as kp
import utilities.coord_csv_module as ccsv

me = Tello()

class DroneController:
    def __init__(self):
        me.connect()
        me.streamon()
        self.root = customtkinter.CTk()
        self.root.title("Drone Keyboard Controller")
        self.root.minsize(640, 480)

        self.cap_lbl = Label(self.root)
        self.cap_lbl.grid(row=0, column=0, columnspan=6)

        self.takeoff_land_button = customtkinter.CTkButton(self.root, text="Takeoff/Land", command=self.toggle_takeoff_land)
        self.manual_control_button = customtkinter.CTkButton(self.root, text="Manual Control", command=self.toggle_manual_control)
        self.yolo_button = customtkinter.CTkCheckBox(self.root, text="Object Detection", command=self.toggle_yolo)
        self.battery_label = customtkinter.CTkLabel(self.root, text="Battery: ")
        self.height_label = customtkinter.CTkLabel(self.root, text="Height: ")
        self.capture_button = customtkinter.CTkButton(self.root, text="Capture Image", command=self.capture_image)
        self.mode_button = customtkinter.CTkButton(self.root, text="Switch Mode", command=self.switch_mode)
        self.mode_label = customtkinter.CTkLabel(self.root, text="Mode: Operational")

        self.battery_label.grid(row=1, column=0, pady=10)
        self.height_label.grid(row=1, column=1, pady=10)
        self.mode_label.grid(row=1, column=2, pady=10)

        self.takeoff_land_button.grid(row=2, column=0, pady=10, padx=5)
        self.manual_control_button.grid(row=2, column=1, pady=10, padx=5)
        self.yolo_button.grid(row=2, column=2, pady=10, padx=5)
        self.capture_button.grid(row=2, column=3, pady=10, padx=5)
        self.mode_button.grid(row=2, column=4, pady=10, padx=5)

        self.yolo_enabled = True
        self.is_flying = False
        self.manual_control_enabled = False
        self.current_mode = "operational"

        self.yolo_button.select()

        self.width = 640
        self.height = 480
        self.deadZone = 100
        self.min_area = 3000

        self.center_x = self.width // 2
        self.center_y = self.height // 2
        self.half_deadzone = self.deadZone // 2
        self.top_left = (self.center_x - self.half_deadzone, self.center_y - self.half_deadzone)
        self.bottom_right = (self.center_x + self.half_deadzone, self.center_y + self.half_deadzone)

        if not os.path.exists('captured_images'):
            os.makedirs('captured_images')

        self.interval = 0.25
        self.x, self.y, self.z = 500, 500, 0
        self.yaw = 0
        self.a = 0

        self.points = [(self.x, self.y, self.z)]
        self.yolo_model = YOLOModel()

    def run_app(self):
        try:
            self.video_stream()
            self.root.mainloop()
        except Exception as e:
            print(f"Error running the application: {e}")
        finally:
            self.cleanup()

    def toggle_yolo(self):
        self.yolo_enabled = not self.yolo_enabled

    def toggle_takeoff_land(self):
        if self.is_flying:
            self.is_flying = False
            me.land()
            self.save_flight_log()
        else:
            self.is_flying = True
            me.takeoff()
            self.points = [(self.x, self.y, self.z)]

    def toggle_manual_control(self):
        self.manual_control_enabled = not self.manual_control_enabled
        if self.manual_control_enabled:
            kp.init()

    def switch_mode(self):
        if self.current_mode == "operational":
            self.current_mode = "search_and_rescue"
            self.mode_label.configure(text="Mode: Search and Rescue")
        else:
            self.current_mode = "operational"
            self.mode_label.configure(text="Mode: Operational")

    def capture_image(self):
        frame = me.get_frame_read().frame
        if self.yolo_enabled:
            frame, _ = self.process_frame(frame)
        img_pil = Image.fromarray(frame)
        timestamp = time.strftime("%Y%m%d-%H%M%S")
        filename = f'captured_images/capture_{timestamp}.jpg'
        img_pil.save(filename)
        print(f"Image saved as {filename}")

    def video_stream(self):
        start_time = time.time()
        frame = me.get_frame_read().frame
        if self.yolo_enabled:
            frame = cv2.resize(frame, (640, 480))
            frame, detected_objects = self.process_frame(frame)
        
        self.update_battery_and_height()
        img = Image.fromarray(frame)
        imgtk = ImageTk.PhotoImage(image=img)
        self.cap_lbl.grid(row=0, column=0, columnspan=6)
        self.cap_lbl.imgtk = imgtk
        self.cap_lbl.configure(image=imgtk)
        self.cap_lbl.after(5, self.video_stream)

        if self.manual_control_enabled:
            self.manual_control()

        end_time = time.time()
        print(f"Frame processed in {end_time - start_time:.2f} seconds")

    def cleanup(self):
        try:
            print("Cleaning up resources...")
            me.streamoff()
            self.root.quit()
            exit()
        except Exception as e:
            print(f"Error performing cleanup: {e}")

    def update_battery_and_height(self):
        battery = me.get_battery()
        height = me.get_height()
        self.battery_label.configure(text=f"Battery: {battery}%")
        self.height_label.configure(text=f"Height: {height} cm")

    def process_frame(self, img):
        results = self.yolo_model.predict(img)
        centers = []
        areas = []
        for result in results:
            for box in result.boxes:
                if result.names[int(box.cls[0])] == "person":
                    x1, y1, x2, y2 = int(box.xyxy[0][0]), int(box.xyxy[0][1]), int(box.xyxy[0][2]), int(box.xyxy[0][3])
                    cx, cy = (x1 + x2) // 2, (y1 + y2) // 2
                    area = (x2 - x1) * (y2 - y1)
                    if area >= self.min_area:
                        centers.append([cx, cy])
                        areas.append(area)
                        if self.current_mode == "search_and_rescue":
                            cv2.putText(img, "Person Detected", (x1, y1 - 15), cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 0, 255), 2)
                            cv2.rectangle(img, (x1, y1), (x2, y2), (0, 0, 255), 2)
                        else:
                            cv2.putText(img, "Ally Detected", (x1, y1 - 15), cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 255, 0), 2)
                            cv2.rectangle(img, (x1, y1), (x2, y2), (0, 255, 0), 2)
                    else:
                        if self.current_mode == "search_and_rescue":
                            cv2.putText(img, "Person Detected", (x1, y1 - 15), cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 0, 255), 2)
                            cv2.rectangle(img, (x1, y1), (x2, y2), (0, 0, 255), 2)
                        else:
                            cv2.putText(img, "Hostile Detected", (x1, y1 - 15), cv2.FONT_HERSHEY_SIMPLEX, 1, (255, 0, 0), 2)
                            cv2.rectangle(img, (x1, y1), (x2, y2), (255, 0, 0), 2)

        if centers:
            centers_np = np.array(centers)
            group_center = centers_np.mean(axis=0).astype(int)
            cv2.circle(img, tuple(group_center), 10, (255, 0, 255), -1)
            cv2.putText(img, "Group Center", (group_center[0], group_center[1] - 15), cv2.FONT_HERSHEY_SIMPLEX, 1, (255, 0, 255), 2)

        if not self.manual_control_enabled:
            self.control_drone(centers, areas)

        return img, results

    def control_drone(self, centers, areas):
        direction, group_center = self.calculate_direction(centers, self.width, self.height, self.deadZone)
        distance_adjustment = self.calculate_distance_adjustment(areas)

        me.left_right_velocity = 0
        me.for_back_velocity = 0
        me.up_down_velocity = 0
        me.yaw_velocity = 0

        if direction == 1:
            me.yaw_velocity = -13
        elif direction == 2:
            me.yaw_velocity = 13
        if direction == 3:
            me.up_down_velocity = 20
        elif direction == 4:
            me.up_down_velocity = -20

        me.for_back_velocity = distance_adjustment

        if me.send_rc_control:
            print(me.left_right_velocity, me.for_back_velocity, me.up_down_velocity, me.yaw_velocity, time.time())
            me.send_rc_control(me.left_right_velocity, me.for_back_velocity, me.up_down_velocity, me.yaw_velocity)

        self.log_flight_path(me.left_right_velocity, me.for_back_velocity, me.up_down_velocity, me.yaw_velocity)

    def calculate_direction(self, centers, frameWidth, frameHeight, deadZone):
        dir = 0
        group_center = None
        if centers:
            group_center = np.mean(np.array(centers), axis=0).astype(int)
            cx, cy = group_center
            if (cx < int(frameWidth / 2) - deadZone):
                dir = 1
            elif (cx > int(frameWidth / 2) + deadZone):
                dir = 2
            elif (cy < int(frameHeight / 2) - deadZone):
                dir = 3
            elif (cy > int(frameHeight / 2) + deadZone):
                dir = 4 
        return dir, group_center

    def calculate_distance_adjustment(self, areas):
        distance_adjustment = 0
        if areas:
            avg_area = np.mean(areas)
            if avg_area < 8000:
                distance_adjustment = 30
            elif avg_area > 25000:
                distance_adjustment = -30
        return distance_adjustment

    def manual_control(self):
        lr, fb, ud, yv = self.get_keyboard_input()
        me.send_rc_control(lr, fb, ud, yv)
        self.log_flight_path(lr, fb, ud, yv)

    def get_keyboard_input(self):
        lr, fb, ud, yv = 0, 0, 0, 0
        speed = 50
        aspeed = 50

        if kp.getKey("LEFT"):
            lr = -speed
        elif kp.getKey("RIGHT"):
            lr = speed
        if kp.getKey("UP"):
            fb = speed
        elif kp.getKey("DOWN"):
            fb = -speed
        if kp.getKey("w"):
            ud = speed
        elif kp.getKey("s"):
            ud = -speed
        if kp.getKey("a"):
            yv = -aspeed
        elif kp.getKey("d"):
            yv = aspeed
        if kp.getKey("q"): 
            me.land()
            self.save_flight_log()
            time.sleep(3)
        if kp.getKey("e"): 
            me.takeoff()

        time.sleep(self.interval)

        return [lr, fb, ud, yv]

    def log_flight_path(self, lr, fb, ud, yv):
        if lr != 0 or fb != 0 or ud != 0 or yv != 0:
            distance = math.sqrt((lr ** 2) + (fb ** 2))
            angle = math.atan2(fb, lr)

            self.x += distance * math.cos(angle + math.radians(self.yaw))
            self.y += distance * math.sin(angle + math.radians(self.yaw))
            self.z += ud * self.interval

            self.yaw += yv * self.interval

            self.points.append((self.x, self.y, self.z))

    def save_flight_log(self):
        if self.points:
            self.points.pop(0)
        ccsv.make_csv(self.points)
        self.points = [(self.x, self.y, self.z)]

