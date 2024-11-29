function auto() {
    TOKEN=$(cat token.txt)
    echo -e "$TOKEN" | python3 main.py &
    NODEPAY_PID=$!
    echo "running with PID: $NODEPAY_PID"
}

function stop() {
    if [ ! -z "$NODEPAY_PID" ]; then
        echo "Stopping grass_freeproxy.py with PID: $NODEPAY_PID"
        kill -9 $NODEPAY_PID
        clear
    else
        echo "No process found to stop."
    fi
}

while true; do
    echo "Starting auto process..."
    auto
    RANDOM_SLEEP=$((RANDOM % 360 * 10 * 8))
    sleep $RANDOM_SLEEP
    stop
done
