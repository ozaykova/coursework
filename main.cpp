#include <iostream>
#include "LibParser.h"
#include <unistd.h>
#include <sys/stat.h>
#include <syslog.h>
#include <fstream>

int main() {
    int pid = fork();

    if (pid == -1) {
        return -1;
    } else if (!pid) {
        umask(0);
        setsid();
        chdir("/");
        openlog("slog", LOG_PID|LOG_CONS, LOG_USER);
        syslog(LOG_INFO, "Start working... ");
        closelog();
        while (true) {
            LibParser p;
            p.Execute();
            sleep(300);
        }
    } else {
        return 0;
    }
}