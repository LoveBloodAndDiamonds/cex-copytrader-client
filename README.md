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

4. Установите python3.11.8:
    ```shell
    sudo apt install software-properties-common && \
    sudo add-apt-repository ppa:deadsnakes/ppa && \
    sudo apt update && \
    sudo apt install python3.11
    ```
5. Установите poetry:
   ```shell
   pip3 install poetry
   ```
6. Скопируйте репозиторий или перенесите проект через SFTP в папку root/:
   ```shell
   git clone https://github.com/LoveBloodAndDiamonds/cex-copytrader-client.git
   ```
7. Перейдите в директорию проекта используя команду cd (зависит от того, в какой директории Вы сейчас, доступные
каталоги для перехода можно узнать используя команду 'ls' или 'ls -a')
    ```shell
    cd cex-copytrader-client
    ```
8. Заполните .env.dist и переменуйте его в .env используя консольный тектовый редактор nano:
    ```shell
   nano .env.dist
    ```
9. Установите утилиту для работы с Makefile:
   ```shell
   apt install make
   ```
10. Используя Makefile переместите и запустите сервис, который позволит 
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
   