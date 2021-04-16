#include "LibParser.h"
#include <fstream>
#include <sstream>
#include <unordered_set>
#include <unistd.h>

bool operator==(const LibVersion& left, const LibVersion& right) {
    if (left.LibName == right.LibName) {
        return true;
    }
    return false;
}

size_t LibVersionHasher::operator()(const LibVersion& key) const {
    return std::hash<std::string>()(key.Version) ^ std::hash<std::string>()(key.LibName);
}


std::vector<std::string> LibParser::GetLibPaths() {
    std::ifstream libFile(LIBS_PATH_LIST);
    std::string curr;
    std::vector<std::string> result;
    while(getline(libFile, curr)) {
        if (curr[0] == '/') { // this check helps skip comments in file
            result.push_back(curr);
        }
    }
    return result;
}

std::vector<LibVersion> LibParser::GetLibraryVersions() {
    auto paths = GetLibPaths();
    for (const auto& path: paths) {
        for (const auto& entry: fs::directory_iterator(path)) {
            std::string libPath = entry.path();
            if (libPath.find("so") != std::string::npos) {
                LibVersion version;
                auto pos = libPath.rfind("so");
                version.LibName = libPath.substr(0, pos - 1);
                if (pos + 3 < libPath.size()) {
                    version.Version = libPath.substr(pos + 3);
                } else {
                    version.Version = "0";
                }
                auto modTime = fs::last_write_time(entry);
                using namespace std::chrono;
                auto sctp = time_point_cast<system_clock::duration>(modTime);
                version.ModificationTime =  system_clock::to_time_t(sctp);

                LibraryVersions.push_back(version);
            }
        }
    }

    return LibraryVersions;
}

void LibParser::Notify(std::string& message) {
    auto pid = fork();
    if (!pid) {
        std::string s = "--message=" + message;
        execl("/home/zaikova/coursework/sender.py", "sender.py", s.c_str(), (char *)NULL); 
    }
}

void LibParser::BackupLibMap() {
    if (LibsMap.size()) {
        return;
    }
    std::ifstream fin;
    fin.open(CONFIG);
    if (fin) {
        int count;
        std::string name, version, time;
        fin >> count;

        for (size_t i = 0; i < count; ++i) {
            fin >> name >> version >> time;
            LibsMap.insert(LibVersion(name, version, time));
        }
    }
    fin.close();
}

void LibParser::ParseLibs(std::vector<LibVersion>& libs) {
    std::ofstream logger("/home/zaikova/lib_change_log", std::ios::app);
    std::ostringstream log;
    std::ostringstream humanMessage;
    for (auto& lib: libs) {
        auto it = LibsMap.find(lib);
        if (it != LibsMap.end()) {
            const_cast<LibVersion*>(&(*it))->Marked = true;
            if (it->Version != lib.Version) {
                log << "upd\n" << lib.LibName << "\n" << it->Version << "\n" << lib.Version << "\n" << lib.ModificationTime << "\n";
                humanMessage << "Library " << lib.LibName << ".so" << " was updated from version " << it->Version << " to " << lib.Version;
                const_cast<LibVersion*>(&(*it))->Version = lib.Version;
            }
        } else {
            log << "add\n" << lib.LibName << "\n" << lib.Version << "\n" << lib.ModificationTime << "\n";
            humanMessage << "Library " << lib.LibName << ".so" << " was added with version " << lib.Version;
            lib.Marked = true;
            LibsMap.insert(lib);
        }
    }
    std::vector<LibVersion> deleted;
    for (auto& lib: LibsMap) {
        if (!lib.Marked) {
            deleted.push_back(lib);
            log << "del\n" << lib.LibName << "\n" << lib.Version << "\n" << lib.ModificationTime << "\n";
            humanMessage << "Library " << lib.LibName << ".so" << " was deleted";
        }
    }
    for (size_t i = 0; i < deleted.size(); ++i) {
        LibsMap.erase(deleted[i]);
    }
    for (auto& lib: LibsMap) {
        const_cast<LibVersion*>(&lib)->Marked = false;
    }

    auto result = log.str();
    auto msg = humanMessage.str();
    if (result.size()) {
        logger << result;
        Notify(msg);
    }
    logger.close();
}

void LibParser::Execute() {
    BackupLibMap();
    auto libs = GetLibraryVersions();
    ParseLibs(libs);
    std::ofstream fout(CONFIG, std::ios::trunc);
    fout << libs.size() << std::endl;
    for (auto& lib: libs) {
        fout << lib.LibName << std::endl << lib.Version << std::endl << (unsigned long long)(lib.ModificationTime) << std::endl;
    }
    fout.close();
}
