# cex-copytrader-client

## Установка:

1. Обновите список доступных пакетов:
   ```shell
   sudo apt update
   ```
2. Обновите пакеты:
   ```shell
   sudo apt upgrade
   ```
3. Установите менеджер пакетов для python:
    ```shell
    sudo apt install python3-pip
    ```
4. Скопируйте репозиторий или перенесите проект через SFTP в папку root/:
   ```shell
   git clone https://github.com/LoveBloodAndDiamonds/cex-copytrader-client.git
   ```
5. Установите python3.11.8:
    ```shell
    sudo apt install software-properties-common && \
    sudo add-apt-repository ppa:deadsnakes/ppa && \
    sudo apt update && \
    sudo apt install python3.11
    ```
6. Перейдите в директорию проекта используя команду cd (зависит от того, в какой директории Вы сейчас, доступные
каталоги для перехода можно узнать используя команду 'ls' или 'ls -a')
    ```shell
    cd cex-copytrader-client
    ```
7. Заполните .env.dist и переменуйте его в .env используя консольный тектовый редактор nano:
    ```shell
   nano .env.dist
    ```

8. Используя Makefile переместите и запустите сервис, который позволит 
запустить программу в фоновым режим и с автоматическим перезапуском
    ```shell
   make move-service && make run-service
    ```
--- 
Логи можно посмотреть введя команду:
```shell
sudo systemctl status app
```

Логи хранятся в папке проекта, там же и находится база данных, если вы не настроили ее и не указали ее URL в .env.
   