import random
import argparse
from object_cube import random_camera, random_cube, randomize_hdri, randomize_light, render, delete_collection_objects

def init():
    parser = argparse.ArgumentParser(
        prog='synthetic data generation',
        description='randomly renders a lot of stuff')
    parser.add_argument('-d', '--directory', type=str, default=0, help='base location of files')
    parser.add_argument('-n', '--filename', type=str, default='render', help='base file name to use')
    parser.add_argument('--renders', type=int, help='number of scenes to render')
    # parser.add_argument('--gpu', type=int, default=0, help='gpu number (if you want to run multiple jobs)')
    args = parser.parse_args()
    return args

def main():
    args = init()

    hdri_folder= f"{args.directory}/hdri"
    save_folder = f"{args.directory}/renders"

    for i in range(args.renders):
        delete_collection_objects("hardware") # remove previously generated objects
        names = ['screw', 'spacer', 'nylock_nut', 'bearing_a'] # names of objects

        num_objects = random.randint(0, 50)
        random_cube(0.5, names, num_objects, collection='hardware')

        # set background
        randomize_hdri(hdri_folder)

        # camera + lighting randomization
        randomize_light("spot_white", 2.0, False)
        randomize_light("spot_color", 1.0, True)

        # view
        random_camera("Camera", 0.5)

        render_name = f'{args.filename}_{i}'

        render(save_folder, render_name, cycles=True)
   
if __name__ == "__main__":
    main()
