#include "LibParser.h"
#include <fstream>
#include <unordered_set>

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
                auto modTime = fs::last_write_time(path);
                using namespace std::chrono;
                auto sctp = time_point_cast<system_clock::duration>(modTime - std::filesystem::file_time_type::clock::now()
                                                                    + system_clock::now());
                version.ModificationTime =  system_clock::to_time_t(sctp);

                LibraryVersions.push_back(version);
            }
        }
    }

    return LibraryVersions;
}

void LibParser::Execute() {
    auto libs = GetLibraryVersions();
    std::ifstream fin;
    fin.open(CONFIG);
    std::ofstream logger("/var/log/lib_change_log", std::ios::app);
    if (fin) {
        int count;
        std::string name, version, time;
        fin >> count;
        std::unordered_set<LibVersion, LibVersionHasher> mp;
        for (size_t i = 0; i < count; ++i) {
            fin >> name >> version >> time;
            mp.insert(LibVersion(name, version, time));
        }
        for (auto& lib: libs) {
            auto it = mp.find(lib);
            if (it != mp.end()) {
                if (it->Version != lib.Version) {
                    logger << "Lib " << lib.LibName << " was updated to " << lib.Version << " " << lib.ModificationTime <<  std::endl;
                }
            } else {
                logger << "Lib " << lib.LibName << " was added with version " << lib.Version << " " << lib.ModificationTime << std::endl;
            }
        }
    }
    logger.close();
    std::ofstream fout(CONFIG, std::ios::trunc);
    fout << libs.size() << std::endl;
    for (auto& lib: libs) {
        fout << lib.LibName << std::endl << lib.Version << std::endl << (unsigned long long)(lib.ModificationTime) << std::endl;
    }
    fout.close();
}