import argparse
import numpy as np
from validation_metrics import get_null, preprocess

def congruence(vis_history, annotations):
    '''
    Calculates the congruence of the human
    annotations and the model annotations.

    inputs:
    vis_history (list): The total model attention.
    annotations (list): The human annotations.

    outputs:
    avg_congruence (int): The average congruence per image
                      between human and model annotations.
    '''

    cong_per_img = []

    for i in range(len(vis_history)):
        vis = vis_history[i]
        anno = annotations[i]
        
        correct_attention = 0
        total_attention = np.sum(vis)

        for j in range(len(anno)//2):
            start = anno[2*j]
            end = anno[2*j+1]

            correct_attention += np.sum(vis[start:end])

        cong_per_img.append(correct_attention / total_attention)

    return np.mean(cong_per_img)


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Process some arguments.')
    parser.add_argument('--path', type=str, required=True, help='path of history npz.')
    parser.add_argument('--abs', type=bool, default=False,
                        help='whether to use the absolute preprocessing.')
    args = parser.parse_args()
    
    history = np.load(args.path, allow_pickle=True)

    vis_history = history.get("arr_0")
    annotations = history.get("arr_2")

    if len(vis_history.shape) == 3:
        print("2d model detected; taking sum over columns to condense image.")
        vis_history = vis_history.sum(1)

    null_indices = get_null(vis_history)
    if null_indices != []:
        print("Removing {} elements because they're all zero".format(len(null_indices)))
        indices = []

        for i in range(len(vis_history)):
            if i not in null_indices:
                indices.append(i)
        
        vis_history = vis_history[indices]
        annotations = annotations[indices]

    vis_history = preprocess(vis_history, abs_=args.abs)
    cong = congruence(vis_history, annotations)

    print("Congruence is: {}".format(cong))

