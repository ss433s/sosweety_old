import torch

a = torch.arange(36).reshape(2, 1, 3, 6)
b = torch.arange(48).reshape(2, 2, 2, 6)
print(a)
print(b)
print(a+b)