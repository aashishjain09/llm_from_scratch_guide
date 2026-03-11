import torch, torch.nn.functional as F, os, numpy as np
from tqdm import tqdm
from config.config import default_config as config
from src.models.transformer import Transformer
from data_loader.data_loader import get_batch_iterator
from typing import Dict


model = Transformer(
    n_head=config['n_head'],
    n_embed=config['n_embed'],
    context_length=config['context_length'],
    vocab_size=config['vocab_size'],
    N_BLOCKS=config['n_blocks'],
).to(config['device'])

total_params = sum(p.numel() for p in model.parameters())
print(f"Total number of parameters in the model: {total_params:,}")

optimizer = torch.optim.AdamW(model.parameters(), lr=config['t_lr'])

losses = []

AVG_WINDOW = 64

@torch.no_grad()
def estimate_loss(steps: int) -> Dict[str, float]:
    """
    Evaluate the model on training and development datasets and calculate average loss.
    
    Args:
        steps (int): Number of steps to evaluate.
        
    Returns:
        dict: Dictionary containing average losses for 'train' and 'dev' splits.
    """
    out = {}
    model.eval()

    for split in ['train', 'dev']:
        data_path = config['train_path'] if split == 'train' else config['dev_path']

        batch_iterator_eval = get_batch_iterator(
            data_path, config['t_batch_size'], config['t_context_length'], device=config['device']
        )

        losses_eval = torch.zeros(steps)
        for k in range(steps):
            try:
                xb, yb = next(batch_iterator_eval)
                _, loss = model(xb, yb)
                losses_eval[k] = loss.items()
            except StopIteration:
                print(f"Warning: Iterator for {split} ended early.")
                break
        
            out[split] = losses_eval[:k+1].mean()
    model.train()
    return out


batch_iterator = get_batch_iterator(
    config['train_path'],
    config['t_batch_size'],
    config['t_context_length'],
    device=config['device'],
)

pbar = tqdm(range(config['t_train_steps']))
for step in pbar:
    try:
        xb, yb = next(batch_iterator)

        _, loss = model(xb, yb)

        losses.append(loss.item())
        pbar.set_description(f"Train loss: {np.mean(losses[-AVG_WINDOW:]):.4f}")

        optimizer.zero_grad(set_to_none=True)
        loss.backward()
        optimizer.step()

        if step % config['t_eval_steps'] == 0:
            evaluation_losses = estimate_loss(config['t_eval_iters'])
            train_loss = evaluation_losses['train']
            dev_loss = evaluation_losses['dev']
            print(f"Step: {step}, Train loss: {train_loss:.4f}, Dev loss: {dev_loss:.4f}")

        if step == config['t_lr_decay_step']:
            print('Decaying learning rate')
            for g in optimizer.param_groups:
                g['lr'] = config['t_lr_decayed']
    except StopIteration:
        print("Training data iterator finished early.")
        break


os.makedirs(config['t_out_path'].split('/')[0], exist_ok=True)

evaluation_losses = estimate_loss(200)
train_loss = evaluation_losses['train']
dev_loss = evaluation_losses['dev']

modified_model_out_path = config['t_out_path']
save_tries = 0
while os.path.exists(modified_model_out_path):
    save_tries += 1
    model_out_name = os.path.splitext(config['t_out_path'])[0]
    modified_model_out_path = model_out_name + f"_{save_tries}" + ".pt"

torch.save(
    {
        'model_state_dict': model.state_dict(),
        'optimizer_state_dict': optimizer.state_dict(),
        'losses': losses,
        'train_loss': train_loss,
        'dev_loss': dev_loss,
        'steps': len(losses),
    },
    modified_model_out_path
)
print(f"Saved model to {modified_model_out_path}")
print(f"Finishing training. Train loss: {train_loss:.4f}, Dev loss: {dev_loss:.4f}")