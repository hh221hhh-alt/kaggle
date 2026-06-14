"""Phase 2 (value net): train V(position) -> eventual win/loss in [-1,1].

Gate metric: does V predict the winner BETTER than the trivial "whoever has
more ships right now" baseline -- especially on CLOSE positions where material
is near-even? If V only matches material, it adds nothing to the search.
"""
import torch, torch.nn as nn, torch.nn.functional as Fn

N, F = 40, 7


class Value(nn.Module):
    def __init__(self):
        super().__init__()
        self.net = nn.Sequential(
            nn.Linear(N*F, 256), nn.LayerNorm(256), nn.ReLU(),
            nn.Linear(256, 256), nn.ReLU(),
            nn.Linear(256, 128), nn.ReLU(),
            nn.Linear(128, 1), nn.Tanh(),
        )
    def forward(self, x):
        return self.net(x.view(x.size(0), -1)).squeeze(-1)


def material_margin(X):
    # per-planet own(+/-/0) * ships/100  -> signed material proxy
    own = X[:, :, 0]
    ships = X[:, :, 1]
    return (own * ships).sum(-1)


def main():
    d = torch.load("value_data.pt")
    X, Y = d["X"], d["Y"]
    n = X.size(0)
    g = torch.Generator().manual_seed(0)
    idx = torch.randperm(n, generator=g)
    X, Y = X[idx], Y[idx]
    nv = n // 10
    Xtr, Ytr, Xva, Yva = X[nv:], Y[nv:], X[:nv], Y[:nv]

    # baseline: predict winner by current material margin
    mm_va = material_margin(Xva)
    base_acc = ((mm_va.sign() == Yva.sign()) & (Yva != 0)).float().mean().item()
    # close positions = smallest |material margin| third
    thr = mm_va.abs().quantile(0.34)
    close = mm_va.abs() <= thr
    base_close = ((mm_va.sign() == Yva.sign())[close]).float().mean().item()

    m = Value()
    opt = torch.optim.Adam(m.parameters(), lr=1e-3, weight_decay=1e-5)
    lossf = nn.MSELoss()
    best = 0.0
    for ep in range(40):
        m.train(); perm = torch.randperm(Xtr.size(0))
        for i in range(0, Xtr.size(0), 1024):
            b = perm[i:i+1024]
            pred = m(Xtr[b]); loss = lossf(pred, Ytr[b])
            opt.zero_grad(); loss.backward(); opt.step()
        m.eval()
        with torch.no_grad():
            pv = m(Xva)
            acc = ((pv.sign() == Yva.sign()) & (Yva != 0)).float().mean().item()
            acc_close = ((pv.sign() == Yva.sign())[close]).float().mean().item()
            mse = lossf(pv, Yva).item()
        if (ep+1) % 5 == 0 or ep == 0:
            print(f"ep{ep+1:>3} val_mse {mse:.3f}  val_acc {acc:.3f}  close_acc {acc_close:.3f}")
        if acc > best:
            best = acc; torch.save(m.state_dict(), "orbit_value.pth")
    print(f"\nBEST val_acc={best:.3f}  saved orbit_value.pth")
    print(f"BASELINE (material): all_acc={base_acc:.3f}  close_acc={base_close:.3f}")
    print(f"--> value net {'BEATS' if best>base_acc+0.01 else 'does NOT beat'} material baseline")


if __name__ == "__main__":
    main()
