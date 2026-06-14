"""Transformer clone — planet-token encoder with relational target head.

Architecture: 40 planet tokens -> TransformerEncoder (permutation-equivariant,
padded slots masked) -> three heads:
  launch: per-token logit (BCE with pos_weight for the ~1% positive rate)
  target: bilinear pair scores q_i·k_j + learned distance bias  [40,40]
  size  : per-token fraction (sigmoid, MSE)

Augmentation: the board is 4-fold rotationally symmetric (+ mirror) — only the
x,y features change under rotation/flip, labels are slot-indexed and invariant.
8x effective data.

Usage: owenv/bin/python train_tf.py [dataset.pt] [out.pth] [epochs]
"""
import sys
import torch
import torch.nn as nn
import torch.nn.functional as Fn

N, F = 40, 17


class TFClone(nn.Module):
    def __init__(self, d=96, nlayer=3, nhead=4):
        super().__init__()
        self.embed = nn.Linear(F, d)
        layer = nn.TransformerEncoderLayer(
            d_model=d, nhead=nhead, dim_feedforward=4 * d,
            batch_first=True, dropout=0.1, norm_first=True)
        self.enc = nn.TransformerEncoder(layer, nlayer)
        self.launch = nn.Linear(d, 1)
        self.q = nn.Linear(d, d)
        self.k = nn.Linear(d, d)
        self.size = nn.Linear(d, 1)
        self.dist_w = nn.Parameter(torch.tensor(-4.0))

    def forward(self, x):
        pad = x.abs().sum(-1) == 0                      # [B,40] padded slots
        h = self.enc(self.embed(x), src_key_padding_mask=pad)
        lo = self.launch(h).squeeze(-1)
        lo = lo.masked_fill(pad, -20.0)
        q = self.q(h); k = self.k(h)
        tl = torch.einsum("bid,bjd->bij", q, k) / (q.size(-1) ** 0.5)
        px, py = x[..., 3], x[..., 4]
        dmat = torch.sqrt((px.unsqueeze(2) - px.unsqueeze(1)) ** 2
                          + (py.unsqueeze(2) - py.unsqueeze(1)) ** 2 + 1e-9)
        tl = tl + self.dist_w * dmat
        tl = tl.masked_fill(pad.unsqueeze(1), -20.0)    # can't target padding
        so = self.size(h).squeeze(-1)
        return lo, tl, so


def augment(x):
    """Random rotation k*90° + optional mirror around board centre (0.5,0.5).
    Only features 3 (x) and 4 (y) change."""
    B = x.size(0)
    x = x.clone()
    dx = x[..., 3] - 0.5
    dy = x[..., 4] - 0.5
    k = torch.randint(0, 4, (B,))
    flip = torch.rand(B) < 0.5
    for b in range(B):
        a, c = dx[b], dy[b]
        for _ in range(int(k[b])):
            a, c = -c, a.clone()
        if flip[b]:
            a = -a
        dx[b], dy[b] = a, c
    x[..., 3] = dx + 0.5
    x[..., 4] = dy + 0.5
    return x


def main():
    data_path = sys.argv[1] if len(sys.argv) > 1 else "jake2_dataset.pt"
    out_path = sys.argv[2] if len(sys.argv) > 2 else "orbit_tf.pth"
    epochs = int(sys.argv[3]) if len(sys.argv) > 3 else 40
    d = torch.load(data_path)
    X, L, T, S = d["X"], d["L"], d["T"], d["S"]
    n = X.size(0)
    nv = n // 10
    Xtr, Ltr, Ttr, Str = X[:-nv], L[:-nv], T[:-nv], S[:-nv]
    Xva, Lva, Tva, Sva = X[-nv:], L[-nv:], T[-nv:], S[-nv:]
    pos = Ltr.sum().item()
    neg = (Xtr[:, :, 0] > 0.5).sum().item() - pos      # owned, didn't launch
    pw = torch.tensor(max(1.0, neg / max(1.0, pos)))
    print(f"train {Xtr.size(0)}  val {Xva.size(0)}  launch pos_weight {pw:.1f}")

    m = TFClone()
    opt = torch.optim.AdamW(m.parameters(), lr=6e-4, weight_decay=1e-4)

    def evaluate():
        m.eval()
        with torch.no_grad():
            lo, tl, so = m(Xva)
            owned = Xva[:, :, 0] > 0.5
            p = torch.sigmoid(lo)
            # F1 at the best threshold (scan)
            best_f1, best_th = 0.0, 0.5
            true_l = Lva > 0.5
            for th in [0.1, 0.2, 0.3, 0.4, 0.5, 0.6, 0.7]:
                pred = (p > th) & owned
                tp = (pred & true_l).sum().item()
                pr = tp / max(1, pred.sum().item())
                rc = tp / max(1, true_l.sum().item())
                f1 = 2 * pr * rc / max(1e-9, pr + rc)
                if f1 > best_f1:
                    best_f1, best_th = f1, th
            launching = Lva > 0.5
            top1 = (tl.argmax(-1)[launching] == Tva.argmax(-1)[launching]).float().mean().item()
            mae = (torch.sigmoid(so[launching]) - Sva[launching]).abs().mean().item()
        m.train()
        return best_f1, best_th, top1, mae

    best = 0.0
    for ep in range(epochs):
        perm = torch.randperm(Xtr.size(0))
        for i in range(0, Xtr.size(0), 256):
            b = perm[i:i + 256]
            xb = augment(Xtr[b])
            lb, tb, sb = Ltr[b], Ttr[b], Str[b]
            lo, tl, so = m(xb)
            owned = xb[:, :, 0] > 0.5
            l_launch = Fn.binary_cross_entropy_with_logits(
                lo[owned], lb[owned], pos_weight=pw)
            launching = lb > 0.5
            if launching.any():
                rows = tl[launching]
                dist = tb[launching]
                dist = dist / dist.sum(-1, keepdim=True).clamp(min=1e-6)
                l_tgt = -(dist * Fn.log_softmax(rows, dim=-1)).sum(-1).mean()
                l_size = Fn.mse_loss(torch.sigmoid(so[launching]), sb[launching])
            else:
                l_tgt = lo.sum() * 0; l_size = lo.sum() * 0
            loss = l_launch + l_tgt + 0.5 * l_size
            opt.zero_grad(); loss.backward(); opt.step()
        f1, th, top1, mae = evaluate()
        score = f1 * 0.4 + top1 * 0.6
        print(f"ep{ep+1:>3}  launch_F1 {f1:.3f}@th{th:.1f}  target_top1 {top1:.3f}  size_MAE {mae:.3f}",
              flush=True)
        if score > best:
            best = score
            torch.save({"state": m.state_dict(), "th": th}, out_path)
    print(f"BEST combo={best:.3f}  saved {out_path}")


if __name__ == "__main__":
    main()
