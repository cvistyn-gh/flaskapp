gunicorn --bind 127.0.0.1:5000 wsgi:app & APP_PID=$!
sleep 5
echo start client
python3 client.py
CLIENT_EXIT_CODE=$?
echo $APP_PID
kill -TERM $APP_PID
if [ $CLIENT_EXIT_CODE -ne 0 ]; then
    echo "Тест завершился с ошибкой: $CLIENT_EXIT_CODE"
    exit $CLIENT_EXIT_CODE
else
    echo "Тест завершился успешно"
    exit 0
fi
