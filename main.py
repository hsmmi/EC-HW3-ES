import json
from ES import ES
import matplotlib.pyplot as plt
import numpy as np

cofig = json.load(open("config.json", "r"))

# for i in range(0, 8, 2):
#     es = ES(cofig[str(i)])
#     es.run()
#     print(
#         "config",
#         i,
#         cofig[str(i)]["problem"],
#         cofig[str(i)]["dimension"],
#         cofig[str(i)]["survival_selection"],
#     )
#     print("best", es.population[0][0])


def result():
    for i in range(4, 8):
        cfg = cofig[str(i)]
        print("config", i, cfg["problem"], cfg["dimension"], cfg["survival_selection"])
        avg_best = np.empty((0, cfg["max_generation"]))
        avg_avg = np.empty((0, cfg["max_generation"]))
        # 2 plot in a row
        fig, axs = plt.subplots(1, 2)
        fig.set_size_inches(18, 7)
        for j in range(10):
            es = ES(cofig[str(i)])
            es.run()
            axs[0].plot(es.best, label=f"run {j+1}", alpha=0.25)
            axs[1].plot(es.avg, label=f"run {j+1}", alpha=0.25)
            avg_best = np.vstack((avg_best, np.array(es.best)))
            avg_avg = np.vstack((avg_avg, np.array(es.avg)))
        avg_best = np.mean(avg_best, axis=0)
        avg_avg = np.mean(avg_avg, axis=0)
        axs[0].plot(avg_best, label="avg")
        axs[1].plot(avg_avg, label="avg")
        axs[0].set_title("best")
        axs[1].set_title("avg")
        axs[0].legend()
        axs[1].legend()
        plt.suptitle(f"{cfg['problem']} {cfg['dimension']} {cfg['survival_selection']}")
        # plt.show()
        # Save the figure
        fig.savefig(
            f"fig/{cfg['problem']}_{cfg['dimension']}_{cfg['survival_selection']}.png"
        )


result()
