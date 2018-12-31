import io

from gpiozero import MotionSensor
from picamera import PiCamera
from pydrive.auth import GoogleAuth
from pydrive.drive import GoogleDrive


class GardenTV:
    def __init__(self, motion_sensor_pin, drive_base_dir='gardentv'):
        """
        Initializes a GardenTV class. Uses PyDrive to open a browser window for users to login to the web interface.
        :param drive_base_dir: The Google Drive folder to store the files in.
        :param motion_sensor_pin: The GPIO pin of the motion sensor.
        """
        assert isinstance(motion_sensor_pin, int)
        gauth = GoogleAuth()
        gauth.LocalWebserverAuth()
        self.drive = GoogleDrive(gauth)

        # Check if the gardentv folder exists
        base_file = [file for file in self.drive.ListFile({'q': "'root' in parents and trashed=false"}).GetList() if
                     file['title'] == drive_base_dir]

        if not base_file:
            # Create gardentv folder
            folder_metadata = {'title': drive_base_dir, 'mimeType': 'application/vnd.google-apps.folder'}
            folder = self.drive.CreateFile(folder_metadata)
            folder.Upload()
            self.base_directory = {
                'title': folder['title'],
                'id': folder['id']
            }
        else:
            self.base_directory = base_file[
                0]  # If there are multiple directories with the same name, ensure that only one of them is used.
        self.camera = PiCamera()

        self.pir = MotionSensor(4)

    def capture(self):
        """
        Capture with the camera and upload the result to Google Drive, in the drive_base_dir (see init method for
        details on that) google drive folder.
        """
        stream = io.BytesIO()
        with picamera.Camera() as camera:
            camera.start_preview()
            camera.capture(stream, 'jpeg')
        file = self.drive.CreateFile({"parents": [{"kind": "drive#fileLink", "id": self.base_directory['id']}]})

    def run(self):
        self.pir.when_motion = self.capture
