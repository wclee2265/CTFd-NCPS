#include<stdio.h>
#include<stdlib.h>
#include<arpa/inet.h>
#include<sys/socket.h>
#include<unistd.h>
#include<string.h>

#define BUF_SIZE 1024

char buffer[BUF_SIZE];

double temperature = 30.0;
char *token = "CHANGEME";

void health_check(char buffer[])
{
    sprintf(buffer, "temperature : %.1lf\ntoken : sampletoken", temperature);
}

void temperature_up()
{
    if(temperature <= 100.0)
        temperature+=0.5;
}

void temperature_down()
{
    if(temperature >= -20.0)
        temperature-=0.5;
}

int main(int argc, char* argv[])
{
    int serv_sock;
    int clint_sock;

    struct sockaddr_in serv_addr;
    struct sockaddr_in clint_addr;
    socklen_t clint_addr_size;

    if(argc != 2)
    {
        printf("%s <port>\n", argv[0]);
        exit(1);
    }
    serv_sock = socket(PF_INET, SOCK_STREAM,0);
    if(serv_sock == -1)
        printf("socket error\n");

    memset(&serv_addr, 0, sizeof(serv_addr));
    serv_addr.sin_family = AF_INET;
    serv_addr.sin_addr.s_addr = inet_addr("127.0.0.1");
    serv_addr.sin_port = htons(atoi(argv[1]));

    if(bind(serv_sock,(struct sockaddr*)&serv_addr, sizeof(serv_addr)) == -1)
        printf("bind error\n");

    if(listen(serv_sock,20)==-1)
        printf("listen error\n");

    while(1){
        clint_addr_size = sizeof(clint_addr);
        clint_sock = accept(serv_sock,(struct sockaddr*)&clint_addr, &clint_addr_size);

        if(clint_sock == -1)
            printf("accept error\n");

        read(clint_sock, buffer, BUF_SIZE);

        switch(buffer[0]){
            case '1':
                health_check(buffer);
                break;
            case '2':
                temperature_up();
                health_check(buffer);
                break;
            case '3':
                temperature_down();
                health_check(buffer);
                break;
            default:
                sprintf(buffer, "wrong command!");
                break;
        }
        write(clint_sock, buffer, strlen(buffer)+1);
        close(clint_sock);
    }

    close(serv_sock);
    return 0;
}