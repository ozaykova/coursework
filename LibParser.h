#pragma once

#include <chrono>
#include <filesystem>
#include <iomanip>
#include <iostream>
#include <string>
#include <vector>
#include <ctime>

namespace fs = std::filesystem;

struct LibVersion {
    LibVersion(std::string& name, std::string version, std::string time) {
        LibName = name;
        Version = version;
        ModificationTime = std::stoull(time);
    }
    LibVersion() {};
    std::string LibName;
    std::string Version;
    std::time_t ModificationTime;

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
    std::string LIBS_PATH_LIST = "/home/olga/libs";
    std::string CONFIG = "/home/olga/conf";
};