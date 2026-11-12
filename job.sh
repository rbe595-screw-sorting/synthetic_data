#!/bin/bash
#SBATCH -N 1                    # number of nodes. should only need 1
#SBATCH -n 32                   # CPU cores
#SBATCH --mem=64g               # RAM
#SBATCH -J "Render"             # job name
#SBATCH -p short                # partition
#SBATCH -t 23:59:00             # time limit
#SBATCH --gres=gpu:1            # number of gpus
#SBATCH -C "L40S"               # GPU type

source ./load_module.sh
cd ..
CUDA_VISIBLE_DEVICES=0 ./blender-5.2.3-linux-x64/blender -b screws.blend --quiet --python main.py -- --gpu 7 --n_scene 5000 --cycles-device OPTIX

# Wait for all processes to complete
wait

echo "All GPU processes completed!"