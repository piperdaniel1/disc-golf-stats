from typing import Dict, List
from datetime import datetime as dt
import matplotlib.pyplot as plt

class CourseRun:
    def __init__(self, play_date: dt, player_run: List[str],
                 par_scores: List[int], ind_keys: Dict[str, int],
                 player_name: str, course_name: str):
        self.player_name: str = player_name

        self.player_scores: List[int] = \
            self._parse_run(player_run, ind_keys)

        self.par_scores: List[int] = par_scores
        self.run_date: dt = play_date

        self.course_name = course_name
    
    def __str__(self):
        return f"{self.player_name:<15} {self.course_name:<30} {self.run_date.strftime('%b %d'):<10} {self.get_par_difference():>3}"
    
    def _parse_run(self, player_run: List[str], ind_keys: Dict[str, int]) \
            -> List[int]:
        hole_num: int = 1
        scores: List[int] = []
        while True:
            try:
                hole_score = player_run[ind_keys["Hole" + str(hole_num)]]
                hole_score = int(hole_score)
            except (KeyError, ValueError):
                break

            scores.append(hole_score)
            hole_num += 1

        return scores
    
    def get_hole_stats(self, num: int) -> int:
        return self.player_scores[num - 1] - self.par_scores[num - 1]

    def get_total_score(self) -> int:
        return sum(self.player_scores)
    
    def get_total_par(self) -> int:
        return sum(self.par_scores)
    
    def get_par_difference(self) -> int:
        return self.get_total_score() - self.get_total_par()



class Dataset:
    def __init__(self, file_path: str):
        self.course_runs: List[CourseRun] = []

        self._destructive_file_parse(file_path)
    
    def __str__(self):
        base_str = f"Dataset (n={len(self.course_runs)}):\n"

        for run in self.course_runs:
            base_str += f"{run}\n"
        
        return base_str

    def add_run(self, course_run: CourseRun | None):
        if course_run is not None:
            self.course_runs.append(course_run)

    def _parse_par_line(self, pars: List[str],
                        ind_keys: Dict[str, int]) -> List[int]:
        hole_num: int = 1
        scores: List[int] = []
        while True:
            try:
                hole_score = pars[ind_keys["Hole" + str(hole_num)]]
                hole_score = int(hole_score)
            except (KeyError, ValueError):
                break

            scores.append(hole_score)
            hole_num += 1

        return scores

    def _destructive_file_parse(self, path: str) -> bool:
        self.clear()

        try:
            with open(path) as f:
                lines = f.readlines()
        except FileNotFoundError:
            return False

        lines = [line.strip("\n").split(",") for line in lines]

        if len(lines) < 2:
            return False

        indexes: Dict[str, int] = {}
        for i, ind_name in enumerate(lines[0]):
            indexes.setdefault(ind_name, i)

        curr_par: List[int] = []
        for line in lines[1:]:
            line_date = dt.strptime(line[indexes["Date"]], "%Y-%m-%d %H:%M")

            if line[indexes["PlayerName"]] == "Par":
                curr_par = self._parse_par_line(line, indexes)
            else:
                new_run = CourseRun(line_date, line, curr_par,
                                    indexes, line[indexes["PlayerName"]],
                                    line[indexes["CourseName"]])
                self.add_run(new_run)

        return True
    
    def split_on_players(self) -> Dict[str, "Dataset"]:
        players = self.get_player_list()
        
        player_datasets: Dict[str, Dataset] = {}
        for player in players:
            player_datasets.setdefault(player, Dataset(""))
            for run in self.course_runs:
                if run.player_name == player:
                    player_datasets[player].add_run(run)
        
        return player_datasets
    
    def split_on_player(self, player: str) -> "Dataset":
        return self.split_on_players()[player]
    
    def split_on_courses(self) -> Dict[str, "Dataset"]:
        courses = self.get_course_list()
        
        course_datasets: Dict[str, Dataset] = {}
        for course in courses:
            course_datasets.setdefault(course, Dataset(""))
            for run in self.course_runs:
                if run.course_name == course:
                    course_datasets[course].add_run(run)
        
        return course_datasets
    
    def split_on_course(self, course: str) -> "Dataset":
        return self.split_on_courses()[course]
    
    def get_player_list(self) -> List[str]:
        players = set()
        for run in self.course_runs:
            players.add(run.player_name)
        
        return list(players)
    
    def get_course_list(self) -> List[str]:
        courses = set()
        for run in self.course_runs:
            courses.add(run.course_name)
        
        return list(courses)
    
    def sort_by_date(self):
        self.course_runs.sort(key=lambda x: x.run_date)
    
    def get_par_diffs(self, player: str | None = None) -> List[int]:
        if player is not None:
            player_dataset = self.split_on_player(player)
            player_dataset.sort_by_date()
        else:
            self.sort_by_date()
            player_dataset = self
        
        assert(len(player_dataset.get_player_list()) == 1)
        
        return [run.get_par_difference() for run in player_dataset.course_runs]
    
    def plot_par_difference(self, player: str | None = None):
        if player is not None:
            player_dataset = self.split_on_player(player)
            player_dataset.sort_by_date()
        else:
            self.sort_by_date()
            player_dataset = self
        
        assert(len(player_dataset.get_player_list()) == 1)
        
        dates = [run.run_date for run in player_dataset.course_runs]
        par_diffs = [run.get_par_difference() for run in player_dataset.course_runs]
        
        plt.plot(dates, par_diffs, label=player)
        plt.legend()
    
    def get_avg_par_difference(self, player: str | None = None) -> float:
        assert(len(self.get_course_list()) == 1)

        par_diffs = [run.get_par_difference() for run in self.course_runs]

        return sum(par_diffs) / len(par_diffs)
    
    def get_hole_stats(self, hole_num: int) -> List[int]:
        assert(len(self.get_course_list()) == 1)
        
        hole_stats = [run.get_hole_stats(hole_num) for run in self.course_runs]
        
        return hole_stats
    
    def get_num_holes(self) -> int:
        assert(len(self.get_course_list()) == 1)

        min_num = 999

        for run in self.course_runs:
            min_num = min(min_num, len(run.par_scores))
        
        return min_num
        

    def clear(self):
        pass