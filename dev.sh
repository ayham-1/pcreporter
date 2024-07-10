#!/bin/sh
tmux new-session -s pcreporter   -n code -d

tmux new-window  -t pcreporter:2 -n run
tmux new-window  -t pcreporter:3 -n gdb
tmux new-window  -t pcreporter:4 -n files
tmux new-window  -t pcreporter:5 -n git
tmux new-window  -t pcreporter:6 -n kanban

tmux send-keys -t 'files' 'man tmux' Enter
tmux send-keys -t 'git' 'git log' Enter
tmux send-keys -t 'kanban' 'taskell' Enter

tmux select-window -t pcreporter:1
tmux -2 attach-session -t pcreporter
