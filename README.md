## Docker Demo
```bash
make start-rabbitmq
# set data.json path
export PHONE_DATA_STORAGE_PATH="path to data.json file." 
make start-docker-demo

# send task/recieve result after some time - ~100sec
docker logs deployment-client-1
# check task recieved/send result to client
docker logs deployment-server-1
```

## Other start options
```bash
pip install poetry
poetry install
# for tests
make test
# for local runs
make start-server
make start-client
```

## Original task

Необходимо разработать сервис генерации отчетов и скрипт-клиент, который будет отправлять данные на этот сервис
 
 
Сервис генерации отчетов  
- получает задачу на генерацию отчета через RabbitMQ (в задаче список из 10 номеров, пример в sample_input.json) 
- агрегирует данные по номеру(поле phone) и возвращает клиенту ответ в виде json по: 
 
 1) количеству строк 
 2) количеству строк в разрезе длительности (до 10 сек, от 10 до 30, от 30) 
 3) цене самой дорогой попытки (цена = длительность * 10) 
 4) цене самой дешевой попытки (цена = длительность * 10) 
 5) средней длительности 
 6) сумме цен, длительность которых свыше 15 секунд 
 
- сервис получает от клиента несколько таких задач одновременно и должен возвращать ответы ассинхронно 
- ответ содержит время выполнения каждого отчета (total_duration) 
 
Пример ответа клиенту во вложении sample_output.json 
 
-- 
 
Примечание. 
- данные по номерам представляют собой json c ключами phone, start_date и end_date. Номера в phone это числа от 1 до 200. start_date - время начала звонка, end_date - время окончания звонка 
- важной составляющей задачи является быстродействие, необходимо ориентироваться на 10 одновременных тасков сервису от клиента. В каждом таске 10 номеров. 
- задание необходимо выложить на Github, сервис должен сопровождаться Dockerfile.