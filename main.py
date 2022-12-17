from dataset import Dataset
import matplotlib.pyplot as plt
import numpy as np

def main():
    data = Dataset("scorecards.csv")
    psplit_data = data.split_on_players()
    vicki_state = psplit_data["Vicki Piper"].split_on_course("Oregon State Hospital Course")
    daniel_state = psplit_data["Daniel"].split_on_course("Oregon State Hospital Course")

    # vicki_state.plot_par_difference()
    # daniel_state.plot_par_difference()
    # print("Vicki Average:", vicki_state.get_avg_par_difference())
    # print("Daniel Average:", daniel_state.get_avg_par_difference())
    # plt.show()

    vicki_willamette = psplit_data["Vicki Piper"].split_on_course("Willamette Park")
    daniel_willamette = psplit_data["Daniel"].split_on_course("Willamette Park")

    # vicki_willamette.plot_par_difference()
    # daniel_willamette.plot_par_difference()
    # print("Vicki Average:", vicki_willamette.get_avg_par_difference())
    # print("Daniel Average:", daniel_willamette.get_avg_par_difference())

    state_diffs = np.array(vicki_state.get_par_diffs()) + np.array(daniel_state.get_par_diffs())
    willamete_diffs = np.array(vicki_willamette.get_par_diffs()) + np.array(daniel_willamette.get_par_diffs())

    # plt.plot(state_diffs, label="State")
    # plt.legend()
    # plt.show()

    # plt.plot(willamete_diffs, label="Willamette")
    # plt.legend()
    # plt.show()

    # dstate_hole1 = np.array(daniel_state.get_hole_stats(1))
    # for i, point in enumerate(dstate_hole1):
    #     plt.plot(i, point, label="Daniel Hole 1", marker="o", markersize=5, color="g")
    # plt.axhline(y=dstate_hole1.mean(), color="r", linestyle="-", label="Mean")
    # plt.show()

    # vstate_hole1 = np.array(vicki_state.get_hole_stats(1))
    # for i, point in enumerate(vstate_hole1):
    #     plt.plot(i, point, label="Vicki Hole 1", marker="o", markersize=5, color="g")
    # plt.axhline(y=vstate_hole1.mean(), color="r", linestyle="-", label="Mean")
    # plt.show()

    for course in data.get_course_list():
        split1 = data.split_on_course(course)
        print(f"==================== {course} ====================")
        for player in split1.get_player_list():
            split2 = split1.split_on_player(player)
            split2.sort_by_date()
            print(f"Player: {player}")

            holes = np.arange(1, split2.get_num_holes()+1)
            counts = []
            for hole in range(1, split2.get_num_holes()+1):
                stats = split2.get_hole_stats(hole)
                counts.append(sum(stats) / len(stats))
            
            inds = np.argsort(np.array(counts))
            holes = holes[inds]

            for hole in holes:
                print(f"Hole {hole:>2}: ", end="")
                hole_stats = split2.get_hole_stats(hole)
                for stat in hole_stats:
                    print(f"{stat:>3}", end="")
                print(f"  (avg = {round(np.mean(hole_stats), 2):<5})")
            
            print(f"Course Average: {round(sum(counts) / len(counts), 2):<5}")

            print()



            

if __name__ == "__main__":
    main()