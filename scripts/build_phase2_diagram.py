"""Render the actual workflow as a separate Phase 2 asset; no ML artifacts change."""
from pathlib import Path

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.patches import FancyBboxPatch


def main():
    out = Path(__file__).resolve().parents[1] / "outputs" / "phase2"
    out.mkdir(parents=True, exist_ok=True)
    fig, ax = plt.subplots(figsize=(16, 10), facecolor="#f6f8fa")
    ax.set(xlim=(0,16), ylim=(0,10))
    ax.axis("off")
    ax.text(.5,9.5,"CampusEnergy AI",size=27,weight="bold",color="#182d40")
    ax.text(.5,9.05,"IMPLEMENTED WORKFLOW  /  SYNTHETIC PROTOTYPE  /  HUMAN DECISION SUPPORT",size=10,color="#087f78")

    def box(x,y,w,h,title,detail="",color="#ffffff",edge="#ccd8e0"):
        ax.add_patch(FancyBboxPatch((x,y),w,h,boxstyle="round,pad=0.08,rounding_size=0.12",facecolor=color,edgecolor=edge,lw=1.3))
        ax.text(x+w/2,y+h*.66 if detail else y+h/2,title,ha="center",va="center",size=12,weight="bold",color="#182d40")
        if detail:
            ax.text(x+w/2,y+h*.29,detail,ha="center",va="center",size=10,color="#435b70")
    def arrow(start,end):
        ax.annotate("",xy=end,xytext=start,arrowprops=dict(arrowstyle="-|>",color="#587484",lw=1.5,mutation_scale=15))

    box(.5,7.35,4.2,1.2,"Historical inputs","Electricity · Temperature\nOccupancy / calendar")
    box(5.25,7.35,4.2,1.2,"Data validation","Sorted, unique hourly records\nValid values and domains")
    box(10,7.35,5.5,1.2,"Feature engineering","Calendar cycles · Temperature · Occupancy\nHistorical lag_24 and lag_168")
    arrow((4.8,7.95),(5.15,7.95)); arrow((9.55,7.95),(9.9,7.95))
    box(10,5.55,5.5,1.1,"Chronological split","Train → validation → held-out test")
    arrow((12.75,7.25),(12.75,6.75))
    box(.5,5.55,4.2,1.1,"Previous-day baseline","Exact actual consumption at t−24")
    box(5.25,5.55,4.2,1.1,"ML candidates","HGB + Random Forest\nTrain on the training period only")
    arrow((9.9,6.1),(9.55,6.1))
    ax.plot([12.75,12.75,2.6],[6.75,6.98,6.98],color="#587484",lw=1.3)
    arrow((2.6,6.98),(2.6,6.75))
    box(5.25,3.65,4.2,1.15,"Validation selection → RF","Lowest canonical validation MAE\nRefit fixed model on train + validation",color="#e7f2ef")
    arrow((7.35,5.45),(7.35,4.9))
    box(.5,3.65,4.2,1.15,"Held-out test evaluation","Baseline + ML on identical timestamps\nMAE / RMSE · Success + failure cases")
    arrow((2.6,5.45),(2.6,4.9))
    arrow((5.15,4.23),(4.8,4.23))
    box(10,3.65,5.5,1.15,"Next 24-hour forecast","Frozen model + observed historical lags\nAssumed future temperature / occupancy",color="#e7f2ef")
    arrow((9.55,4.23),(9.9,4.23))
    box(10,1.85,5.5,1.1,"High-use detection","Threshold: training consumption P90")
    arrow((12.75,3.55),(12.75,3.05))
    box(5.25,1.85,4.2,1.1,"Explanation + recommendations","Contributing indicators\nRecommended manager checks")
    arrow((9.9,2.4),(9.55,2.4))
    box(.5,1.85,4.2,1.1,"Facility manager verification","Review context, events and equipment",color="#fff4df",edge="#d3aa6c")
    arrow((5.15,2.4),(4.8,2.4))
    box(.5,.35,4.2,.75,"Human decision",color="#fff4df",edge="#d3aa6c")
    arrow((2.6,1.75),(2.6,1.2))
    ax.text(5.3,.65,"No automatic equipment control.\nValidation candidates are effectively tied; RF is the canonical selection.",size=10,color="#435b70",va="center")
    fig.savefig(out/"architecture.png",dpi=180,bbox_inches="tight")
    fig.savefig(out/"architecture.svg",bbox_inches="tight")
    plt.close(fig)


if __name__ == "__main__":
    main()
