import torch, numpy as np, h5py
from typing import Iterator, Tuple

def get_batch_iterator(data_path: str, batch_size: int, context_length: int, device: str = "cpu") -> Iterator[Tuple[torch.Tensor, torch.Tensor]]:
    """
    Creates an iterator for generating batches of data from an HDF5 file.

    Args:
        data_path (str): Path to the HDF5 file containing tokenized data.
        batch_size (int): Number of sequences in each batch.
        context_length (int): Length of each sequence.
        device (str, optional): Device to load the data onto ('cpu' or 'cuda'). Defaults to "cpu".

    Yields:
        tuple: A tuple containing input sequences (xb) and target sequences (yb).
    """
    with h5py.File(data_path, 'r') as hdf5_file:
        dataset = hdf5_file['tokens']

        dataset_size = dataset.shape[0]

        n_examples = (dataset_size - 1) // context_length

        example_idxs = np.arange(n_examples)
        np.random.shuffle(example_idxs)

        epochs = 0
        counter = 0

        while True:
            if counter + batch_size > n_examples:
                np.random.shuffle(example_idxs)
                counter = 0
                print(f"Finished epoch {epochs}")
                epochs += 1

            random_indices = example_idxs[counter:counter+batch_size] * context_length

            random_samples = torch.Tensor(np.array([dataset[idx:idx+context_length+1] for idx in random_indices]))

            xb = random_samples[:, :context_length].to(device)
            yb = random_samples[:, 1:context_length+1].to(device)

            counter += batch_size
            yield xb, yb


if __name__ == "__main__":
    import os
    dummy_data_path = "dummy_data.h5"
    if not os.path.exists(dummy_data_path):
        with h5py.File(dummy_data_path, 'w') as f:
            f.create_dataset('tokens', data=np.arange(1000))
    
    batch_size = 4
    context_length = 10
    for xb, yb in get_batch_iterator(dummy_data_path, batch_size, context_length):
        print("Input Batch Shape:", xb.shape)
        print("Target Batch Shape:", yb.shape)
        break