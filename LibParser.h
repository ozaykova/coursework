#pragma once

#include <chrono>
#include <filesystem>
#include <iomanip>
#include <iostream>
#include <string>
#include <vector>
#include <ctime>
#include <fstream>
#include <unordered_set>

namespace fs = std::filesystem;

struct LibVersion {
    LibVersion(std::string& name, std::string version, std::string time) {
             std::ofstream debug ("/home/zaikova/debug", std::ios::app);
             debug << name << time << "\n";
             debug.close();
        LibName = name;
        Version = version;
        ModificationTime = std::stoull(time);
    }
    LibVersion() {};
    std::string LibName;
    std::string Version;
    std::time_t ModificationTime;
    bool Marked = false;

    friend bool operator==(const LibVersion& left, const LibVersion& right);
};

struct LibVersionHasher {
    size_t operator()(const LibVersion& key) const;

};


class LibParser {
public:
    std::vector<LibVersion> GetLibraryVersions();
    void Execute();
private:
    std::vector<std::string> GetLibPaths();
    std::vector<LibVersion> LibraryVersions;
    std::string LIBS_PATH_LIST = "/home/zaikova/libs";
    std::string CONFIG = "/home/zaikova/conf";

    void DumpConfig(std::vector<LibVersion>& libs) const;
    void Notify(std::string& message);
    void BackupLibMap();
    void ParseLibs(std::vector<LibVersion>& libs);
    std::unordered_set<LibVersion, LibVersionHasher> LibsMap;
};
