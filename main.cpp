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
        std::ofstream logger("/home/zaikova/coursework/pidfile", std::ios::app);
        logger << "Daemon Start working with pid" << std::to_string(getpid());
        logger.close();
        while (true) {
            LibParser p;
            p.Execute();
            sleep(300);
        }
    } else {
        return 0;
    }
}
