"""Phase 3b: behavioural cloning of Jake's source->target choices.
Model: per-planet features [40,F] -> 40x40 (src->tgt) logits + value.
Loss: for each source that launched, CE between softmax(pred[src,:]) and Jake's
target distribution. Non-launching/padded sources contribute nothing."""
import torch, torch.nn as nn, torch.nn.functional as Fn
N=40; F=7
class Brain(nn.Module):
    def __init__(self):
        super().__init__()
        self.shared=nn.Sequential(nn.Linear(N*F,256),nn.LayerNorm(256),nn.ReLU(),
                                   nn.Linear(256,256),nn.ReLU(),nn.Linear(256,128),nn.ReLU())
        self.policy=nn.Linear(128,N*N)
        self.value=nn.Sequential(nn.Linear(128,1),nn.Tanh())
    def forward(self,x):
        h=self.shared(x.view(x.size(0),-1)); return self.policy(h), self.value(h)

def main():
    d=torch.load("jake_dataset.pt"); X,Y=d["X"],d["Y"]
    n=X.size(0); idx=torch.randperm(n); X,Y=X[idx],Y[idx]
    nv=max(1,n//10); Xtr,Ytr,Xva,Yva=X[nv:],Y[nv:],X[:nv],Y[:nv]
    m=Brain(); opt=torch.optim.Adam(m.parameters(),lr=1e-3,weight_decay=1e-5)
    def loss_fn(logit,Yb):
        B=Yb.size(0); pl=logit.view(B,N,N)
        rowsum=Yb.sum(-1)                      # [B,N] ships launched per source
        mask=rowsum>0                          # launched sources
        logp=Fn.log_softmax(pl,dim=-1)         # [B,N,N]
        tdist=Yb/rowsum.clamp(min=1e-6).unsqueeze(-1)
        ce=-(tdist*logp).sum(-1)               # [B,N]
        return (ce*mask).sum()/mask.sum().clamp(min=1)
    def top1_acc(logit,Yb):                    # does argmax target match Jake's max-ship target?
        B=Yb.size(0); pl=logit.view(B,N,N); rowsum=Yb.sum(-1); mask=rowsum>0
        pred=pl.argmax(-1); true=Yb.argmax(-1)
        return ((pred==true)&mask).sum().float()/mask.sum().clamp(min=1)
    best=0
    for ep in range(60):
        m.train(); perm=torch.randperm(Xtr.size(0))
        for i in range(0,Xtr.size(0),256):
            b=perm[i:i+256]; lo,_=m(Xtr[b]); l=loss_fn(lo,Ytr[b])
            opt.zero_grad(); l.backward(); opt.step()
        m.eval()
        with torch.no_grad():
            lo,_=m(Xva); vl=loss_fn(lo,Yva).item(); va=top1_acc(lo,Yva).item()
            lo2,_=m(Xtr); ta=top1_acc(lo2,Ytr).item()
        if (ep+1)%10==0 or ep==0:
            print(f"ep{ep+1:>3} val_loss {vl:.3f}  train_top1 {ta:.2f}  val_top1 {va:.2f}")
        if va>best:
            best=va; torch.save(m.state_dict(),"orbit_brain.pth")
    print(f"BEST val_top1={best:.2f}  saved orbit_brain.pth")
if __name__=="__main__": main()
