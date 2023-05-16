import streamlit as st

def detection(image_file):
    # Convert uploaded file to image object
    file_path = image_file.name  # Get Image file name

    # Save the uploaded file to disk
    with open("uploads/" + file_path, "wb") as f:
        f.write(image_file.getbuffer())
        # Show image save success
        st.write("File saved!")

    # Change detect1 parameters
    if 'weights' not in [action.dest for action in detect1.parser._actions]:
        detect.parser.add_argument('--weights', nargs='+', type=str, default='yolov7.pt', help='model.pt path(s)')
        print('weights args added')
    if 'source' not in [action.dest for action in detect1.parser._actions]:
        detect.parser.add_argument('--source', type=str, default='inference/images',
                                    help='source')  # file/folder, 0 for webcam
        print('source args added')
    if 'conf_thres' not in [action.dest for action in detect1.parser._actions]:
        detect.parser.add_argument('--conf-thres', type=float, default=0.25, help='object confidence threshold')
        print('conf args added')

    detect.parser.set_defaults(weights='runs/weights/exp-18-last.pt', conf_thres=0.1, source=("uploads/" + file_path))
    args = detect.parser.parse_args()