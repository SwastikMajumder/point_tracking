import cv2
import numpy as np

def track_user_specified_points(video_path, initial_points):
    # Read the video
    video = cv2.VideoCapture(video_path)

    # Convert the initial_points list to a NumPy array
    initial_points = np.array(initial_points, dtype=np.float32).reshape(-1, 1, 2)

    # Initialize the feature positions in the first frame
    prev_frame = None
    prev_pts = initial_points

    while True:
        # Read a frame from the video
        ret, frame = video.read()

        if not ret:
            break

        # Convert the frame to grayscale
        frame_gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)

        if prev_frame is None:
            prev_frame = frame_gray
            continue

        # Calculate optical flow
        next_pts, status, _ = cv2.calcOpticalFlowPyrLK(prev_frame, frame_gray, prev_pts, None)

        # Filter points with good status
        good_pts = next_pts[status[:, 0] == 1]
        prev_pts = good_pts.reshape(-1, 1, 2)

        # Draw the tracked points on the frame
        for point in prev_pts:
            x, y = point[0]
            cv2.circle(frame, (int(x), int(y)), 5, (0, 255, 0), -1)

        # Show the frame with the tracked points
        cv2.imshow('Tracked Points', frame)

        # Wait for a key press and break the loop if 'q' is pressed
        if cv2.waitKey(1) & 0xFF == ord('q'):
            break

        # Update the previous frame and points for the next iteration
        prev_frame = frame_gray

    # Release video capture and close the window
    video.release()
    cv2.destroyAllWindows()

if __name__ == '__main__':
    # Specify the path to the video file
    video_path = 'rubik.mp4'

    # Specify the initial coordinates (x, y) of the features in the first frame
    initial_points = [[277, 611], [388, 622], [298, 540]]

    # Call the function to track the specified points in the video
    track_user_specified_points(video_path, initial_points)
