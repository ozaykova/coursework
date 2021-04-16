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
        auto subpid = fork();
        if (!subpid) { 
            umask(0);
            setsid();
            chdir("/");
            execl("/home/zaikova/coursework/installer.py", "installer.py", (char *)NULL);
        } else {
        while (true) {
            LibParser p;
            p.Execute();
            sleep(30);
        }
        }
    } else {
        return 0;
   }
}
