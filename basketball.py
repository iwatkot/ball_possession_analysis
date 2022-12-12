import json

from collections import Counter, defaultdict

import plotly.figure_factory as ff
import plotly.express as px

# The path to the data file.
filename = 'data/basketball_data.json'
# FPS in the origin videofile.
frames_per_second = 50

# Opening JSON file and save it to a variable.
with open(filename) as f:
    all_basketball_data = json.load(f)

# Saving the needed part of data.
frame_data = all_basketball_data['frames'][1:]

# Preparing two lists for number of frames, where team was
# in possession of the ball.
team0_frames, team1_frames = [], []
for frame in frame_data:
    frame_number = frame['frame_number']
    detections = frame['detections']
    for i, detection in enumerate(detections):
        team_id = detection['team_id']
        if detection['name'] == 'ball':
            # Fetching coordinates of the ball.
            ball_x1, ball_x2 = detection['x1'], detection['x2']
            ball_y1, ball_y2 = detection['y1'], detection['y2']
            continue
        if detection['name'] == 'person':
            # Fetching coordinates of the player.
            person_x1, person_x2 = detection['x1'], detection['x2']
            person_y1, person_y2 = detection['y1'], detection['y2']
            # Checking if the ball located in players area.
            if ((person_x1 < ball_x1 and person_x2 > ball_x2) and
                    (person_y1 < ball_y1 and person_y2 > ball_y2)):
                if team_id == '0':
                    # Converting frame number to a seconds and adding it to the
                    # corresponding list for a team.
                    team0_frames.append(int(frame_number) // frames_per_second)
                elif team_id == '1':
                    team1_frames.append(int(frame_number) // frames_per_second)

# Counting each group of seconds in the lists.
team0_counts = Counter(team0_frames)
team1_counts = Counter(team1_frames)
# Declaring variables as defaultdict and sorting them
# by the key (seconds) by ascending.
team0_counts = defaultdict(int, sorted(team0_counts.items(),
                           key=lambda x: x[0]))
team1_counts = defaultdict(int, sorted(team1_counts.items(),
                           key=lambda x: x[0]))


# Prepraring lists for storing X and Y coordinates for the graph.
# y0_values - list of y coordinates of team0, y1_values - for team1.
# x_values is a common lists for both teams.
x_values, y0_values, y1_values = [], [], []
# Сhecking which team has more possession of the ball in each second.
for second in range(list(team0_counts.keys())[-1] + 1):
    # Generating list with X coordinates (from 1 to the last second).
    x_values.append(second)
    if team0_counts[second] > team1_counts[second]:
        # Adding 1 to the list of team which has possession of the ball
        # and None to the team which has not.
        y0_values.append(1)
        y1_values.append(None)
    elif team1_counts[second] > team0_counts[second]:
        # Adding 1 to the list of team which has possession of the ball
        # and None to the team which has not.
        y0_values.append(None)
        y1_values.append(1)
    else:
        y0_values.append(None)
        y1_values.append(None)


def make_sections(y_values):
    # Process the lists containing None and 1 and returning two lists with
    # begin and end indices of continuous sequences.
    begin, end = [], []
    for i, v in enumerate(y_values):
        if v == 1:
            if i == 0:
                # If it's the first not None element in list, adding it to the
                # list with beginnings of continious sequences.
                begin.append(i)
            elif i == len(y_values) - 1:
                # If it's the last not None element in list, adding it to the
                # list with endings of continious sequences.
                end.append(i)
            elif y_values[i - 1] is None and y_values[i + 1] is None:
                # If the not None element is a one in row (None elements are
                # both on the left and right) adding index to the both lists.
                begin.append(i)
                end.append(i)
            elif y_values[i - 1] is None:
                # If previous element of not None element was None, adding
                # index to the list of beginnings.
                begin.append(i)
            elif y_values[i + 1] is None:
                # If next element of not None element is None, adding
                # index to the list of endings.
                end.append(i)
    return begin, end


# Making to pair of lists (beginnings and endings of sections) for each team.
begin_0, end_0 = make_sections(y0_values)
begin_1, end_1 = make_sections(y1_values)

# Generating dictionaries with sections for graph.
df = []
for i in range(len(begin_0)):
    df.append(dict(Task='', Start=begin_0[i], Finish=end_0[i]+1,
              Resource='Team 0'))
for i in range(len(begin_1)):
    df.append(dict(Task='', Start=begin_1[i], Finish=end_1[i]+1,
              Resource='Team 1'))
# Choosing colors for chart.
colors = {
    'Team 0': 'rgb(0, 191, 255)',
    'Team 1': 'rgb(255, 0, 128)',
}
# Configuration of X axis.
xaxis_config = {
    'title': 'Time (seconds)',
    'tickmode': 'linear',
    'tick0': 0,
    'dtick': 30,
}
# Generating and showing Gantt chart.
fig_tl = ff.create_gantt(df, colors=colors, group_tasks=True,
                         showgrid_x=True,
                         index_col='Resource', show_colorbar=True)
fig_tl.update_layout(title='Statistics of possessions of the ball by teams',
                     xaxis=xaxis_config, xaxis_type='linear', hovermode=False)
fig_tl.show()


def count_times(begin, end):
    # Recieving lists of begin and end indices of sections.
    # Returning summary lenght of all sections.
    lenght = 0
    for i in range(len(begin)):
        # Counting time including the last second (that's why adding + 1).
        lenght += (end[i] - begin[i]) + 1
    return lenght


# Preparing time values with possession of the ball for both teams.
lenght0 = count_times(begin_0, end_0)
lenght1 = count_times(begin_1, end_1)

# Generating and showing pie chart.
labels = ['Team 0', 'Team 1']
values = [lenght0, lenght1]
fig_stats = px.pie(values=values, names=labels, hover_name=labels,
                   title='Possession of the ball by teams',
                   color=labels, color_discrete_map={
                    'Team 0': 'rgb(0, 191, 255)',
                    'Team 1': 'rgb(255, 0, 128)',
                   })
fig_stats.show()
