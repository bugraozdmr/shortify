#!/bin/bash

SESSION="shortify"
DIR="$HOME/Desktop/projects/Shortify/backend"

if tmux has-session -t "$SESSION" 2>/dev/null; then
    tmux attach -t "$SESSION"
    exit 0
fi

# İlk pencere
tmux new-session -d -s "$SESSION" -c "$DIR"

# Uvicorn
tmux send-keys -t "$SESSION":0.0 "source venv/bin/activate && uvicorn main:app --reload" C-m

# Sağ tarafa böl
tmux split-window -h -t "$SESSION":0 -c "$DIR"

# Celery
tmux send-keys -t "$SESSION":0.1 "source venv/bin/activate && celery -A worker.celery_app worker --loglevel=info" C-m

# Panelleri eşit boyutlandır
tmux select-layout -t "$SESSION":0 even-horizontal

# Session'a bağlan
tmux attach -t "$SESSION"