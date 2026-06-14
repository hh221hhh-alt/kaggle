"""Train the full-policy clone of top-8 winners.

Model: per-planet features [40,F] -> trunk -> 3 heads:
  launch[40]      (BCE, masked to owned planets)
  target[40,40]   (CE per launching source, vs ship-weighted target dist)
  size[40]        (MSE on launched fraction, masked to launching sources)

Gate metrics on held-out GAMES (split by sample blocks to reduce leakage):
launch-F1, target top-1 accuracy, size MAE.
"""
import sys
import torch
import torch.nn as nn
import torch.nn.functional as Fn

N, F = 40, 13


class Clone(nn.Module):
    def __init__(self, h=384):
        super().__init__()
        self.trunk = nn.Sequential(
            nn.Linear(N * F, h), nn.LayerNorm(h), nn.ReLU(),
            nn.Linear(h, h), nn.ReLU(),
            nn.Linear(h, 256), nn.ReLU(),
        )
        self.launch = nn.Linear(256, N)
        self.target = nn.Linear(256, N * N)
        self.size = nn.Linear(256, N)

    def forward(self, x):
        z = self.trunk(x.view(x.size(0), -1))
        return self.launch(z), self.target(z).view(-1, N, N), self.size(z)


def main():
    data_path = sys.argv[1] if len(sys.argv) > 1 else "top8_dataset.pt"
    out_path = sys.argv[2] if len(sys.argv) > 2 else "orbit_clone.pth"
    d = torch.load(data_path)
    X, L, T, S = d["X"], d["L"], d["T"], d["S"]
    n = X.size(0)
    # block split: last 10% of samples (≈ last games) as validation
    nv = n // 10
    Xtr, Ltr, Ttr, Str = X[:-nv], L[:-nv], T[:-nv], S[:-nv]
    Xva, Lva, Tva, Sva = X[-nv:], L[-nv:], T[-nv:], S[-nv:]
    print(f"train {Xtr.size(0)}  val {Xva.size(0)}")

    m = Clone()
    opt = torch.optim.Adam(m.parameters(), lr=8e-4, weight_decay=1e-5)

    def losses(xb, lb, tb, sb):
        lo, to, so = m(xb)
        owned = xb[:, :, 0] > 0.5
        # launch BCE on owned planets
        l_launch = Fn.binary_cross_entropy_with_logits(
            lo[owned], lb[owned]) if owned.any() else lo.sum() * 0
        # target CE on launching sources
        launching = lb > 0.5
        if launching.any():
            rows = to[launching]                       # [K, N]
            dist = tb[launching]
            dist = dist / dist.sum(-1, keepdim=True).clamp(min=1e-6)
            l_tgt = -(dist * Fn.log_softmax(rows, dim=-1)).sum(-1).mean()
            l_size = Fn.mse_loss(torch.sigmoid(so[launching]), sb[launching])
        else:
            l_tgt = lo.sum() * 0; l_size = lo.sum() * 0
        return l_launch, l_tgt, l_size

    def evaluate():
        m.eval()
        with torch.no_grad():
            lo, to, so = m(Xva)
            owned = Xva[:, :, 0] > 0.5
            pred_l = (torch.sigmoid(lo) > 0.5) & owned
            true_l = (Lva > 0.5)
            tp = (pred_l & true_l).sum().item()
            prec = tp / max(1, pred_l.sum().item())
            rec = tp / max(1, true_l.sum().item())
            f1 = 2 * prec * rec / max(1e-9, prec + rec)
            launching = Lva > 0.5
            if launching.any():
                top1 = (to.argmax(-1)[launching] == Tva.argmax(-1)[launching]).float().mean().item()
                mae = (torch.sigmoid(so[launching]) - Sva[launching]).abs().mean().item()
            else:
                top1 = mae = 0.0
        m.train()
        return f1, top1, mae

    best = 0.0
    for ep in range(50):
        perm = torch.randperm(Xtr.size(0))
        for i in range(0, Xtr.size(0), 512):
            b = perm[i:i + 512]
            la, tg, sz = losses(Xtr[b], Ltr[b], Ttr[b], Str[b])
            loss = la + tg + 0.5 * sz
            opt.zero_grad(); loss.backward(); opt.step()
        f1, top1, mae = evaluate()
        score = f1 * 0.4 + top1 * 0.6
        if (ep + 1) % 5 == 0 or ep == 0:
            print(f"ep{ep+1:>3}  launch_F1 {f1:.3f}  target_top1 {top1:.3f}  size_MAE {mae:.3f}")
        if score > best:
            best = score
            torch.save(m.state_dict(), out_path)
    print(f"BEST combo={best:.3f}  saved {out_path}")


if __name__ == "__main__":
    main()
